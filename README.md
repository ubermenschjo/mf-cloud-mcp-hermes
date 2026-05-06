# MF Cloud MCP + Hermes Agent

Hermes Agent에서 MoneyForward Cloud 회계 데이터를 자동 취득하는 설정.

## 인증 2중 구조

- HTTP Header: `Authorization: Bearer mf_api_pro_...` (영구)
- OAuth Token: `access_token` 파라미터 (1시간마다 갱신)

## 빠른 시작

### 1. 환경변수 설정

~/.hermes/.env:
```
MF_CLIENT_ID=271822152199586
MF_CLIENT_SECRET=your_secret
MF_API_KEY=mf_api_pro_...
MF_REDIRECT_URI=http://localhost:8080/callback
```

### 2. 토큰 초기 설정

Hermes Agent에서 mcp_mfc_ca_mfc_ca_authorize -> 브라우저 승인 -> 콜백

### 3. 토큰 자동 갱신 (Hermes Cron, 1회만 등록)

```bash
hermes cron create \
  --name mf-token-refresh \
  --schedule "50m" \
  --repeat 999999 \
  --deliver local \
  --prompt "MF Cloud Access Token 자동 갱신..."
```

현재 등록된 job: job_id=a92739108f79 (50분마다, deliver=local)

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
    └── mf_refresh_token.py     # 토큰 갱신 (Hermes cron 또는 직접 실행)
```

## 토큰 관리 파일

| 파일 | 내용 |
|------|------|
| ~/.hermes/.env | MF_CLIENT_ID, MF_CLIENT_SECRET, MF_API_KEY |
| ~/.hermes/mf_tokens.json | access_token + refresh_token (Hermes cron이 자동 갱신) |
| ~/.hermes/logs/mf_refresh.log | 갱신 이력 |

## 주의사항

- Access Token TTL = 1시간 (3600s)
- Refresh Token TTL = 540일
- Hermes cron 50분마다 설정 — 만료 5분 전 갱신
- crontab 불필요 (Hermes Agent cronjob 사용)
