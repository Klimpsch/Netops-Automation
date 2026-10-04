# Check configuratoin vs golden config yaml file
# tested working C8000v Version 17.18.2, C1000v 17.03.08a


import os
import sys
import requests
import yaml


DEVICE_HOST = "192.168.122.110"
DEVICE_USER = ""
DEVICE_PASS = ""
GOLDEN_FILE = "golden_ntp.yml"


NTP_URL = f"https://{DEVICE_HOST}/restconf/data/Cisco-IOS-XE-native:native/ntp"
HEADERS = {"Accept": "application/yang-data+json"}


def load_golden(path):
    with open(path) as f:
        return yaml.safe_load(f)


def fetch_actual_ntp():
    response = requests.get(
        NTP_URL,
        auth=(DEVICE_USER, DEVICE_PASS),
        headers=HEADERS,
        verify=False,  # lab self-signed cert; use a real CA bundle in production
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    server_entries = data["Cisco-IOS-XE-native:ntp"]["Cisco-IOS-XE-ntp:server"]["server-list"]
    return [entry["ip-address"] for entry in server_entries]



def compare(golden_servers, actual_servers):
    missing = set(golden_servers) - set(actual_servers)
    extra = set(actual_servers) - set(golden_servers)
    return missing, extra



def main():

    golden = load_golden(GOLDEN_FILE)
    actual_servers = fetch_actual_ntp()
    missing, extra = compare(golden["servers"], actual_servers)

    if not missing and not extra:
        print(f"PASS: {DEVICE_HOST} NTP config matches golden config")
        return 0

    print(f"FAIL: {DEVICE_HOST} NTP config drifted from golden config")
    if missing:
        print(f"  missing servers (in golden, not on device): {sorted(missing)}")
    if extra:
        print(f"  extra servers (on device, not in golden):   {sorted(extra)}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
