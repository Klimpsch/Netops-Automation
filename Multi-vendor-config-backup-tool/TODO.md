# TODO — Multivendor Config Backup Tool

## Setup & dependencies
- [X] Pin deps in `requirements.txt` (paramiko, pyyaml, keyring; optional netmiko)
- [X] Set up `logging` (file + console), no print statements
- [X] Ensure secrets never hit logs or committed files

## Inventory & config
- [X] `Device` dataclass: hostname, ip, vendor, port=22, username=""
- [X] Add `backup_command()` method with vendor→command map
- [X] `inventory.yaml` for devices; load with `Device(**entry)`
- [ ] Vendor→paging-disable map (e.g. `terminal length 0`)

## Auth
- [X] Pull secrets from keyring (per-device or global username strategy)
- [ ] Support SSH key auth as well as password

## Core logic
- [X] `connect(device)` — SSH with connect + command timeouts
- [X] `fetch_config(device)` — run backup command (invoke_shell for network gear)
- [ ] `normalize(output)` — strip echoed command, prompts, volatile timestamps
- [X] `write_file(device, output)` — timestamped filename, ensure dir exists
- [ ] `commit()` — git add/commit, only when content changed
- [ ] Keep fetch / write / commit independent (git failure ≠ lost config)
- [ ] `ThreadPoolExecutor` to back up devices in parallel

## Validation & error handling
- [ ] Catch specific exceptions: AuthenticationException, SSHException, socket.timeout, socket.error
- [ ] Handle auth-failure vs unreachable differently
- [X] `os.makedirs(path, exist_ok=True)` for backup dir
- [ ] Validate output: min plausible length + known-good marker (not just >0 bytes)
- [X] Per-device isolation — one failure doesn't abort the run
- [ ] Retry with backoff on transient failures

## Run & reporting
- [ ] Summary at end: succeeded / failed / skipped
- [ ] Dry-run / test mode (connectivity only, no writes)
- [ ] Meaningful exit codes for cron/CI

## Nice-to-have (later)
- [ ] Config diffing / alert on change
- [ ] Concurrency limit / rate control for large fleets
