# MF Cloud MCP + Hermes Agent

Hermes Agent에서 MoneyForward Cloud 회계 데이터를 자동 취득하는 설정.

## 인증 2중 구조

```
Hermes Agent
  └── MCP Server (alpha.mcp.developers...)
        ├── HTTP Header:  Authorization: Bearer mf_api_pro_...  (영구)
        └── OAuth Token:   access_token 파라미터 (1시간마다 갱신)
```

## 빠른 시작

### 1. 환경변수 설정

~/.hermes/.env:
```
MF_CLIENT_ID=271822152199586
MF_CLIENT_SECRET=your_secret
MF_API_KEY=mf_api_pro_...
```

### 2. 토큰 초기 설정

Hermes Agent에서:
```
mcp_mfc_ca_mfc_ca_authorize
→ 브라우저에서 승인
→ 콜백 서버가 Authorization Code 수신
```

### 3. 토큰 자동 갱신 (Hermes Cron — 1회만 등록)

이미 등록되어 있습니다:
```
job_id:     a92739108f79
schedule:   50분마다 (Access Token TTL 3600s, 5분 버퍼)
repeat:     999,999회
deliver:    local (채팅 방해 없음)
```

재등록이 필요한 경우:
```
cronjob(action='create', name='mf-token-refresh',
        schedule='50m', repeat=999999, deliver='local',
        prompt='MF Cloud Access Token 자동 갱신...')
```

### 4. 로그 확인

```bash
cat ~/.hermes/logs/mf_refresh.log
hermes cron list
```

## 파일 구조

```
mf-cloud-mcp-hermes/
├── README.md
├── SKILL.md
├── LICENSE (MIT)
├── .env.example
├── .gitignore
└── scripts/
    ├── mf_callback_server.py   # OAuth 콜백 서버 (1회성)
    ├── mf_refresh_token.py     # 토큰 갱신 (Hermes cron primary)
    └── mf_refresh_token.sh     # Fallback (deprecated, bash용)
```

## 토큰 관리 파일

| 파일 | 내용 |
|------|------|
| ~/.hermes/.env | MF_CLIENT_ID, MF_CLIENT_SECRET, MF_API_KEY |
| ~/.hermes/mf_tokens.json | access_token + refresh_token |
| ~/.hermes/logs/mf_refresh.log | 갱신 이력 |

## 주의사항

- Access Token TTL = 1시간 (3600s)
- Refresh Token TTL = 540일
- **crontab 불필요** — Hermes Agent cronjob 사용
- Hermes cron이 비활성화된 경우: `python3 ~/.hermes/scripts/mf_refresh_token.py`
