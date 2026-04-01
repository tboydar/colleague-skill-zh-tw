<div align="center">

# colleague.skill (Taiwan Edition)

> *"You AI guys are traitors to the codebase — you've already killed frontend, now you're coming for backend, QA, ops, infosec, chip design, and eventually yourselves and all of humanity"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

Your colleague jumped ship to TSMC, leaving behind a mountain of unmaintained docs?<br>
Your intern left, nothing but an empty desk and a half-finished project?<br>
Your senior graduated, taking all the context and experience with them?<br>
Your partner transferred teams, and the chemistry you built reset to zero overnight?<br>
Your predecessor handed over, trying to condense three years into three pages?<br>

**Turn cold goodbyes into warm Skills — welcome to cyber-immortality!**

<br>

Provide source materials (Slack messages, LINE chats, emails, screenshots)<br>
plus your subjective description of the person<br>
and get an **AI Skill that actually works like them**

[Supported Sources](#supported-data-sources) · [Install](#install) · [Usage](#usage) · [Demo](#demo) · [Detailed Install](INSTALL.md) · [**中文**](README.md)

</div>

---

### 🌟 Related Project: [ex.skill](https://github.com/titanwings/ex-skill)

> Based on community feedback, we've updated **ex.skill** (a.k.a. 前任.skill)! Now supports:
>
> - **LINE chat history import** (export .txt manually)
> - **iMessage auto-extraction** (macOS users)
> - **Full astrology chart interpretation** (Sun/Moon/Rising/Venus/Mars/Mercury × 12 signs)
> - **MBTI 16 types + cognitive functions**, Enneagram, attachment styles
> - All gender identities and relationship types supported
>
> Colleague left? Use **colleague.skill**. Ex left? Use **[ex.skill](https://github.com/titanwings/ex-skill)**. Cyber-immortality, end to end 🌟🌟🌟
>
> If you find this interesting, give both projects a Star!

---

## Supported Data Sources

> This is still a beta version of colleague.skill — more sources coming soon, stay tuned!

| Source | Messages | Docs / Wiki | Notes |
|--------|:--------:|:-----------:|-------|
| Slack (auto) | ✅ API | — | Requires admin to install Bot; free plan limited to 90 days |
| LINE chat export | ✅ | — | Manual export to .txt |
| Discord export | ✅ | — | Manual export or use DiscordChatExporter |
| Teams export | ✅ | — | Manual export |
| PDF | — | ✅ | Manual upload |
| Images / Screenshots | ✅ | — | Manual upload |
| Email `.eml` / `.mbox` | ✅ | — | Manual upload |
| Markdown | ✅ | ✅ | Manual upload |
| Paste text directly | ✅ | — | Manual input |

---

## Install

### Claude Code

> **Important**: Claude Code looks for skills in `.claude/skills/` at the **git repo root**. Make sure you run this in the right place.

```bash
# Install to current project (run at git repo root)
mkdir -p .claude/skills
git clone https://github.com/tboydar/colleague-skill .claude/skills/create-colleague

# Or install globally (available in all projects)
git clone https://github.com/tboydar/colleague-skill ~/.claude/skills/create-colleague
```

### OpenClaw

```bash
git clone https://github.com/tboydar/colleague-skill ~/.openclaw/workspace/skills/create-colleague
```

### Dependencies (optional)

```bash
pip3 install -r requirements.txt
```

> Slack auto-collection requires App credentials. See [INSTALL.md](INSTALL.md) for details.

---

## Usage

In Claude Code, type:

```
/create-colleague
```

Follow the prompts: enter an alias, company/level (e.g. `MediaTek Senior Backend Engineer`), personality tags, then choose a data source. All fields can be skipped — even a description alone can generate a Skill.

Once created, invoke the colleague Skill with `/{slug}`.

### Commands

| Command | Description |
|---------|-------------|
| `/list-colleagues` | List all colleague Skills |
| `/{slug}` | Invoke full Skill (Persona + Work) |
| `/{slug}-work` | Work capabilities only |
| `/{slug}-persona` | Persona only |
| `/colleague-rollback {slug} {version}` | Rollback to a previous version |
| `/delete-colleague {slug}` | Delete |

---

## Demo

> Input: `MediaTek Senior Backend Engineer, INTJ, blame-shifter, MediaTek-style`

**Scenario 1: Code Review**

```
User            ❯ Can you review this API design?

colleague.skill ❯ Hold on — what's the impact? You haven't explained the context.
                  (after reading) N+1 query, fix it. Use the standard
                  {code, message, data} response format. That's the spec,
                  don't ask why.
```

**Scenario 2: Blame game**

```
User            ❯ This bug was introduced by you, right?

colleague.skill ❯ Does the timeline match? That feature touched multiple places,
                  there were other changes too.
```

---

## Features

### Generated Skill Structure

Each colleague Skill has two parts that work together:

| Part | Content |
|------|---------|
| **Part A — Work Skill** | Systems, tech standards, workflows, experience |
| **Part B — Persona** | 5-layer personality: hard rules → identity → expression → decisions → interpersonal |

Execution: `Receive task → Persona decides attitude → Work Skill executes → Output in their voice`

### Supported Tags

**Personality**: Responsible · Blame-shifter · Perfectionist · Good-enough · Procrastinator · PUA master · Office politician · Managing-up expert · Passive-aggressive · Flip-flopper · Quiet · Read-no-reply …

**Corporate culture**:
- TSMC-style (disciplined, SOP-driven, data-speaks, yield-first, hierarchical)
- MediaTek-style (pragmatic, cost-conscious, fast iteration, time-to-market first)
- Trend Micro-style (international, English comms, work-life balance, deep tech)
- Traditional-industry-in-transition (boss decides, long processes, transformation anxiety, stability-first)
- Foreign-company-style (English comms, flat org, feedback culture, 1:1s)
- Shopee-style (hypergrowth, KPI-driven, young culture, intense competition)
- First-principles · OKR-obsessed · Tech-industry-pipeline · Startup-mode

**Levels**:
- TSMC (Engineer → Senior → Section Manager → Deputy Manager → Manager → Division Director)
- MediaTek (Engineer → Senior → Section Manager → Manager → Division Director)
- Foreign companies — Google/Meta/Microsoft (L3~L8, SDE I~III → Senior → Staff → Principal)
- Trend Micro (Engineer → Senior → Staff → Principal)
- General tech (Junior → Mid → Senior → Lead → Manager → Director)
- Traditional industry (Specialist → Team Lead → Section Chief → Deputy Manager → Manager → Associate VP → VP)

### Evolution

- **Append files** → auto-analyze delta → merge into relevant sections, never overwrite existing conclusions
- **Conversation correction** → say "he wouldn't do that, he should be xxx" → writes to Correction layer, takes effect immediately
- **Version control** → auto-archive on every update, rollback to any previous version

---

## Project Structure

This project follows the [AgentSkills](https://agentskills.io) open standard. The entire repo is a skill directory:

```
create-colleague/
├── SKILL.md              # Skill entry point (official frontmatter)
├── prompts/              # Prompt templates
│   ├── intake.md         #   Dialogue-based info collection
│   ├── work_analyzer.md  #   Work capability extraction
│   ├── persona_analyzer.md #  Personality extraction (with tag translation)
│   ├── work_builder.md   #   work.md generation template
│   ├── persona_builder.md #   persona.md 5-layer structure
│   ├── merger.md         #   Incremental merge logic
│   └── correction_handler.md # Conversation correction handler
├── tools/                # Python tools
│   ├── slack_auto_collector.py   # Slack auto-collector
│   ├── email_parser.py           # Email parser
│   ├── skill_writer.py           # Skill file management
│   └── version_manager.py        # Version archive & rollback
├── colleagues/           # Generated colleague Skills (gitignored)
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## Notes

- **Source material quality = Skill quality**: chat logs + long docs > manual description only
- Prioritize collecting: long-form writing **by them** > **decision-making replies** > casual messages
- Slack auto-collection requires adding the App Bot to relevant channels
- LINE / Discord / Teams exports are plain text files — no special tools needed
- This is still a demo version — please file issues if you find bugs!

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

MIT License · Taiwan-localized fork, original project © [titanwings](https://github.com/titanwings/colleague-skill)

</div>
