"""
Parse raw 'show running-config' -> per-router intent dict.

Uses CiscoConfParse to walk the config hierarchy. Each protocol has its own
parser that pulls the fields the YAML schema cares about and drops the rest.
"""

import re
from ciscoconfparse import CiscoConfParse


def _hostname(parse: CiscoConfParse) -> str:
    objs = parse.find_objects(r"^hostname\s+")
    return objs[0].text.split()[1] if objs else "unknown"

def parse_bgp(parse: CiscoConfParse) -> dict:
    """Walk 'router bgp' -> asn, router_id, and split neighbors into iBGP/eBGP."""
    bgp_objs = parse.find_objects(r"^router bgp ")
    if not bgp_objs:
        return {}
    bgp = bgp_objs[0]
    asn = int(bgp.text.split()[2])

    router_id = None
    # collect neighbor attributes from the top level of the bgp block
    neigh = {}   # ip -> {remote_as, description, update_source}
    for child in bgp.children:
        t = child.text.strip()
        m = re.match(r"bgp router-id (\S+)", t)
        if m:
            router_id = m.group(1)
            continue
        m = re.match(r"neighbor (\S+) remote-as (\d+)", t)
        if m:
            neigh.setdefault(m.group(1), {})["remote_as"] = int(m.group(2))
            continue
        m = re.match(r"neighbor (\S+) description (.+)", t)
        if m:
            neigh.setdefault(m.group(1), {})["description"] = m.group(2)
            continue
        m = re.match(r"neighbor (\S+) update-source (\S+)", t)
        if m:
            neigh.setdefault(m.group(1), {})["update_source"] = m.group(2)

    # address-family blocks: activation + next-hop-self per neighbor
    af_flags = {}  # ip -> {af_name -> {next_hop_self}}
    for af in bgp.re_search_children(r"address-family "):
        af_name = af.text.strip().replace("address-family ", "").replace(" ", "_")
        for c in af.children:
            m = re.match(r"neighbor (\S+) next-hop-self", c.text.strip())
            if m:
                af_flags.setdefault(m.group(1), {}).setdefault(af_name, {})["next_hop_self"] = True
            m = re.match(r"neighbor (\S+) activate", c.text.strip())
            if m:
                af_flags.setdefault(m.group(1), {}).setdefault(af_name, {})

    ibgp, ebgp = [], []
    for ip, attrs in neigh.items():
        entry = {"peer": ip, "remote_as": attrs.get("remote_as")}
        if attrs.get("description"):
            entry["description"] = attrs["description"]
        if attrs.get("update_source"):
            entry["update_source"] = attrs["update_source"]
        afs = []
        for af_name, flags in af_flags.get(ip, {"ipv4_unicast": {}}).items():
            af_entry = {"name": af_name}
            if flags.get("next_hop_self"):
                af_entry["next_hop_self"] = True
            afs.append(af_entry)
        entry["address_families"] = afs or [{"name": "ipv4_unicast"}]

        if attrs.get("remote_as") == asn:
            # iBGP: drop description/update_source that the mesh will re-add,
            # but keep them here so nothing is silently lost on first extract.
            ibgp.append(entry)
        else:
            ebgp.append(entry)

    return {
        "_router_id": router_id,   # lifted to top level by the caller
        "asn": asn,
        "ibgp_neighbors": ibgp,
        "ebgp_neighbors": ebgp,
    }


def parse_ospf(parse: CiscoConfParse) -> dict:
    objs = parse.find_objects(r"^router ospf ")
    if not objs:
        return {}
    ospf = objs[0]
    process_id = int(ospf.text.split()[2])
    out = {"process_id": process_id, "networks": [], "passive_interfaces": []}
    for c in ospf.children:
        t = c.text.strip()
        m = re.match(r"auto-cost reference-bandwidth (\d+)", t)
        if m:
            # Schema stores this in Mbps, identical to the IOS command value.
            out.setdefault("defaults", {})["reference_bandwidth"] = int(m.group(1))
            continue
        m = re.match(r"network (\S+) (\S+) area (\S+)", t)
        if m:
            out["networks"].append(
                {"prefix": m.group(1), "wildcard": m.group(2), "area": _maybe_int(m.group(3))}
            )
            continue
        m = re.match(r"passive-interface (\S+)", t)
        if m:
            out["passive_interfaces"].append(m.group(1))
    if not out["passive_interfaces"]:
        del out["passive_interfaces"]
    return out


def parse_eigrp(parse: CiscoConfParse) -> dict:
    objs = parse.find_objects(r"^router eigrp ")
    if not objs:
        return {}
    eigrp = objs[0]
    out = {"networks": []}
    # named-mode: 'address-family ipv4 unicast autonomous-system N'
    for af in eigrp.re_search_children(r"address-family ipv4 unicast autonomous-system"):
        m = re.search(r"autonomous-system (\d+)", af.text)
        if m:
            out["as_number"] = int(m.group(1))
        for c in af.children:
            m = re.match(r"network (\S+) (\S+)", c.text.strip())
            if m:
                out["networks"].append({"prefix": m.group(1), "wildcard": m.group(2)})
    # classic-mode fallback: networks directly under 'router eigrp N'
    if "as_number" not in out:
        parts = eigrp.text.split()
        if len(parts) >= 3 and parts[2].isdigit():
            out["as_number"] = int(parts[2])
        for c in eigrp.children:
            m = re.match(r"network (\S+)(?:\s+(\S+))?", c.text.strip())
            if m:
                net = {"prefix": m.group(1)}
                if m.group(2):
                    net["wildcard"] = m.group(2)
                out["networks"].append(net)
    return out


def _maybe_int(s: str):
    return int(s) if s.isdigit() else s


def parse_running_config(running: str) -> dict:
    parse = CiscoConfParse(running.splitlines(), syntax="ios")
    bgp = parse_bgp(parse)
    router_id = bgp.pop("_router_id", None) if bgp else None

    router = {"hostname": _hostname(parse)}
    if router_id:
        router["router_id"] = router_id
    if bgp:
        router["bgp"] = bgp
    ospf = parse_ospf(parse)
    if ospf:
        router["ospf"] = ospf
    eigrp = parse_eigrp(parse)
    if eigrp:
        router["eigrp"] = eigrp
    return router
