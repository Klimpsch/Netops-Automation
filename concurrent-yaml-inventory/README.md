# concurrent-yaml-inventory

Connects to Cisco IOS routers over SSH, collects interface and OSPF details, and saves them to a YAML inventory file (`hosts.yaml`).

## Tested on

| Component | Version |
| --- | --- |
| Platform | Cisco CSR1000v |
| IOS-XE | 17.03.08a |
| Python | 3.14 |
| Netmiko | 4.8.0 |


## What it collects

For each router, the script runs:

- `show ip interface brief`: interface names, IP addresses, and whether each interface is shut down
- `show ip ospf interface brief`: OSPF process, area, and prefix length for OSPF-enabled interfaces

The output is parsed with TextFSM (ntc-templates). Short interface names from the OSPF output (like `Gi0/1`) are expanded to full names (like `GigabitEthernet0/1`) so both commands line up on the same interface.

## Example output

```yaml
devices:
  R1:
    interfaces:
      GigabitEthernet0/0:
        ipv4: 10.0.12.1/24
        enabled: true
        ospf:
          process: 1
          area: 0
      GigabitEthernet0/3:
        enabled: false
      Loopback0:
        ipv4: 1.1.1.1/32
        enabled: true
        ospf:
          process: 1
          area: 0
```

- `ipv4` includes the prefix length only for OSPF interfaces, since `show ip interface brief` doesn't show masks.
- Interfaces with no IP address have no `ipv4` key.
- Routers without OSPF are still collected; their interfaces just have no `ospf` section.

## Requirements

- Python 3.8 or newer
- SSH access to the routers
- Python packages:

```bash
pip install netmiko pyyaml ntc-templates
```

## Setup

Edit the settings at the top of the script:

```python
ROUTERS = ['10.0.12.1', '10.0.12.2', '10.0.13.2', '10.0.34.2']
USERNAME = "admin"
MAX_WORKERS = 10   # concurrent version only
```

- **ROUTERS**: one reachable IP per router. Two IPs on the same router will collect it twice and miss others.
- **MAX_WORKERS**: how many routers the concurrent version connects to at the same time.

## Usage

```bash
python collect_inventory_concurrent.py
```

Example output from the concurrent version:

```
Collected 5 interfaces from R3 (10.0.13.2)
Collected 4 interfaces from R2 (10.0.12.2)
Collected 4 interfaces from R1 (10.0.12.1)
Collected 4 interfaces from R4 (10.0.34.2)
Wrote 4 devices to hosts.yaml
```

Routers print in the order they finish, so this varies between runs. `hosts.yaml` is always sorted by hostname.

## How hosts.yaml is updated

The script **merges** into `hosts.yaml` rather than replacing it:

- New routers are added under `devices`.
- Routers already in the file are refreshed with the latest data.
- Routers in the file that weren't collected this run are left as they are.
- If `hosts.yaml` doesn't exist, it is created.

The concurrent version always reads and writes `hosts.yaml` in the same folder as the script, wherever you run it from.

## Error handling

- **Concurrent version**: if a router can't be reached or its output can't be parsed, that router is skipped and listed at the end as failed. The other routers are still saved.

## Troubleshooting

| Problem | Likely cause |
| --- | --- |
| `Could not parse 'show ip interface brief'` | ntc-templates isn't installed, or the device isn't Cisco IOS |
| A router appears twice in the output | Two IPs in `ROUTERS` belong to the same router |
| A router is missing from `hosts.yaml` | No IP in `ROUTERS` reaches it, or it failed (check the "Failed" line) |
| `NameError: name 'Path' is not defined` | Missing `from pathlib import Path` import |
| Connection timeouts | SSH not enabled, wrong IP, or an ACL blocking the connection |
