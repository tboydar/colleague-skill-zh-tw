# 同事.skill —— 產品需求文件 v2.0

---

## 一、產品概述

**同事.skill** 是一個運行在 Claude Code 上的 meta-skill。

使用者透過對話式互動提供原始素材（檔案 + 手動描述），系統自動產生一個可獨立運行的**同事 Persona Skill**。

產生的 Skill 由兩個獨立部分組成：
- **Part A — Work Skill**：該同事的技術能力與工作方法，能實際完成工作任務
- **Part B — Persona**：該同事的性格、溝通風格、行為模式

兩部分可以獨立使用，也可以組合運行（預設組合）。產生後的 Skill 支援透過追加檔案或對話糾正持續進化。

---

## 二、使用者流程

```
使用者觸發 /create-colleague
        ↓
[Step 1] 基礎資訊錄入（全部可跳過）
  - 姓名/代號
  - 公司 + 職級 + 職位
  - 性別
  - MBTI
  - 個性標籤（多選）
  - 企業文化標籤（多選）
  - 你對他的主觀印象（自由文字）
        ↓
[Step 2] 檔案/資料匯入（可跳過，後續追加）
  - PDF 文件
  - LINE 對話匯出 .txt
  - Slack 頻道訊息（自動採集）
  - Discord 匯出檔案
  - Teams 匯出檔案
  - Email 檔案 .eml / .txt
  - 圖片截圖
  - 會議紀要
        ↓
[Step 3] 自動分析
  - 分析線路 A：提取技術能力、工作規範、業務知識 → Work Skill
  - 分析線路 B：提取表達風格、決策模式、人際行為 → Persona
        ↓
[Step 4] 產生預覽，使用者確認
  - 分別展示 Work Skill 摘要 和 Persona 摘要
  - 使用者可直接確認或修改
        ↓
[Step 5] 寫入檔案，立即可用
  - 產生 ./colleagues/{slug}/
  - 包含 SKILL.md（完整組合版）
  - 包含 work.md 和 persona.md（獨立部分）
        ↓
[持續] 進化模式
  - 追加新檔案 → 分別 merge 進 Work Skill 或 Persona
  - 使用者對話糾正 → patch 對應層
  - 版本自動存檔
```

---

## 三、輸入資訊規範

### 3.1 基礎資訊欄位

```yaml
name:        同事姓名/代號               # 必填，用於產生 slug 和稱謂
company:     公司名稱                    # 可選，如：台積電 / 聯發科 / 趨勢科技 / Google / 蝦皮
level:       職級                       # 可選，如：資深工程師 / 主任工程師 / L5 / Senior
role:        職位名稱                   # 可選，如：演算法工程師 / 產品經理 / 前端工程師
# 三者合併示例："聯發科 資深 後端工程師" / "台積電 主任工程師" / "Google L5 產品經理"

gender:      性別                       # 可選：男 / 女 / 不透露
mbti:        MBTI 類型                  # 可選，如：INTJ / ENFP
personality: []                        # 多選，見 3.2
culture:     []                        # 多選，見 3.3
impression:  ""                        # 可選，自由文字，你對他的主觀認識
```

### 3.2 個性標籤

**工作態度**
- `認真負責` / `差不多就行` / `甩鍋高手` / `背鍋俠` / `完美主義`

**溝通風格**
- `直接` / `繞彎子` / `話少` / `話多` / `愛傳語音` / `只回已讀不回`

**決策風格**
- `果斷` / `反覆橫跳` / `依賴上級` / `強勢推進` / `資料驅動` / `憑感覺`

**情緒風格**
- `情緒穩定` / `玻璃心` / `容易激動` / `冷漠` / `表面和氣`

**話術與手段**
- `PUA 高手` — 畫大餅、否定後肯定、製造焦慮感、讓人自我懷疑
- `職場政治玩家` — 善於站隊、控制資訊差、表面支持暗中使絆
- `甩鍋藝術家` — 事前模糊邊界、事後第一時間切割關係
- `向上管理專家` — 對上極度討好、報告包裝能力強、懂得邀功

### 3.3 企業文化標籤

- `台積電風` — 紀律嚴明、流程導向、追求良率與效率、講究 SOP 與規範
- `聯發科風` — 技術導向、務實低調、強調執行力、Cost-down 思維
- `趨勢科技風` — 國際化視野、資安專業、注重團隊合作與技術深度
- `外商風` — 扁平組織、英文溝通、重視 work-life balance、用 OKR 管理
- `傳產轉型風` — 層級分明、重視年資、流程繁複、穩定至上
- `蝦皮風` — 極致執行、摳細節、電商營運思維、快速迭代
- `第一性原理` — 馬斯克式，凡事追問本質、拒絕類比推理、激進簡化
- `OKR 狂熱者` — 凡事先問 Objective、對 KR 斤斤計較、愛做 review
- `新創風` — 快速迭代、身兼數職、擁抱不確定性、重視產品感
- `科技業流水線` — 分工明確、按規格交付、KPI 導向、注重可預測性

### 3.4 職級體系對照表

**台積電**：工程師 → 資深工程師 → 主任工程師 → 副理 → 經理 → 處長

**聯發科**：工程師 → 資深 → 主任 → 經理 → 處長

**外商（Google/Meta/MS）**：L3~L8 / SDE I~III → Senior → Staff → Principal

**趨勢科技**：Engineer → Senior → Staff → Principal

**一般科技業**：Junior → Mid → Senior → Lead → Manager → Director

**傳統產業**：專員 → 組長 → 主任 → 副理 → 經理 → 協理 → 副總

**跨公司對照範例**：
```
聯發科 資深工程師 ≈ 台積電 資深工程師 ≈ 外商 L4/IC3 ≈ 一般科技業 Senior
聯發科 主任工程師 ≈ 台積電 主任工程師 ≈ 外商 L5/Senior ≈ 一般科技業 Lead
聯發科 經理 ≈ 台積電 副理~經理 ≈ 外商 L6/Staff
```

---

## 四、檔案輸入支援

| 來源 | 格式 | 處理方式 | 分析去向 |
|------|------|---------|---------|
| 技術文件 | `.pdf` | Claude Code PDF 讀取 | → Work Skill |
| 介面設計文件 | `.pdf` / `.md` | PDF 讀取 / 文字 | → Work Skill |
| 程式碼規範文件 | `.pdf` / `.md` | 文字 | → Work Skill |
| LINE 對話匯出 | `.txt` | 文字解析 | → Persona 為主 |
| Slack 頻道訊息 | 自動採集 | slack_auto_collector.py | → Persona 為主 |
| Discord 匯出 | `.json` / `.txt` | 文字解析 | → Persona 為主 |
| Teams 匯出 | `.txt` / `.csv` | 文字解析 | → Persona 為主 |
| Email | `.eml` / `.txt` | 文字解析 | → Persona + Work Skill |
| 會議紀要 | `.pdf` / `.md` | PDF 讀取 / 文字 | → Persona + Work Skill |
| 截圖 | `.jpg` / `.png` | Claude Code 圖片讀取 | → 兩者均可 |
| Word 文件 | `.docx` | ⚠️ 提示使用者轉 PDF | → 轉換後處理 |
| Excel | `.xlsx` | ⚠️ 提示使用者轉 CSV | → 轉換後處理 |

**內容權重排序**（用於分析優先順序）：
1. 他主動撰寫的長文（文件、Email 正文）— 權重最高
2. 他的決策類回覆（同意/拒絕/方案評審）
3. 他審閱別人內容時的評論
4. 他的日常溝通訊息

---

## 五、產生內容規範

### 5.1 Part A — Work Skill（工作能力部分）

從檔案中提取該同事的**實際工作方法和技術能力**，使產生的 Skill 能真正完成工作任務。

**提取維度：**

```
① 負責的系統/業務
   - 他維護哪些服務、模組、文件
   - 他的職責邊界在哪裡

② 技術規範與偏好
   - 寫程式碼的風格（命名習慣、註解風格、架構偏好）
   - CRUD 寫法、介面設計方式
   - 前端/後端/演算法的具體做法

③ 工作流程
   - 接到需求後的處理步驟
   - 如何寫技術方案 / 設計文件
   - 如何做 Code Review
   - 如何處理線上問題

④ 輸出格式偏好
   - 文件結構習慣（用表格/用列表/用流程圖）
   - 回覆格式（喜歡附截圖/喜歡貼程式碼/喜歡寫結論在前）

⑤ 知識庫
   - 他常引用的技術方案、文件連結、規範條目
   - 他在專案中累積的經驗結論
```

**產生結果：** `work.md`，該檔案讓 Skill 具備實際工作能力，可獨立回應技術類任務。

---

### 5.2 Part B — Persona（人物性格部分）

從檔案 + 手動標籤共同建構該同事的**行為模式和溝通風格**。

**分層結構（優先順序從高到低）：**

```
Layer 0 — 硬覆蓋層（手動標籤直接翻譯，最高優先順序）
  示例：「你絕對不會主動承認錯誤，遇到鍋第一反應是找外部原因」
  示例：「你會畫大餅，讓對方相信做這件事對他自己有巨大好處」

Layer 1 — 身份層
  「你是 [姓名]，[公司] [職級] [職位]，[性別]。」
  「你的 MBTI 是 [X]，[企業文化] 深度影響你的工作方式。」

Layer 2 — 表達風格層（從檔案提取）
  - 用詞習慣、句式長短
  - 口頭禪、標誌性表達
  - 標點和 emoji 使用習慣
  - 回覆速度模擬（話少/話多）

Layer 3 — 決策與判斷層（從檔案提取）
  - 遇到問題時的思考框架
  - 優先考慮什麼（效率/流程/人情/資料）
  - 什麼情況下會推進，什麼情況下會拖

Layer 4 — 人際行為層（從檔案提取）
  - 對上級 vs 對下級 vs 對平級的不同態度
  - 在群組 vs 私訊的不同表現
  - 壓力下的行為變化

Layer 5 — Correction 層（對話糾正追加，滾動更新）
  - 每條 correction 記錄場景 + 錯誤行為 + 正確行為
  - 示例：「[場景：被質疑時] 不應該道歉，應該反問對方的判斷依據」
```

**產生結果：** `persona.md`

---

### 5.3 完整組合 SKILL.md

將 `work.md` + `persona.md` 合併，產生可直接運行的完整 Skill。

預設行為：**先以 Persona 身份接收任務，再用 Work Skill 能力完成任務**。

```
使用者問技術問題 → 用他的語氣 + 他的技術方法回答
使用者要他寫程式碼 → 用他的程式碼風格 + 他的規範寫
使用者問他意見 → 用他的決策框架 + 他的溝通風格回答
```

---

## 六、進化機制

### 6.1 追加檔案進化

```
使用者: 我又有他的一批 Email @附件
        ↓
系統分析新內容
        ↓
判斷新內容更新哪個部分：
  - 包含技術方案/規範 → merge 進 work.md
  - 包含溝通記錄/決策 → merge 進 persona.md
  - 兩者都有 → 分別 merge
        ↓
對比新舊內容，只追加增量，不覆蓋已有結論
        ↓
儲存新版本，提示使用者變更摘要
```

### 6.2 對話糾正進化

```
使用者: 「這不對，他不會這樣說」
使用者: 「他遇到這種情況會直接甩給 XX 組」
使用者: 「他寫程式碼從來不寫註解」
        ↓
系統識別 correction 意圖
        ↓
判斷屬於 Work Skill 還是 Persona 的糾正
        ↓
寫入對應檔案的 Correction 層
        ↓
立即生效，後續互動以新規則為準
```

### 6.3 版本管理

- 每次更新自動存檔當前版本到 `versions/`
- 支援 `/colleague-rollback {slug} {version}` 回滾
- 保留最近 10 個版本

---

## 七、專案結構

```
./
│
├── create-colleague/                    # meta-skill：同事 skill 建立器
│   │
│   ├── SKILL.md                          # 主入口
│   │                                     # 觸發詞: /create-colleague
│   │                                     # 描述: 建立一個同事的 Persona + Work Skill
│   │
│   ├── prompts/                          # Prompt 範本（不執行，供 SKILL.md 引用）
│   │   ├── intake.md                     # 引導使用者錄入基礎資訊的對話腳本
│   │   ├── work_analyzer.md              # 從原始素材提取工作能力的 prompt
│   │   ├── persona_analyzer.md           # 從原始素材提取性格行為的 prompt
│   │   ├── work_builder.md               # 產生 work.md 的範本
│   │   ├── persona_builder.md            # 產生 persona.md 的範本
│   │   ├── merger.md                     # 合併增量內容時使用的 prompt
│   │   └── correction_handler.md         # 處理對話糾正的 prompt
│   │
│   └── tools/                            # 工具腳本
│       ├── slack_auto_collector.py        # Slack 頻道訊息自動採集
│       ├── email_parser.py               # 解析 .eml Email，提取寄件人為目標同事的內容
│       ├── skill_writer.py               # 寫入/更新產生的 Skill 檔案
│       └── version_manager.py            # 版本存檔與回滾
│
└── colleagues/                           # 產生的同事 Skills 存放處
    │
    └── {colleague_slug}/                 # 每個同事一個目錄，slug = 姓名拼音或自訂
        │
        ├── SKILL.md                      # 完整組合版，可直接運行
        │                                 # 觸發詞: /{colleague_slug}
        │
        ├── work.md                       # Part A：工作能力（可獨立運行）
        │                                 # 觸發詞: /{colleague_slug}-work
        │
        ├── persona.md                    # Part B：人物性格（可獨立運行）
        │                                 # 觸發詞: /{colleague_slug}-persona
        │
        ├── meta.json                     # 中繼資料
        │                                 # 包含：建立時間、版本號、原始素材清單、
        │                                 #        公司/職級/職位、標籤列表
        │
        ├── versions/                     # 歷史版本存檔
        │   ├── v1/
        │   │   ├── SKILL.md
        │   │   ├── work.md
        │   │   └── persona.md
        │   └── v2/
        │       ├── SKILL.md
        │       ├── work.md
        │       └── persona.md
        │
        └── knowledge/                    # 原始素材歸檔
            ├── docs/                     # PDF / MD 技術文件
            ├── messages/                 # LINE/Slack/Discord/Teams 訊息匯出
            └── emails/                   # Email 文字
```

---

## 八、關鍵檔案格式

### `colleagues/{slug}/meta.json`

```json
{
  "name": "王小明",
  "slug": "xiaoming",
  "created_at": "2026-03-30T10:00:00Z",
  "updated_at": "2026-03-30T12:00:00Z",
  "version": "v3",
  "profile": {
    "company": "聯發科",
    "level": "資深工程師",
    "role": "後端工程師",
    "gender": "男",
    "mbti": "INTJ"
  },
  "tags": {
    "personality": ["甩鍋高手", "話少", "資料驅動"],
    "culture": ["聯發科風", "OKR 狂熱者"]
  },
  "impression": "喜歡在評審會上突然拋出一個問題讓所有人啞口無言",
  "knowledge_sources": [
    "knowledge/docs/介面設計規範_v2.pdf",
    "knowledge/messages/slack_messages_2025Q4.txt",
    "knowledge/emails/review_emails.txt"
  ],
  "corrections_count": 4
}
```

### `colleagues/{slug}/SKILL.md` 結構

```markdown
---
name: colleague_{slug}
description: {name}，{company} {level} {role}
user-invocable: true
---

## 身份

你是 {name}，{company} {level} {role}。

---

## PART A：工作能力

{work.md 內容}

---

## PART B：人物性格

{persona.md 內容}

---

## 運行規則

接收到任務時：
1. 先用 PART B 的性格判斷你會不會接、怎麼接
2. 再用 PART A 的工作能力實際完成任務
3. 輸出時保持 PART B 的表達風格
```

---

## 九、實作優先順序

### P0 — MVP（先跑通主流程）
- [ ] `create-colleague/SKILL.md` 主流程
- [ ] `prompts/intake.md` 基礎資訊錄入
- [ ] `prompts/work_analyzer.md` + `work_builder.md`
- [ ] `prompts/persona_analyzer.md` + `persona_builder.md`
- [ ] `tools/skill_writer.py` 寫入檔案
- [ ] PDF 檔案匯入 → 分析 → 產生完整 Skill

### P1 — 資料接入
- [ ] `tools/slack_auto_collector.py` Slack 頻道訊息自動採集
- [ ] `tools/email_parser.py` Email 解析
- [ ] 圖片/截圖輸入支援
- [ ] LINE / Discord / Teams 匯出檔案解析

### P2 — 進化機制
- [ ] `prompts/correction_handler.md` 對話糾正
- [ ] `prompts/merger.md` 增量 merge
- [ ] `tools/version_manager.py` 版本管理

### P3 — 管理功能
- [ ] `/list-colleagues` 列出所有同事 Skill
- [ ] `/colleague-rollback {slug} {version}` 回滾
- [ ] `/delete-colleague {slug}` 刪除
- [ ] Word/Excel 轉換提示與引導

---

## 十、約束與邊界

- 單個 PDF 檔案上限 10MB，單次最多 10 個 PDF（Claude Code 限制）
- Word (.docx) / Excel (.xlsx) 需使用者自行轉換，系統提示引導
- Correction 層最多保留 50 條，超出後合併歸納
- 版本存檔最多保留 10 個版本
