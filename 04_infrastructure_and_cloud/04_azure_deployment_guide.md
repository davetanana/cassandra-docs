# Azure Deployment Guide

> [!CAUTION]
> Commands on this page can change or delete data and affect running clusters. Try them on a test or staging cluster first, and read the [disclaimer](../README.md#disclaimer). The guide is provided "as is", without warranty.

Running Apache Cassandra 5.0 on Microsoft Azure means choosing between local NVMe and managed disks, enabling Accelerated Networking, mapping datacenters and racks onto regions and Availability Zones, and configuring backups. VM specs change; check current Azure documentation before sizing.

---

## 1. VM Selection: Local NVMe vs. Managed Disks

| | Lsv4 / Lsv3 / Lasv3 (local NVMe) | Dsv6 / Esv5 / Ebdsv5 + Premium SSD v2 or Ultra Disk |
| :--- | :--- | :--- |
| Latency | Lowest, physically attached | Network-attached, higher latency |
| Durability | **Ephemeral.** Local NVMe data is lost on deallocation, resize or host failure. Recovery is by re-streaming from replicas. | Persists; can be attached to a replacement VM |
| Performance | Fixed by VM size | Provisioned IOPS/throughput per disk, capped by the VM's disk limits |

### Example VM sizes

| VM size | vCPU | RAM | Storage |
| :--- | :--- | :--- | :--- |
| `Standard_L8s_v4` | 8 | 64 GiB | 4 × 480 GB local NVMe (550,000 read IOPS; stripe them, or list each in `data_file_directories`) |
| `Standard_L8s_v3` | 8 | 64 GiB | 1 × 1.92 TB local NVMe |
| `Standard_L16s_v3` | 16 | 128 GiB | 2 × 1.92 TB local NVMe (stripe with RAID0, or list both in `data_file_directories`) |
| `Standard_D8s_v6` | 8 | 32 GiB | No local disk; Premium SSD v2 up to 16,667 IOPS and 496 MB/s per VM (uncached) |
| `Standard_E16bds_v5` | 16 | 128 GiB | Premium SSD v2, provisioned IOPS/throughput |

Lsv4 is the newer generation of Lsv3 at the same list price. Dsv6 is the newest general-purpose series. Its per-VM disk limit, not the disk's own limit, caps IOPS, so read-heavy workloads need more Dsv6 nodes than L-series nodes. [Capacity planning](../05_cluster_deployment_and_config/05_capacity_planning.md#11-machine-profiles-and-their-sources) compares them, with rough cost. For the 99.9% single-VM SLA, every OS and data disk must be Premium SSD, Premium SSD v2 or Ultra Disk.

On L-series VMs, the NVMe devices are raw. Partition, format and mount them yourself (at every start after deallocation), and refer to them by stable identifiers, not device order.

---

## 2. Accelerated Networking

Enable **Accelerated Networking** on every Cassandra NIC. It uses SR-IOV so the VM talks to the physical NIC directly, bypassing the host's virtual switch. Microsoft documents lower latency, lower jitter and lower CPU use with it; it's supported on most D/E/L-series sizes at no extra cost.

```bash
# The SR-IOV virtual function appears as a Mellanox device:
lspci | grep -i mellanox
# The accelerated path shows as a second interface bonded to eth0:
ip link show
```

---

## 3. Snitch: `AzureSnitch`

```yaml
# conf/cassandra.yaml
endpoint_snitch: AzureSnitch
```

### How `AzureSnitch` resolves DC and rack
1. Calls the Instance Metadata Service: `http://169.254.169.254/metadata/instance/compute?api-version=<azure_api_version>&format=json` with header `Metadata: true`. The default API version is `2021-12-13`.
2. **Datacenter** = the `location` field (e.g. `eastus2`), plus `dc_suffix` if set.
3. **Rack** = `rack-` + the `zone` field (e.g. `rack-1`, `rack-2`, `rack-3`).
4. If the VM has no zone, **rack** = `rack-` + `platformFaultDomain` (e.g. `rack-0`, `rack-1`).

Both are set in `conf/cassandra-rackdc.properties`:
```ini
# azure_api_version=2021-12-13   # default
dc_suffix=_prod                   # DC becomes eastus2_prod
```

> [!NOTE]
> A VM's zone or fault domain becomes its rack, and **a node cannot change rack after joining**. Don't mix zonal and non-zonal VMs in one DC, and with fault domains make sure the replacement for a node lands in the same fault domain.

`GossipingPropertyFileSnitch` is a portable alternative where you set DC and rack yourself.

---

## 4. Availability Zones & Placement

```
Virtual Network 10.1.0.0/16 (eastus2)
├── Zone 1 (rack-1): Node 1, Node 4
├── Zone 2 (rack-2): Node 2, Node 5
└── Zone 3 (rack-3): Node 3, Node 6
```

With `NetworkTopologyStrategy` `{'eastus2': 3}`, Cassandra places one replica per zone. If one zone fails, `LOCAL_QUORUM` still succeeds.

### Proximity Placement Groups (PPG)
A PPG places VMs physically close together for lower latency. A PPG is tied to one datacenter (so effectively one zone). Use **one PPG per zone** at most, never one PPG for the whole cluster, which would force every node into the same zone and defeat zone-level fault tolerance. PPGs can also make allocation fail when capacity is tight. Most clusters don't need them.

### Network security
Allow port 7000 (internode) between Cassandra nodes and 9042 (CQL) from application subnets in the NSG. Keep 7199 (JMX) restricted to admin hosts. See [03_security_hardening.md](../05_cluster_deployment_and_config/03_security_hardening.md).

---

## 5. Backups to Azure Blob Storage

Upload **only the snapshot you just took**. Each snapshot directory contains the SSTables plus `schema.cql` and `manifest.json`.

```bash
#!/usr/bin/env bash
set -euo pipefail
TAG="backup_$(date +%Y%m%d_%H%M%S)"
DATA_DIR=/mnt/cassandra/data
DEST="https://myaccount.blob.core.windows.net/cassandra-backups/$(hostname)/${TAG}"

nodetool snapshot -t "${TAG}"

# Authenticate with a managed identity (azcopy login --identity) or a SAS token.
# --include-regex matches the relative path, so only this tag's directories are copied.
azcopy copy "${DATA_DIR}/*" "${DEST}/data/" \
    --recursive=true \
    --include-regex ".*/snapshots/${TAG}/.*"

# Record this node's tokens for same-topology restores
nodetool info -T | grep '^Token' | awk '{print $3}' | paste -sd, - > /tmp/tokens.txt
azcopy copy /tmp/tokens.txt "${DEST}/tokens.txt"

nodetool clearsnapshot -t "${TAG}"
```

* **Tiers**: use Blob Lifecycle Management to move backups to Cool (e.g. after 30 days) and Archive (e.g. after 90). Archive-tier blobs must be rehydrated before they can be read, which takes hours, so keep recent backups in Hot or Cool.
* Enable soft delete or immutability policies on the container to protect backups from accidental or malicious deletion.
* For restore procedures, see [disaster recovery](../07_disaster_recovery/01_backup_and_disaster_recovery.md).
