#!/bin/bash
# MF Cloud Token Refresh Script (DEPRECATED)
# =============================================
# 이 스크립트는 deprecated입니다.
# 주요 토큰 갱신 수단: Hermes Agent cronjob
#   job_id: a92739108f79
#   schedule: 50분마다, deliver: local
#
# 이 스크립트는 Hermes cron이 비활성화된 경우에만 사용:
#   python3 ~/.hermes/scripts/mf_refresh_token.py
#   또는: bash ~/.hermes/scripts/mf_refresh_token.sh
#
set -e
source ~/.hermes/.env 2>/dev/null || true

AUTH=$(echo -n "${MF_CLIENT_ID}:${MF_CLIENT_SECRET}" | base64)
RESPONSE=$(curl -s -X POST "https://api.biz.moneyforward.com/token" \
  -H "Authorization: Basic $AUTH" \
  -d "grant_type=refresh_token&refresh_token=${MF_REFRESH_TOKEN}")

ACCESS=$(echo "$RESPONSE" | python3 -c \
  "import sys,json; print(json.load(sys.stdin)['access_token'])")
REFRESH=$(echo "$RESPONSE" | python3 -c \
  "import sys,json; print(json.load(sys.stdin)['refresh_token'])")

# Update mf_tokens.json
python3 - <<'PYEOF'
import json, os, time
tf = os.path.expanduser("~/.hermes/mf_tokens.json")
data = {
    "access_token":  """ + ""$ACCESS"" + """,
    "refresh_token": """ + ""$REFRESH"" + """,
    "expires_at":    time.time() + 3600,
    "updated_at":    time.time(),
}
with open(tf, "w") as f:
    json.dump(data, f, indent=2)
os.chmod(tf, 0o600)
PYEOF

echo "$(date): Token refreshed OK" >> ~/.hermes/logs/mf_refresh.log
