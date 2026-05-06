# MF Cloud MCP + Hermes Agent

Moneyforward Cloud 会計のMCPサーバーにOAuth 2.0で接続し、Hermes Agentから勘定科目・試算表・仕訳を自動取得するための設定ガイドです。

## 前提条件

- Moneyforward Cloud 会計 利用者
- Moneyforward Developer Console アクセス可能
- Hermes Agent 導入済み

## 設定の流れ

### 1. Developer ConsoleでOAuthアプリ作成

https://developer.moneyforward.com/ にアクセスし、「連携用アプリを作成」:

| 項目 | 値 |
|------|-----|
| アプリ名 | `Hermes Agent CA` (任意) |
| クライアント認証方式 | `CLIENT_SECRET_BASIC` |
| リダイレクトURI | `http://localhost:8080/callback` |

**必要なスコープ**:
- `mfc/accounting/journal.read`
- `mfc/accounting/journal.write`
- `mfc/accounting/report.read`
- `mfc/accounting/master.read`
- `mfc/accounting/offices.read`
- `mfc/accounting/accounts.read`
- `mfc/accounting/departments.read`
- `mfc/accounting/taxes.read`
- `mfc/accounting/trade_partners.read`
- `mfc/accounting/connected_account.read`
- `mfc/accounting/transaction.write`

> ⚠️ `mfc/ca_api/*` スコープは **NOT_FOUND** エラーのため使用禁止

以下を保存: `CLIENT_ID`, `CLIENT_SECRET`

### 2. OAuth認証

```bash
# コールバックサーバー起動
lsof -ti:8080 | xargs kill -9 2>/dev/null
python3 scripts/mf_callback_server.py &

# Authorization URL生成 & ブラウザで開く
python3 - <<'PY'
import urllib.parse
CLIENT_ID = "YOUR_CLIENT_ID"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "mfc/accounting/journal.read mfc/accounting/journal.write mfc/accounting/report.read mfc/accounting/master.read"
AUTH_URL = "https://api.biz.moneyforward.com/authorize?" + urllib.parse.urlencode({
    "response_type": "code", "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI, "scope": SCOPE, "state": "hermes_mf",
})
print(AUTH_URL)
PY
```

ブラウザでURLを開き、MFCログイン → 許可。

### 3. Access Token取得

```bash
AUTH=$(echo -n "CLIENT_ID:CLIENT_SECRET" | base64)
curl -s -X POST "https://api.biz.moneyforward.com/token" \
  -H "Authorization: Basic $AUTH" \
  -d "grant_type=authorization_code&code=YOUR_CODE&redirect_uri=http://localhost:8080/callback"
```

### 4. MCPサーバー設定

`~/.hermes/config.yaml`:

```yaml
mcp_servers:
  mfc_ca:
    url: https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3
    headers:
      Authorization: Bearer mf_api_pro_YOUR_API_KEY
    timeout: 120
    connect_timeout: 60
```

> ⚠️ **必ず `alpha` エンドポイントを使用**。`beta` は401/403 エラー

### 5. APIキー取得 (アプリポータル)

https://app-portal.moneyforward.com/ で:

1. 「ユーザー」→ 該当ユーザー選択 → 「編集」
2. 「アプリ連携権限」→ 「アプリ連携」+ 「クラウド会計・確定申告」にチェック
3. アプリ選択 → 「認証情報」→ APIキー確認

### 6. Hermes再起動

```
/exit
hermes
```

## 認証方式 (二重認証)

```
HTTP Header: Authorization: Bearer mf_api_pro_...  (MCPサーバー用)
Tool引数:    access_token: <OAuth access_token>    (MF API呼び出し用)
```

## トラブルシューティング

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `invalid_token` | APIキー不正 | alphaエンドポイント確認 |
| `insufficient_scope` | スコープ不足 | Developer Consoleで追加 |
| `insufficient_permissions` | アプリ権限不足 | アプリポータルで付与 |
| 全API NOT_FOUND | サービス連携未完了 | Developer Console → 連携 |
| redirect_uri_mismatch | URI不一致 | Developer Console登録URI確認 |
| ブラウザ画面が止まる | コールバックサーバー未起動 | `lsof -ti:8080` 確認 |

## License

MIT
