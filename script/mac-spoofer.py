import subprocess
import random
import re
import sys
import time
import argparse
from datetime import datetime

def get_current_mac(interface):
    result = subprocess.run(["ip", "link", "show", interface], capture_output=True, text=True)
    mac_match = re.search(r"link/ether ([0-9a-f:]{17})", result.stdout)
    return mac_match.group(1) if mac_match else None

def generate_random_mac():
    mac = [0x02, random.randint(0x00, 0xff), random.randint(0x00, 0xff),
           random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    return ':'.join(f"{octet:02x}" for octet in mac)

def change_mac(interface, new_mac):
    subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "down"], check=True)
    subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "address", new_mac], check=True)
    subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "up"], check=True)

def rotate_mac(interface, interval, count=None):
    """Change MAC repeatedly every `interval` seconds. If count is None, run until Ctrl+C."""
    original_mac = get_current_mac(interface)
    print(f"Original MAC: {original_mac}")
    print(f"Rotating every {interval}s on {interface}... (Ctrl+C to stop)\n")

    cycles = 0
    try:
        while count is None or cycles < count:
            new_mac = generate_random_mac()
            change_mac(interface, new_mac)
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] MAC changed to {new_mac}")

            cycles += 1
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        restore = input(f"Restore original MAC ({original_mac})? [y/N]: ")
        if restore.lower() == "y":
            change_mac(interface, original_mac)
            print(f"Restored to {original_mac}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotate a network interface's MAC address periodically")
    parser.add_argument("interface", help="e.g. eth0, wlan0")
    parser.add_argument("--interval", type=float, default=5, help="Seconds between changes (default: 5)")
    parser.add_argument("--count", type=int, default=None, help="Number of changes (default: run until Ctrl+C)")
    args = parser.parse_args()

    rotate_mac(args.interface, args.interval, args.count)
