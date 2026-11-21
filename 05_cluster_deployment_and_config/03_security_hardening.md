# Security Hardening: Authentication, Authorization, Encryption & Auditing

Out of the box, Cassandra 5.0 has **no security enabled**. Both shipped templates (`conf/cassandra.yaml` and `conf/cassandra_latest.yaml`) default to:

| Setting | Shipped default | Effect |
| :--- | :--- | :--- |
| `authenticator` | `AllowAllAuthenticator` | Anyone who can reach port 9042 can connect, with no credentials. |
| `authorizer` | `AllowAllAuthorizer` | Every connection can read, write, and drop anything. |
| `network_authorizer` | `AllowAllNetworkAuthorizer` | No per-datacenter access restrictions. |
| `cidr_authorizer` | `AllowAllCIDRAuthorizer` | No per-client-IP restrictions. |
| `server_encryption_options.internode_encryption` | `none` | Node-to-node traffic is plaintext. |
| `client_encryption_options.enabled` | `false` | Client traffic is plaintext. |
| `audit_logging_options.enabled` | `false` | No audit trail. |
| JMX (`LOCAL_JMX` in `cassandra-env.sh`) | `yes` | JMX (port 7199) binds to localhost only, **without** authentication. |

Do the steps on this page before you load production data. Changing authentication on a running cluster is possible (Section 2), but it is easier on an empty one.

> [!NOTE]
> `cassandra.yaml` uses the flat form (`authenticator: PasswordAuthenticator`), while `cassandra_latest.yaml` uses the nested form (`authenticator:` / `class_name: PasswordAuthenticator`). Both forms are accepted.

---

## 1. Prepare `system_auth` Replication First

Roles, password hashes and permissions are stored in the `system_auth` keyspace. On a new cluster it is created with `SimpleStrategy` and a replication factor of `max(cassandra.system_auth.default_rf, default_keyspace_rf)`, which is **1** by default (`AuthKeyspace.java`). With RF 1, losing a single node can lock everyone out.

Before enabling authentication, replicate `system_auth` to every datacenter:

```sql
ALTER KEYSPACE system_auth WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east-1': 3,
    'us-west-2': 3
};
```

Then run a full repair of the keyspace on every node so that existing rows reach their new replicas:

```bash
nodetool repair --full system_auth
```

Also set `system_distributed` and `system_traces` to `NetworkTopologyStrategy` while you are there. Repeat these steps whenever you add a datacenter.

Auth reads use `auth_read_consistency_level` (default `LOCAL_QUORUM`) and writes use `auth_write_consistency_level` (default `EACH_QUORUM`). The built-in `cassandra` superuser is the exception: it is read at `QUORUM` across **all** datacenters, which is one more reason to replace it (Section 3).

---

## 2. Enable Authentication & Authorization

In `cassandra.yaml` on every node:

```yaml
authenticator: PasswordAuthenticator
authorizer: CassandraAuthorizer
role_manager: CassandraRoleManager       # required by PasswordAuthenticator; this is already the default
network_authorizer: CassandraNetworkAuthorizer   # optional: restrict roles to datacenters
cidr_authorizer:
  class_name: CassandraCIDRAuthorizer    # optional: restrict roles to client IP ranges
  parameters:
    cidr_authorizer_mode: MONITOR        # MONITOR (log only, the default) or ENFORCE
```

Then do a **rolling restart**, one node at a time.

* While the restart is in progress, nodes that already require credentials and nodes that don't run side by side. Clients must already be sending credentials (drivers ignore credentials that a node does not ask for), so deploy the application change first.
* When a node starts with `CassandraRoleManager` and no roles exist, it creates the default superuser `cassandra` / `cassandra`. It does this after `cassandra.superuser_setup_delay_ms`, which defaults to 10 seconds.

### CIDR authorizer notes
* Its checks apply only to non-superusers unless you set `cidr_checks_for_superusers: true`.
* Start in `MONITOR` mode and check the logs for warnings before you switch to `ENFORCE`.
* CIDR checks cannot be applied to JMX calls.
* Run `nodetool reloadcidrgroupscache` to refresh the CIDR groups cache immediately.

---

## 3. Replace the Default `cassandra` Superuser

The default credentials are public knowledge, so replace them straight away:

```sql
-- Log in once with the default account
-- cqlsh -u cassandra -p cassandra <node_ip>

CREATE ROLE dba WITH SUPERUSER = true AND LOGIN = true AND PASSWORD = '<strong-password>';

-- Log out, then log back in as the new superuser:
-- cqlsh -u dba <node_ip>

DROP ROLE cassandra;          -- or: ALTER ROLE cassandra WITH SUPERUSER = false AND LOGIN = false;
```

Dropping `cassandra` is safe. The node only re-creates it when `system_auth.roles` contains **no roles at all** (`CassandraRoleManager.hasExistingRoles()`).

### Application roles: least privilege
```sql
CREATE ROLE app_rw WITH LOGIN = true AND PASSWORD = '<secret>';
GRANT SELECT ON KEYSPACE production_keyspace TO app_rw;
GRANT MODIFY ON KEYSPACE production_keyspace TO app_rw;

-- Restrict to one datacenter (needs CassandraNetworkAuthorizer)
ALTER ROLE app_rw WITH ACCESS TO DATACENTERS {'us-east-1'};
```

Masked columns (see [Consistency & Transactions](../03_application_development/04_consistency_and_transactions.md)) add two more permissions, `UNMASK` and `SELECT_MASKED`. Superusers have both by default; regular roles have neither.

---

## 4. Client-to-Node Encryption (`client_encryption_options`)

The shipped yaml recommends a two-step rollout so that clients aren't cut off:

```yaml
client_encryption_options:
  enabled: true
  optional: true            # Step 1: accept both TLS and plaintext on 9042. Rolling restart.
  keystore: /etc/cassandra/certs/keystore.jks
  keystore_password: <password>      # must be set explicitly in 5.0 (there is no code default any more)
  require_client_auth: false         # true = clients must present certificates (mTLS)
  # truststore: /etc/cassandra/certs/truststore.jks
  # truststore_password: <password>
```

1. Set `enabled: true` and `optional: true`, then do a rolling restart. Move every client to TLS.
2. Set `optional: false` (or remove the line), then do another rolling restart. Port 9042 now accepts only TLS.

> [!WARNING]
> **Use the single port 9042.** The dual-port setup (`native_transport_port_ssl`, commonly 9142) is **deprecated in 5.0** and will be removed. Nodes using it were not correctly identified in `system.peers` and in server-sent events, which broke driver connection pools (CASSANDRA-19392).

For PEM files instead of JKS keystores, set `ssl_context_factory.class_name: org.apache.cassandra.security.PEMBasedSslContextFactory`.

---

## 5. Node-to-Node Encryption (`server_encryption_options`)

```yaml
server_encryption_options:
  internode_encryption: all      # none | dc | rack | all
  optional: true                 # transitional: accept encrypted and plaintext on storage_port
  legacy_ssl_storage_port_enabled: false
  keystore: /etc/cassandra/certs/keystore.jks
  keystore_password: <password>
  truststore: /etc/cassandra/certs/truststore.jks
  truststore_password: <password>
  require_client_auth: true      # nodes verify each other's certificates
  require_endpoint_verification: true   # the certificate host name must match the peer
```

* **One port.** Since 4.0, encrypted and plaintext internode traffic share `storage_port` (**7000**). `ssl_storage_port` (7001) is used only if `legacy_ssl_storage_port_enabled: true`, which exists for clusters that still contain pre-4.0 nodes. On a 5.0-only cluster you do not need to open 7001.
* **Rollout.** Deploy keystores everywhere. Set `internode_encryption: all` with `optional: true` and do a rolling restart. Then set `optional: false` and do another rolling restart.
* **Mutual TLS between nodes.** To also authenticate peers by certificate, configure `internode_authenticator` with `org.apache.cassandra.auth.MutualTlsInternodeAuthenticator` (Section 6).

### Rotating certificates
Cassandra periodically checks the keystore and truststore files for changes and hot-reloads them (`SSLFactory.checkCertFilesForHotReloading`). To force an immediate reload after replacing the files:

```bash
nodetool reloadssl
```

---

## 6. Certificate-Based Authentication (mTLS)

Cassandra 5.0 can authenticate clients and nodes by X.509 certificate:

| Class | Purpose |
| :--- | :--- |
| `org.apache.cassandra.auth.MutualTlsAuthenticator` | Clients authenticate with a certificate only. |
| `org.apache.cassandra.auth.MutualTlsWithPasswordFallbackAuthenticator` | Clients use a certificate if they present one, and a password otherwise. Useful during migration. |
| `org.apache.cassandra.auth.MutualTlsInternodeAuthenticator` | Nodes authenticate each other (`internode_authenticator`). |

```yaml
authenticator:
  class_name: org.apache.cassandra.auth.MutualTlsAuthenticator
  parameters:
    validator_class_name: org.apache.cassandra.auth.SpiffeCertificateValidator
```

The validator extracts an identity from the certificate. The shipped `SpiffeCertificateValidator` reads a SPIFFE URI from the SAN. To map identities to roles:

```sql
ADD IDENTITY 'spiffe://example.com/app/orders' TO ROLE 'app_rw';
```

Client mTLS also needs `client_encryption_options.require_client_auth: true` and a truststore.

---

## 7. Securing JMX (Port 7199)

`nodetool` talks to Cassandra over JMX. Whoever controls JMX can drain, decommission, or truncate a node.

* **Default (`LOCAL_JMX=yes`)**: JMX binds to localhost only, with `jmxremote.authenticate=false`. Anyone with a shell on the host can use it. This is acceptable only when host access is tightly controlled.
* **Remote JMX**: set `LOCAL_JMX=no` in `conf/cassandra-env.sh`. Authentication is then turned on (`-Dcom.sun.management.jmxremote.authenticate=true`) and backed by `/etc/cassandra/jmxremote.password`. Restrict that file with `chmod 400`.
* **Use Cassandra roles for JMX**: uncomment the `cassandra.jmx.remote.login.config=CassandraLogin` and `java.security.auth.login.config` lines in `cassandra-env.sh`. Login then goes through the configured `IAuthenticator`, using the sample `conf/cassandra-jaas.config`. The same file has an option for authorizing JMX calls through `CassandraAuthorizer`.
* **JMX over TLS**: see the commented `com.sun.management.jmxremote.ssl*` options in `cassandra-env.sh`.
* Whichever mode you use, never expose 7199 beyond your bastion or monitoring hosts.

---

## 8. Audit Logging

Audit logging records every CQL request and authentication attempt.

```yaml
audit_logging_options:
  enabled: true
  logger:
    - class_name: BinAuditLogger      # compact binary (Chronicle Queue); read it with auditlogviewer
    # - class_name: FileAuditLogger   # plain text via logback
  # audit_logs_dir defaults to <cassandra.logdir>/audit
  included_categories: AUTH,DCL,DDL   # QUERY, DML, DDL, DCL, OTHER, AUTH, ERROR, PREPARE
  excluded_keyspaces: system,system_schema,system_virtual_schema
  roll_cycle: HOURLY
  max_log_size: 17179869184           # 16 GiB, after which the oldest files are deleted unless archive_command is set
```

* You can also turn it on and off at runtime with `nodetool enableauditlog` / `nodetool disableauditlog`; `nodetool getauditlog` shows the current configuration.
* Read binary logs with `tools/bin/auditlogviewer <audit_dir>`.
* Logging every `QUERY`/`DML` event on a busy cluster is expensive. Start with `AUTH,DCL,DDL`.

---

## 9. Hardening Checklist

- [ ] `system_auth`, `system_distributed` and `system_traces` use `NetworkTopologyStrategy` with RF 3 per DC, and have been repaired.
- [ ] `PasswordAuthenticator` (or mTLS) and `CassandraAuthorizer` are enabled.
- [ ] The default `cassandra` role has been dropped or disabled.
- [ ] Applications use least-privilege roles, not a superuser.
- [ ] Client TLS is on port 9042 with `optional: false`. 9142 is not used.
- [ ] Internode TLS is `internode_encryption: all` with `require_client_auth` and `require_endpoint_verification`.
- [ ] Keystore and truststore passwords are set explicitly in the yaml.
- [ ] JMX is local-only or authenticated, and 7199 is firewalled.
- [ ] Audit logging is enabled for at least `AUTH,DCL,DDL`.
- [ ] Firewalls expose only 7000 (between nodes) and 9042 (to application subnets).
