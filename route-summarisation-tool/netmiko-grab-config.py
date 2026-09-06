from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException

""" base logic for the config grab
"""

arr = ['192.168.0.190']
def connect_netmiko(host):
    device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": "admin",
        "password": "cisco",
        "port": 22,
        "fast_cli": 10,
        "read_timeout_override": None,
    }
    with ConnectHandler(**device) as conn:
        config = conn.send_command("sh ip route ospf", use_textfsm=True)

    return config
    

routing_table = {}

for a in arr:
    output = connect_netmiko(a)
    for i in output:
        if isinstance(i, dict):
            network = i.get("network")
            prefix = i.get("prefix_length") or i.get("mask")
            if network and prefix:
                routing_table[network] = prefix


