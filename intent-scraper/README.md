# Running-Config → Intent YAML

Scrape Cisco IOS routers and turn their routing configuration into clean, structured YAML.

This is a brownfield bootstrap tool for building a network source of truth. Instead of writing intent files by hand for a network that already exists, you pull the live `show running-config`, extract the routing intent (BGP, OSPF, EIGRP), and get one YAML file per router. You then review and tidy up those files, and from that point on the YAML becomes the source of truth that drives config, rather than the other way round.

```
device (or mock) ──► pull.py ──► raw running-config ──► parse.py ──► dict ──► scrape_to_yaml.py ──► out_yaml/<hostname>.yaml
```

## Features

- **BGP**: local ASN, router-id, and neighbors (remote AS, description, update-source), with per-address-family activation and `next-hop-self`. Neighbors are automatically split into iBGP and eBGP.
- **OSPF**: process ID, `network ... area ...` statements, passive interfaces, and `auto-cost reference-bandwidth`.
- **EIGRP**: both named mode (`address-family ipv4 unicast autonomous-system N`) and classic mode (`router eigrp N`).
- **Mock mode**: develop and test the parser against saved configs, with no device or lab required.
- **Live mode**: pull configs directly from devices over SSH with Netmiko.

## Project structure

```
.
├── pull.py             # Transport: get 'show running-config' from a device or a saved file
├── parse.py            # Parsing: running-config text -> per-router intent dict
├── scrape_to_yaml.py   # Driver: loop over inventory, parse, write YAML
├── mock_configs/       # Saved 'show running-config' outputs, one <name>.txt per router
└── out_yaml/           # Generated output, one <hostname>.yaml per router (created on run)
```

## Requirements

- Python 3.8+
- [ciscoconfparse](https://github.com/mpenning/ciscoconfparse) (the original 1.x package, not `ciscoconfparse2`)
- [PyYAML](https://pyyaml.org/)
- [Netmiko](https://github.com/ktbyers/netmiko) (only needed for live pulls)

```bash
pip install ciscoconfparse pyyaml netmiko
```

## Usage

### Mock mode (default)

1. Save a router's `show running-config` output to `mock_configs/<name>.txt`.
2. Add `<name>` to the `INVENTORY` list in `scrape_to_yaml.py`:

   ```python
   INVENTORY = ["rtr1", "rtr2"]
   ```

3. Run the script:

   ```bash
   python scrape_to_yaml.py
   ```

Each router is written to `out_yaml/<hostname>.yaml` and also printed to the terminal for a quick review.

### Live mode

In `scrape_to_yaml.py`, swap the mock pull for a device pull:

```python
import os
from pull import pull_from_device

running = pull_from_device(
    host=name,
    username=os.environ["NET_USER"],
    password=os.environ["NET_PASS"],
)
```

Keep credentials in environment variables or a secrets manager rather than hard-coding them in the script.

## Example output

Key order follows the order the parser builds each section.

```yaml
hostname: rtr1
router_id: 10.0.0.1
bgp:
  asn: 65000
  ibgp_neighbors:
  - peer: 10.0.0.2
    remote_as: 65000
    description: rtr2
    update_source: Loopback0
    address_families:
    - name: ipv4_unicast
      next_hop_self: true
  ebgp_neighbors:
  - peer: 192.0.2.1
    remote_as: 64512
    description: ISP-A
    address_families:
    - name: ipv4_unicast
ospf:
  process_id: 1
  networks:
  - prefix: 10.0.0.0
    wildcard: 0.0.0.255
    area: 0
  passive_interfaces:
  - Loopback0
  defaults:
    reference_bandwidth: 10000
eigrp:
  networks:
  - prefix: 172.16.0.0
    wildcard: 0.0.255.255
  as_number: 100
```

## Known limitations

- **Router-id comes from BGP.** `router_id` is taken from `bgp router-id`. Routers without BGP, or with an OSPF/EIGRP router-id set separately, will not have it captured.
- **Scope.** Only routing protocols are extracted. Interfaces, ACLs, route-maps, prefix-lists, and other config are ignored.
