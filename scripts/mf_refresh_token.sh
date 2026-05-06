#!/bin/bash
# MF Cloud Token Refresh Script
# crontab: 0 * * * * ~/.hermes/scripts/mf_refresh_token.sh
set -e
source ~/.hermes/.env 2>/dev/null || true
AUTH=$(echo -n "${MF_CLIENT_ID}:${MF_CLIENT_SECRET}" | base64)
RESPONSE=$(curl -s -X POST "https://api.biz.moneyforward.com/token" \
  -H "Authorization: Basic $AUTH" \
  -d "grant_type=refresh_token&refresh_token=${MF_REFRESH_TOKEN}")
ACCESS=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
REFRESH=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['refresh_token'])")
sed -i "s|MF_ACCESS_TOKEN=.*|MF_ACCESS_TOKEN=${ACCESS}|" ~/.hermes/.env
sed -i "s|MF_REFRESH_TOKEN=.*|MF_REFRESH_TOKEN=${REFRESH}|" ~/.hermes/.env
python3 - <<EOF
import yaml, os
cfg = os.path.expanduser("~/.hermes/config.yaml")
with open(cfg) as f: c = yaml.safe_load(f)
if c.get("mcp_servers", {}).get("mfc_ca", {}):
    c["mcp_servers"]["mfc_ca"]["headers"]["Authorization"] = f"Bearer {ACCESS}"
    with open(cfg, "w") as f: yaml.dump(c, f)
EOF
echo "$(date): Token refreshed OK" >> ~/.hermes/logs/mf_token_refresh.log
