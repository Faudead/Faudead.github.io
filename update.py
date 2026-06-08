import json
import os
import pandas as pd
import requests

# Твоє нове посилання на червневу Google Таблицю
BUDGET_SHEET_URL = "https://docs.google.com/spreadsheets/d/1D11kd5byyB17kJ88mUGvBdhkLOX8IKsPn6CcGKK0COU/edit?usp=drivesdk"

base_path = os.getcwd()
log_path = os.path.join(base_path, "debug_log.txt")
json_path = os.path.join(base_path, "data.json")

def write_log(msg):
    print(msg)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Початок логування
with open(log_path, "w", encoding="utf-8") as f:
    f.write(f"Скрипт запущено в: {base_path}\n")

try:
    write_log("Спроба підключення до Google Таблиці...")
    
    # Використовуємо ID твоєї таблиці
    sheet_id = "1D11kd5byyB17kJ88mUGvBdhkLOX8IKsPn6CcGKK0COU"
    # Спробуємо завантажити одну вкладку (Транзакції) через requests
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=33010173"
    
    res = requests.get(url, timeout=15)
    write_log(f"Статус відповіді Google: {res.status_code}")
    
    if res.status_code == 200:
        write_log("Успішно отримано дані від Google!")
        # Перевірка на HTML (часта помилка, коли таблиця закрита)
        if "html" in res.text.lower()[:100]:
            write_log("ПОМИЛКА: Отримано HTML замість CSV. Перевір права доступу до таблиці!")
        else:
            write_log(f"Довжина отриманого CSV: {len(res.text)} символів")
            
            # Спробуємо створити data.json з реальними даними
            data = {"status": "success", "length": len(res.text)}
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            write_log("Успішно створено data.json з даними.")
    else:
        write_log(f"Помилка доступу до таблиці: {res.status_code}")

except Exception as e:
    write_log(f"КРИТИЧНА ПОМИЛКА: {str(e)}")
