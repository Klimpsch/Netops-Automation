# Route summarisation tool

Fetch OSPF routes from Cisco devices via Netmiko. Compute minimal set of aggregate prefixes to summarise them.

## Description

Python tool that automates OSPF route summarisation. It connects via SSH (Netmiko), and pulls all OSPF learned routes ('show ip route ospf') and computes the minal set of aggregate prefixes for summary statements.

**benefits**
- Smaller routing tables
- Faster, more stable OSPF convergence
- Plan OSPF area boundaries and aggregation before touch a device.
- Catch bad addressing (discontiguous blocks)
- Eliminates manual error

## Prerequisites

- CML Labs 2.10
- Python 3, Netmiko


