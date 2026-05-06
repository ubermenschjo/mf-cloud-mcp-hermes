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

Access Token은 만료 시 자동 갱신 필요.

## 토큰 자동 갱신

토큰은 `~/.hermes/mf_tokens.json` 에 저장되고 관리됨.

cron 등록:
```
*/50 * * * * /usr/bin/python3 ~/.hermes/scripts/mf_refresh_token.py >> ~/.hermes/logs/mf_refresh.log 2>&1
```

스크립트: `scripts/mf_refresh_token.py`

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

1. 토큰 갱신 스크립트 cron 등록 (1회)
2. 새 세션: memory에서 access_token 확인 후 툴에 전달
3. 필요 시 mcp_mfc_ca_authorize 로 새 인증
4. 50분마다 cron이 자동 토큰 갱신
