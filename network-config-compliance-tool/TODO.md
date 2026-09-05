# TODO — Compliance Drift Tool (NTP / domain / banner)

## Setup & inputs
- [ ] `requirements.txt`: pyats[full] (pulls genie), PyYAML
- [ ] `golden_ntp.yaml` (or `compliance.yaml`) with expected ntp_servers / domain / banner
- [ ] `testbed.yaml` with devices + connection details
- [ ] Decide: one flat golden file, or per-group (site/role) golden
- [ ] Set up logging

## Loaders
- [ ] `load_golden(path)` — YAML → dict of expected values
- [ ] `load_testbed(path)` — genie.testbed.load → device objects
- [ ] `golden_for(device, golden)` — only if per-group; merge default + group overrides

## Device state (gather)
- [ ] `connect(device)` — with error handling
- [ ] `get_ntp(device)` — device.parse() the NTP command
- [ ] `get_domain(device)` — parse or "show run | include domain"
- [ ] `get_banner(device)` — device.execute() (no parser for banners)
- [ ] Confirm the real parsed structure of each show command before writing checks

## Checks (compare vs golden)
- [ ] `check_ntp(actual, expected)` — set compare; return None or {missing, extra}
- [ ] `check_domain(actual, expected)` — return None or {expected, actual}
- [ ] `check_banner(actual, expected)` — normalized/substring; None or {expected, actual}
- [ ] Convention: None = compliant, dict = drift detail

## Aggregation
- [ ] `build_drift(device, rules)` — run 3 checks, return per-device dict ({} = clean)
- [ ] `collect_drift(devices, rules)` — loop, connect/disconnect, assemble {host: drift}
- [ ] Per-device isolation — one failure doesn't stop the run

## Output
- [ ] `print_drift(drift)` — "all compliant" or per-device detail
- [ ] `write_drift(drift, path)` — JSON (machine) or YAML (human); timestamp filename
- [ ] `disconnect(device)` — always close (finally)

## Orchestration
- [ ] `main()` — load golden + testbed → collect_drift → print + write
- [ ] Exit non-zero when drift found (cron/CI signal)
- [ ] `if __name__ == "__main__": main()`

## Validation & error handling
- [ ] Handle connect failures (unreachable/auth) per device
- [ ] Handle missing/unparseable output (device returns nothing)
- [ ] Guard against empty golden file / missing keys

## Later
- [ ] ThreadPoolExecutor
- [ ] Timestamped drift history for trend/diffing
- [ ] Per-group golden (site/role)
- [ ] Summary counts (compliant vs drifted)
- [ ] aetest wrapper for formal pass/fail reporting
