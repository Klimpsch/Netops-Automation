import os
import sys
import getpass
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml
from netmiko import ConnectHandler


# Short interface names used by some show commands -> full names
ABBR = {"Gi": "GigabitEthernet", "Te": "TenGigabitEthernet", "Lo": "Loopback", "Vl": "Vlan"}

ROUTERS = ['10.0.12.2', '10.0.13.2', '10.0.23.2', '10.0.34.2'] 
USERNAME = 'admin'
PASSWORD = getpass.getpass()

def full_name(name):
    for short, long in ABBR.items():
        if name.startswith(short) and not name.startswith(long):
            return long + name[len(short):]
    return name 

def collect_interface_data(host, username, password):
    """ returns dicts of interface and ospf data"""
    device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": password, 
        "port": 22
    }


    # Collect
    try:
        with ConnectHandler(**device) as conn:
            hostname = conn.base_prompt
            ip_brief = conn.send_command("show ip interface brief", use_textfsm=True)
            ospf_brief = conn.send_command("show ip ospf interface brief", use_textfsm=True)
    except Exception as e:
        sys.exit(f"Connection to {device['host']} failed: {e}")


    # TextFSM returns plain text instead of a list if parsing fails
    if not isinstance(ip_brief, list):
        sys.exit("Could not parse 'show ip interface brief' - is ntc-templates installed?")
    if not isinstance(ospf_brief, list):
        ospf_brief = []  # OSPF not running 

    return ip_brief, ospf_brief, hostname



def parse_interface_data(ip_brief, ospf_brief):
    """parses ip and ospf data into single dict"""
    interfaces = {}
    for row in ip_brief:
        iface = interfaces.setdefault(row['interface'], {})
        if row['ip_address'] != 'unassigned':
            iface['ipv4'] = row['ip_address']
        iface['enabled'] = row['status'] != 'administratively down'
     
    for row in ospf_brief:
        iface = interfaces.setdefault(full_name(row["interface"]), {})
        iface["ipv4"] = f"{row['ip_address']}/{row['prefix_length']}"
        area = row["area"]
        iface["ospf"] = {
            "process": int(row["process"]),
            "area": int(area) if area.isdigit() else area,  
        }

    return interfaces


hosts_file = Path("hosts.yaml")

# Load what's already in the file once, before the loop
inventory = {}
if hosts_file.exists():
    inventory = yaml.safe_load(hosts_file.read_text()) or {}
devices = inventory.setdefault("devices", {})

for host in ROUTERS:
    ip_brief, ospf_brief, hostname = collect_interface_data(host, "admin", "Cisco123")
    interfaces = parse_interface_data(ip_brief, ospf_brief)

    devices[hostname] = {"interfaces": interfaces}  # adds a new router, or updates an existing one
    print(f"Collected {len(interfaces)} interfaces from {hostname}")

# Write once, after every router is done
with hosts_file.open("w") as f:
    yaml.safe_dump(inventory, f, sort_keys=False, indent=2)

print(f"Wrote {len(devices)} devices to {hosts_file}")




    
