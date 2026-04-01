#!/usr/bin/env python3
"""
Email 解析器

支援格式：
1. .eml 檔案（標準 Email 格式）
2. .txt 檔案（純文字 Email 記錄）
3. .mbox 檔案（多封 Email 合集）

用法：
    python email_parser.py --file emails.eml --target "ahua@company.com" --output output.txt
    python email_parser.py --file inbox.mbox --target "阿華" --output output.txt
"""

import email
import email.policy
import mailbox
import re
import sys
import argparse
from pathlib import Path
from email.header import decode_header
from html.parser import HTMLParser


class HTMLTextExtractor(HTMLParser):
    """從 HTML Email 內容中擷取純文字"""

    def __init__(self):
        super().__init__()
        self.result = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False
        if tag in ("p", "br", "div", "tr"):
            self.result.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.result.append(data)

    def get_text(self):
        return re.sub(r"\n{3,}", "\n\n", "".join(self.result)).strip()


def decode_mime_str(s: str) -> str:
    """解碼 MIME 編碼的 Email 標頭欄位"""
    if not s:
        return ""
    parts = decode_header(s)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            charset = charset or "utf-8"
            try:
                result.append(part.decode(charset, errors="replace"))
            except Exception:
                result.append(part.decode("utf-8", errors="replace"))
        else:
            result.append(str(part))
    return "".join(result)


def extract_email_body(msg) -> str:
    """從 Email 物件中擷取正文文字"""
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in disposition:
                continue

            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                try:
                    body = payload.decode(charset, errors="replace")
                    break
                except Exception:
                    body = payload.decode("utf-8", errors="replace")
                    break

            elif content_type == "text/html" and not body:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                try:
                    html = payload.decode(charset, errors="replace")
                except Exception:
                    html = payload.decode("utf-8", errors="replace")
                extractor = HTMLTextExtractor()
                extractor.feed(html)
                body = extractor.get_text()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                body = payload.decode(charset, errors="replace")
            except Exception:
                body = payload.decode("utf-8", errors="replace")

    # 清理引用內容（Re: 時的原文引用）
    body = re.sub(r"\n>.*", "", body)
    body = re.sub(r"\n-{3,}.*?原始郵件.*?\n", "\n", body, flags=re.DOTALL)
    body = re.sub(r"\n_{3,}\n.*", "", body, flags=re.DOTALL)

    return body.strip()


def is_from_target(from_field: str, target: str) -> bool:
    """判斷 Email 是否來自目標人"""
    from_str = decode_mime_str(from_field).lower()
    target_lower = target.lower()
    return target_lower in from_str


def parse_eml_file(file_path: str, target: str) -> list[dict]:
    """解析單個 .eml 檔案"""
    with open(file_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=email.policy.default)

    from_field = str(msg.get("From", ""))
    if not is_from_target(from_field, target):
        return []

    subject = decode_mime_str(str(msg.get("Subject", "")))
    date = str(msg.get("Date", ""))
    body = extract_email_body(msg)

    if not body:
        return []

    return [{
        "from": decode_mime_str(from_field),
        "subject": subject,
        "date": date,
        "body": body,
    }]


def parse_mbox_file(file_path: str, target: str) -> list[dict]:
    """解析 .mbox 檔案（多封 Email 合集）"""
    results = []
    mbox = mailbox.mbox(file_path)

    for msg in mbox:
        from_field = str(msg.get("From", ""))
        if not is_from_target(from_field, target):
            continue

        subject = decode_mime_str(str(msg.get("Subject", "")))
        date = str(msg.get("Date", ""))
        body = extract_email_body(msg)

        if not body:
            continue

        results.append({
            "from": decode_mime_str(from_field),
            "subject": subject,
            "date": date,
            "body": body,
        })

    return results


def parse_txt_file(file_path: str, target: str) -> list[dict]:
    """
    解析純文字格式的 Email 記錄
    支援簡單的分隔格式：
    From: xxx
    Subject: xxx
    Date: xxx
    ---
    正文內容
    ===
    """
    results = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 嘗試按分隔符切割多封 Email
    emails_raw = re.split(r"\n={3,}\n|\n-{3,}\n(?=From:)", content)

    for raw in emails_raw:
        from_match = re.search(r"^From:\s*(.+)$", raw, re.MULTILINE)
        subject_match = re.search(r"^Subject:\s*(.+)$", raw, re.MULTILINE)
        date_match = re.search(r"^Date:\s*(.+)$", raw, re.MULTILINE)

        from_field = from_match.group(1).strip() if from_match else ""
        if not is_from_target(from_field, target):
            continue

        # 擷取正文（去掉標頭欄位後的內容）
        body = re.sub(r"^(From|To|Subject|Date|CC|BCC):.*\n?", "", raw, flags=re.MULTILINE)
        body = body.strip()

        if not body:
            continue

        results.append({
            "from": from_field,
            "subject": subject_match.group(1).strip() if subject_match else "",
            "date": date_match.group(1).strip() if date_match else "",
            "body": body,
        })

    return results


def classify_emails(emails: list[dict]) -> dict:
    """
    對 Email 按內容分類：
    - 長信（正文 > 200 字）：技術方案、觀點陳述
    - 決策類：包含明確判斷的信件
    - 日常溝通：短信
    """
    long_emails = []
    decision_emails = []
    daily_emails = []

    decision_keywords = [
        "同意", "不同意", "建議", "方案", "覺得", "應該", "決定", "確認",
        "approve", "reject", "lgtm", "suggest", "recommend", "think",
        "我的看法", "我認為", "我覺得", "需要", "必須", "不需要"
    ]

    for e in emails:
        body = e["body"]

        if len(body) > 200:
            long_emails.append(e)
        elif any(kw in body.lower() for kw in decision_keywords):
            decision_emails.append(e)
        else:
            daily_emails.append(e)

    return {
        "long_emails": long_emails,
        "decision_emails": decision_emails,
        "daily_emails": daily_emails,
        "total_count": len(emails),
    }


def format_output(target: str, classified: dict) -> str:
    """格式化輸出，供 AI 分析使用"""
    lines = [
        f"# Email 擷取結果",
        f"目標人物：{target}",
        f"總信件數：{classified['total_count']}",
        "",
        "---",
        "",
        "## 長信（技術方案/觀點類，權重最高）",
        "",
    ]

    for e in classified["long_emails"]:
        lines.append(f"**主旨：{e['subject']}** [{e['date']}]")
        lines.append(e["body"])
        lines.append("")
        lines.append("---")
        lines.append("")

    lines += [
        "## 決策類信件",
        "",
    ]

    for e in classified["decision_emails"]:
        lines.append(f"**主旨：{e['subject']}** [{e['date']}]")
        lines.append(e["body"])
        lines.append("")

    lines += [
        "---",
        "",
        "## 日常溝通（風格參考）",
        "",
    ]

    for e in classified["daily_emails"][:30]:
        lines.append(f"**{e['subject']}**：{e['body'][:200]}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="解析 Email 檔案，擷取目標人寄出的信件")
    parser.add_argument("--file", required=True, help="輸入檔案路徑（.eml / .mbox / .txt）")
    parser.add_argument("--target", required=True, help="目標人物（Email 地址或姓名）")
    parser.add_argument("--output", default=None, help="輸出檔案路徑（預設印到 stdout）")

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"錯誤：檔案不存在 {file_path}", file=sys.stderr)
        sys.exit(1)

    suffix = file_path.suffix.lower()

    if suffix == ".eml":
        emails = parse_eml_file(str(file_path), args.target)
    elif suffix == ".mbox":
        emails = parse_mbox_file(str(file_path), args.target)
    else:
        emails = parse_txt_file(str(file_path), args.target)

    if not emails:
        print(f"警告：未找到來自 '{args.target}' 的信件", file=sys.stderr)
        print("提示：請確認目標名稱/信箱是否與檔案中的 From 欄位一致", file=sys.stderr)

    classified = classify_emails(emails)
    output = format_output(args.target, classified)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已輸出到 {args.output}，共 {len(emails)} 封信件")
    else:
        print(output)


if __name__ == "__main__":
    main()
