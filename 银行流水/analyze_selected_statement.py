import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
IN_PATH = BASE / "招商银行交易流水_20260603.selected.json"
OUT_PATH = BASE / "招商银行交易流水_20260603.analysis.json"


def category(tx):
    text = f"{tx.get('transaction_type') or ''} {tx.get('counterparty') or ''}"
    amount = tx["amount"]
    if any(k in text for k in ["工资", "代发工资"]):
        return "工资/劳务收入"
    if any(k in text for k in ["汇入汇款", "账户结息", "快捷退款", "退款", "赎回"]):
        return "回款/退款/理财赎回"
    if any(k in text for k in ["申购", "理财", "朝朝宝自动转入", "朝朝宝转入", "月月存", "养老金缴存"]):
        return "储蓄/理财/养老金"
    if "信用卡自动还款" in text:
        return "信用卡还款"
    if any(k in text for k in ["微信转账", "转账汇款"]):
        return "转账"
    if any(k in text for k in ["携程", "旅行"]):
        return "旅行/交通"
    if any(k in text for k in ["美团", "超市", "便利", "盒马", "拼多多", "京东", "抖音", "扫码", "壹佰米", "格物"]):
        return "日常消费/购物"
    if any(k in text for k in ["阿里云", "百度", "Stripe", "OpenAI", "保险", "人民健康"]):
        return "订阅/数字服务/保险"
    if any(k in text for k in ["短信服务费", "手续费"]):
        return "银行手续费"
    if amount > 0:
        return "其他收入"
    return "其他支出"


def month_of(date):
    return date[:7]


def signed_sum(items):
    return round(sum(items), 2)


def main():
    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    txs = data["transactions"]
    for tx in txs:
        tx["category"] = category(tx)

    monthly = defaultdict(lambda: {"income": 0.0, "expense": 0.0, "net": 0.0, "count": 0})
    by_category = defaultdict(lambda: {"income": 0.0, "expense": 0.0, "count": 0})
    counterparty_expense = Counter()
    counterparty_count = Counter()

    for tx in txs:
        m = month_of(tx["date"])
        amount = tx["amount"]
        monthly[m]["count"] += 1
        monthly[m]["net"] += amount
        if amount > 0:
            monthly[m]["income"] += amount
            by_category[tx["category"]]["income"] += amount
        else:
            monthly[m]["expense"] += amount
            by_category[tx["category"]]["expense"] += amount
            cp = (tx.get("counterparty") or tx.get("transaction_type") or "未知").strip()
            counterparty_expense[cp[:80]] += -amount
        by_category[tx["category"]]["count"] += 1
        counterparty_count[(tx.get("counterparty") or tx.get("transaction_type") or "未知").strip()[:80]] += 1

    for stats in monthly.values():
        for key in ["income", "expense", "net"]:
            stats[key] = round(stats[key], 2)
    for stats in by_category.values():
        for key in ["income", "expense"]:
            stats[key] = round(stats[key], 2)

    large_expenses = sorted(
        [tx for tx in txs if tx["amount"] < 0],
        key=lambda x: x["amount"],
    )[:50]

    payload = {
        "source": IN_PATH.name,
        "overall": {
            "transaction_count": len(txs),
            "income_total": signed_sum(tx["amount"] for tx in txs if tx["amount"] > 0),
            "expense_total": signed_sum(tx["amount"] for tx in txs if tx["amount"] < 0),
            "net": signed_sum(tx["amount"] for tx in txs),
            "month_count": len(monthly),
        },
        "monthly": dict(sorted(monthly.items())),
        "categories": dict(sorted(by_category.items(), key=lambda kv: abs(kv[1]["expense"]) + kv[1]["income"], reverse=True)),
        "top_expense_counterparties": counterparty_expense.most_common(30),
        "top_counterparty_counts": counterparty_count.most_common(30),
        "large_expenses": large_expenses,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT_PATH)
    print(json.dumps(payload["overall"], ensure_ascii=False, indent=2))
    print("monthly")
    for k, v in payload["monthly"].items():
        print(k, v)
    print("categories")
    for k, v in list(payload["categories"].items())[:12]:
        print(k, v)


if __name__ == "__main__":
    main()
