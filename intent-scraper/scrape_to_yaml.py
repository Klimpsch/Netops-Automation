"""
device (or mock) -> running-config -> intent YAML.

Writes one out_yaml/<hostname>.yaml per router. These are a BOOTSTRAP of the
source of truth: extracted intent that you then review and hand-clean (e.g.
collapse the iBGP neighbors back into a shared mesh block).
"""

import sys
import yaml
from pathlib import Path

from pull import pull_from_mock  # swap for pull_from_device(...) with a device
from parse import parse_running_config

HERE = Path(__file__).parent

# For the mock we just list the saved configs.
INVENTORY = ["rtr1"]


def main():
    out_dir = HERE / "out_yaml"
    out_dir.mkdir(exist_ok=True)

    for name in INVENTORY:
        # LIVE: running = pull_from_device(host=..., username=..., password=...)
        running = pull_from_mock(name)
        router = parse_running_config(running)
        text = yaml.safe_dump(router, sort_keys=False, default_flow_style=False)
        out_path = out_dir / f"{router['hostname']}.yaml"
        out_path.write_text(text)
        print(f"  {name} -> out_yaml/{out_path.name}")
        print("-" * 60)
        print(text)


if __name__ == "__main__":
    main()
