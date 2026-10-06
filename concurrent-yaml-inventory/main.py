import os
import sys
from getpass import getpass
 
import yaml
from netmiko import ConnectHandler
 
# Short interface names used by some show commands -> full names
ABBR = {"Gi": "GigabitEthernet", "Te": "TenGigabitEthernet", "Lo": "Loopback", "Vl": "Vlan"}
 
 
def full_name(name):
    for short, long in ABBR.items():
        if name.startswith(short) and not name.startswith(long):
            return long + name[len(short):]
    return name
 
 
device = {
    "device_type": "cisco_ios",
    "host": "192.168.122.221",
    "username": "admin",
    "password": os.environ.get("NET_PASSWORD") or getpass("Password: "),
    "port": 22,
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
 


