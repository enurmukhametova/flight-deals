from .fetcher import fetch_all, get_rub_to_aed_rate
from .analyzer import (
    load_history, save_history, load_sent, save_sent,
    update_history, find_deals, mark_sent,
)
from .notifier import format_deals, send_telegram


def main():
    items = fetch_all()
    print(f"Fetched {len(items)} price points")

    history = load_history()
    sent = load_sent()

    deals = find_deals(items, history, sent)
    print(f"Found {len(deals)} deals")

    history = update_history(history, items)
    save_history(history)

    if deals:
        sent = mark_sent(sent, deals)
        save_sent(sent)

    rate = get_rub_to_aed_rate()
    messages = format_deals(deals, rate)
    send_telegram(messages)


if __name__ == "__main__":
    main()
