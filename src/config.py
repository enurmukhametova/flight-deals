import os

ORIGINS = ["AUH", "DXB", "SHJ"]
CURRENCY_API = "rub"              # в чём тянем у Travelpayouts
DAYS_AHEAD = 30                   # окно дат: сегодня … +30
MAX_STOPS = 1                     # ≤1 пересадка
DISCOUNT_THRESHOLD = 0.40         # 40% ниже медианы
MIN_OBSERVATIONS = 7              # сколько замеров нужно для активации маршрута
ANTI_DUP_DAYS = 3                 # не дублировать тот же маршрут чаще
MAX_DEALS_PER_DAY = 50            # топ-N в рассылку
HISTORY_WINDOW_DAYS = 30          # окно для расчёта медианы

TP_TOKEN = os.environ["TRAVELPAYOUTS_TOKEN"]
TG_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TG_CHAT = os.environ["TELEGRAM_CHAT_ID"]

HISTORY_FILE = "data/history.json"
SENT_FILE = "data/sent.json"
