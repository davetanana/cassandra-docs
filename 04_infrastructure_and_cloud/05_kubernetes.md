# Cassandra 5.0 on Kubernetes

> [!CAUTION]
> Commands on this page can change or delete data and affect running clusters. Try them on a test or staging cluster first, and read the [disclaimer](../README.md#disclaimer). The guide is provided "as is", without warranty.

Kubernetes can run Cassandra well, but only with an operator that understands Cassandra. This page explains what the operator does for you, gives a minimal Cassandra 5.0 datacenter definition, and lists the Cassandra rules that still apply inside Kubernetes.

The examples use **cass-operator** from the K8ssandra project (Apache-2.0), the most widely used open-source Cassandra operator. Field names and default behaviors below were checked against the cass-operator source (`v1.33.x`, November 2026). K8ssandra also ships `k8ssandra-operator`, which wraps cass-operator and adds Reaper (repair), Medusa (backups) and multi-cluster support.

> [!NOTE]
> **Not validated in `test_env`.** The Cassandra settings on this page are the same ones validated elsewhere in the guide. The operator behavior comes from reading cass-operator's source, not from a test run. Check the [cass-operator README](https://github.com/k8ssandra/cass-operator) for the release that matches your Kubernetes version.

---

## 1. Should you run Cassandra on Kubernetes?

| Run it on Kubernetes when… | Prefer VMs or bare metal when… |
| :--- | :--- |
| Your team already runs stateful workloads on Kubernetes and has on-call experience with it | Nobody on the team has debugged Kubernetes storage or scheduling under pressure |
| You want the same deployment and config workflow as your applications | You need every bit of disk and network performance, or very large nodes |
| You run many small clusters (per team, per tenant, per test environment) | You run a few large, long-lived clusters |

Either way, the [mental model](../01_architecture_and_mental_model/01_mental_model.md) is the same: each Cassandra node owns token ranges and data on its own disk. Kubernetes doesn't change that. It only changes how nodes are scheduled, restarted and replaced.

---

## 2. Use an operator, not a hand-written StatefulSet

A plain StatefulSet starts and stops pods, but it doesn't know Cassandra's rules. An operator adds the parts that need Cassandra knowledge. According to its README, cass-operator:

* bootstraps one node at a time, so token allocation stays correct (see the [deployment runbook](../05_cluster_deployment_and_config/02_cluster_deployment_runbook.md#5-bootstrap-sequence));
* manages seeds: one per rack, or three per datacenter, whichever is more;
* renders `cassandra.yaml` and the JVM options from the custom resource;
* does rolling restarts when you change the resource;
* spreads replicas across racks, and pins each rack to a zone;
* scales racks up evenly, and scales down by **decommissioning** nodes, not by deleting pods;
* replaces dead nodes, and runs cleanup and other node tasks through `CassandraTask` resources.

The Cassandra container runs the **Management API**, an agent that starts Cassandra and that the operator calls instead of using `nodetool` over JMX. `kubectl exec` with `nodetool` still works for diagnosis.

---

## 3. A minimal Cassandra 5.0 datacenter

Install cass-operator first by following its README (Helm or Kustomize). Then a datacenter is one `CassandraDatacenter` resource:

```yaml
apiVersion: cassandra.datastax.com/v1beta1
kind: CassandraDatacenter
metadata:
  name: dc1                      # becomes the Cassandra datacenter name (drivers' local DC)
spec:
  clusterName: prod-cluster      # cluster_name; can't be changed later
  serverType: cassandra
  serverVersion: "5.0.9"         # an exact 5.0.x version the operator has an image for
  size: 3
  racks:                         # one rack per zone; RF 3 then puts one replica in each zone
    - name: r1
      nodeAffinityLabels: { topology.kubernetes.io/zone: <zone_a> }
    - name: r2
      nodeAffinityLabels: { topology.kubernetes.io/zone: <zone_b> }
    - name: r3
      nodeAffinityLabels: { topology.kubernetes.io/zone: <zone_c> }
  storageConfig:
    cassandraDataVolumeClaimSpec:
      storageClassName: <fast_local_or_ssd_class>
      accessModes: [ReadWriteOnce]
      resources:
        requests:
          storage: 500Gi
  resources:
    requests: { cpu: "4", memory: 32Gi }
    limits:   { cpu: "4", memory: 32Gi }
  config:
    jvm-server-options:
      initial_heap_size: "8G"
      max_heap_size: "8G"
    cassandra-yaml:              # 5.0 key names, as in the configuration page
      num_tokens: 16
      authenticator: PasswordAuthenticator
      authorizer: CassandraAuthorizer
      role_manager: CassandraRoleManager
```

Replace each `<…>` value: the three zone names your cloud uses, and a StorageClass backed by local NVMe or SSD block storage. The sizes are illustrative. Work out the node count and machine type with [capacity planning](../05_cluster_deployment_and_config/05_capacity_planning.md), then set the pod resources with the [configuration and tuning](../05_cluster_deployment_and_config/01_configuration_and_tuning.md) and [Java & JVM flavors](01_java_and_jvm_flavors.md) pages.

What each part does:
* **`metadata.name`** becomes the Cassandra datacenter name, unless you set `spec.datacenterName`. Use it in `NetworkTopologyStrategy` replication and as the driver's local datacenter.
* **`racks` with `nodeAffinityLabels`** pin each rack to a zone. Use as many racks as your replication factor, so that losing a zone loses one replica of each range. The older `zone` field is deprecated.
* **`superuserSecretName`** (not shown) names a Secret with the superuser's credentials. If you leave it out, the operator generates one. Either way, follow [security hardening](../05_cluster_deployment_and_config/03_security_hardening.md) for `system_auth` replication, TLS and roles.
* **`managementApiAuth`**: the operator's samples use `insecure: {}`. In production, configure mutual TLS for the Management API (see the cass-operator docs).

---

## 4. What cass-operator does by default

These defaults come from the operator source, and each one matches a Cassandra rule elsewhere in this guide:

| Default | Why it matters |
| :--- | :--- |
| **One Cassandra pod per Kubernetes worker.** The pod template gets a *required* anti-affinity rule. Setting `allowMultipleNodesPerWorker: true` removes it, and the operator then refuses the resource unless CPU and memory requests **and** limits are all set. | Two replicas on one worker means one machine failure loses two replicas. |
| **A PodDisruptionBudget of `size - 1` available pods.** Node drains and cluster upgrades can take down only one Cassandra pod at a time. `spec.maxUnavailable` raises it, capped at one rack's worth of pods. | With RF 3 and `LOCAL_QUORUM`, losing one replica is safe and losing two in the same range is not. |
| **A preStop hook that drains the node** through the Management API before the container stops. | The same as `nodetool drain` in a [rolling restart](../06_operations_and_housekeeping/02_housekeeping_and_automations.md): memtables are flushed and clients move away first, so commitlog replay is short. |
| **Seeds managed for you**, one per rack or three per datacenter. | Seeds must not all be in one failure domain. |

---

## 5. Cassandra rules that still apply

Kubernetes doesn't remove any of the operational work in this guide.

* **Storage.** Use `ReadWriteOnce` block storage: local NVMe (with a local-volume provisioner) or SSD-backed cloud disks. Never use network filesystems (NFS, RWX volumes). Local NVMe gives the best performance, but its data is lost if the pod moves to another worker, so plan for node replacement. The cloud guides ([AWS](02_aws_deployment_guide.md), [GCP](03_gcp_deployment_guide.md), [Azure](04_azure_deployment_guide.md)) compare the disk options.
* **Memory.** The container's memory limit must cover the heap **and** off-heap memory: direct memory, memtables if `memtable_allocation_type` puts them off-heap, the chunk cache, bloom filters and compression metadata. Set the heap explicitly; don't size it from the limit. If the limit is too tight, the kernel kills the container (`OOMKilled`) with no Java error in the log. See [Java & JVM flavors](01_java_and_jvm_flavors.md).
* **CPU.** Set CPU requests equal to limits. CPU throttling under a limit causes the same latency spikes as a GC pause.
* **Capacity.** With one Cassandra pod per worker, the node count from [capacity planning](../05_cluster_deployment_and_config/05_capacity_planning.md) is the worker count. Use the worker's machine type as the profile: a PVC on a cloud disk (EBS, Hyperdisk, Premium SSD v2) is the network-storage case, with its per-VM IOPS cap, and a local-volume provisioner on NVMe is the local case. The Linux page cache that serves most reads is charged to the pod's memory limit, so the memory above the heap and off-heap allowance decides the cache hit rate (`--cache-hit`). Benchmark with the pod limits you will run in production.
* **Repair.** Data still needs repair within `gc_grace_seconds`. Use the built-in [auto-repair](../06_operations_and_housekeeping/06_auto_repair.md) (5.0.8+) or Reaper (included in k8ssandra-operator).
* **Backups.** Snapshots on a PVC are not backups. Copy them off the cluster: Medusa (included in k8ssandra-operator) or the procedures in [backup and disaster recovery](../07_disaster_recovery/01_backup_and_disaster_recovery.md).
* **Clients outside Kubernetes.** Drivers connect to every node's address, not to one load-balanced address. Clients outside the Kubernetes network need routable pod IPs, host networking, or a driver address translator. A single `LoadBalancer` Service in front of Cassandra doesn't work for token-aware drivers.
* **Monitoring.** Use the same metrics and thresholds as on VMs; see [monitoring and observability](../06_operations_and_housekeeping/03_monitoring_and_observability.md).

> [!WARNING]
> **Don't delete PersistentVolumeClaims to "fix" a pod.** The PVC holds the node's data and its identity (host ID and tokens). Deleting it and letting the pod start empty is a node replacement done wrong. Use the operator's replace-node task, which follows the [replacement procedure](../07_disaster_recovery/01_backup_and_disaster_recovery.md).
