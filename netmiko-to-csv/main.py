from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException
import csv
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("NETADMIN")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")



def get_interface_data(username, password, host):
    """ Collects just hostname with interface and IPs """

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
            hostname = conn.send_command("sh run | i hostname", use_textfsm=True)
            conn.disconnect()

    except NetmikoTimeoutException:
        print("Unreachable / SSH not responding")
    except NetmikoAuthenticationException:
        print("Bad username/password/secret")

    return data, hostname



data, hostname = get_interface_data(username, password, host)


hostname = hostname.strip('hostname')
rows = []
for item in data:
    rows.append({
                "hostname": hostname,
                "interface": item.get("interface"),
                "ip address": item.get("ip_address"),
    })


with open("Interface_IP_Data.csv", 'w', newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["hostname", "interface", "ip address"])
    writer.writeheader()
    writer.writerows(rows)


