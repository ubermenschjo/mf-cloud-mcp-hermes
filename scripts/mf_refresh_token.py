#!/usr/bin/env python3
"""
MF Cloud OAuth Token Auto-Refresh Script
=========================================
주요 갱신 수단: Hermes Agent cronjob (job_id=a92739108f79)
이 스크립트: Hermes cron의 fallback / 수동 실행용

토큰 저장소: ~/.hermes/mf_tokens.json

사용법 (수동/emergency):
  python3 ~/.hermes/scripts/mf_refresh_token.py

Hermes cron 등록 (이미 완료):
  cronjob tool — job_id=a92739108f79
  schedule: 50m, repeat: 999999, deliver: local
"""

import os, json, time, urllib.request, base64, urllib.parse

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
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {}


def save_tokens(data: dict) -> None:
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.chmod(TOKEN_FILE, 0o600)


def needs_refresh(tokens: dict) -> bool:
    if not tokens.get("access_token") or not tokens.get("refresh_token"):
        return True
    expires_at = tokens.get("expires_at", 0)
    return (expires_at - time.time()) < 300   # 5-min buffer


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    credentials  = f"{client_id}:{client_secret}"
    auth_header   = f"Basic {base64.b64encode(credentials.encode()).decode()}"
    data = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "refresh_token": refresh_token,
    }).encode()

    req = urllib.request.Request(
        TOKEN_URL, data=data,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept":        "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())

    now = time.time()
    return {
        "access_token":  result["access_token"],
        "refresh_token": result.get("refresh_token", refresh_token),
        "expires_at":    now + result.get("expires_in", 3600),
        "updated_at":    now,
    }


def main() -> None:
    env = load_env()
    if not env.get("MF_CLIENT_ID") or not env.get("MF_CLIENT_SECRET"):
        log("ERROR: MF_CLIENT_ID or MF_CLIENT_SECRET not found in ~/.hermes/.env")
        raise SystemExit(1)

    tokens = load_tokens()
    if not needs_refresh(tokens):
        expires_in = max(0, int(tokens.get("expires_at", 0) - time.time()))
        log(f"still fresh (expires in {expires_in}s). Skip.")
        return

    log("Refreshing token...")
    try:
        new_tokens = refresh_access_token(
            env["MF_CLIENT_ID"], env["MF_CLIENT_SECRET"],
            tokens.get("refresh_token", ""),
        )
    except Exception as e:
        log(f"ERROR: Refresh failed: {e}")
        raise SystemExit(1)

    save_tokens(new_tokens)
    expires_in = int(new_tokens.get("expires_at", 0) - time.time())
    log(f"OK — new token expires in ~{expires_in}s")


if __name__ == "__main__":
    main()
