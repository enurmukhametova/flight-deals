import json
import os
from datetime import date, timedelta
from statistics import median
from . import config


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_history() -> dict:
    return _load_json(config.HISTORY_FILE, {})


def save_history(h: dict):
    _save_json(config.HISTORY_FILE, h)


def load_sent() -> dict:
    return _load_json(config.SENT_FILE, {})


def save_sent(s: dict):
    _save_json(config.SENT_FILE, s)


def route_key(item: dict) -> str:
    tag = "OW" if item["one_way"] else "RT"
    return f"{item['origin']}-{item['destination']}-{tag}"


def update_history(history: dict, items: list[dict]) -> dict:
    """Дописывает сегодняшние минимальные цены по каждому маршруту."""
    today = date.today().isoformat()
    cutoff = (date.today() - timedelta(days=config.HISTORY_WINDOW_DAYS)).isoformat()

    today_min: dict[str, int] = {}
    for it in items:
        k = route_key(it)
        if k not in today_min or it["price_rub"] < today_min[k]:
            today_min[k] = it["price_rub"]

    for k, price in today_min.items():
        bucket = history.setdefault(k, {"prices": []})
        bucket["prices"] = [p for p in bucket["prices"] if p["date"] >= cutoff]
        bucket["prices"] = [p for p in bucket["prices"] if p["date"] != today]
        bucket["prices"].append({"date": today, "price": price})
    return history


def find_deals(items: list[dict], history: dict, sent: dict) -> list[dict]:
    today = date.today()
    cutoff_sent = today - timedelta(days=config.ANTI_DUP_DAYS)

    best_per_route: dict[str, dict] = {}
    for it in items:
        k = route_key(it)
        if k not in best_per_route or it["price_rub"] < best_per_route[k]["price_rub"]:
            best_per_route[k] = it

    deals = []
    for k, it in best_per_route.items():
        hist = history.get(k, {}).get("prices", [])
        if len(hist) < config.MIN_OBSERVATIONS:
            continue
        med = median(p["price"] for p in hist)
        if med <= 0:
            continue
        discount = 1 - (it["price_rub"] / med)
        if discount < config.DISCOUNT_THRESHOLD:
            continue
        last_sent = sent.get(k)
        if last_sent:
            try:
                if date.fromisoformat(last_sent) >= cutoff_sent:
                    continue
            except ValueError:
                pass
        it = dict(it)
        it["median_rub"] = int(med)
        it["discount"] = discount
        deals.append(it)

    deals.sort(key=lambda x: -x["discount"])
    return deals[: config.MAX_DEALS_PER_DAY]


def mark_sent(sent: dict, deals: list[dict]) -> dict:
    today = date.today().isoformat()
    for d in deals:
        sent[route_key(d)] = today
    cutoff = (date.today() - timedelta(days=config.ANTI_DUP_DAYS * 3)).isoformat()
    return {k: v for k, v in sent.items() if v >= cutoff}
