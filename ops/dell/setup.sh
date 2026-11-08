#!/usr/bin/env bash
# One-time setup on the Dell (run as root): user, checkout, venv, systemd service. Idempotent.
set -euo pipefail
REPO="${GITHUB_REPO:-watkast/predictionbots}"
id -u predictionbots >/dev/null 2>&1 || useradd -r -m -d /var/lib/predictionbots -s /bin/bash predictionbots
mkdir -p /etc/predictionbots /var/lib/predictionbots /opt
[ -f /etc/predictionbots/env ] || { cp "$(dirname "$0")/env.example" /etc/predictionbots/env; echo "edit /etc/predictionbots/env, then re-run"; exit 1; }
chmod 600 /etc/predictionbots/env
set -a; . /etc/predictionbots/env; set +a
if [ ! -d /opt/predictionbots/.git ]; then
  git clone -q --depth 1 "https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git" /opt/predictionbots
fi
chown -R predictionbots:predictionbots /opt/predictionbots /var/lib/predictionbots
sudo -u predictionbots bash -c 'cd /opt/predictionbots && python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip && .venv/bin/pip install -q -r mrp/requirements.txt'
install -m 644 /opt/predictionbots/ops/dell/predictionbots-recorder.service /etc/systemd/system/
chmod +x /opt/predictionbots/ops/dell/record_loop.sh
systemctl daemon-reload
systemctl enable --now predictionbots-recorder
systemctl --no-pager status predictionbots-recorder | head -5
echo "recorder running; journalctl -u predictionbots-recorder -f to watch"
