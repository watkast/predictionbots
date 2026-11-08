# The Dell T3600: always-on recorder (no trading)

The home box runs the Mr. P recorder continuously and publishes to the `mrp-data` branch every 10 minutes, exactly as
the GitHub Actions job does, minus the 5.6-hour restarts and the gaps between them. GitHub Actions stays as the backstop
(`mrp-record.yml` keeps its schedule; both write under different `run-*` folders, so they never collide).

Outbound only (T-Mobile CGNAT); nothing needs to reach the box. The site deploys from GitHub Actions to Cloudflare
Pages, not from here.

## One-time setup (Ubuntu 22.04/24.04, or Windows 11 with WSL2 Ubuntu)

1. Packages: `sudo apt install -y git python3-venv python3-pip`
2. A GitHub token that can push to this repo (fine-grained PAT, Contents: read/write, this repo only) or a deploy key
   with write access. Put it in `/etc/predictionbots/env` (see `env.example`), together with the Kalshi and
   Polymarket US API keys the recorder uses for its WebSocket layers (the same values as the repo secrets).
3. `sudo bash ops/dell/setup.sh` — clones to `/opt/predictionbots`, makes a venv, installs `mrp/requirements.txt`,
   installs and starts the `predictionbots-recorder` systemd service (auto-restart, starts on boot).
4. Check: `systemctl status predictionbots-recorder` and `journalctl -u predictionbots-recorder -f`. Within 10 minutes a
   `run-<date>-dell` folder appears on the `mrp-data` branch.

## What the service does
`ops/dell/record_loop.sh` runs `mrp/mrp_recorder.py` under the venv, publishes every `MRP_PUBLISH_SECONDS` (600) to
`mrp-data` with the same gzip + report steps as the Actions runner, and self-updates when `mrp/` changes on `main`
(pulls, reinstalls requirements, restarts the recorder). Data lives under `/var/lib/predictionbots/mrpdata` and is
rotated by the recorder itself.

## Power and noise
The recorder is I/O-light: one Python process, a few WebSocket connections, well under 1 GB RAM. The GPU is idle; the
box can run at its lowest fan curve. Expect roughly $10/month in power.
