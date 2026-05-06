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

## 토큰 자동 갱신 (Hermes Cron)

Hermes Agent 내장 스케줄러 사용 — crontab 불필요.

```bash
# Hermes Agent에서 등록
hermes cron create \
  --name mf-token-refresh \
  --schedule "50m" \
  --repeat 999999 \
  --deliver local \
  --prompt "MF Cloud Access Token 자동 갱신..."
```

또는 cronjob 툴로 직접 등록 (이 세션에서 이미 등록됨: job_id=a92739108f79)

토큰 상태 파일: `~/.hermes/mf_tokens.json`

## 주요 MCP 툴

### 회계 데이터
- `mfc_ca_currentOffice` - 법인/결산 기간 정보
- `mfc_ca_getJournals` - 仕訳一覧
- `mfc_ca_getReportsTrialBalanceProfitLoss` - PL試算表
- `mfc_ca_getReportsTrialBalanceBalanceSheet` - BS試算表
- `mfc_ca_getReportsTransitionProfitLoss` - 月次推移

### 마스터 데이터 (権限必要)
- `mfc_ca_getAccounts` - 勘定科目
- `mfc_ca_getTaxes` - 税区分
- `mfc_ca_getTradePartners` - 取引先

### 仕訳作成
- `mfc_ca_postJournals` - 仕訳作成

## 엔드포인트

- MCP: `https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3`
- OAuth Token: `https://api.biz.moneyforward.com/token`

## アプリ情報

- OAuth client_id: 271822152199586
- MCP 자체 OAuth client_id: 166838700725625

## ワークフロー

1. Hermes cron 등록 (1회): 50분마다 토큰 자동 갱신
2. 새 세션: memory에서 access_token 확인 후 툴에 전달
3. 필요 시 mcp_mfc_ca_authorize 로 새 인증
4. Hermes cron이 자동 토큰 갱신 ( deliver=local, 로그 저장)
