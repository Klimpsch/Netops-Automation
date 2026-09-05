# Configuration-Compliance-tool
This repository enforces baseline configuration standards across the device fleet using declarative YAML policy definitions. Each policy specifies the expected state for common compliance checks NTP servers, login banners, SNMP settings, AAA, logging targets, and similar controls

## Tested Platforms

| Platform | IOS-XE Version | Status |
|----------|---------------|--------|
| Catalyst 8000v | 17.18.2 | ✅ Working |
| Catalyst 1000v | 17.03.08a | ✅ Working |

### Requirements

- RESTCONF enabled on the device:
restconf
ip http secure-server

- A user with privilege level 15 (or appropriate RESTCONF/AAA authorization)
- Python 3.x with `requests` and `pyyaml`
- Network reachability to the device's HTTPS (443) management interface

### Notes

- Uses the `Cisco-IOS-XE-native` YANG model; tested against 17.x. Earlier IOS-XE
  releases may nest things differently.
- `verify=False` is used for lab self-signed certificates

### Test endpoints manually prior to find correct nesting
```
curl -k -u admin:Cisco123 \
  -H "Accept: application/yang-data+json" \
  https://192.168.122.128/restconf/data/Cisco-IOS-XE-native:native/ip/domain | jq
```
