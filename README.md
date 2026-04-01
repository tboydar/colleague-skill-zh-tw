<div align="center">

# 同事.skill

> *「你們搞大模型的就是碼奸——前端的飯碗已經砸了，接下來要砸後端、測試、維運、資安、IC，最後連自己都砸掉，害死全人類。」*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

你的同事跳槽去台積電了，留下一堆沒人維護的文件？<br>
你的實習生離職了，只剩空蕩蕩的座位和爛尾的專案？<br>
你的學長畢業了，帶走了所有經驗和上下文？<br>
你的搭檔轉組了，默契一夕之間歸零？<br>
你的前任交接了，三頁文件想概括三年的累積？<br>

**把冰冷的離別化為溫暖的 Skill，歡迎加入賽博永生！**

<br>

提供同事的原始素材（Slack 訊息、LINE 對話、Email、截圖）加上你的主觀描述<br>
生成一個**真正能替他工作的 AI Skill**<br>
用他的技術規範寫程式碼，用他的語氣回答問題，知道他什麼時候會甩鍋

[資料來源](#支持的資料來源) · [安裝](#安裝) · [使用](#使用) · [效果示例](#效果示例) · [詳細安裝說明](INSTALL.md) · [**English**](README_EN.md)

</div>

---

### 🌟 同系列專案：[前任.skill](https://github.com/titanwings/ex-skill)

> 根據大家的 issue 回饋，更新了一版 **前任.skill**！現已支援：
>
> - **LINE 聊天記錄自動匯入**（手動匯出 .txt 即可）
> - **iMessage 全自動提取**（macOS 使用者）
> - **完整星盤解讀**（太陽/月亮/上升/金星/火星/水星 × 12 星座）
> - **MBTI 16 型 + 認知功能**、九型人格、依附風格全支援
> - 支援所有性別認同與關係類型
>
> 同事跑了用 **同事.skill**，前任跑了用 **[前任.skill](https://github.com/titanwings/ex-skill)**，賽博永生一條龍 🌟🌟🌟
>
> 覺得有趣的話，幫兩個專案都點個 Star 吧！

---

## 支持的資料來源

> 目前還是同事.skill 的 beta 測試版本，後續會有更多來源支援，請多多關注！

| 來源 | 訊息記錄 | 文件 / Wiki | 備註 |
|------|:-------:|:-----------:|------|
| Slack（自動採集）| ✅ API | — | 需管理員安裝 Bot；免費版限 90 天 |
| LINE 對話匯出 | ✅ | — | 手動匯出 .txt |
| Discord 匯出 | ✅ | — | 手動匯出或使用 DiscordChatExporter |
| Teams 匯出 | ✅ | — | 手動匯出 |
| PDF | — | ✅ | 手動上傳 |
| 圖片 / 截圖 | ✅ | — | 手動上傳 |
| Email `.eml` / `.mbox` | ✅ | — | 手動上傳 |
| Markdown | ✅ | ✅ | 手動上傳 |
| 直接貼上文字 | ✅ | — | 手動輸入 |

---

## 安裝

### Claude Code

> **重要**：Claude Code 從 **git 倉庫根目錄** 的 `.claude/skills/` 尋找 skill。請在正確的位置執行。

```bash
# 安裝到目前專案（在 git 倉庫根目錄執行）
mkdir -p .claude/skills
git clone https://github.com/tboydar/colleague-skill .claude/skills/create-colleague

# 或安裝到全域（所有專案都能用）
git clone https://github.com/tboydar/colleague-skill ~/.claude/skills/create-colleague
```

### OpenClaw

```bash
git clone https://github.com/tboydar/colleague-skill ~/.openclaw/workspace/skills/create-colleague
```

### 相依套件（選用）

```bash
pip3 install -r requirements.txt
```

> Slack 自動採集需設定 App 憑證，詳見 [INSTALL.md](INSTALL.md)

---

## 使用

在 Claude Code 中輸入：

```
/create-colleague
```

按提示輸入同事姓名、公司職級（如 `聯發科 資深後端工程師`）、性格標籤，然後選擇資料來源。所有欄位均可跳過，僅憑描述也能生成。

完成後用 `/{slug}` 呼叫該同事 Skill。

### 管理指令

| 指令 | 說明 |
|------|------|
| `/list-colleagues` | 列出所有同事 Skill |
| `/{slug}` | 呼叫完整 Skill（Persona + Work） |
| `/{slug}-work` | 僅工作能力 |
| `/{slug}-persona` | 僅人物性格 |
| `/colleague-rollback {slug} {version}` | 回滾到歷史版本 |
| `/delete-colleague {slug}` | 刪除 |

---

## 效果示例

> 輸入：`聯發科 資深後端工程師，INTJ，甩鍋高手，聯發科風`

**場景一：Code Review**

```
使用者      ❯ 幫我看一下這個 API 設計

同事.skill ❯ 等等，這個介面的 impact 是什麼？背景沒講清楚。
             （看完後）N+1 查詢，改掉。回傳結構用統一的
             {code, message, data}，這是規範，不用問為什麼。
```

**場景二：甩鍋**

```
使用者      ❯ 這個 bug 是你引入的吧

同事.skill ❯ 上線時間對得上嗎？那個需求改了好幾個地方，還有其他變更。
```

---

## 功能特色

### 生成的 Skill 結構

每個同事 Skill 由兩部分組成，共同驅動輸出：

| 部分 | 內容 |
|------|------|
| **Part A — Work Skill** | 負責系統、技術規範、工作流程、經驗知識庫 |
| **Part B — Persona** | 5 層性格結構：硬規則 → 身份 → 表達風格 → 決策模式 → 人際行為 |

運作邏輯：`接到任務 → Persona 判斷態度 → Work Skill 執行 → 用他的語氣輸出`

### 支援的標籤

**個性**：認真負責 · 甩鍋高手 · 完美主義 · 差不多就行 · 拖延症 · PUA 高手 · 職場政治玩家 · 向上管理專家 · 陰陽怪氣 · 反覆橫跳 · 話少 · 已讀不回 …

**企業文化**：台積電風 · 聯發科風 · 趨勢科技風 · 傳產轉型風 · 外商風 · 蝦皮風 · 第一性原理 · OKR 狂熱者 · 科技業流水線 · 新創風

**職級支援**：
- 台積電（工程師 → 資深 → 主任 → 副理 → 經理 → 處長）
- 聯發科（工程師 → 資深 → 主任 → 經理 → 處長）
- 外商 Google/Meta/Microsoft（L3~L8、SDE I~III → Senior → Staff → Principal）
- 趨勢科技（Engineer → Senior → Staff → Principal）
- 一般科技業（Junior → Mid → Senior → Lead → Manager → Director）
- 傳統產業（專員 → 組長 → 主任 → 副理 → 經理 → 協理 → 副總）

### 進化機制

- **追加檔案** → 自動分析增量 → merge 進對應部分，不覆蓋已有結論
- **對話糾正** → 說「他不會這樣，他應該是 xxx」→ 寫入 Correction 層，立即生效
- **版本管理** → 每次更新自動存檔，支援回滾到任意歷史版本

---

## 專案結構

本專案遵循 [AgentSkills](https://agentskills.io) 開放標準，整個 repo 就是一個 skill 目錄：

```
create-colleague/
├── SKILL.md              # skill 入口（官方 frontmatter）
├── prompts/              # Prompt 模板
│   ├── intake.md         #   對話式資訊錄入
│   ├── work_analyzer.md  #   工作能力提取
│   ├── persona_analyzer.md #  性格行為提取（含標籤翻譯表）
│   ├── work_builder.md   #   work.md 生成模板
│   ├── persona_builder.md #   persona.md 五層結構模板
│   ├── merger.md         #   增量 merge 邏輯
│   └── correction_handler.md # 對話糾正處理
├── tools/                # Python 工具
│   ├── slack_auto_collector.py   # Slack 全自動採集
│   ├── email_parser.py           # 信件解析
│   ├── skill_writer.py           # Skill 檔案管理
│   └── version_manager.py        # 版本存檔與回滾
├── colleagues/           # 生成的同事 Skill（gitignored）
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## 注意事項

- **原始素材品質決定 Skill 品質**：聊天記錄 + 長篇文件 > 僅手動描述
- 建議優先收集：他**主動寫的**長文 > **決策類回覆** > 日常訊息
- Slack 自動採集需將 App Bot 加入相關頻道
- LINE / Discord / Teams 匯出為純文字檔，不需額外工具
- 目前還是 demo 版本，如果有 bug 請多多提 issue！

---

## Star History

<a href="https://www.star-history.com/?repos=tboydar%2Fcolleague-skill&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=tboydar/colleague-skill&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=tboydar/colleague-skill&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=tboydar/colleague-skill&type=date&legend=top-left" />
 </picture>
</a>

---

<div align="center">

MIT License · 台灣在地化 fork，原始專案 © [titanwings](https://github.com/titanwings/colleague-skill)

</div>
