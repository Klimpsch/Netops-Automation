"""
Transport layer: pull 'show running-config' off a device with Netmiko.
"""

from pathlib import Path

HERE = Path(__file__).parent


def pull_from_device(host: str, username: str, password: str,
                     device_type: str = "cisco_ios") -> str:
    """Live pull. Uncomment the import when netmiko is installed + device reachable."""
    from netmiko import ConnectHandler

    conn = ConnectHandler(
        device_type=device_type,
        host=host,
        username=username,
        password=password,
    )
    try:
        # 'terminal length 0' handled automatically by Netmiko
        return conn.send_command("show running-config")
    finally:
        conn.disconnect()


def pull_from_mock(name: str) -> str:
    """Read a saved 'show run' so the parser runs without a device."""
    return (HERE / "mock_configs" / f"{name}.txt").read_text()
