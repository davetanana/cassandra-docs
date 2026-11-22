#!/usr/bin/env python3
"""Size an Apache Cassandra 5.0 cluster: how many nodes of a given machine type you need, what availability
and durability you get, and a rough monthly list-price cost. Profiles cover local-NVMe and network-storage
machines on AWS, Google Cloud and Azure. The formulas are explained in
05_cluster_deployment_and_config/05_capacity_planning.md; this script only does the arithmetic.

Example (illustrative workload):
  python3 tools/capacity_plan.py --machine aws-i4i.2xlarge --data 3TB --growth 50 --years 2 \\
      --writes 15000 --write-size 1KiB --reads 30000 --read-size 2KiB --compression 0.5 --strategy ucs \\
      --replace-hours 12 --afr 2

Run with --list-machines to see the built-in machine profiles. Any profile value can be overridden
(--disk, --read-iops, --nic-gbps, --instance-sla, --zone-sla), or describe your own machine with those flags
and no --machine.

Everything here is a planning estimate. Cassandra's own limits come from the 5.0 source; machine figures are
the providers' published maximums; throughput per node must come from your own benchmark (--ops-per-node).
Standard library only.
"""
import argparse
import math
import re
import sys

KIB, MIB, GIB, TIB = 1024, 1024 ** 2, 1024 ** 3, 1024 ** 4
UNITS = {'b': 1, 'kb': 1e3, 'mb': 1e6, 'gb': 1e9, 'tb': 1e12, 'kib': KIB, 'mib': MIB, 'gib': GIB, 'tib': TIB}
MONTH_MIN = 30 * 24 * 60
HOURS_PER_YEAR = 8760

# Cassandra 5.0 defaults (conf/cassandra.yaml, Config.java on cassandra-5.0)
STREAM_THROTTLE_MIBPS = 24          # stream_throughput_outbound / entire_sstable_stream_throughput_outbound
COMPACTION_THROTTLE_MIBPS = 64      # compaction_throughput
COMMITLOG_RESERVE = 8192 * MIB      # commitlog_total_space: min(8192MiB, 1/4 of the commitlog volume)

# Planning assumptions (see the page; override them with your measurements)
MAX_FILL = {'stcs': 0.50, 'lcs': 0.70, 'ucs': 0.70, 'twcs': 0.70}     # keep 50% free for STCS, ~30% otherwise
WRITE_AMP = {'stcs': 5, 'lcs': 15, 'ucs': 5, 'twcs': 2}             # bytes rewritten by compaction per byte flushed

# Published maximums and list prices, checked 2026-11-22. Sources are listed in the capacity-planning page.
# storage: 'local' (NVMe that belongs to the VM) or 'network' (a volume that outlives the VM).
# disk: usable local NVMe bytes, or the largest network volume; read/write IOPS: the provider's random-I/O
# figures (for network storage, the per-VM limit, which is what you provision up to); disk_mbps: the per-VM
# network-storage throughput limit; nic: baseline Gbps (Google and Azure publish only an "up to" figure);
# instance_sla / zone_sla: monthly uptime commitments for one VM / VMs in 2+ zones;
# price: on-demand list price per hour (VM, plus Local SSD where it is billed separately), in the region named;
# gib_month / iops_month / mbps_month: network-volume prices above the free baseline (free_iops, free_mbps).
AWS, GCP, AZ = 'AWS us-east-1', 'GCP us-central1', 'Azure eastus'
# Price per GB that crosses zones, both directions together: AWS $0.01/GB in each direction; Google $0.01/GiB
# charged to the sender; Azure lists inter-zone meters of $0.01/GB in and out.
XZ = {AWS: 0.02, GCP: 0.01, AZ: 0.02}
GP3 = dict(storage='network', disk=64 * TIB, gib_month=0.08, iops_month=0.005, mbps_month=0.04,
           free_iops=3000, free_mbps=125)
MACHINES = {
    'aws-i4i.2xlarge':  dict(storage='local', vcpu=8,  disk=1875e9, read_iops=200_000, write_iops=110_000,
                             nic=4.687, instance_sla=99.5, zone_sla=99.99, price=0.686, region=AWS),
    'aws-i4i.4xlarge':  dict(storage='local', vcpu=16, disk=3750e9, read_iops=400_000, write_iops=220_000,
                             nic=9.375, instance_sla=99.5, zone_sla=99.99, price=1.373, region=AWS),
    'aws-i4i.8xlarge':  dict(storage='local', vcpu=32, disk=7500e9, read_iops=800_000, write_iops=440_000,
                             nic=18.75, instance_sla=99.5, zone_sla=99.99, price=2.746, region=AWS),
    'aws-i7i.2xlarge':  dict(storage='local', vcpu=8,  disk=1875e9, read_iops=300_000, write_iops=165_000,
                             nic=4.687, instance_sla=99.5, zone_sla=99.99, price=0.755, region=AWS),
    'aws-i8g.2xlarge':  dict(storage='local', vcpu=8,  disk=1875e9, read_iops=300_000, write_iops=165_000,
                             nic=4.688, instance_sla=99.5, zone_sla=99.99, price=0.6864, region=AWS),
    'aws-m8g.2xlarge-gp3': dict(GP3, vcpu=8, read_iops=12_000, write_iops=12_000, disk_mbps=312.5, nic=3.75,
                                instance_sla=99.5, zone_sla=99.99, price=0.35904, region=AWS),
    'gcp-n2-standard-32-4ssd': dict(storage='local', vcpu=32, disk=1500 * GIB, read_iops=680_000,
                                    write_iops=360_000, nic=32, instance_sla=99.9, zone_sla=99.99,
                                    price=1.553888 + 1500 * 0.000109589, region=GCP),
    'gcp-z3-highmem-8-highlssd': dict(storage='local', vcpu=8, disk=3000 * GIB, read_iops=750_000,
                                      write_iops=500_000, nic=23, instance_sla=99.9, zone_sla=99.99,
                                      price=1.151931, region=GCP),
    'gcp-n4-standard-8-hdb': dict(storage='network', vcpu=8, disk=64 * TIB, read_iops=30_000, write_iops=30_000,
                                  disk_mbps=480 * MIB / 1e6, nic=16, instance_sla=99.9, zone_sla=99.99,
                                  price=0.3628, gib_month=0.08, iops_month=0.005, mbps_month=0.04,
                                  free_iops=3000, free_mbps=140, region=GCP),
    'azure-L8s_v3':     dict(storage='local', vcpu=8,  disk=1.92e12, read_iops=400_000, write_iops=400_000,
                             nic=12.5, instance_sla=99.9, zone_sla=99.99, price=0.696, region=AZ),
    'azure-L16s_v3':    dict(storage='local', vcpu=16, disk=3.84e12, read_iops=800_000, write_iops=800_000,
                             nic=12.5, instance_sla=99.9, zone_sla=99.99, price=1.392, region=AZ),
    'azure-L8s_v4':     dict(storage='local', vcpu=8,  disk=1.92e12, read_iops=550_000, write_iops=220_000,
                             nic=12.5, instance_sla=99.9, zone_sla=99.99, price=0.696, region=AZ),
    'azure-D8s_v6-pv2': dict(storage='network', vcpu=8, disk=64 * TIB, read_iops=16_667, write_iops=16_667,
                             disk_mbps=496, nic=12.5, instance_sla=99.9, zone_sla=99.99, price=0.403,
                             gib_month=0.0803, iops_month=0.00511, mbps_month=0.04015, free_iops=3000,
                             free_mbps=125, region=AZ),
}


def size(text):
    m = re.fullmatch(r'\s*([0-9.]+)\s*([a-zA-Z]*)\s*', text)
    if not m or m.group(2).lower() not in UNITS | {'': 1}:
        raise argparse.ArgumentTypeError(f'not a size: {text!r} (use e.g. 3TB, 500GiB, 1KiB)')
    return float(m.group(1)) * UNITS.get(m.group(2).lower(), 1)


def human(n, binary=False):
    steps = [(TIB, 'TiB'), (GIB, 'GiB'), (MIB, 'MiB'), (KIB, 'KiB')] if binary else \
            [(1e12, 'TB'), (1e9, 'GB'), (1e6, 'MB'), (1e3, 'kB')]
    for f, u in steps:
        if n >= f:
            return f'{n / f:,.2f} {u}'
    return f'{n:,.0f} B'


def sig2(x):
    """Round to two significant figures, so the output doesn't claim more precision than the model has."""
    if x <= 0:
        return '0'
    d = 10 ** (math.floor(math.log10(x)) - 1)
    v = round(x / d) * d
    for f, u in ((1e12, ' trillion'), (1e9, ' billion'), (1e6, ' million')):
        if v >= f:
            return f'{v / f:g}{u}'
    return f'{v:,.0f}'


def quorum(rf):
    return rf // 2 + 1


def range_unavailable(n, racks, rf, q, tolerated):
    """Probability that at least one token range has fewer live replicas than it needs.
    With vnodes, every combination of nodes in different racks shares some range, so a range fails as soon as
    (tolerated + 1) racks each have a node down (racks >= RF), or (tolerated + 1) nodes are down (one rack)."""
    if racks >= rf:
        per_rack = n / racks
        p = 1 - (1 - q) ** per_rack
        return sum(math.comb(racks, k) * p ** k * (1 - p) ** (racks - k) for k in range(tolerated + 1, racks + 1))
    return 1 - sum(math.comb(n, k) * q ** k * (1 - q) ** (n - k) for k in range(0, tolerated + 1))


def loss_per_year(n, racks, rf, afr, hours):
    """Chance per year that every replica of some range is lost before the first loss is re-streamed."""
    w = hours / HOURS_PER_YEAR
    p = n * afr
    for i in range(1, rf):
        others = n * (racks - i) / racks if racks >= rf else n - i
        p *= max(others, 0) * afr * w
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    w = ap.add_argument_group('workload')
    w.add_argument('--data', type=size, help='data today: one copy, uncompressed (e.g. 3TB)')
    w.add_argument('--growth', type=float, default=0, help='growth per year, percent (default 0)')
    w.add_argument('--years', type=float, default=0, help='years of growth to plan for (default 0)')
    w.add_argument('--writes', type=float, default=0, help='writes per second, per datacenter')
    w.add_argument('--write-size', type=size, default=1024, help='average write (mutation) size (default 1KiB)')
    w.add_argument('--reads', type=float, default=0, help='reads per second, per datacenter')
    w.add_argument('--read-size', type=size, default=1024, help='average read result size (default 1KiB)')
    w.add_argument('--read-cl', choices=['local_one', 'local_quorum'], default='local_quorum')
    c = ap.add_argument_group('cluster')
    c.add_argument('--rf', type=int, default=3, help='replication factor per datacenter (default 3)')
    c.add_argument('--dcs', type=int, default=1, help='datacenters, each holding a full copy (default 1)')
    c.add_argument('--racks', type=int, default=3, help='racks (zones) per datacenter (default 3)')
    c.add_argument('--strategy', choices=sorted(MAX_FILL), default='ucs', help='compaction strategy (default ucs)')
    c.add_argument('--compression', type=float, default=1.0,
                   help='on-disk / raw size, from nodetool tablestats "SSTable Compression Ratio" (default 1.0)')
    c.add_argument('--write-amp', type=float, help='compaction write amplification (default: by strategy)')
    c.add_argument('--index-overhead', type=float, default=0,
                   help='SAI index size as a fraction of the table on disk (default 0; see the page for measured'
                        ' figures, e.g. 0.05 for a few non-vector indexes)')
    c.add_argument('--sstables-per-read', type=float, default=2,
                   help='from nodetool tablehistograms, "SSTables" column at p75 (default 2)')
    c.add_argument('--cache-hit', type=float, default=0, help='fraction of disk reads served from page cache')
    c.add_argument('--replace-hours', type=float,
                   help='longest acceptable time to rebuild one node (sets the data-per-node limit)')
    c.add_argument('--stream-mibps', type=float, default=STREAM_THROTTLE_MIBPS,
                   help=f'streaming rate per node, MiB/s (default {STREAM_THROTTLE_MIBPS}, the 5.0 throttle)')
    c.add_argument('--ops-per-node', type=float,
                   help='operations/s one node sustains at your latency target, from your own benchmark')
    m = ap.add_argument_group('machine')
    m.add_argument('--machine', choices=sorted(MACHINES))
    m.add_argument('--list-machines', action='store_true')
    m.add_argument('--disk', type=size, help='local data disk per node')
    m.add_argument('--read-iops', type=float, help='published random read IOPS per node')
    m.add_argument('--nic-gbps', type=float, help='baseline network bandwidth per node, Gbps')
    m.add_argument('--disk-mbps', type=float, help='disk throughput limit per node, MB/s (network storage)')
    m.add_argument('--price-hour', type=float, help='price per node per hour, for the cost estimate')
    m.add_argument('--iops-util', type=float, default=0.5, help='share of published IOPS to plan on (default 0.5)')
    m.add_argument('--nic-util', type=float, default=0.5, help='share of network bandwidth to plan on (default 0.5)')
    a = ap.add_argument_group('availability and durability')
    a.add_argument('--instance-sla', type=float, help='provider uptime commitment for one VM, percent')
    a.add_argument('--zone-sla', type=float, help='provider uptime commitment for VMs across zones, percent')
    a.add_argument('--maintenance-min', type=float, default=0,
                   help='planned downtime per node per month (rolling restarts, upgrades), minutes')
    a.add_argument('--afr', type=float, help='chance per year that a node loses its data, percent')
    o = ap.parse_args(argv)

    if o.list_machines:
        print(f'{"machine":<27}{"storage":<8}{"vCPU":>5}{"disk":>11}{"read IOPS":>10}{"NIC Gbps":>9}'
              f'{"VM SLA":>8}{"$/hour":>8}')
        for k, v in MACHINES.items():
            disk = human(v['disk']) if v['storage'] == 'local' else 'volume'
            print(f'{k:<27}{v["storage"]:<8}{v["vcpu"]:>5}{disk:>11}{v["read_iops"]:>10,}{v["nic"]:>9g}'
                  f'{v["instance_sla"]:>7g}%{v["price"]:>8.3f}')
        return 0
    if o.data is None:
        ap.error('--data is required')
    mach = dict(MACHINES.get(o.machine, {}))
    for key, val in (('disk', o.disk), ('read_iops', o.read_iops), ('nic', o.nic_gbps),
                     ('instance_sla', o.instance_sla), ('zone_sla', o.zone_sla), ('disk_mbps', o.disk_mbps),
                     ('price', o.price_hour)):
        if val is not None:
            mach[key] = val
    if 'disk' not in mach:
        ap.error('give --machine or at least --disk')
    network = mach.get('storage') == 'network'

    rf, racks, dcs = o.rf, o.racks, o.dcs
    wa = o.write_amp if o.write_amp is not None else WRITE_AMP[o.strategy]
    out = []
    p = out.append

    def row(label, value):
        p(f'  {label:<66}{value:>6}')

    # ---- storage
    final = o.data * (1 + o.growth / 100) ** o.years
    per_dc = final * o.compression * rf * (1 + o.index_overhead)
    usable = mach['disk'] * MAX_FILL[o.strategy] - min(COMMITLOG_RESERVE, mach['disk'] / 4)
    need = {'storage': math.ceil(per_dc / usable)}
    storage_label = (f'storage: fill disks to {MAX_FILL[o.strategy]:.0%} ({o.strategy.upper()}), '
                     f'{human(usable)} usable each')
    if network:
        storage_label = (f'storage: network volume sized to fit, up to {human(mach["disk"], True)} '
                         f'at {MAX_FILL[o.strategy]:.0%} full')
    p('Workload, per datacenter')
    p(f'  data after {o.years:g} years at {o.growth:g}%/year: {human(final)} (one copy, uncompressed)')
    p(f'  on disk with RF {rf} and compression {o.compression:g}'
      f'{f", plus {o.index_overhead:.0%} for indexes" if o.index_overhead else ""}: {human(per_dc)}')
    p('')
    label = o.machine or 'the given machine'
    p(f'Nodes needed per datacenter on {label}')
    row(storage_label, need['storage'])

    # ---- data per node from recovery time
    stream = o.stream_mibps * MIB
    if o.replace_hours:
        cap = o.replace_hours * 3600 * stream
        need['recovery'] = math.ceil(per_dc / cap)
        row(f'recovery: rebuild a node in {o.replace_hours:g} h at {o.stream_mibps:g} MiB/s, <= {human(cap)} each',
            need['recovery'])

    # ---- read IOPS
    replicas = quorum(rf) if o.read_cl == 'local_quorum' else 1
    disk_reads = o.reads * replicas * o.sstables_per_read * 2 * (1 - o.cache_hit)
    if o.reads and mach.get('read_iops'):
        need['read IOPS'] = math.ceil(disk_reads / (mach['read_iops'] * o.iops_util))
        row(f'read IOPS: {disk_reads:,.0f}/s, planning on {o.iops_util:.0%} of {mach["read_iops"]:,.0f} per node',
            need['read IOPS'])

    # ---- network
    net = o.writes * o.write_size * (rf + dcs - 1) + o.reads * o.read_size * 2
    if net and mach.get('nic'):
        need['network'] = math.ceil(net * 8 / (mach['nic'] * 1e9 * o.nic_util))
        row(f'network: {net * 8 / 1e9:,.2f} Gbps, planning on {o.nic_util:.0%} of {mach["nic"]:g} Gbps per node',
            need['network'])

    # ---- throughput from a benchmark
    if o.ops_per_node:
        need['throughput'] = math.ceil((o.reads + o.writes) / o.ops_per_node)
        row(f'throughput: {o.reads + o.writes:,.0f} ops/s at {o.ops_per_node:,.0f} per node (your benchmark)',
            need['throughput'])
    else:
        p('  throughput: not computed; benchmark one node and pass --ops-per-node')

    need['fault tolerance'] = max(rf, racks)
    row('fault tolerance: at least RF, and one node per rack', need['fault tolerance'])
    biggest = max(need, key=need.get)
    n = math.ceil(need[biggest] / racks) * racks
    p(f'  => {n} nodes per datacenter, {n * dcs} in total (largest need: {biggest}; rounded up to a multiple of'
      f' {racks} racks)')
    p('')

    # ---- per-node figures at n
    node_now = o.data * o.compression * rf * (1 + o.index_overhead) / n
    node_final = per_dc / n
    ingest = o.writes * o.write_size * rf / n
    compaction = ingest * o.compression * wa
    rebuild_h = node_final / stream / 3600
    if network:   # provision the volume for the end-of-plan data at the max fill, plus the commit log, in 100 GiB steps
        volume = math.ceil((node_final / MAX_FILL[o.strategy] + COMMITLOG_RESERVE) / (100 * GIB)) * 100 * GIB
    p(f'Each node at {n} nodes')
    if network:
        p(f'  data: {human(node_now)} today, {human(node_final)} at the end; provision a {human(volume, True)} '
          f'volume ({node_final / volume:.0%} full at the end)')
    else:
        p(f'  data: {human(node_now)} today, {human(node_final)} at the end; disk {node_final / mach["disk"]:.0%} full')
    p(f'  rebuild time at {o.stream_mibps:g} MiB/s: {rebuild_h:,.1f} h')
    if network:
        p('  a failed VM can be replaced by attaching its volume to a new VM: no rebuild unless the volume is lost')
    p(f'  writes in: {human(ingest, True)}/s; compaction must rewrite {human(compaction, True)}/s '
      f'(write amplification {wa:g}; compaction_throughput default {COMPACTION_THROTTLE_MIBPS} MiB/s)')
    if compaction > COMPACTION_THROTTLE_MIBPS * MIB * 0.5:
        p(f'  WARNING: compaction needs more than half of compaction_throughput; raise it or add nodes')
    if mach.get('disk_mbps'):
        # commit log + flush + compaction, plus the streaming throttle when this node helps a rebuild
        disk_w = ingest + ingest * o.compression + compaction + stream
        p(f'  disk writes incl. commit log, flush and a rebuild at {o.stream_mibps:g} MiB/s: '
          f'{disk_w / 1e6:,.0f} MB/s of {mach["disk_mbps"]:,.0f} MB/s ({disk_w / 1e6 / mach["disk_mbps"]:.0%})')
        if disk_w / 1e6 > mach['disk_mbps'] * 0.5:
            p('  WARNING: disk writes need more than half the volume throughput; reads share the same limit')
    if mach.get('read_iops') and o.reads:
        p(f'  read IOPS: {disk_reads / n:,.0f}/s, {disk_reads / n / mach["read_iops"]:.1%} of published maximum')
    if mach.get('nic') and net:
        p(f'  network: {net * 8 / 1e9 / n:,.2f} Gbps, {net * 8 / n / (mach["nic"] * 1e9):.0%} of baseline')
    p('')

    # ---- availability
    if mach.get('instance_sla'):
        q = (1 - mach['instance_sla'] / 100) + o.maintenance_min / MONTH_MIN
        tolerated = rf - (quorum(rf) if o.read_cl == 'local_quorum' else 1)
        cl = o.read_cl.upper()
        u = range_unavailable(n, racks, rf, q, tolerated)
        zone = mach.get('zone_sla', 100) / 100
        avail = (1 - u) * zone
        p('Availability, if every VM were down for its whole SLA allowance (a pessimistic floor)')
        p(f'  one VM: {mach["instance_sla"]:g}% (+{o.maintenance_min:g} min/month planned) -> '
          f'{(1 - q) * 100:.4f}% up')
        p(f'  some token range below {cl}: {u * 100:.4f}% of the time, ~{u * MONTH_MIN:,.0f} min/month')
        if 'zone_sla' in mach:
            p(f'  provider commitment for VMs across zones: {mach["zone_sla"]:g}%')
        p(f'  planning figure for {cl} in one datacenter: {avail * 100:.4f}%, ~{(1 - avail) * MONTH_MIN:,.0f} '
          f'min/month')
        p('')

    # ---- rough cost
    if mach.get('price'):
        hours = 730
        node_month = mach['price'] * hours
        parts = 'VM with its local disks'
        if network:
            gib = volume / GIB
            iops = max(0, mach['read_iops'] - mach.get('free_iops', 0))
            mbps = max(0, mach.get('disk_mbps', 0) - mach.get('free_mbps', 0))
            vol = gib * mach['gib_month'] + iops * mach['iops_month'] + mbps * mach['mbps_month']
            node_month += vol
            parts = (f'VM ${mach["price"] * hours:,.0f} + volume ${vol:,.0f} ({gib:,.0f} GiB, {mach["read_iops"]:,} IOPS, '
                      f'{mach.get("disk_mbps", 0):,.0f} MB/s)')
        p(f'Rough cost: on-demand list price{", " + mach["region"] if "region" in mach else ""}, checked 2026-11-22')
        p(f'  per node per month: ~${node_month:,.0f} ({parts})')
        p(f'  cluster per month: ~${node_month * n * dcs:,.0f} for {n * dcs} nodes; excludes backups, support '
          f'and discounts')
        if racks > 1 and mach.get('region') in XZ:
            # replication to the other replicas, the second replica's read response at LOCAL_QUORUM, and the
            # client hop for the share of clients in another zone (internode_compression: dc = uncompressed)
            other = (racks - 1) / racks
            xz = (o.writes * o.write_size * (rf - 1) + o.reads * o.read_size * (replicas - 1)
                  + (o.writes * o.write_size + o.reads * o.read_size) * other) * 2_592_000 * dcs
            p(f'  traffic between zones: ~{human(xz)}/month, ~${xz / 1e9 * XZ[mach["region"]]:,.0f}/month at '
              f'${XZ[mach["region"]]:g}/GB (replication, quorum reads, clients in other zones; repair, '
              f'streaming and other DCs extra)')
        p('')

    # ---- durability
    if o.afr:
        loss = loss_per_year(n, racks, rf, o.afr / 100, rebuild_h) ** dcs
        p('Durability (independent failures only; backups cover correlated failures and mistakes)')
        p(f'  node data loss {o.afr:g}%/year, rebuild window {rebuild_h:,.1f} h, RF {rf} in {racks} racks, {dcs} DC(s)')
        p(f'  chance per year of losing every replica of some range: about 1 in {sig2(1 / loss)} years'
          if loss > 0 else '  chance per year of losing every replica of some range: negligible')
    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
