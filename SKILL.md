---
name: moneyforward-mcp
description: MFクラウド API(MCP CA v3) 연결 및 자동 회계 처리. 1인日本법인 결산월 9월.
---

# MFクラウド MCP Skill

## 인증 구조 (2중)

| 계층 | 값 | 갱신 주기 |
|------|----|----------|
| API 키 (HTTP 헤더) | `Authorization: Bearer mf_api_pro_...` | 영구 |
| OAuth Access Token (툴 파라미터) | `access_token` | **1시간** (TTL=3600s) |

## 토큰 자동 갱신 (Hermes Cron — primary)

Hermes Agent 내장 스케줄러가 자동으로 50분마다 갱신.

현재 등록 상태:
```
job_id:     a92739108f79
name:       mf-token-refresh
schedule:   50분마다
repeat:     999999회
deliver:    local (로그만 저장)
```

관리 명령:
```
hermes cron list       # 상태 확인
hermes cron pause <id> # 일시 정지
hermes cron remove <id> # 삭제
```

토큰 파일: `~/.hermes/mf_tokens.json`
로그 파일: `~/.hermes/logs/mf_refresh.log`

## Fallback 스크립트

Hermes cron이 비활성화된 경우 수동 실행:
```bash
python3 ~/.hermes/scripts/mf_refresh_token.py
```

## 주요 MCP 툴

### 회계 데이터
- `mfc_ca_currentOffice` — 법인/결산 기간
- `mfc_ca_getJournals` — 仕訳一覧
- `mfc_ca_getReportsTrialBalanceProfitLoss` — PL試算表
- `mfc_ca_getReportsTrialBalanceBalanceSheet` — BS試算表
- `mfc_ca_getReportsTransitionProfitLoss` — 月次推移

### 마스터 데이터 (権限必要)
- `mfc_ca_getAccounts` — 勘定科目
- `mfc_ca_getTaxes` — 税区分
- `mfc_ca_getTradePartners` — 取引先

### 仕訳作成
- `mfc_ca_postJournals` — 仕訳作成

## 엔드포인트 / アプリ情報

- MCP: `https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3`
- OAuth Token: `https://api.biz.moneyforward.com/token`
- OAuth client_id: 271822152199586
- MCP OAuth client_id: 166838700725625
