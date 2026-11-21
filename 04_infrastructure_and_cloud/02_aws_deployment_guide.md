# AWS Deployment Guide

Running Apache Cassandra 5.0 on AWS means mapping Cassandra's datacenters and racks onto Regions and Availability Zones, choosing between instance-store NVMe and EBS, and configuring networking and backups. Instance specs and prices change; check current AWS documentation before sizing.

---

## 1. EC2 Instance Selection: Instance-Store NVMe vs. EBS

| | Instance-store NVMe (e.g. `i4i`, `i3en`) | EBS `gp3` / `io2` (e.g. `m6i`, `r6i`) |
| :--- | :--- | :--- |
| Latency | Local device, lowest latency | Network-attached, higher and more variable latency |
| Throughput / IOPS | High, fixed by instance size | Provisioned per volume; capped by the instance's EBS bandwidth |
| Durability | **Ephemeral.** Data is lost if the instance stops or is terminated. A replacement node re-streams its data from replicas. | Persists independently of the instance. A volume can be reattached to a replacement instance. |
| Operations | Requires reliable node replacement and backups | Simpler recovery; snapshots possible at the EBS layer |

Cassandra's replication (RF=3 across 3 AZs) is what protects data on instance storage, not the disk. With instance storage, practise node replacement (see [disaster recovery](../07_disaster_recovery/01_backup_and_disaster_recovery.md)) before production.

### Example instance families

| Instance type | vCPU | RAM | Storage | Typical use |
| :--- | :--- | :--- | :--- | :--- |
| `i4i.2xlarge` | 8 | 64 GiB | 1 × 1,875 GB NVMe | General production baseline |
| `i4i.4xlarge` | 16 | 128 GiB | 1 × 3,750 GB NVMe | Higher concurrency, larger data per node |
| `i3en.3xlarge` | 12 | 96 GiB | 1 × 7,500 GB NVMe | Dense storage, lower request rates |
| `m6i.2xlarge` + `gp3` | 8 | 32 GiB | EBS, provisioned IOPS/throughput | Moderate load, simpler recovery |

Very large per-node data (multiple TB) makes streaming, repair and replacement slow. Keep data per node at a size you can re-stream within your recovery-time objective.

---

## 2. Snitch Selection: `Ec2Snitch` vs. `Ec2MultiRegionSnitch` vs. `GossipingPropertyFileSnitch`

| Snitch | Use when | Addressing |
| :--- | :--- | :--- |
| `GossipingPropertyFileSnitch` | Any topology, including multi-region over VPC peering or Transit Gateway. Most portable; DC/rack set in `cassandra-rackdc.properties`. | Private IPs |
| `Ec2Snitch` | Single region. DC and rack come from instance metadata. | **Private IPs only.** Will not work across regions. |
| `Ec2MultiRegionSnitch` | Multiple regions connected **over public IPs**. | Sets `broadcast_address` to the instance's **public** IP; within a region it switches to the private IP after connecting. |

### How the EC2 snitches resolve DC and rack

Both query the instance metadata service for the availability zone. They use **IMDSv2** by default (`ec2_metadata_type=v2` in `cassandra-rackdc.properties`; set `v1` only if IMDSv2 is unavailable).

Naming depends on `ec2_naming_scheme` in `cassandra-rackdc.properties`:

| `ec2_naming_scheme` | AZ `us-east-1a` → DC | → Rack |
| :--- | :--- | :--- |
| `standard` **(default)** | `us-east-1` | `us-east-1a` |
| `legacy` (pre-4.1 behaviour) | `us-east` | `1a` |

Clusters that started with the old naming must keep `legacy`. The snitch refuses to start if the existing DC/rack names don't match the configured scheme.

Optional suffix (e.g. to distinguish two clusters in one region):
```ini
# conf/cassandra-rackdc.properties
dc_suffix=_prod        # DC becomes us-east-1_prod
```

The DC name you get is what you must use in `NetworkTopologyStrategy`, e.g. `{'us-east-1': 3}`.

### `Ec2MultiRegionSnitch` requirements
If you choose it:
* Every node needs a public IP (Elastic IPs are recommended so they survive stop/start).
* **Seeds must be listed by public IP.**
* `listen_address` stays the private IP. Don't set `broadcast_address`; the snitch sets it. If `broadcast_rpc_address` is unset, the snitch sets it to the public IP too, so clients connect via public IPs unless you set it.
* Security-group rules that reference another security group only match traffic arriving on **private** IPs. Traffic to public IPs needs **CIDR rules** listing the other nodes' public IPs (or Elastic IP ranges) for port 7000.
* Encrypt internode traffic (`server_encryption_options.internode_encryption: all` or `dc`), because it crosses the public internet.

For most new deployments, VPC peering or Transit Gateway with private IPs and `GossipingPropertyFileSnitch` is simpler and avoids public exposure.

---

## 3. Availability Zones & Placement Groups

Deploy each region across **3 AZs**, with the same number of nodes in each:

```
VPC 10.0.0.0/16 (us-east-1)
├── Subnet us-east-1a (rack us-east-1a): Node 1, Node 4
├── Subnet us-east-1b (rack us-east-1b): Node 2, Node 5
└── Subnet us-east-1c (rack us-east-1c): Node 3, Node 6
```

With `NetworkTopologyStrategy` `{'us-east-1': 3}`, Cassandra places one replica per rack, so one per AZ. If one AZ fails, `LOCAL_QUORUM` (2 of 3) reads and writes still succeed.

### Placement groups
* `spread` or `partition` placement groups keep instances in an AZ on separate hardware.
* Avoid `cluster` placement groups: they pack instances close together, so one hardware fault can take out several replicas.

---

## 4. Network MTU

Within a VPC, EC2 supports jumbo frames (**MTU 9001**). Larger frames reduce per-packet overhead for bulk transfers such as streaming and repair. Most current AMIs already set MTU 9001 on supported instances; check with `ip link show`.

> [!WARNING]
> Jumbo frames apply **only within a VPC** (and some peering setups). Traffic through an internet gateway, inter-region VPC peering, or VPN is limited to **1500** (lower for VPN). Mixed MTUs depend on Path MTU Discovery, which breaks if ICMP "fragmentation needed" messages are blocked; connections then hang on large packets. For multi-region clusters, allow ICMP type 3 code 4 in security groups and NACLs, or use MTU 1500 on interfaces carrying cross-region traffic.

```bash
ip link show eth0                       # check current MTU
sudo ip link set dev eth0 mtu 9001      # not persistent; set it in netplan/NetworkManager config
```

---

## 5. Security Groups & Ports

| Port | Source | Purpose |
| :--- | :--- | :--- |
| **7000** | Cassandra node SG (CIDR rules for public IPs with `Ec2MultiRegionSnitch`) | Internode messaging, gossip and streaming. Since 4.0 this single port carries both plaintext and TLS internode traffic. |
| 7001 | Only if `legacy_ssl_storage_port_enabled: true` | Legacy dedicated TLS internode port, for upgrades from pre-4.0 clusters. Normally closed. |
| **7199** | Bastion / admin hosts only | JMX (nodetool). Bound to localhost by default; enable remote JMX only with authentication and TLS. |
| **9042** | Application SG | CQL native transport (plaintext or TLS). |
| 9142 | Only if `native_transport_port_ssl` is set | Dedicated TLS CQL port. **Deprecated in 5.0**; prefer TLS on 9042. |
| 9100 | Prometheus | *External:* Prometheus `node_exporter` (not part of Cassandra). |
| 7070 (or your choice) | Prometheus | *External:* a JMX/metrics exporter agent you install (not part of Cassandra). |

See [03_security_hardening.md](../05_cluster_deployment_and_config/03_security_hardening.md) for enabling TLS and authentication.

---

## 6. Backups to S3

Snapshots are hard links in each table's `snapshots/<tag>/` directory. Upload **only the snapshot you just took**, and include the schema it contains (`schema.cql` and `manifest.json` are written into every snapshot directory).

```bash
#!/usr/bin/env bash
set -euo pipefail
TAG="backup_$(date +%Y%m%d_%H%M%S)"
DATA_DIR=/mnt/cassandra/data
DEST="s3://my-cassandra-backups/$(hostname)/${TAG}"

nodetool snapshot -t "${TAG}"                 # flushes memtables first by default

# Upload only this tag (SSTables + schema.cql + manifest.json)
aws s3 sync "${DATA_DIR}/" "${DEST}/data/" \
    --exclude "*" --include "*/snapshots/${TAG}/*" \
    --storage-class STANDARD_IA --only-show-errors

# Record this node's tokens: required to restore onto a same-size cluster
nodetool info -T | grep '^Token' | awk '{print $3}' | paste -sd, - > /tmp/tokens.txt
aws s3 cp /tmp/tokens.txt "${DEST}/tokens.txt"

nodetool clearsnapshot -t "${TAG}"
```

* Use **S3 lifecycle rules** for retention, e.g. transition to Glacier Flexible Retrieval after 30 days and expire after 90. Note that Glacier restores take hours, which adds to your recovery time.
* Prefer an IAM instance role over static keys, and enable bucket encryption and versioning.
* Snapshots of different nodes are taken at slightly different times. They are not a cluster-wide consistent point in time.
* For restore procedures, see [disaster recovery](../07_disaster_recovery/01_backup_and_disaster_recovery.md).
