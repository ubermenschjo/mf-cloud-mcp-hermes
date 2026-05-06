---
name: moneyforward-mcp
description: "MFクラウド API OAuth + MCPサーバー設定"
version: 2.0.0
author: Hermes Agent
license: MIT
tags: [moneyforward, oauth, mcp, accounting, japan]
---

# Moneyforward MCP + OAuth Setup

## 発見済みエンドポイント

| 用途 | URL |
|------|-----|
| Authorization | `https://api.biz.moneyforward.com/authorize` |
| Token | `https://api.biz.moneyforward.com/token` |
| OAuth Discovery | `https://api.biz.moneyforward.com/.well-known/oauth-authorization-server` |
| **MCP Server** | `https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3` (betaではない) |

## 認証方式 (二重認証)

```
HTTP Header: Authorization: Bearer mf_api_pro_...  (MCPサーバー認証)
Tool引数:    access_token: <OAuth access_token>   (MF API呼び出し)
```

## 重要: alpha vs beta

- alpha: APIキー + OAuth 토큰 모두 동작
- beta: API키 401, OAuth insufficient_scope
- **alpha만 사용**

## アプリポータル設定

https://app-portal.moneyforward.com/ で:
1. 「ユーザー」→ 該当ユーザー → 編集
2. 「アプリ連携権限」→ 「アプリ連携」+ 「クラウド会計・確定申告」にチェック

## Pitfalls

1. `beta` MCPエンドポイント → 401/403。必ず`alpha`使用
2. `curl localhost:8080` 直接実行 → タイムアウト。バックグラウンド実行必須
3. Redirect URI不一致 → ブラウザ画面が止まる
4. サービス未連携 → 全API `NOT_FOUND`
5. `mfc/ca_api/*` スコープ → 必ず `mfc/accounting/*` を使用
