import requests
from . import config


def _aviasales_link(d: dict) -> str:
    dep = d["depart"].replace("-", "")[2:]   # YYMMDD
    dd = dep[4:6] + dep[2:4]
    url = f"https://www.aviasales.com/search/{d['origin']}{dd}{d['destination']}"
    if not d["one_way"] and d["return"]:
        ret = d["return"].replace("-", "")[2:]
        url += ret[4:6] + ret[2:4]
    return url + "1"


def format_deals(deals: list[dict], rub_to_aed: float) -> list[str]:
    if not deals:
        return ["✈️ Сегодня скидок ≥40% от медианы не найдено."]
    header = f"✈️ Дешёвые билеты на {len(deals)} маршрутов (скидка ≥{int(config.DISCOUNT_THRESHOLD*100)}% от медианы):\n"
    lines = [header]
    for d in deals:
        aed = int(d["price_rub"] * rub_to_aed)
        med_aed = int(d["median_rub"] * rub_to_aed)
        kind = "→" if d["one_way"] else "⇄"
        dates = d["depart"] + (f" → {d['return']}" if d["return"] else "")
        link = _aviasales_link(d)
        lines.append(
            f"\n<b>{d['origin']} {kind} {d['destination']}</b>  "
            f"−{int(d['discount']*100)}%\n"
            f"  💰 {d['price_rub']:,} ₽ / {aed:,} AED "
            f"(обычно {d['median_rub']:,} ₽ / {med_aed:,} AED)\n"
            f"  📅 {dates}  ✈️ пересадок: {d['stops']}\n"
            f"  <a href='{link}'>открыть на Aviasales</a>"
        )
    return _chunk(lines)


def _chunk(lines: list[str], limit: int = 3800) -> list[str]:
    chunks, cur = [], ""
    for line in lines:
        if len(cur) + len(line) > limit:
            chunks.append(cur)
            cur = ""
        cur += line
    if cur:
        chunks.append(cur)
    return chunks


def send_telegram(messages: list[str]):
    url = f"https://api.telegram.org/bot{config.TG_TOKEN}/sendMessage"
    for msg in messages:
        r = requests.post(url, data={
            "chat_id": config.TG_CHAT,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }, timeout=30)
        if not r.ok:
            print(f"[telegram error] {r.status_code} {r.text}")
