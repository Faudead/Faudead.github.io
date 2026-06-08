import json
import re
import sys
import pandas as pd
import requests

# ТВОЄ НОВЕ ПОСИЛАННЯ НА СВІЖУ GOOGLE ТАБЛИЦЮ
BUDGET_SHEET_URL = "https://docs.google.com/spreadsheets/d/1D11kd5byyB17kJ88mUGvBdhkLOX8IKsPn6CcGKK0COU/edit?usp=drivesdk"
WISHLIST_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Wgs2XgmamRKgoEd_R4Z2tbOa21h8t6UjlslB62hAtYs/edit?usp=drivesdk"

def extract_id(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else None

# Створюємо чистий файл логу перед початком
log_file = "debug_log.txt"
with open(log_file, "w", encoding="utf-8") as log:
    log.write("=== ПОЧАТОК ЛОГУВАННЯ СИНХРОНІЗАЦІЇ ===\n")

def write_log(message):
    print(message)
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(message + "\n")

combined_data = {"transactions": [], "budget": [], "wishlist": []}

try:
    budget_id = extract_id(BUDGET_SHEET_URL)
    wishlist_id = extract_id(WISHLIST_SHEET_URL)

    if not budget_id or not wishlist_id:
        raise ValueError("Не вдалося розпізнати ID таблиць.")

    # Прописуємо точні gid вкладок, які ми витягнули з твоєї червневої структури таблиці
    url_transactions = f"https://docs.google.com/spreadsheets/d/{budget_id}/export?format=csv&gid=33010173"  # Транзакції
    url_budget = f"https://docs.google.com/spreadsheets/d/{budget_id}/export?format=csv&gid=1626297495"      # Бюджет
    url_wishlist = f"https://docs.google.com/spreadsheets/d/{wishlist_id}/export?format=csv&gid=0"          # Вішліст

    # 1. Логування Бюджету
    write_log("\n⏳ [БЮДЖЕТ] Надсилання запиту до Google...")
    try:
        res_bg = requests.get(url_budget, timeout=10)
        write_log(f"   Статус відповіді: {res_bg.status_code}")
        write_log(f"   Довжина отриманого тексту: {len(res_bg.text)} символів")
        
        if "html" in res_bg.text.lower() and "google" in res_bg.text.lower():
            write_log("   ⚠️ УВАГА: Google повернув HTML-сторінку (можливо авторизація або помилка доступу) замість таблиці!")
        else:
            write_log(f"   Перші 200 символів відповіді: \n{res_bg.text[:200]}\n---")
            
        df_bg = pd.read_csv(url_budget, encoding="utf-8")
        write_log(f"   Знайдені колонки у Бюджеті: {list(df_bg.columns)}")
        write_log(f"   Успішно зчитано рядків: {len(df_bg)}")
        combined_data["budget"] = df_bg.fillna("").to_dict(orient="records")
    except Exception as bg_err:
        write_log(f"❌ Помилка обробки Бюджету: {bg_err}")

    # 2. Логування Тразнакцій
    write_log("\n⏳ [ТРАНЗАКЦІЇ] Надсилання запиту до Google...")
    try:
        res_tx = requests.get(url_transactions, timeout=10)
        write_log(f"   Статус відповіді: {res_tx.status_code}")
        write_log(f"   Довжина отриманого тексту: {len(res_tx.text)} symbols")
        
        if "html" in res_tx.text.lower() and "google" in res_tx.text.lower():
            write_log("   ⚠️ УВАГА: Google повернув HTML-сторінку (можливо авторизація або помилка доступу) замість таблиці!")
        else:
            write_log(f"   Перші 200 символів відповіді: \n{res_tx.text[:200]}\n---")

        df_tx = pd.read_csv(url_transactions, encoding="utf-8")
        write_log(f"   Знайдені колонки у Транзакціях: {list(df_tx.columns)}")
        write_log(f"   Успішно зчитано рядків: {len(df_tx)}")
        combined_data["transactions"] = df_tx.fillna("").to_dict(orient="records")
    except Exception as tx_err:
        write_log(f"❌ Помилка обробки Транзакцій: {tx_err}")

    # 3. Логування Вішліста
    write_log("\n⏳ [ВІШЛІСТ] Запит до Google...")
    try:
        df_wl = pd.read_csv(url_wishlist, encoding="utf-8")
        write_log(f"   Знайдені колонки у Вішлісті: {list(df_wl.columns)}")
        write_log(f"   Успішно зчитано рядків: {len(df_wl)}")
        combined_data["wishlist"] = df_wl.fillna("").to_dict(orient="records")
    except Exception as wl_err:
        write_log(f"❌ Помилка обробки Вішліста: {wl_err}")

    # Записуємо основні дані
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    write_log("\n✅ Логування завершено успішно. Файл data.json оновлено новими даними.")

except Exception as main_e:
    write_log(f"\n❌ Критична помилка скрипта: {main_e}")
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False)
    sys.exit(1)
