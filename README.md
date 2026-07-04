# MAC Address Spoofing (with Rotation)

## Objective
Learn how MAC addresses work at the network interface level by building a
tool that spoofs and periodically rotates a device's MAC address. This
demonstrates both a common privacy/anti-fingerprinting technique and how
MAC-based access controls can be bypassed on your own network.

## Tools Used
- Python 3 (`subprocess`, `argparse`, `re`, `time`)
- Linux `ip` command (`iproute2`)

## ⚠️ Legal & Ethical Notice
Only run this on network interfaces and devices you own. Spoofing MAC
addresses to bypass access controls on networks you don't own or don't have
explicit permission to test is illegal in most jurisdictions. Rotating your
MAC will also disconnect you from any active network session each time it
changes — this is expected behavior, not a bug.

## Setup

### 1. Requirements
- Linux (uses `ip link` — no extra Python packages needed)
- Run as root/with `sudo` (changing a MAC address requires elevated
  privileges)

### 2. Find your interface name
```bash
ip a
```
Look for something like `eth0`, `wlan0`, or `enp0s3`.

## Usage

```bash
# Rotate MAC every 5 seconds (default) until stopped with Ctrl+C
sudo python3 scripts/mac-spoofer.py eth0

# Rotate every 3 seconds
sudo python3 scripts/mac-spoofer.py eth0 --interval 3

# Rotate every 5 seconds, but only 10 times total, then stop automatically
sudo python3 scripts/mac-spoofer.py eth0 --interval 5 --count 10
```

When stopped (via Ctrl+C or after `--count` is reached), the script asks
whether to restore the original MAC address.

## How It Works
1. Reads and stores the interface's current (original) MAC address using
   `ip link show`.
2. Generates a new random MAC address each cycle:
   - The first byte is fixed to `02`, marking it as a "locally administered"
     address so it won't collide with real vendor-assigned MACs.
   - The remaining 5 bytes are randomized.
3. Applies the new MAC by bringing the interface down, setting the new
   address, then bringing it back up (required — the kernel won't allow a
   live MAC change on an active interface).
4. Repeats this every `--interval` seconds, either indefinitely or for
   `--count` cycles.
5. On exit, offers to restore the original MAC so the interface isn't left
   in a spoofed state.

## Sample Output
```
Original MAC: aa:bb:cc:dd:ee:ff
Rotating every 5.0s on eth0... (Ctrl+C to stop)

[14:02:11] MAC changed to 02:a3:9f:11:88:7c
[14:02:16] MAC changed to 02:5d:c2:44:0e:91
[14:02:21] MAC changed to 02:e7:1a:bb:33:02
^C
Stopped by user.
Restore original MAC (aa:bb:cc:dd:ee:ff)? [y/N]: y
Restored to aa:bb:cc:dd:ee:ff
```

## Project Structure
```
03-mac-spoofing/
├── README.md
├── scripts/
│   └── mac_spoofer.py
└── examples/
    └── sample_output.txt
```

## What I Learned
- How MAC addresses are structured, and what the "locally administered"
  bit means and why it matters when generating fake addresses
- Why a network interface must be taken down before its hardware address
  can be changed
- How MAC rotation disrupts active connections (DHCP leases, ARP tables)
  and why this is a real side effect, not an error
- How to build a configurable CLI tool with `argparse` (positional vs.
  optional arguments, defaults)
- Safe cleanup patterns using `try/except/finally` so interrupting a script
  mid-loop doesn't leave the system in a broken state
