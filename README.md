# Netops Automation

Each tool lives in its own folder and can be used on its own. See the README inside each folder for full setup and usage details.
i
# Network Automation Toolkit

A collection of Python and Ansible tools for automating everyday network engineering tasks: pulling data from devices, checking configs against standards, building a source of truth, and doing the routing maths.

Each tool lives in its own folder and can be used on its own. See the README inside each folder for full setup and usage details.

## Tools

| Tool | What it does | Built with |
|------|--------------|------------|
| [Ansible Automation](./ansible-automation-basic) | Starter Ansible playbooks and inventory for automating network devices | Ansible |
| [Intent Scraper](./intent-scraper) | Scrapes running configs and extracts BGP, OSPF and EIGRP intent into per-router YAML | Python, Netmiko, CiscoConfParse |
| [Netmiko to CSV](./netmiko-to-csv) | Runs show commands on devices with Netmiko and exports the results to CSV | Python, Netmiko |
| [Network Config Compliance Tool](./network-config-compliance-tool) | Checks device configurations against a defined standard and reports what doesn't match | Python |
| [Route Summarisation Tool](./route-summarization-tool) | Calculates summary routes from a list of prefixes | Python |

## Repository structure

```
.
├── ansible-automation/
├── intent-scraper/
├── netmiko-to-csv/
├── network-config-compliance-tool/
├── route-summarisation-tool/
└── README.md
```


Create a virtual environment so each tool's dependencies stay separate from your system Python:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

Then move into the tool you want and install its requirements:

```bash
cd intent-scraper
pip install -r requirements.txt
```

### General requirements

- Python 3.8+
- Ansible (for `ansible-automation-basic` only)
- SSH access to your network devices for any tool that connects live

## Tool overview

### Ansible Automation Basic

Introductory Ansible setup for network automation: an inventory of devices and playbooks for common tasks. A good starting point if you're new to running Ansible against network gear.


### Intent Scraper

A brownfield bootstrap tool for building a network source of truth. It pulls `show running-config` from Cisco IOS routers (or reads saved configs in mock mode), extracts BGP, OSPF and EIGRP intent, and writes one YAML file per router for you to review and adopt as your source of truth.


### Netmiko to CSV

Connects to devices over SSH with Netmiko, runs show commands, and exports the output to CSV so it can be opened in a spreadsheet, shared, or fed into other tools.


### Network Config Compliance Tool

Compares device configurations against a defined baseline or policy and reports any deviations, so you can spot drift and non-standard config across the network.


### Route Summarization Tool

Takes a list of IP prefixes and works out the summary routes that cover them, saving you from doing the binary maths by hand when designing or cleaning up routing.


## Credentials and safety

- **Never commit credentials.** Use environment variables, an Ansible Vault, or a secrets manager, and add any local credential files to `.gitignore`.
- **Test in a lab first.** Run tools against mock data or lab devices before pointing them at production.
- **Read-only by default.** Prefer tools and playbooks that only gather data until you're confident in what a change will do.

