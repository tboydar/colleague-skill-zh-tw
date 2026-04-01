#!/usr/bin/env python3
"""
Slack 自動採集器

輸入同事的 Slack 姓名/使用者名稱，自動：
  1. 搜尋 Slack 使用者，取得 user_id
  2. 找到與 Bot 共同的頻道，拉取該使用者發出的訊息
  3. 輸出統一格式，直接進 create-colleague 分析流程

前置：
  python3 slack_auto_collector.py --setup   # 設定 Bot Token（一次性）

用法：
  python3 slack_auto_collector.py --name "阿華" --output-dir ./knowledge/ahua
  python3 slack_auto_collector.py --name "john" --msg-limit 500 --channel-limit 30

所需 Bot Token Scopes（OAuth & Permissions）：
  channels:history      讀取 public channel 訊息
  channels:read         列出 public channels
  groups:history        讀取 private channel 訊息
  groups:read           列出 private channels
  im:history            讀取 DM 訊息（可選）
  im:read               列出 DM（可選）
  mpim:history          讀取群組 DM 訊息（可選）
  mpim:read             列出群組 DM（可選）
  users:read            搜尋使用者列表

注意：
  - 免費版 Workspace 僅保留最近 90 天訊息
  - 需要 Workspace 管理員安裝 Bot App
"""

from __future__ import annotations

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# ─── 依賴檢查 ──────────────────────────────────────────────────────────────────

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    print(
        "錯誤：請先安裝 slack_sdk：pip3 install slack-sdk",
        file=sys.stderr,
    )
    sys.exit(1)

# ─── 常數 ──────────────────────────────────────────────────────────────────────

CONFIG_PATH = Path.home() / ".colleague-skill" / "slack_config.json"

# Slack 頻道類型（採集範圍）
CHANNEL_TYPES = "public_channel,private_channel,mpim,im"

# 速率限制重試設定
MAX_RETRIES = 5
RETRY_BASE_WAIT = 1.0     # 最短等待秒數
RETRY_MAX_WAIT = 60.0     # 最長等待秒數

# 採集預設值
DEFAULT_MSG_LIMIT = 1000
DEFAULT_CHANNEL_LIMIT = 50  # 最多檢查的頻道數


# ─── 錯誤類型 ──────────────────────────────────────────────────────────────────

class SlackCollectorError(Exception):
    """採集過程中的可預期錯誤，直接結束"""


class SlackScopeError(SlackCollectorError):
    """Bot Token 缺少必要的 scope 權限"""


class SlackAuthError(SlackCollectorError):
    """Token 無效或已過期"""


# ─── 設定管理 ──────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(
            "未找到設定，請先執行：python3 slack_auto_collector.py --setup",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        return json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError:
        print(f"設定檔損壞，請重新執行 --setup：{CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False))


def setup_config() -> None:
    print("=== Slack 自動採集設定 ===\n")
    print("步驟 1：前往 https://api.slack.com/apps 建立新 App")
    print("        選擇「From scratch」→ 填寫 App Name → 選擇目標 Workspace\n")
    print("步驟 2：進入 OAuth & Permissions，在 Bot Token Scopes 新增：")
    print()
    print("  訊息類（必要）：")
    print("    channels:history     讀取 public channel 歷史訊息")
    print("    groups:history       讀取 private channel 歷史訊息")
    print("    mpim:history         讀取群組 DM 歷史訊息")
    print("    im:history           讀取 DM 歷史訊息（可選）")
    print()
    print("  頻道資訊（必要）：")
    print("    channels:read        列出 public channels")
    print("    groups:read          列出 private channels")
    print("    mpim:read            列出群組 DM")
    print("    im:read              列出 DM（可選）")
    print()
    print("  使用者資訊（必要）：")
    print("    users:read           搜尋使用者列表")
    print()
    print("步驟 3：Install to Workspace → 複製 Bot User OAuth Token（xoxb-...）")
    print("步驟 4：將 Bot 加入目標頻道（/invite @your-bot-name）\n")

    token = input("Bot User OAuth Token (xoxb-...): ").strip()
    if not token.startswith("xoxb-"):
        print("警告：Token 格式不對，應以 xoxb- 開頭", file=sys.stderr)

    # 驗證 token 是否有效
    print("\n驗證 Token ...", end=" ", flush=True)
    try:
        client = WebClient(token=token)
        resp = client.auth_test()
        workspace = resp.get("team", "Unknown")
        bot_name = resp.get("user", "Unknown")
        print(f"OK\n  Workspace：{workspace}，Bot：{bot_name}")
    except SlackApiError as e:
        err = e.response.get("error", str(e))
        print(f"失敗\n  錯誤：{err}", file=sys.stderr)
        if err == "invalid_auth":
            print("  Token 無效，請重新產生", file=sys.stderr)
        sys.exit(1)

    config = {"bot_token": token}
    save_config(config)
    print(f"\n✅ 設定已儲存到 {CONFIG_PATH}")
    print("   請確認已將 Bot 加入目標頻道，否則無法讀取訊息")


# ─── Slack Client 封裝（帶速率限制重試）─────────────────────────────────────────

class RateLimitedClient:
    """封裝 slack_sdk WebClient，自動處理 429 速率限制"""

    def __init__(self, token: str) -> None:
        self._client = WebClient(token=token)

    def call(self, method: str, **kwargs) -> dict:
        """呼叫任意 Slack API，遇到 ratelimited 自動等待重試"""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                fn = getattr(self._client, method)
                resp = fn(**kwargs)
                return resp.data
            except SlackApiError as e:
                error = e.response.get("error", "")

                # 速率限制：讀取 Retry-After header 等待
                if error == "ratelimited":
                    wait = float(
                        e.response.headers.get("Retry-After", RETRY_BASE_WAIT * attempt)
                    )
                    wait = min(wait, RETRY_MAX_WAIT)
                    print(
                        f"  [速率限制] 等待 {wait:.0f}s（第 {attempt}/{MAX_RETRIES} 次重試）...",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    continue

                # 權限錯誤：直接拋出，不重試
                if error == "missing_scope":
                    missing = e.response.get("needed", "unknown")
                    raise SlackScopeError(
                        f"Bot Token 缺少權限 scope：{missing}\n"
                        f"  請前往 https://api.slack.com/apps → OAuth & Permissions → Bot Token Scopes 新增"
                    ) from e

                if error in ("invalid_auth", "token_revoked", "account_inactive"):
                    raise SlackAuthError(
                        f"Token 認證失敗（{error}），請重新執行 --setup 設定新 Token"
                    ) from e

                # 頻道無權限（Bot 未加入）：呼叫方處理
                if error in ("not_in_channel", "channel_not_found"):
                    raise

                # 其他錯誤：印出警告，回傳空資料
                print(f"  [API 警告] {method} 回傳錯誤：{error}", file=sys.stderr)
                return {}

        # 重試耗盡
        print(f"  [錯誤] {method} 多次重試後仍失敗，跳過", file=sys.stderr)
        return {}

    def paginate(self, method: str, result_key: str, **kwargs) -> list:
        """自動翻頁，回傳所有結果的合併清單"""
        items: list = []
        cursor = None

        while True:
            params = dict(kwargs)
            if cursor:
                params["cursor"] = cursor

            data = self.call(method, **params)
            if not data:
                break

            items.extend(data.get(result_key, []))

            meta = data.get("response_metadata", {})
            cursor = meta.get("next_cursor")
            if not cursor:
                break

        return items


# ─── 使用者搜尋 ──────────────────────────────────────────────────────────────────

def find_user(name: str, client: RateLimitedClient) -> Optional[dict]:
    """
    透過姓名（real_name / display_name / name）搜尋 Slack 使用者。
    支援中文姓名、英文使用者名稱、模糊比對。
    """
    print(f"  搜尋使用者：{name} ...", file=sys.stderr)

    try:
        members = client.paginate("users_list", "members", limit=200)
    except SlackScopeError as e:
        print(f"  ❌ {e}", file=sys.stderr)
        sys.exit(1)

    # 過濾掉 Bot / 已停用帳號
    members = [
        m for m in members
        if not m.get("is_bot") and not m.get("deleted") and m.get("id") != "USLACKBOT"
    ]

    name_lower = name.lower()

    def score(member: dict) -> int:
        profile = member.get("profile", {})
        real_name = (profile.get("real_name") or "").lower()
        display_name = (profile.get("display_name") or "").lower()
        username = (member.get("name") or "").lower()

        if name_lower in (real_name, display_name, username):
            return 3  # 精確比對
        if (
            name_lower in real_name
            or name_lower in display_name
            or name_lower in username
        ):
            return 2  # 包含比對
        # 中文名字拆字比對
        if all(ch in real_name or ch in display_name for ch in name_lower if ch.strip()):
            return 1
        return 0

    scored = [(score(m), m) for m in members]
    candidates = [(s, m) for s, m in scored if s > 0]

    if not candidates:
        print(f"  未找到使用者：{name}", file=sys.stderr)
        print(
            "  提示：請確認姓名拼寫，或嘗試用英文使用者名稱（如 john.doe）",
            file=sys.stderr,
        )
        return None

    candidates.sort(key=lambda x: -x[0])

    if len(candidates) == 1:
        _, user = candidates[0]
        _print_user(user)
        return user

    # 多個候選，讓使用者選擇
    print(f"\n  找到 {len(candidates)} 個符合，請選擇：")
    for i, (_, m) in enumerate(candidates[:10]):
        profile = m.get("profile", {})
        real_name = profile.get("real_name", "")
        display_name = profile.get("display_name", "")
        username = m.get("name", "")
        title = profile.get("title", "")
        print(f"    [{i+1}] {real_name}（@{display_name or username}）  {title}")

    choice = input("\n  選擇編號（預設 1）：").strip() or "1"
    try:
        idx = int(choice) - 1
        _, user = candidates[idx]
    except (ValueError, IndexError):
        _, user = candidates[0]

    _print_user(user)
    return user


def _print_user(user: dict) -> None:
    profile = user.get("profile", {})
    real_name = profile.get("real_name", user.get("name", ""))
    display_name = profile.get("display_name", "")
    title = profile.get("title", "")
    print(
        f"  找到使用者：{real_name}（@{display_name}）  {title}",
        file=sys.stderr,
    )


# ─── 頻道探索 ──────────────────────────────────────────────────────────────────

def get_channels_with_user(
    user_id: str,
    channel_limit: int,
    client: RateLimitedClient,
) -> list:
    """
    回傳 Bot 已加入、且目標使用者也在其中的所有頻道。
    策略：先列出 Bot 的所有頻道，再逐一檢查成員清單。
    """
    print("  取得頻道清單 ...", file=sys.stderr)

    try:
        channels = client.paginate(
            "conversations_list",
            "channels",
            types=CHANNEL_TYPES,
            exclude_archived=True,
            limit=200,
        )
    except SlackScopeError as e:
        print(f"  ❌ {e}", file=sys.stderr)
        return []

    # 只保留 Bot 是成員的頻道
    bot_channels = [c for c in channels if c.get("is_member")]
    print(f"  Bot 已加入 {len(bot_channels)} 個頻道，檢查成員 ...", file=sys.stderr)

    if len(bot_channels) > channel_limit:
        print(
            f"  頻道數超過上限 {channel_limit}，只檢查前 {channel_limit} 個",
            file=sys.stderr,
        )
        bot_channels = bot_channels[:channel_limit]

    result = []
    for ch in bot_channels:
        ch_id = ch.get("id", "")
        ch_name = ch.get("name", ch_id)

        try:
            members = client.paginate(
                "conversations_members",
                "members",
                channel=ch_id,
                limit=200,
            )
        except SlackApiError as e:
            err = e.response.get("error", "")
            if err in ("not_in_channel", "channel_not_found"):
                continue
            print(f"    跳過頻道 {ch_name}（{err}）", file=sys.stderr)
            continue
        except SlackScopeError as e:
            print(f"  ❌ {e}", file=sys.stderr)
            continue

        if user_id in members:
            result.append(ch)
            print(f"    ✓ #{ch_name}", file=sys.stderr)

    return result


# ─── 訊息採集 ──────────────────────────────────────────────────────────────────

def fetch_messages_from_channel(
    channel_id: str,
    channel_name: str,
    user_id: str,
    limit: int,
    client: RateLimitedClient,
) -> list:
    """
    從指定頻道拉取目標使用者發出的訊息。
    按時間倒序翻頁，直到達到 limit 或無更多資料。
    """
    messages = []
    cursor = None
    pages_fetched = 0
    MAX_PAGES = 50  # 防止無限翻頁

    while len(messages) < limit and pages_fetched < MAX_PAGES:
        params: dict = {"channel": channel_id, "limit": 200}
        if cursor:
            params["cursor"] = cursor

        try:
            data = client.call("conversations_history", **params)
        except SlackApiError as e:
            err = e.response.get("error", "")
            if err == "not_in_channel":
                print(
                    f"    Bot 不在頻道 #{channel_name}，跳過（請 /invite @bot）",
                    file=sys.stderr,
                )
            else:
                print(f"    拉取 #{channel_name} 失敗（{err}）", file=sys.stderr)
            break

        if not data:
            break

        pages_fetched += 1
        raw_msgs = data.get("messages", [])

        for msg in raw_msgs:
            # 只要目標使用者發的、非系統訊息
            if msg.get("user") != user_id:
                continue
            if msg.get("subtype"):  # join/leave/bot_message 等系統類型
                continue

            text = msg.get("text", "").strip()
            if not text:
                continue

            # 過濾純 emoji 或純附件訊息
            if _is_noise(text):
                continue

            ts_raw = msg.get("ts", "")
            time_str = _format_ts(ts_raw)

            # 包含 thread_reply_count 說明是話題發起訊息，權重更高
            is_thread_starter = bool(msg.get("reply_count", 0))

            messages.append(
                {
                    "content": text,
                    "time": time_str,
                    "channel": channel_name,
                    "is_thread_starter": is_thread_starter,
                }
            )

        meta = data.get("response_metadata", {})
        cursor = meta.get("next_cursor")
        if not cursor:
            break

    return messages[:limit]


def _is_noise(text: str) -> bool:
    """判斷是否為無意義訊息（純表情、@mention、URL）"""
    import re
    # 去掉 Slack 特殊格式後幾乎為空
    cleaned = re.sub(r"<[^>]+>", "", text).strip()
    cleaned = re.sub(r":[a-z_]+:", "", cleaned).strip()
    return len(cleaned) < 2


def _format_ts(ts: str) -> str:
    """將 Slack timestamp（Unix float string）轉為可讀時間"""
    try:
        return datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError):
        return ts


# ─── 主採集流程 ────────────────────────────────────────────────────────────────

def collect_messages(
    user: dict,
    channels: list,
    msg_limit: int,
    client: RateLimitedClient,
) -> str:
    """從所有頻道採集目標使用者訊息，回傳格式化文字"""
    user_id = user["id"]
    name = user.get("profile", {}).get("real_name") or user.get("name", user_id)

    if not channels:
        return (
            f"# 訊息記錄\n\n"
            f"未找到與 {name} 共同的頻道。\n"
            f"請確認 Bot 已被加入到相關頻道（/invite @bot）\n"
        )

    all_messages: list = []
    per_channel_limit = max(100, msg_limit // len(channels))

    for ch in channels:
        ch_id = ch.get("id", "")
        ch_name = ch.get("name", ch_id)
        print(f"  拉取 #{ch_name} 的訊息 ...", file=sys.stderr)

        msgs = fetch_messages_from_channel(
            ch_id, ch_name, user_id, per_channel_limit, client
        )
        all_messages.extend(msgs)
        print(f"    取得 {len(msgs)} 則", file=sys.stderr)

    # 按權重分類
    thread_msgs = [m for m in all_messages if m["is_thread_starter"]]
    long_msgs = [
        m for m in all_messages
        if not m["is_thread_starter"] and len(m["content"]) > 50
    ]
    short_msgs = [
        m for m in all_messages
        if not m["is_thread_starter"] and len(m["content"]) <= 50
    ]

    channel_names = ", ".join(f"#{c.get('name', c.get('id', ''))}" for c in channels)

    lines = [
        "# Slack 訊息記錄（自動採集）",
        f"目標：{name}",
        f"來源頻道：{channel_names}",
        f"共 {len(all_messages)} 則訊息",
        f"  話題發起訊息：{len(thread_msgs)} 則",
        f"  長訊息（>50字）：{len(long_msgs)} 則",
        f"  短訊息：{len(short_msgs)} 則",
        "",
        "---",
        "",
        "## 話題發起訊息（權重最高：觀點/決策/技術分享）",
        "",
    ]
    for m in thread_msgs:
        lines.append(f"[{m['time']}][#{m['channel']}] {m['content']}")
        lines.append("")

    lines += [
        "---",
        "",
        "## 長訊息（觀點/方案/討論類）",
        "",
    ]
    for m in long_msgs:
        lines.append(f"[{m['time']}][#{m['channel']}] {m['content']}")
        lines.append("")

    lines += ["---", "", "## 日常訊息（風格參考）", ""]
    for m in short_msgs[:300]:
        lines.append(f"[{m['time']}] {m['content']}")

    return "\n".join(lines)


def collect_all(
    name: str,
    output_dir: Path,
    msg_limit: int,
    channel_limit: int,
    config: dict,
) -> dict:
    """採集某同事的所有 Slack 資料，輸出到 output_dir"""
    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict = {}

    print(f"\n🔍 開始採集：{name}\n", file=sys.stderr)

    # 初始化 Client
    try:
        client = RateLimitedClient(config["bot_token"])
        # 快速驗證 token 有效性
        auth_data = client.call("auth_test")
        if not auth_data:
            raise SlackAuthError("auth_test 無回應，請檢查 Token")
        print(
            f"  Workspace：{auth_data.get('team')}，Bot：{auth_data.get('user')}",
            file=sys.stderr,
        )
    except SlackAuthError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    # Step 1: 搜尋使用者
    user = find_user(name, client)
    if not user:
        print(f"❌ 未找到使用者 {name}，請確認姓名/使用者名稱是否正確", file=sys.stderr)
        sys.exit(1)

    user_id = user["id"]
    profile = user.get("profile", {})
    real_name = profile.get("real_name") or user.get("name", user_id)

    # Step 2: 找共同頻道
    print(f"\n📡 查找與 {real_name} 共同的頻道（上限 {channel_limit} 個）...", file=sys.stderr)
    channels = get_channels_with_user(user_id, channel_limit, client)
    print(f"  共同頻道：{len(channels)} 個", file=sys.stderr)

    # Step 3: 採集訊息
    print(f"\n📨 採集訊息記錄（上限 {msg_limit} 則）...", file=sys.stderr)
    try:
        msg_content = collect_messages(user, channels, msg_limit, client)
        msg_path = output_dir / "messages.txt"
        msg_path.write_text(msg_content, encoding="utf-8")
        results["messages"] = str(msg_path)
        print(f"  ✅ 訊息記錄 → {msg_path}", file=sys.stderr)
    except SlackCollectorError as e:
        print(f"  ❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"  ⚠️  訊息採集失敗：{e}", file=sys.stderr)

    # 寫摘要
    summary = {
        "name": real_name,
        "slack_user_id": user_id,
        "display_name": profile.get("display_name", ""),
        "title": profile.get("title", ""),
        "channels": [
            {"id": c.get("id"), "name": c.get("name")} for c in channels
        ],
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "files": results,
        "note": "免費版 Workspace 僅保留最近 90 天訊息",
    }
    summary_path = output_dir / "collection_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"  ✅ 採集摘要 → {summary_path}", file=sys.stderr)

    print(f"\n✅ 採集完成，輸出目錄：{output_dir}", file=sys.stderr)
    return results


# ─── CLI 入口 ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Slack 資料自動採集器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 首次設定
  python3 slack_auto_collector.py --setup

  # 採集同事資料
  python3 slack_auto_collector.py --name "阿華"
  python3 slack_auto_collector.py --name "john.doe" --output-dir ./knowledge/john --msg-limit 500
        """,
    )
    parser.add_argument("--setup", action="store_true", help="初始化設定（Bot Token）")
    parser.add_argument("--name", help="同事姓名或 Slack 使用者名稱")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="輸出目錄（預設 ./knowledge/{name}）",
    )
    parser.add_argument(
        "--msg-limit",
        type=int,
        default=DEFAULT_MSG_LIMIT,
        help=f"最多採集訊息則數（預設 {DEFAULT_MSG_LIMIT}）",
    )
    parser.add_argument(
        "--channel-limit",
        type=int,
        default=DEFAULT_CHANNEL_LIMIT,
        help=f"最多檢查頻道數（預設 {DEFAULT_CHANNEL_LIMIT}）",
    )

    args = parser.parse_args()

    if args.setup:
        setup_config()
        return

    if not args.name:
        parser.print_help()
        parser.error("請提供 --name 參數")

    config = load_config()
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else Path(f"./knowledge/{args.name}")
    )

    try:
        collect_all(
            name=args.name,
            output_dir=output_dir,
            msg_limit=args.msg_limit,
            channel_limit=args.channel_limit,
            config=config,
        )
    except SlackCollectorError as e:
        print(f"\n❌ 採集失敗：{e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n已取消", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
