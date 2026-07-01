import json
import re
from decimal import Decimal
from pathlib import Path


BASE = Path(__file__).resolve().parent
TXT_PATH = BASE / "招商银行交易流水_20260603.txt"
JSON_PATH = BASE / "招商银行交易流水_20260603.json"

DATE_LINE_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<currency>[A-Z]{3})\s+(?P<rest>.*)$")
AMOUNT_RE = re.compile(r"^[+-]?\d[\d,]*\.\d{2}$")
PAGE_RE = re.compile(r"^\d+/\d+$")


def money_to_number(value: str):
    if not value:
        return None
    return float(Decimal(value.replace(",", "")))


def split_rest(rest: str):
    tokens = rest.split()
    amount = None
    balance = None
    idx = 0

    if idx < len(tokens) and AMOUNT_RE.match(tokens[idx]):
        amount = tokens[idx]
        idx += 1

    if idx < len(tokens) and AMOUNT_RE.match(tokens[idx]):
        balance = tokens[idx]
        idx += 1

    tail = rest
    if amount:
        tail = tail.replace(amount, "", 1)
    if balance:
        tail = tail.replace(balance, "", 1)
    tail = tail.strip()
    return amount, balance, tail


def clean_line(line: str):
    return line.replace("\f", "").rstrip()


def is_noise(line: str):
    stripped = line.strip()
    if not stripped:
        return True
    if PAGE_RE.match(stripped):
        return True
    noise_terms = [
        "招商银行交易流水",
        "Transaction Statement",
        "--",
        "户 名：",
        "账号：",
        "账户类型：",
        "开 户 行：",
        "申请时间：",
        "验 证 码：",
        "Name",
        "Account No",
        "Account Type",
        "Sub Branch",
        "Verification Code",
        "记账日期",
        "交易金额",
        "联机余额",
        "交易摘要",
        "对手信息",
        "Date  Currency",
        "Transaction",
        "Amount",
        "Balance",
        "Counter Party",
        "温馨提示",
        "交易流水验真",
    ]
    return any(term in stripped for term in noise_terms) or stripped.startswith("——")


def parse_header(lines):
    header_text = "\n".join(lines[:20])
    period = re.search(r"(\d{4}-\d{2}-\d{2})\s+--\s+(\d{4}-\d{2}-\d{2})", header_text)
    name_account = re.search(r"户 名：(.+?)\s+账号：(\d+)", header_text)
    account_branch = re.search(r"账户类型：(.+?)\s+开 户 行：(.+)", header_text)
    applied = re.search(r"申请时间：(.+?)\s+验\s*证\s*码：([A-Z0-9]+)", header_text)
    return {
        "bank": "招商银行",
        "statement_type": "交易流水",
        "period_start": period.group(1) if period else None,
        "period_end": period.group(2) if period else None,
        "name": name_account.group(1).strip() if name_account else None,
        "account_no": name_account.group(2) if name_account else None,
        "account_type": account_branch.group(1).strip() if account_branch else None,
        "branch": account_branch.group(2).strip() if account_branch else None,
        "application_time": applied.group(1).strip() if applied else None,
        "verification_code": applied.group(2) if applied else None,
    }


def parse_transactions(lines):
    transactions = []
    current = None
    pending_counterparty = []

    for raw in lines:
        line = clean_line(raw)
        if "温馨提示" in line:
            break
        match = DATE_LINE_RE.match(line.strip())

        if match:
            if current:
                transactions.append(current)
            amount, balance, tail = split_rest(match.group("rest"))
            current = {
                "date": match.group("date"),
                "currency": match.group("currency"),
                "amount": money_to_number(amount),
                "amount_text": amount,
                "direction": "income" if amount and not amount.startswith("-") else "expense" if amount else None,
                "balance": money_to_number(balance),
                "balance_text": balance,
                "transaction_type": None,
                "counterparty": None,
                "notes": [],
                "raw_lines": [line.strip()],
            }
            if tail:
                parts = re.split(r"\s{2,}", tail, maxsplit=1)
                current["transaction_type"] = parts[0].strip() if parts else None
                if len(parts) > 1:
                    current["counterparty"] = parts[1].strip()
                elif parts:
                    current["notes"].append(parts[0].strip())
            if pending_counterparty:
                prefix = " ".join(pending_counterparty).strip()
                current["counterparty"] = f"{prefix}{current['counterparty'] or ''}".strip()
                current["raw_lines"] = pending_counterparty + current["raw_lines"]
                pending_counterparty = []
            continue

        if not current or is_noise(line):
            leading_spaces = len(line) - len(line.lstrip(" "))
            if current is None and not is_noise(line) and line.strip() and leading_spaces >= 55:
                pending_counterparty.append(line.strip())
            continue

        stripped = line.strip()
        if stripped:
            leading_spaces = len(line) - len(line.lstrip(" "))
            if leading_spaces >= 55 and current.get("counterparty"):
                pending_counterparty.append(stripped)
                continue
            if current.get("amount") is None:
                continuation_tokens = stripped.split()
                if continuation_tokens and AMOUNT_RE.match(continuation_tokens[0]):
                    amount = continuation_tokens[0]
                    current["amount"] = money_to_number(amount)
                    current["amount_text"] = amount
                    current["direction"] = "income" if not amount.startswith("-") else "expense"
                    remainder = stripped.replace(amount, "", 1).strip()
                    if remainder:
                        current["notes"].append(remainder)
                    current["raw_lines"].append(stripped)
                    continue
            current["raw_lines"].append(stripped)
            current["notes"].append(stripped)

    if current:
        transactions.append(current)

    for tx in transactions:
        note_text = " ".join(tx["notes"]).strip()
        if note_text:
            if tx["counterparty"]:
                tx["counterparty"] = f"{tx['counterparty']} {note_text}".strip()
            else:
                tx["counterparty"] = note_text
        tx["notes"] = note_text

    return transactions


def main():
    lines = TXT_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    transactions = parse_transactions(lines)
    payload = {
        "source_pdf": "招商银行交易流水(申请时间2026年06月03日16时39分42秒).pdf",
        "source_text": TXT_PATH.name,
        "parser": "parse_cmb_statement.py",
        "header": parse_header(lines),
        "summary": {
            "transaction_count": len(transactions),
            "income_count": sum(1 for tx in transactions if tx["direction"] == "income"),
            "expense_count": sum(1 for tx in transactions if tx["direction"] == "expense"),
            "income_total": round(sum(tx["amount"] for tx in transactions if tx["amount"] and tx["amount"] > 0), 2),
            "expense_total": round(sum(tx["amount"] for tx in transactions if tx["amount"] and tx["amount"] < 0), 2),
        },
        "transactions": transactions,
    }
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(JSON_PATH)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
