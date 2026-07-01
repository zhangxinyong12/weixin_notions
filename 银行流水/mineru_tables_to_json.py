import html
import json
import re
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path


BASE = Path(__file__).resolve().parent
MINERU_DIR = BASE / "mineru_招商银行交易流水_20260603" / "extracted"
OUT_PATH = BASE / "招商银行交易流水_20260603.mineru.json"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self._rows = []
        self._cells = []
        self._buf = []
        self._in_table = False
        self._in_td = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._in_table = True
            self._rows = []
        elif self._in_table and tag == "tr":
            self._cells = []
        elif self._in_table and tag == "td":
            self._in_td = True
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "td" and self._in_td:
            self._cells.append(html.unescape("".join(self._buf)).strip())
            self._in_td = False
        elif tag == "tr" and self._in_table:
            if self._cells:
                self._rows.append(self._cells)
        elif tag == "table" and self._in_table:
            self.tables.append(self._rows)
            self._in_table = False

    def handle_data(self, data):
        if self._in_td:
            self._buf.append(data)


def money(value):
    value = value.replace(" ", "").replace(",", "").strip()
    if not value:
        return None
    try:
        return float(Decimal(value))
    except Exception:
        return None


def iter_tables():
    for path in sorted(MINERU_DIR.glob("*content_list*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        stack = list(data) if isinstance(data, list) else [data]
        while stack:
            item = stack.pop(0)
            if isinstance(item, list):
                stack.extend(item)
                continue
            if not isinstance(item, dict):
                continue
            text = item.get("table_body") or item.get("text", "")
            if item.get("type") == "table" or "<table" in text:
                parser = TableParser()
                parser.feed(text)
                for table in parser.tables:
                    yield path.name, table


def main():
    transactions = []
    for source, table in iter_tables():
        for row in table:
            if len(row) < 6:
                continue
            date, currency, amount_text, balance_text, tx_type, counterparty = row[:6]
            date = date.replace("CNY", "").strip()
            if not DATE_RE.match(date):
                continue
            amount = money(amount_text)
            if amount is None:
                continue
            transactions.append(
                {
                    "date": date,
                    "currency": currency.strip() or "CNY",
                    "amount": amount,
                    "amount_text": amount_text,
                    "direction": "income" if amount > 0 else "expense",
                    "balance": money(balance_text),
                    "balance_text": balance_text,
                    "transaction_type": tx_type,
                    "counterparty": counterparty,
                    "source": source,
                }
            )

    payload = {
        "source": "MinerU pipeline content_list table extraction",
        "transaction_count": len(transactions),
        "income_count": sum(1 for tx in transactions if tx["amount"] > 0),
        "expense_count": sum(1 for tx in transactions if tx["amount"] < 0),
        "income_total": round(sum(tx["amount"] for tx in transactions if tx["amount"] > 0), 2),
        "expense_total": round(sum(tx["amount"] for tx in transactions if tx["amount"] < 0), 2),
        "transactions": transactions,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT_PATH)
    print(json.dumps({k: payload[k] for k in payload if k != "transactions"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
