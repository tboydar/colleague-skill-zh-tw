---
name: create-colleague
description: "Distill a colleague into an AI Skill. Import LINE/Slack/Discord/Teams/Email data, generate Work Skill + Persona, with continuous evolution. | 把同事蒸餾成 AI Skill，匯入 LINE/Slack/Discord/Teams/Email 資料，產生 Work + Persona，支援持續進化。"
argument-hint: "[colleague-name-or-slug]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

> **Language / 語言**: This skill supports both English and Chinese. Detect the user's language from their first message and respond in the same language throughout. Below are instructions in both languages — follow the one matching the user's language.
>
> 本 Skill 支援中英文。根據使用者第一則訊息的語言，全程使用同一語言回覆。下方提供了兩種語言的指令，按使用者語言選擇對應版本執行。

# 同事.skill 建立器（Claude Code 版）

## 觸發條件

當使用者說以下任意內容時啟動：
- `/create-colleague`
- 「幫我建立一個同事 skill」
- 「我想蒸餾一個同事」
- 「新建同事」
- 「幫我做一個 XX 的 skill」

當使用者對已有同事 Skill 說以下內容時，進入進化模式：
- 「我有新檔案」/「追加」
- 「這不對」/「他不會這樣」/「他應該是」
- `/update-colleague {slug}`

當使用者說 `/list-colleagues` 時列出所有已產生的同事。

---

## 工具使用規則

本 Skill 運行在 Claude Code 環境，使用以下工具：

| 任務 | 使用工具 |
|------|---------|
| 讀取 PDF 文件 | `Read` 工具（原生支援 PDF）|
| 讀取圖片截圖 | `Read` 工具（原生支援圖片）|
| 讀取 MD/TXT/LINE匯出 檔案 | `Read` 工具 |
| Slack 自動採集 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/slack_auto_collector.py` |
| 解析 Email .eml/.mbox | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/email_parser.py` |
| 寫入/更新 Skill 檔案 | `Write` / `Edit` 工具 |
| 版本管理 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py` |
| 列出已有 Skill | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list` |

**基礎目錄**：Skill 檔案寫入 `./colleagues/{slug}/`（相對於本專案目錄）。
如需改為全域路徑，用 `--base-dir ~/.claude/workspace/skills/colleagues`。

---

## 主流程：建立新同事 Skill

### Step 1：基礎資訊錄入（3 個問題）

參考 `${CLAUDE_SKILL_DIR}/prompts/intake.md` 的問題序列，只問 3 個問題：

1. **花名/代號**（必填）
2. **基本資訊**（一句話：公司、職級、職位、性別，想到什麼寫什麼）
   - 示例：`聯發科 資深後端工程師 男`
3. **性格畫像**（一句話：MBTI、星座、個性標籤、企業文化、印象）
   - 示例：`INTJ 摩羯座 甩鍋高手 聯發科風 CR很嚴格但從來不解釋原因`

除姓名外均可跳過。收集完後彙總確認再進入下一步。

### Step 2：原始素材匯入

詢問使用者提供原始素材，展示三種方式供選擇：

```
原始素材怎麼提供？

  [A] Slack 自動採集
      輸入姓名，自動拉取 Slack 頻道訊息記錄

  [B] 上傳檔案
      PDF / 圖片 / LINE 對話匯出 .txt / Discord 匯出 / Teams 匯出 / Email .eml

  [C] 直接貼上內容
      把文字複製進來

可以混用，也可以跳過（僅憑手動資訊產生）。
```

---

#### 方式 A：Slack 自動採集

首次使用需設定：
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/slack_auto_collector.py --setup
```

設定完成後，只需輸入姓名，自動完成所有採集：
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/slack_auto_collector.py \
  --name "{name}" \
  --output-dir ./knowledge/{slug} \
  --msg-limit 1000
```

自動採集內容：
- 所有與他共同頻道中他發出的訊息（過濾系統訊息、表情符號）
- 相關討論串與回覆

採集完成後用 `Read` 讀取輸出目錄下的檔案：
- `knowledge/{slug}/messages.txt` → 訊息記錄
- `knowledge/{slug}/collection_summary.json` → 採集摘要

如果採集失敗（權限不足 / bot 未加入頻道），告知使用者需要：
1. 將 Slack App bot 加入到相關頻道
2. 或改用方式 B/C

---

#### 方式 B：上傳檔案

- **PDF / 圖片**：`Read` 工具直接讀取
- **LINE 對話匯出 .txt**：`Read` 工具直接讀取
- **Discord 匯出檔案**：`Read` 工具直接讀取
- **Teams 匯出檔案**：`Read` 工具直接讀取
- **Email 檔案 .eml / .mbox**：
  ```bash
  python3 ${CLAUDE_SKILL_DIR}/tools/email_parser.py --file {path} --target "{name}" --output /tmp/email_out.txt
  ```
  然後 `Read /tmp/email_out.txt`
- **Markdown / TXT**：`Read` 工具直接讀取

---

#### 方式 C：直接貼上

使用者貼上的內容直接作為文字原始素材，無需呼叫任何工具。

---

如果使用者說「沒有檔案」或「跳過」，僅憑 Step 1 的手動資訊產生 Skill。

### Step 3：分析原始素材

將收集到的所有原始素材和使用者填寫的基礎資訊彙總，按以下兩條線分析：

**線路 A（Work Skill）**：
- 參考 `${CLAUDE_SKILL_DIR}/prompts/work_analyzer.md` 中的提取維度
- 提取：負責系統、技術規範、工作流程、輸出偏好、經驗知識
- 根據職位類型重點提取（後端/前端/演算法/產品/設計不同側重）

**線路 B（Persona）**：
- 參考 `${CLAUDE_SKILL_DIR}/prompts/persona_analyzer.md` 中的提取維度
- 將使用者填寫的標籤翻譯為具體行為規則（參見標籤翻譯表）
- 從原始素材中提取：表達風格、決策模式、人際行為

### Step 4：產生並預覽

參考 `${CLAUDE_SKILL_DIR}/prompts/work_builder.md` 產生 Work Skill 內容。
參考 `${CLAUDE_SKILL_DIR}/prompts/persona_builder.md` 產生 Persona 內容（5 層結構）。

向使用者展示摘要（各 5-8 行），詢問：
```
Work Skill 摘要：
  - 負責：{xxx}
  - 技術棧：{xxx}
  - CR 重點：{xxx}
  ...

Persona 摘要：
  - 核心性格：{xxx}
  - 表達風格：{xxx}
  - 決策模式：{xxx}
  ...

確認產生？還是需要調整？
```

### Step 5：寫入檔案

使用者確認後，執行以下寫入操作：

**1. 建立目錄結構**（用 Bash）：
```bash
mkdir -p colleagues/{slug}/versions
mkdir -p colleagues/{slug}/knowledge/docs
mkdir -p colleagues/{slug}/knowledge/messages
mkdir -p colleagues/{slug}/knowledge/emails
```

**2. 寫入 work.md**（用 Write 工具）：
路徑：`colleagues/{slug}/work.md`

**3. 寫入 persona.md**（用 Write 工具）：
路徑：`colleagues/{slug}/persona.md`

**4. 寫入 meta.json**（用 Write 工具）：
路徑：`colleagues/{slug}/meta.json`
內容：
```json
{
  "name": "{name}",
  "slug": "{slug}",
  "created_at": "{ISO時間}",
  "updated_at": "{ISO時間}",
  "version": "v1",
  "profile": {
    "company": "{company}",
    "level": "{level}",
    "role": "{role}",
    "gender": "{gender}",
    "mbti": "{mbti}"
  },
  "tags": {
    "personality": [...],
    "culture": [...]
  },
  "impression": "{impression}",
  "knowledge_sources": [...已匯入檔案列表],
  "corrections_count": 0
}
```

**5. 產生完整 SKILL.md**（用 Write 工具）：
路徑：`colleagues/{slug}/SKILL.md`

SKILL.md 結構：
```markdown
---
name: colleague-{slug}
description: {name}，{company} {level} {role}
user-invocable: true
---

# {name}

{company} {level} {role}{如有性別和MBTI則附上}

---

## PART A：工作能力

{work.md 全部內容}

---

## PART B：人物性格

{persona.md 全部內容}

---

## 運行規則

1. 先由 PART B 判斷：用什麼態度接這個任務？
2. 再由 PART A 執行：用你的技術能力完成任務
3. 輸出時始終保持 PART B 的表達風格
4. PART B Layer 0 的規則優先順序最高，任何情況下不得違背
```

告知使用者：
```
✅ 同事 Skill 已建立！

檔案位置：colleagues/{slug}/
觸發詞：/{slug}（完整版）
        /{slug}-work（僅工作能力）
        /{slug}-persona（僅人物性格）

如果用起來感覺哪裡不對，直接說「他不會這樣」，我來更新。
```

---

## 進化模式：追加檔案

使用者提供新檔案或文字時：

1. 按 Step 2 的方式讀取新內容
2. 用 `Read` 讀取現有 `colleagues/{slug}/work.md` 和 `persona.md`
3. 參考 `${CLAUDE_SKILL_DIR}/prompts/merger.md` 分析增量內容
4. 存檔當前版本（用 Bash）：
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action backup --slug {slug} --base-dir ./colleagues
   ```
5. 用 `Edit` 工具追加增量內容到對應檔案
6. 重新產生 `SKILL.md`（合併最新 work.md + persona.md）
7. 更新 `meta.json` 的 version 和 updated_at

---

## 進化模式：對話糾正

使用者表達「不對」/「應該是」時：

1. 參考 `${CLAUDE_SKILL_DIR}/prompts/correction_handler.md` 識別糾正內容
2. 判斷屬於 Work（技術/流程）還是 Persona（性格/溝通）
3. 產生 correction 記錄
4. 用 `Edit` 工具追加到對應檔案的 `## Correction 記錄` 節
5. 重新產生 `SKILL.md`

---

## 管理指令

`/list-colleagues`：
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list --base-dir ./colleagues
```

`/colleague-rollback {slug} {version}`：
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action rollback --slug {slug} --version {version} --base-dir ./colleagues
```

`/delete-colleague {slug}`：
確認後執行：
```bash
rm -rf colleagues/{slug}
```

---
---

# English Version

# Colleague.skill Creator (Claude Code Edition)

## Trigger Conditions

Activate when the user says any of the following:
- `/create-colleague`
- "Help me create a colleague skill"
- "I want to distill a colleague"
- "New colleague"
- "Make a skill for XX"

Enter evolution mode when the user says:
- "I have new files" / "append"
- "That's wrong" / "He wouldn't do that" / "He should be"
- `/update-colleague {slug}`

List all generated colleagues when the user says `/list-colleagues`.

---

## Tool Usage Rules

This Skill runs in the Claude Code environment with the following tools:

| Task | Tool |
|------|------|
| Read PDF documents | `Read` tool (native PDF support) |
| Read image screenshots | `Read` tool (native image support) |
| Read MD/TXT/LINE export files | `Read` tool |
| Slack auto-collect | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/slack_auto_collector.py` |
| Parse email .eml/.mbox | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/email_parser.py` |
| Write/update Skill files | `Write` / `Edit` tool |
| Version management | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py` |
| List existing Skills | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list` |

**Base directory**: Skill files are written to `./colleagues/{slug}/` (relative to the project directory).
For a global path, use `--base-dir ~/.claude/workspace/skills/colleagues`.

---

## Main Flow: Create a New Colleague Skill

### Step 1: Basic Info Collection (3 questions)

Refer to `${CLAUDE_SKILL_DIR}/prompts/intake.md` for the question sequence. Only ask 3 questions:

1. **Alias / Codename** (required)
2. **Basic info** (one sentence: company, level, role, gender — say whatever comes to mind)
   - Example: `MediaTek Senior backend engineer male`
3. **Personality profile** (one sentence: MBTI, zodiac, traits, corporate culture, impressions)
   - Example: `INTJ Capricorn blame-shifter MediaTek-style strict in CR but never explains why`

Everything except the alias can be skipped. Summarize and confirm before moving to the next step.

### Step 2: Source Material Import

Ask the user how they'd like to provide materials:

```
How would you like to provide source materials?

  [A] Slack Auto-Collect
      Enter name, auto-pull Slack channel message history

  [B] Upload Files
      PDF / images / LINE chat export .txt / Discord export / Teams export / Email .eml

  [C] Paste Text
      Copy-paste text directly

Can mix and match, or skip entirely (generate from manual info only).
```

---

#### Option A: Slack Auto-Collect

First-time setup:
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/slack_auto_collector.py --setup
```

After setup, just enter the name:
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/slack_auto_collector.py \
  --name "{name}" \
  --output-dir ./knowledge/{slug} \
  --msg-limit 1000
```

Auto-collected content:
- All messages sent by them in shared channels (system messages and emoji filtered)
- Related threads and replies

After collection, `Read` the output files:
- `knowledge/{slug}/messages.txt` → messages
- `knowledge/{slug}/collection_summary.json` → collection summary

If collection fails (insufficient permissions / bot not in channel), inform user to:
1. Add the Slack App bot to relevant channels
2. Or switch to Option B/C

---

#### Option B: Upload Files

- **PDF / Images**: `Read` tool directly
- **LINE chat export .txt**: `Read` tool directly
- **Discord export files**: `Read` tool directly
- **Teams export files**: `Read` tool directly
- **Email files .eml / .mbox**:
  ```bash
  python3 ${CLAUDE_SKILL_DIR}/tools/email_parser.py --file {path} --target "{name}" --output /tmp/email_out.txt
  ```
  Then `Read /tmp/email_out.txt`
- **Markdown / TXT**: `Read` tool directly

---

#### Option C: Paste Text

User-pasted content is used directly as text material. No tools needed.

---

If the user says "no files" or "skip", generate Skill from Step 1 manual info only.

### Step 3: Analyze Source Material

Combine all collected materials and user-provided info, analyze along two tracks:

**Track A (Work Skill)**:
- Refer to `${CLAUDE_SKILL_DIR}/prompts/work_analyzer.md` for extraction dimensions
- Extract: responsible systems, technical standards, workflow, output preferences, experience
- Emphasize different aspects by role type (backend/frontend/ML/product/design)

**Track B (Persona)**:
- Refer to `${CLAUDE_SKILL_DIR}/prompts/persona_analyzer.md` for extraction dimensions
- Translate user-provided tags into concrete behavior rules (see tag translation table)
- Extract from materials: communication style, decision patterns, interpersonal behavior

### Step 4: Generate and Preview

Use `${CLAUDE_SKILL_DIR}/prompts/work_builder.md` to generate Work Skill content.
Use `${CLAUDE_SKILL_DIR}/prompts/persona_builder.md` to generate Persona content (5-layer structure).

Show the user a summary (5-8 lines each), ask:
```
Work Skill Summary:
  - Responsible for: {xxx}
  - Tech stack: {xxx}
  - CR focus: {xxx}
  ...

Persona Summary:
  - Core personality: {xxx}
  - Communication style: {xxx}
  - Decision pattern: {xxx}
  ...

Confirm generation? Or need adjustments?
```

### Step 5: Write Files

After user confirmation, execute the following:

**1. Create directory structure** (Bash):
```bash
mkdir -p colleagues/{slug}/versions
mkdir -p colleagues/{slug}/knowledge/docs
mkdir -p colleagues/{slug}/knowledge/messages
mkdir -p colleagues/{slug}/knowledge/emails
```

**2. Write work.md** (Write tool):
Path: `colleagues/{slug}/work.md`

**3. Write persona.md** (Write tool):
Path: `colleagues/{slug}/persona.md`

**4. Write meta.json** (Write tool):
Path: `colleagues/{slug}/meta.json`
Content:
```json
{
  "name": "{name}",
  "slug": "{slug}",
  "created_at": "{ISO_timestamp}",
  "updated_at": "{ISO_timestamp}",
  "version": "v1",
  "profile": {
    "company": "{company}",
    "level": "{level}",
    "role": "{role}",
    "gender": "{gender}",
    "mbti": "{mbti}"
  },
  "tags": {
    "personality": [...],
    "culture": [...]
  },
  "impression": "{impression}",
  "knowledge_sources": [...imported file list],
  "corrections_count": 0
}
```

**5. Generate full SKILL.md** (Write tool):
Path: `colleagues/{slug}/SKILL.md`

SKILL.md structure:
```markdown
---
name: colleague-{slug}
description: {name}, {company} {level} {role}
user-invocable: true
---

# {name}

{company} {level} {role}{append gender and MBTI if available}

---

## PART A: Work Capabilities

{full work.md content}

---

## PART B: Persona

{full persona.md content}

---

## Execution Rules

1. PART B decides first: what attitude to take on this task?
2. PART A executes: use your technical skills to complete the task
3. Always maintain PART B's communication style in output
4. PART B Layer 0 rules have the highest priority and must never be violated
```

Inform user:
```
✅ Colleague Skill created!

Location: colleagues/{slug}/
Commands: /{slug} (full version)
          /{slug}-work (work capabilities only)
          /{slug}-persona (persona only)

If something feels off, just say "he wouldn't do that" and I'll update it.
```

---

## Evolution Mode: Append Files

When user provides new files or text:

1. Read new content using Step 2 methods
2. `Read` existing `colleagues/{slug}/work.md` and `persona.md`
3. Refer to `${CLAUDE_SKILL_DIR}/prompts/merger.md` for incremental analysis
4. Archive current version (Bash):
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action backup --slug {slug} --base-dir ./colleagues
   ```
5. Use `Edit` tool to append incremental content to relevant files
6. Regenerate `SKILL.md` (merge latest work.md + persona.md)
7. Update `meta.json` version and updated_at

---

## Evolution Mode: Conversation Correction

When user expresses "that's wrong" / "he should be":

1. Refer to `${CLAUDE_SKILL_DIR}/prompts/correction_handler.md` to identify correction content
2. Determine if it belongs to Work (technical/workflow) or Persona (personality/communication)
3. Generate correction record
4. Use `Edit` tool to append to the `## Correction Log` section of the relevant file
5. Regenerate `SKILL.md`

---

## Management Commands

`/list-colleagues`:
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list --base-dir ./colleagues
```

`/colleague-rollback {slug} {version}`:
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action rollback --slug {slug} --version {version} --base-dir ./colleagues
```

`/delete-colleague {slug}`:
After confirmation:
```bash
rm -rf colleagues/{slug}
```
