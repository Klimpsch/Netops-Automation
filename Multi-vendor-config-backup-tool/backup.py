import logging
import yaml
import keyring
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from netmiko import ConnectHandler

logging.basicConfig(level=logging.INFO)

@dataclass
class Device:
    hostname: str
    ip: str
    vendor: str
    port: int = 22
    username:str = ""

    def backup_command(self):
        """return show commands based on vendor. If no command in dict return show running-config"""

        commands = {
            "cisco_ios": "show running-config",
            "cisco_xe": "show running-config",
            "cisco_xr": "show running-config",
            "cisco_nxos": "show running-config",
            "arista_eos": "show running-config",
            "juniper_junos": "show configuration | display set",
            "paloalto_panos": "show config running"
        }
        return commands.get(self.vendor, "show running-config")


def connect(dev, password):
    """pass instance of Device to connection handler and return back to caller"""

    params = {
            "device_type": dev.vendor,
            "host": dev.ip,
            "username": dev.username,
            "password": password,
            "port": dev.port,
            "conn_timeout": 15,
            }
    try:
        return ConnectHandler(**params)
    except Exception as e:
        logging.error("%s: connection failed: %s", dev.hostname, e)
        return None


def fetch_config(conn, dev):
    """Run our backup command and return to caller"""

    return conn.send_command(dev.backup_command())


def write_config(dev, output, backup_dir="backups"):
    """Check for backups dir or make it. Timestamp and name file"""

    Path(backup_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"{dev.hostname}_{timestamp}.cfg"
    path = Path(backup_dir) / filename

    path.write_text(output)
    return path


def git_commit():
    return None


def load_devices(path="inventory.yaml"):
    with open(path) as f:
        raw = yaml.safe_load(f)

    return [Device(**entry) for entry in raw]


def main():

    password = keyring.get_password("IOS-XE", "admin")
    if password is None:
        raise SystemExist("No password in keyring for IOS-XE")
   
    devices = load_devices()

    for dev in devices:
        conn = connect(dev, password)
        if conn is None:
            continue
        try:
            output = fetch_config(conn, dev)
            path = write_config(dev, output)
            logging.info("%s: saved to %s", dev.hostname, path)
        finally:
            conn.disconnect()
    


if __name__ == "__main__":
    main()




