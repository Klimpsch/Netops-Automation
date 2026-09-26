from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException

from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("NETADMIN")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")


csv_data = {}

# Create lists first then assign to dict
interfaces = []
ips = []



device = {
        "device_type": "cisco_ios",
        "username": username,
        "password": password,
        "host": host,
        "port": 22,
        "fast_cli": False,
        "conn_timeout": 10,
        "read_timeout_override": None,
}
try:
    with ConnectHandler(**device) as conn:
        data  = conn.send_command("sh ip int brief", use_textfsm=True)
        conn.disconnect()

except NetmikoTimeoutException:
    print("Unreachable / SSH not responding")
except NetmikoAuthenticationException:
    print("Bad username/password/secret")

for item in data:
    for key, value in item.items():
        if 'interface' in key:
            interfaces.append(value)

        elif 'ip' in key:
            ips.append(value) 

csv_data['interfaces'] = interfaces
csv_data['ip address'] = ips

for item in csv_data.items():
    for i in item:
        print(i)
