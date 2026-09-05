import sys
import requests
import yaml

DEVICE_HOST = "192.168.122.128"
DEVICE_USER = ""
DEVICE_PASS = ""
GOLDEN_FILE = "golden_domain.yml"

DOMAIN_URL = f"https://{DEVICE_HOST}/restconf/data/Cisco-IOS-XE-native:native/ip/domain"
HEADERS = {"Accept": "application/yang-data+json"}


def load_golden(path):
    with open(path) as f:
        return yaml.safe_load(f)


def fetch_actual_domain():
    response = requests.get(
        DOMAIN_URL,
        auth=(DEVICE_USER, DEVICE_PASS),
        headers=HEADERS,
        verify=False,  # lab self-signed cert; use a real CA bundle in production
        timeout=10,
    )
    response.raise_for_status()

    if response.status_code == 204 or not response.text.strip():
        return None  # no domain configured on device

    data = response.json()

    return data["Cisco-IOS-XE-native:domain"].get("name")


def main():
    golden = load_golden(GOLDEN_FILE)
    golden_domain = golden["domain"]
    actual_domain = fetch_actual_domain()

    if actual_domain == golden_domain:
        print(f"PASS: {DEVICE_HOST} domain name matches golden config ({golden_domain})")
        return 0

    print("\n")
    print(f"FAIL: {DEVICE_HOST} domain name drifted from golden config")
    print(f"  golden: {golden_domain}")
    print(f"  device: {actual_domain}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
