from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException


ip_list = [
    '10.0.255.1',
    '10.1.255.101',
    '10.1.255.102',
    '10.1.255.103',
    '10.0.255.3',
    '10.3.255.101',
    '10.3.255.102',
    '10.3.255.103',
    '10.3.255.104',
    '10.0.255.4',
    '10.4.255.101',
    '10.4.255.102',
    '10.4.255.103',
    '10.2.255.101',
    '10.2.255.102',
    '10.2.255.103',
    '10.2.255.104'
]

arr = ['192.168.0.190']
def connect_netmiko(host):
    """ Connect and grab only ospf routes """

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

""" base logic for the config grab """

for a in ip_list:
    output = connect_netmiko(a)
    for i in output:
        if isinstance(i, dict):
            network = i.get("network")
            prefix = i.get("prefix_length") or i.get("mask")
            if network and prefix:
                routing_table[network] = prefix

for key, value in routing_table.items():
    print(key, value)
