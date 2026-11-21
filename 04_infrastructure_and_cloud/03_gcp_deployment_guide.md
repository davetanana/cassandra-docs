# GCP Deployment Guide

Running Apache Cassandra 5.0 on Google Compute Engine (GCE) means choosing between Local SSD and network block storage, mapping datacenters and racks onto regions and zones, and configuring the global VPC and backups. Machine specs and Local SSD performance change; check current GCP documentation before sizing.

---

## 1. Storage: Local SSD vs. Persistent Disk / Hyperdisk

| | Local SSD (NVMe, 375 GB devices) | Persistent Disk (`pd-ssd`, `pd-balanced`) / Hyperdisk |
| :--- | :--- | :--- |
| Latency | Lowest, physically attached | Network-attached, higher latency |
| Capacity | Fixed number of 375 GB devices per machine type | Sized and (for Hyperdisk) performance-provisioned per volume |
| Durability | **Ephemeral.** Data is lost when the VM stops or is deleted (live migration preserves it). Recovery is by re-streaming from replicas. | Persists independently of the VM; can be reattached |
| Multi-device | Several devices are usually striped (RAID0) into one volume | Single volume |

### Example machine types

| Machine type | vCPU | RAM | Storage |
| :--- | :--- | :--- | :--- |
| `n2-standard-16` | 16 | 64 GB | 4 × 375 GB Local SSD (1.5 TB RAID0) |
| `n2-highmem-16` | 16 | 128 GB | 4 × 375 GB Local SSD |
| `c2-standard-16` | 16 | 64 GB | Local SSD; high per-core clock speed |
| `n2-standard-16` | 16 | 64 GB | Hyperdisk Balanced or `pd-ssd`, e.g. 2 TB |

Local SSD performance scales with the number of devices attached; see GCP's Local SSD performance table for current figures.

---

## 2. Striping Local SSDs with RAID0 (`mdadm`)

> [!CAUTION]
> **Never use `/dev/nvme0n1`-style names here.** On many machine types the boot disk is also an NVMe device, and NVMe numbering can change between boots. Running `mdadm --create` on the wrong device **destroys the boot disk**. Use the stable `/dev/disk/by-id/google-local-nvme-ssd-*` links (`google-local-ssd-*` for SCSI Local SSD).

```bash
# 1. Install mdadm
sudo apt-get update && sudo apt-get install -y mdadm

# 2. Find the Local SSDs by stable ID and check that the boot disk is NOT in the list
ls -l /dev/disk/by-id/ | grep -E 'google-local-(nvme-)?ssd'
lsblk -o NAME,SIZE,MOUNTPOINT    # the boot disk has / mounted; the Local SSDs are 375G and unmounted

# 3. Build the array from the by-id paths only
LOCAL_SSDS=$(ls /dev/disk/by-id/google-local-nvme-ssd-*)
sudo mdadm --create /dev/md0 --level=0 \
    --raid-devices=$(echo "${LOCAL_SSDS}" | wc -w) ${LOCAL_SSDS}

# 4. XFS with stripe alignment (su = mdadm chunk size, default 512k; sw = device count)
sudo mkfs.xfs -f /dev/md0

# 5. Mount
sudo mkdir -p /mnt/cassandra
sudo mount -o defaults,noatime /dev/md0 /mnt/cassandra
sudo chown -R cassandra:cassandra /mnt/cassandra

# 6. Persist the array and mount
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf
sudo update-initramfs -u
echo "UUID=$(sudo blkid -s UUID -o value /dev/md0) /mnt/cassandra xfs defaults,noatime,nofail 0 2" | sudo tee -a /etc/fstab
```

`mkfs.xfs` detects the md stripe geometry automatically, so explicit `su`/`sw` options are only needed if you change the chunk size. Use `nofail` in `/etc/fstab` so that a VM whose Local SSDs were lost still boots. If the VM is stopped (not live-migrated), the Local SSD data is gone: recreate the array and replace the node.

---

## 3. Snitch: `GoogleCloudSnitch`

```yaml
# conf/cassandra.yaml
endpoint_snitch: GoogleCloudSnitch
```

### How `GoogleCloudSnitch` resolves DC and rack
1. Queries `http://metadata.google.internal/computeMetadata/v1/instance/zone` with header `Metadata-Flavor: Google`.
2. The response is `projects/<project-number>/zones/us-central1-a`.
3. The snitch takes the zone (`us-central1-a`) and splits it at the **last** `-`:
   * **Datacenter**: `us-central1`
   * **Rack**: `a`
4. Use the DC name in replication: `{'us-central1': 3}`. With 3 zones, `NetworkTopologyStrategy` places one replica per zone.

Optional suffix in `conf/cassandra-rackdc.properties`:
```ini
dc_suffix=_prod      # DC becomes us-central1_prod
```

`GossipingPropertyFileSnitch` is a portable alternative (DC/rack set by you in `cassandra-rackdc.properties`), useful for clusters spanning GCP and other environments.

---

## 4. Global VPC & Multi-Region

GCP VPC networks are **global**: VMs in different regions of the same VPC reach each other on internal IPs without VPN or public IPs.

```yaml
# conf/cassandra.yaml, node in us-central1
listen_address: 10.128.0.12          # internal IP
# broadcast_address not needed: internal IPs route across regions in one VPC
rpc_address: 0.0.0.0
broadcast_rpc_address: 10.128.0.12
```

* Open port 7000 (internode) between nodes and 9042 (CQL) from clients with VPC firewall rules, ideally using network tags or service accounts as source and target. Keep 7199 (JMX) closed except from admin hosts.
* **MTU**: new VPCs default to **1460** bytes; it can be set up to 8896. All VMs pick up the VPC MTU via DHCP. If you change the VPC MTU, restart or reconfigure the VMs so interfaces match; mismatched MTUs cause stalls on large packets (streaming). Check with `ip link show`.
* Cross-region traffic is billed as egress. Use `LOCAL_*` consistency levels and DC-aware driver policies so requests stay in-region.

---

## 5. Backups to Google Cloud Storage

Upload **only the snapshot you just took**. Each snapshot directory contains the SSTables plus `schema.cql` and `manifest.json`.

```bash
#!/usr/bin/env bash
set -euo pipefail
TAG="backup_$(date +%Y%m%d_%H%M%S)"
DATA_DIR=/mnt/cassandra/data
DEST="gs://my-company-cassandra-backups/$(hostname)/${TAG}"

nodetool snapshot -t "${TAG}"

# Copy only this tag's directories, preserving <keyspace>/<table-id>/snapshots/<tag>/ paths
cd "${DATA_DIR}"
find . -type d -path "*/snapshots/${TAG}" -print0 |
  while IFS= read -r -d '' dir; do
      gcloud storage cp --recursive "${dir}/*" "${DEST}/data/${dir#./}/"
  done

# Record this node's tokens for same-topology restores
nodetool info -T | grep '^Token' | awk '{print $3}' | paste -sd, - |
  gcloud storage cp - "${DEST}/tokens.txt"

nodetool clearsnapshot -t "${TAG}"
```

`gcloud storage rsync` filters only by exclusion (`--exclude` regex), so selecting a single tag is simpler by walking the tag directories as above.

* **Lifecycle**: use Object Lifecycle Management to move objects to Nearline after 30 days and Coldline after 90. Nearline and Coldline have minimum storage durations (30 and 90 days), so earlier transitions or deletions are charged as if stored for the minimum.
* Use a dedicated service account with write access to the bucket only.
* For restore procedures, see [disaster recovery](../07_disaster_recovery/01_backup_and_disaster_recovery.md).
