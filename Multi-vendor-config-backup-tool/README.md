# Multivendor Backup Tool

A small multivendor network configuration backup tool. It reads a device inventory and connects to each device over ssh (Netmiko). Credentials are pulled from OS keyring.

## Features
- Multivendor: per-vendor backup commands (Cisco IOS/XE/XR/NX-OS, Arista, Juniper, Palo Alto)
- Inventory defined in a YAML file
- Credentials read from system keyring
- Timestamped config files


## Requirements
- Python 3.9+
- A system keyring (e.g. gnome-keyring on Fedora/GNOME)
- Dependencies in requirements.txt


## Install
``` python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 1. Keyring credentials

The tool looks up one password by service and username. Store it once:
 
```bash
secret-tool store --label="Config Backup" service IOS-XE username admin
```

Verify it's retrievable:
 
```bash
secret-tool lookup service IOS-XEusername admin
```


### 2. Define your inventory
 
Create `inventory.yaml` with one entry per device. Fields map directly to the
`Device` dataclass; `port` and `username` are optional.

```yaml
- hostname: core-rtr-01
  ip: 10.0.0.1
  vendor: cisco_xe
  username: admin
 
- hostname: dist-sw-01
  ip: 10.0.0.10
  vendor: arista_eos
  username: admin
 
- hostname: edge-fw-01
  ip: 10.0.0.2
  vendor: paloalto_panos
  port: 2222
  username: admin
```

**`vendor` must be a valid Netmiko `device_type`.** Common values:
 
| Vendor              | `device_type`     |
|---------------------|-------------------|
| Cisco IOS           | `cisco_ios`       |
| Cisco IOS-XE        | `cisco_xe`        |
| Cisco IOS-XR        | `cisco_xr`        |
| Cisco NX-OS         | `cisco_nxos`      |
| Arista EOS          | `arista_eos`      |
| Juniper Junos       | `juniper_junos`   |
| Palo Alto PAN-OS    | `paloalto_panos`  |
 
## Project Layout
```
config-backup/
├── backup.py          # main script
├── inventory.yaml     # device list (you create this)
├── requirements.txt
├── README.md
├── TODO.md
└── backups/           # generated config files
```

