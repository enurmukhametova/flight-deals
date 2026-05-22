import requests
from datetime import date, timedelta
from . import config

TP_URL = "https://api.travelpayouts.com/v2/prices/latest"
FX_URL = "https://api.frankfurter.app/latest"


def fetch_prices(origin: str, one_way: bool) -> list[dict]:
    """Тянет последние закэшированные цены из Travelpayouts."""
    params = {
        "currency": config.CURRENCY_API,
        "origin": origin,
        "period_type": "month",
        "one_way": str(one_way).lower(),
        "page": 1,
        "limit": 1000,
        "show_to_affiliates": "true",
        "sorting": "price",
        "token": config.TP_TOKEN,
    }
    r = requests.get(TP_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])


def fetch_all() -> list[dict]:
    """Собирает цены по всем городам и обоим типам (one-way / round-trip)."""
    today = date.today()
    horizon = today + timedelta(days=config.DAYS_AHEAD)
    out = []
    for origin in config.ORIGINS:
        for one_way in (True, False):
            try:
                items = fetch_prices(origin, one_way)
            except Exception as e:
                print(f"[fetch error] {origin} one_way={one_way}: {e}")
                continue
            for it in items:
                depart = it.get("depart_date")
                if not depart:
                    continue
                try:
                    dep = date.fromisoformat(depart)
                except ValueError:
                    continue
                if not (today <= dep <= horizon):
                    continue
                if (it.get("number_of_changes") or 0) > config.MAX_STOPS:
                    continue
                out.append({
                    "origin": origin,
                    "destination": it["destination"],
                    "price_rub": int(it["value"]),
                    "depart": depart,
                    "return": it.get("return_date") or "",
                    "stops": it.get("number_of_changes", 0),
                    "one_way": one_way,
                })
    return out


def get_rub_to_aed_rate() -> float:
    """Курс RUB→AED. При сбое — приближение."""
    try:
        r = requests.get(FX_URL, params={"from": "RUB", "to": "AED"}, timeout=15)
        r.raise_for_status()
        return float(r.json()["rates"]["AED"])
    except Exception as e:
        print(f"[fx error] {e}, using fallback")
        return 0.045  # ~ запасной курс
