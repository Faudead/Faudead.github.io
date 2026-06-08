import json
import re
import pandas as pd

# =========================================================================
# ВСТАВ СВОЇ ПОСИЛАННЯ НА ТАБЛИЦІ СЮДИ (Звичайні посилання на перегляд)
# =========================================================================
# Таблиця з бюджетом та транзакціями (червнева)
BUDGET_SHEET_URL = "https://docs.google.com/spreadsheets/d/1W0Lm4Rf9UGrzNPf4JD9Io_XfroqOnrAf/edit?usp=drivesdk"

# Таблиця зі списком бажань (якщо це окрема таблиця, або залиш таку ж саму)
WISHLIST_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Wgs2XgmamRKgoEd_R4Z2tbOa21h8t6UjlslB62hAtYs/edit?usp=drivesdk"


def extract_id(url):
    """Витягує чистий ID таблиці з будь-якого посилання Google Таблиць"""
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else None


try:
    budget_id = extract_id(BUDGET_SHEET_URL)
    wishlist_id = extract_id(WISHLIST_SHEET_URL)

    if not budget_id or not wishlist_id:
        raise ValueError(
            "Не вдалося розпізнати ID таблиць. Перевір формат посилань."
        )

    # Формуємо посилання на CSV-експорт конкретних вкладок за їхніми gid
    # Для червневої таблиці: Транзакції (gid=33010173), Бюджет (gid=1626297495)
    url_transactions = f"https://docs.google.com/spreadsheets/d/{budget_id}/export?format=csv&gid=33010173"
    url_budget = f"https://docs.google.com/spreadsheets/d/{budget_id}/export?format=csv&gid=1626297495"

    # Для таблиці бажань (перша вкладка зазвичай gid=0)
    url_wishlist = f"https://docs.google.com/spreadsheets/d/{wishlist_id}/export?format=csv&gid=0"

    print("⏳ Завантаження даних з Google Таблиць...")

    # Зчитуємо дані через pandas
    df_transactions = pd.read_csv(url_transactions, encoding="utf-8").fillna(
        ""
    )
    df_budget = pd.read_csv(url_budget, encoding="utf-8").fillna("")

    # Безпечно пробуємо зчитати вішліст
    try:
        df_wishlist = pd.read_csv(url_wishlist, encoding="utf-8").fillna("")
        wishlist_records = df_wishlist.to_dict(orient="records")
    except Exception:
        print("⚠️ Не вдалося завантажити Wishlist. Вкладку буде пропущено.")
        wishlist_records = []

    # Пакуємо все в один об'єкт
    combined_data = {
        "transactions": df_transactions.to_dict(orient="records"),
        "budget": df_budget.to_dict(orient="records"),
        "wishlist": wishlist_records,
    }

    # Зберігаємо локальний json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

    print("✅ Успішно! Файл data.json створено/оновлено.")

except Exception as e:
    print(f"❌ Помилка роботи скрипта: {e}")
    print(
        "Переконайся, що в налаштуваннях доступу обох таблиць увімкнено 'Усі, хто мають посилання' -> 'Може переглядати'."
    )
