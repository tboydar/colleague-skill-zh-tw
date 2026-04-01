# 同事.skill 安裝說明

---

## 選擇你的平台

### A. Claude Code（推薦）

本專案遵循官方 [AgentSkills](https://agentskills.io) 標準，整個 repo 就是 skill 目錄。Clone 到 Claude skills 目錄即可：

```bash
# ⚠️ 必須在 git 倉庫根目錄執行！
cd $(git rev-parse --show-toplevel)

# 方式 1：安裝到目前專案
mkdir -p .claude/skills
git clone https://github.com/tboydar/colleague-skill .claude/skills/create-colleague

# 方式 2：安裝到全域（所有專案都能用）
git clone https://github.com/tboydar/colleague-skill ~/.claude/skills/create-colleague
```

然後在 Claude Code 中說 `/create-colleague` 即可啟動。

生成的同事 Skill 預設寫入 `./colleagues/` 目錄。

---

### B. OpenClaw

```bash
# Clone 到 OpenClaw 的 skills 目錄
git clone https://github.com/tboydar/colleague-skill ~/.openclaw/workspace/skills/create-colleague
```

重啟 OpenClaw session，說 `/create-colleague` 啟動。

---

## 相依套件安裝

```bash
# 基礎（Python 3.9+）
pip3 install pypinyin        # 中文姓名轉拼音 slug（選用但推薦）

# 其他格式支援（選用）
pip3 install python-docx     # Word .docx 轉文字
pip3 install openpyxl        # Excel .xlsx 轉 CSV
```

### 資料來源方案選擇指南

| 場景 | 推薦方案 |
|------|---------|
| Slack 使用者 | `slack_auto_collector.py`（自動採集） |
| LINE 使用者 | 手動匯出 .txt → 直接上傳 |
| Discord 使用者 | 手動匯出或使用 [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) → 上傳 |
| Teams 使用者 | 手動匯出 → 上傳 |
| Email | `email_parser.py`（支援 .eml / .mbox） |
| 其他（PDF、截圖、Markdown）| 手動上傳 |

> **LINE / Discord / Teams 匯出說明**：這些平台匯出的都是純文字檔，不需要安裝額外工具或設定 API。匯出後直接上傳即可。

**Slack 自動採集初始化**：
```bash
pip3 install slack-sdk
python3 tools/slack_auto_collector.py --setup
# 按提示輸入 Bot User OAuth Token（xoxb-...）
```

> Slack 詳細設定見下方「[Slack 自動採集設定](#slack-自動採集設定)」章節

---

## Slack 自動採集設定

### 前置條件

- Python 3.9+
- Slack Workspace（需要**管理員權限**安裝 App，或請管理員幫你安裝）
- `pip3 install slack-sdk`

> **免費版 Workspace 限制**：只能存取最近 **90 天**的訊息記錄。付費版（Pro / Business+ / Enterprise）無此限制。

---

### 步驟 1：建立 Slack App

1. 前往 [https://api.slack.com/apps](https://api.slack.com/apps) → **Create New App**
2. 選擇 **From scratch**
3. 填寫 App Name（如 `colleague-skill-bot`），選擇目標 Workspace → **Create App**

---

### 步驟 2：設定 Bot Token Scopes

進入 **OAuth & Permissions** → **Bot Token Scopes** → **Add an OAuth Scope**，新增以下權限：

| Scope | 用途 |
|-------|------|
| `users:read` | 搜尋使用者列表（必要） |
| `channels:read` | 列出 public channels（必要） |
| `channels:history` | 讀取 public channel 歷史訊息（必要） |
| `groups:read` | 列出 private channels（必要） |
| `groups:history` | 讀取 private channel 歷史訊息（必要） |
| `mpim:read` | 列出群組 DM（選用） |
| `mpim:history` | 讀取群組 DM 歷史訊息（選用） |
| `im:read` | 列出 DM（選用，需使用者授權） |
| `im:history` | 讀取 DM 歷史訊息（選用，需使用者授權） |

---

### 步驟 3：安裝 App 到 Workspace

1. 仍在 **OAuth & Permissions** 頁面，點擊 **Install to Workspace**
2. Workspace 管理員審批後，複製 **Bot User OAuth Token**（格式：`xoxb-...`）

---

### 步驟 4：將 Bot 加入目標頻道

Bot 只能讀取**它已加入**的頻道。在 Slack 中，進入每個目標頻道，輸入：

```
/invite @your-bot-name
```

> 提示：如果你不知道目標同事在哪些頻道，可以先不邀請，執行採集時腳本會告知 Bot 加入了哪些頻道，再補充邀請。

---

### 步驟 5：執行設定精靈

```bash
python3 tools/slack_auto_collector.py --setup
```

按提示貼上 Bot Token，腳本會自動驗證並儲存到 `~/.colleague-skill/slack_config.json`。

設定成功後你會看到：
```
驗證 Token ... OK
  Workspace：Your Company，Bot：colleague-skill-bot

✅ 設定已儲存到 /Users/you/.colleague-skill/slack_config.json
```

---

### 步驟 6：採集同事資料

```bash
# 基本用法（輸入同事的中文名或英文使用者名稱）
python3 tools/slack_auto_collector.py --name "王小明"
python3 tools/slack_auto_collector.py --name "john.doe"

# 指定輸出目錄
python3 tools/slack_auto_collector.py --name "王小明" --output-dir ./knowledge/xiaoming

# 限制採集量（大 Workspace 建議先小量測試）
python3 tools/slack_auto_collector.py --name "王小明" --msg-limit 500 --channel-limit 20
```

輸出檔案：
```
knowledge/王小明/
├── messages.txt            # 按權重分類的訊息記錄
└── collection_summary.json # 採集摘要（使用者資訊、頻道列表、時間）
```

---

### 常見錯誤與排除

| 錯誤訊息 | 原因 | 解法 |
|----------|------|------|
| `missing_scope: channels:history` | Bot Token 缺少權限 | 回到 api.slack.com → OAuth & Permissions 新增對應 Scope，重新安裝 App |
| `invalid_auth` | Token 無效或已撤銷 | 重新執行 `--setup` 設定新 Token |
| `not_in_channel` | Bot 未加入該頻道 | 在 Slack 裡 `/invite @bot` 邀請 Bot |
| 未找到使用者 | 姓名拼寫不對 | 改用英文使用者名稱（如 `john.doe`）或 Slack display name |
| 訊息只有 90 天 | 免費版限制 | 升級 Workspace 或手動補充截圖 |
| 速率限制（429）| 請求太頻繁 | 腳本會自動等待重試，無需手動處理 |

---

## LINE / Discord / Teams 匯出方式

這些平台不需要設定 API 或安裝額外工具，匯出純文字檔後直接上傳即可。

### LINE

1. 開啟要匯出的聊天室
2. 點選右上角選單 → **其他設定** → **匯出聊天記錄**
3. 選擇 **以文字檔傳送**
4. 將 `.txt` 檔上傳給 `/create-colleague`

### Discord

**方式 A**：使用 [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter)（推薦，可匯出完整歷史）

```bash
# CLI 版本
dotnet tool install -g DiscordChatExporter.Cli
# 匯出為純文字
DiscordChatExporter.Cli export -t YOUR_TOKEN -c CHANNEL_ID -f PlainText
```

**方式 B**：手動複製訊息 → 貼上文字

### Microsoft Teams

1. 開啟要匯出的聊天或頻道
2. 選取訊息範圍 → 複製
3. 貼上到文字檔，或直接在 `/create-colleague` 中使用「直接貼上文字」

> 提示：Teams 目前沒有官方的完整匯出功能，建議分批複製貼上，或搭配截圖補充。

---

## 快速驗證

```bash
cd ~/.claude/skills/create-colleague   # 或你的專案 .claude/skills/create-colleague

# 測試 Slack 採集器
python3 tools/slack_auto_collector.py --help

# 測試信件解析器
python3 tools/email_parser.py --help

# 列出已有同事 Skill
python3 tools/skill_writer.py --action list --base-dir ./colleagues
```

---

## 目錄結構說明

本專案整個 repo 就是一個 skill 目錄（AgentSkills 標準格式）：

```
colleague-skill/        ← clone 到 .claude/skills/create-colleague/
├── SKILL.md            # skill 入口（官方 frontmatter）
├── prompts/            # 分析和生成的 Prompt 模板
├── tools/              # Python 工具腳本
├── docs/               # 文件（PRD 等）
│
└── colleagues/         # 生成的同事 Skill 存放處（.gitignore 排除）
    └── {slug}/
        ├── SKILL.md            # 完整 Skill（Persona + Work）
        ├── work.md             # 僅工作能力
        ├── persona.md          # 僅人物性格
        ├── meta.json           # 中繼資料
        ├── versions/           # 歷史版本
        └── knowledge/          # 原始素材歸檔
```
