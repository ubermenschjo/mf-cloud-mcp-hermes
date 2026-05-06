#!/usr/bin/env python3
"""
MF Cloud OAuth Token Auto-Refresh Script
=========================================
Hermes Cron: 50분마다 실행 (Access Token TTL=3600s safety margin)

토큰 저장소: ~/.hermes/mf_tokens.json
  {
    "access_token": "...",
    "refresh_token": "...",
    "expires_at": 1746576000,   # Unix timestamp (만료 시점)
    "updated_at":  1746572400    # 마지막 갱신 시각
  }

사용법:
  python3 ~/.hermes/scripts/mf_refresh_token.py

cron 등록 (50분마다):
  crontab -e
  */50 * * * * /usr/bin/python3 ~/.hermes/scripts/mf_refresh_token.py >> ~/.hermes/logs/mf_refresh.log 2>&1
"""

import os
import json
import time
import urllib.request
import base64

HERMES_DIR = os.path.expanduser("~/.hermes")
TOKEN_FILE = os.path.join(HERMES_DIR, "mf_tokens.json")
TOKEN_URL  = "https://api.biz.moneyforward.com/token"
LOG_DIR    = os.path.join(HERMES_DIR, "logs")


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "mf_refresh.log"), "a") as f:
        f.write(f"[{ts}] {msg}\n")


def load_env() -> dict:
    """~/.hermes/.env 에서 MF_CLIENT_ID / MF_CLIENT_SECRET 읽기."""
    env_file = os.path.join(HERMES_DIR, ".env")
    env = {}
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_tokens() -> dict:
    """토큰 저장소 읽기. 없으면 memory에서 참조하라는 메시지 반환."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {}


def save_tokens(data: dict) -> None:
    """토큰 저장소에 기록."""
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.chmod(TOKEN_FILE, 0o600)   #本人以外読めないように


def needs_refresh(tokens: dict) -> bool:
    """Access Token이 5분以内に切れる場合はrefresh必要とみなす."""
    if not tokens.get("access_token") or not tokens.get("refresh_token"):
        return True
    expires_at = tokens.get("expires_at", 0)
    # TTL=3600s → 300s(5分) buffer
    return (expires_at - time.time()) < 300


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    """OAuth refresh_tokengrant でaccess_tokenを更新."""
    credentials = f"{client_id}:{client_secret}"
    auth_header  = f"Basic {base64.b64encode(credentials.encode()).decode()}"

    data = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "refresh_token": refresh_token,
    }).encode()

    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept":       "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())

    access_token  = result["access_token"]
    new_refresh   = result.get("refresh_token", refresh_token)  # 稀にrotate
    expires_in    = result.get("expires_in", 3600)              # 秒単位

    now = time.time()
    return {
        "access_token":  access_token,
        "refresh_token": new_refresh,
        "expires_at":    now + expires_in,
        "updated_at":    now,
    }


def update_memory(new_access_token: str) -> bool:
    """
    Hermes Agent memory 를 새 access_token 으로 업데이트 시도.
    실패해도 스크립트는 종료코드 0 으로 마무리 (log에 기록만).
    """
    try:
        import subprocess
        # memory tool 실행 — 현재 session에서만 동작하므로
        # 별도 프로세스로 hermes-cli memory update 시도
        result = subprocess.run(
            ["hermes", "memory", "update", "--key", "MF_ACCESS_TOKEN",
             "--value", new_access_token],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            log("Memory updated with new access_token")
            return True
        else:
            log(f"Memory update skipped (not in-session): {result.stderr.strip()}")
            return False
    except Exception as e:
        log(f"Memory update error (non-fatal): {e}")
        return False


def main() -> None:
    env    = load_env()
    client_id     = env.get("MF_CLIENT_ID", "")
    client_secret = env.get("MF_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        log("ERROR: MF_CLIENT_ID or MF_CLIENT_SECRET not found in ~/.hermes/.env")
        raise SystemExit(1)

    tokens = load_tokens()

    if not needs_refresh(tokens):
        expires_in = max(0, int(tokens.get("expires_at", 0) - time.time()))
        log(f"Token still fresh (expires in {expires_in}s). Skipping.")
        return

    log("Refreshing token...")
    try:
        new_tokens = refresh_access_token(client_id, client_secret, tokens.get("refresh_token", ""))
    except Exception as e:
        log(f"ERROR: Refresh failed: {e}")
        raise SystemExit(1)

    save_tokens(new_tokens)
    expires_in = int(new_tokens.get("expires_in", 3600))
    log(f"OK — new access_token saved (expires in ~{expires_in}s)")

    # Memory 업데이트 (Non-fatal)
    update_memory(new_tokens["access_token"])


if __name__ == "__main__":
    # urllib.parse は Python 3 才必需
    import urllib.parse
    main()
