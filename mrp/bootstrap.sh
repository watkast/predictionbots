#!/usr/bin/env bash
# Mr. P — one-line install for a fresh Ubuntu 22.04/24.04 or Debian 12 box (run as root):
#
#   curl -sSL https://raw.githubusercontent.com/watkast/predictionbots/mrp/mrp/bootstrap.sh | bash
#
# What it does: installs Python + git, clones the kit to /opt/mrp/repo, creates a venv, asks for the
# Polymarket US key (optional — Enter to skip), installs two systemd services (recorder + status page),
# and prints the status URL. Safe to re-run: it updates the code and restarts the services.
set -euo pipefail

REPO_URL="${MRP_REPO_URL:-https://github.com/watkast/predictionbots.git}"
BRANCH="${MRP_BRANCH:-mrp}"
SUBDIR="${MRP_SUBDIR:-mrp}"
BASE=/opt/mrp

if [ "$(id -u)" -ne 0 ]; then echo "run as root (sudo -i first)"; exit 1; fi
export DEBIAN_FRONTEND=noninteractive
echo "[1/5] packages"
apt-get update -qq >/dev/null
apt-get install -y -qq python3 python3-venv python3-pip git curl ca-certificates >/dev/null

echo "[2/5] code -> $BASE/repo (branch $BRANCH)"
mkdir -p "$BASE/data"
if [ -d "$BASE/repo/.git" ]; then
  git -C "$BASE/repo" fetch -q origin "$BRANCH" && git -C "$BASE/repo" reset -q --hard "origin/$BRANCH"
else
  git clone -q --depth 1 -b "$BRANCH" "$REPO_URL" "$BASE/repo"
fi
KIT="$BASE/repo/$SUBDIR"

echo "[3/5] python env"
[ -d "$BASE/venv" ] || python3 -m venv "$BASE/venv"
"$BASE/venv/bin/pip" install -q --upgrade pip >/dev/null
"$BASE/venv/bin/pip" install -q -r "$KIT/requirements.txt"

echo "[4/5] config"
if [ ! -f "$BASE/.env" ]; then
  TOKEN="$(head -c 24 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 16)"
  KID=""; SEC=""
  if [ -r /dev/tty ]; then
    printf "Polymarket US Key ID (Enter to skip — keyless mode records everything public): "
    read -r KID < /dev/tty || KID=""
    if [ -n "$KID" ]; then
      printf "Polymarket US Secret Key (input hidden): "
      read -rs SEC < /dev/tty || SEC=""
      echo; echo "  secret length: ${#SEC} chars (Polymarket's are 88)"
    fi
  fi
  {
    echo "MRP_DATA_DIR=$BASE/data"
    echo "MRP_STATUS_PORT=8787"
    echo "MRP_STATUS_TOKEN=$TOKEN"
    if [ -n "$KID" ]; then
      echo "POLYMARKET_KEY_ID=$KID"
      echo "POLYMARKET_SECRET_KEY=$SEC"
    fi
  } > "$BASE/.env"
  chmod 600 "$BASE/.env"
  echo "  wrote $BASE/.env"
else
  echo "  keeping existing $BASE/.env"
fi

echo "[5/5] services"
cat > /etc/systemd/system/mrp.service <<EOF
[Unit]
Description=Mr. P recorder
After=network-online.target
Wants=network-online.target
[Service]
WorkingDirectory=$BASE
EnvironmentFile=$BASE/.env
ExecStart=$BASE/venv/bin/python3 $KIT/mrp_recorder.py
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
cat > /etc/systemd/system/mrp-status.service <<EOF
[Unit]
Description=Mr. P status page
After=network-online.target
[Service]
WorkingDirectory=$BASE
EnvironmentFile=$BASE/.env
ExecStart=$BASE/venv/bin/python3 $KIT/mrp_status.py
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
# helper commands
cat > /usr/local/bin/mrp-update <<EOF
#!/usr/bin/env bash
set -e
MRP_BRANCH=$BRANCH MRP_REPO_URL=$REPO_URL MRP_SUBDIR=$SUBDIR bash $KIT/bootstrap.sh
EOF
cat > /usr/local/bin/mrp-logs <<'EOF'
#!/usr/bin/env bash
journalctl -u mrp -f -n 50 -o cat
EOF
cat > /usr/local/bin/mrp-report <<EOF
#!/usr/bin/env bash
set -a; . $BASE/.env; set +a
$BASE/venv/bin/python3 $KIT/mrp_analyze.py "\$MRP_DATA_DIR" --csv $BASE/data/windows.csv "\$@"
EOF
cat > /usr/local/bin/mrp-keys <<EOF
#!/usr/bin/env bash
# rotate keys: mrp-keys   (prompts, rewrites only the key lines, restarts the recorder)
set -e
printf "Polymarket US Key ID: "; read -r KID
printf "Polymarket US Secret Key (hidden): "; read -rs SEC; echo
grep -v '^POLYMARKET_' $BASE/.env > $BASE/.env.tmp
printf 'POLYMARKET_KEY_ID=%s\nPOLYMARKET_SECRET_KEY=%s\n' "\$KID" "\$SEC" >> $BASE/.env.tmp
mv $BASE/.env.tmp $BASE/.env && chmod 600 $BASE/.env
systemctl restart mrp && echo "keys updated, recorder restarted"
EOF
chmod +x /usr/local/bin/mrp-update /usr/local/bin/mrp-logs /usr/local/bin/mrp-report /usr/local/bin/mrp-keys
systemctl daemon-reload
systemctl enable -q mrp mrp-status
systemctl restart mrp mrp-status
if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q "Status: active"; then ufw allow 8787/tcp >/dev/null || true; fi

sleep 2
IP="$(curl -s -4 --max-time 5 https://ifconfig.me || hostname -I | awk '{print $1}')"
TOKEN="$(grep '^MRP_STATUS_TOKEN=' "$BASE/.env" | cut -d= -f2-)"
echo
echo "================================================================"
echo " recorder: $(systemctl is-active mrp)    status page: $(systemctl is-active mrp-status)"
echo " STATUS URL (bookmark it):  http://$IP:8787/?k=$TOKEN"
echo " commands: mrp-logs | mrp-report | mrp-update | mrp-keys"
echo "================================================================"
journalctl -u mrp -n 5 --no-pager -o cat || true
