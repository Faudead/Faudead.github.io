import json
import re
import sys
import pandas as pd

# Твоє нове посилання на червневий файл
BUDGET_SHEET_URL = "https://docs.google.com/spreadsheets/d/1W0Lm4Rf9UGrzNPf4JD9Io_XfroqOnrAf/edit?usp=drivesdk"
WISHLIST_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Wgs2XgmamRKgoEd_R4Z2tbOa21h8t6UjlslB62hAtYs/edit?usp=drivesdk"


def extract_id(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else None


combined_data = {"transactions": [], "budget": [], "wishlist": []}

try:
    budget_id = extract_id(BUDGET_SHEET_URL)
    wishlist_id = extract_id(WISHLIST_SHEET_URL)

    if not budget_id or not wishlist_id:
        raise ValueError("Не вдалося розпізнати ID таблиць.")

    # Прописуємо точні індекси сторінок для твого Excel-формату
    url_budget = f"https://docs.google.com/spreadsheets/d/{budget_id}/export?format=csv&gid=0"  # Перша вкладка (Бюджет)
    url_transactions = f"https://docs.google.com/spreadsheets/d/{budget_id}/export?format=csv&gid=1"  # Друга вкладка (Транзакції)
    url_wishlist = f"https://docs.google.com/spreadsheets/d/{wishlist_id}/export?format=csv&gid=0"

    print("⏳ Завантаження лімітів Бюджету...")
    try:
        df_bg = pd.read_csv(url_budget, encoding="utf-8")
        combined_data["budget"] = df_bg.fillna("").to_dict(orient="records")
    except Exception as bg_err:
        print(f"⚠️ Помилка завантаження бюджету: {bg_err}")

    print("⏳ Завантаження Транзакцій...")
    try:
        df_tx = pd.read_csv(url_transactions, encoding="utf-8")
        combined_data["transactions"] = df_tx.fillna("").to_dict(
            orient="records"
        )
    except Exception as tx_err:
        print(f"⚠️ Помилка завантаження транзакцій: {tx_err}")

    print("⏳ Завантаження вішліста...")
    try:
        df_wl = pd.read_csv(url_wishlist, encoding="utf-8")
        combined_data["wishlist"] = df_wl.fillna("").to_dict(orient="records")
    except Exception as wl_err:
        print(f"⚠️ Помилка завантаження вішліста: {wl_err}")

    # Фінальний запис у файл
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

    print("✅ Успішно! Файл data.json оновлено новими даними.")

except Exception as main_e:
    print(f"❌ Критична помилка скрипта: {main_e}")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False)
    sys.exit(1)
