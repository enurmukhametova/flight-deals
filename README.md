# flight-deals

Ежедневная рассылка дешёвых авиабилетов из AUH / DXB / SHJ в Telegram.

Логика: каждый день GitHub Actions тянет цены через Travelpayouts,
сравнивает с медианой за последние 30 дней по каждому маршруту,
шлёт в Telegram те, где скидка ≥40% и ≤1 пересадки.

## Секреты (Settings → Secrets and variables → Actions)

- `TRAVELPAYOUTS_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Ручной запуск

Actions → Daily flight deals → Run workflow.
