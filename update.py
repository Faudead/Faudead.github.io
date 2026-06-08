import json
import os
import pandas as pd
import requests

BUDGET_SHEET_URL = "https://docs.google.com/spreadsheets/d/1D11kd5byyB17kJ88mUGvBdhkLOX8IKsPn6CcGKK0COU/edit?usp=drivesdk"
WISHLIST_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Wgs2XgmamRKgoEd_R4Z2tbOa21h8t6UjlslB62hAtYs/edit?usp=drivesdk"

base_path = os.getcwd()
log_path = os.path.join(base_path, "debug_log.txt")
json_path = os.path.join(base_path, "data.json")

def write_log(msg):
    print(msg)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

with open(log_path, "w", encoding="utf-8") as f:
    f.write("Початок синхронізації...\n")

try:
    data = {"transactions": [], "budget": [], "wishlist": []}
    budget_id = "1D11kd5byyB17kJ88mUGvBdhkLOX8IKsPn6CcGKK0COU"
    wishlist_id = "1Wgs2XgmamRKgoEd_R4Z2tbOa21h8t6UjlslB62hAtYs"

    # Словник: вкладка -> (URL, тип даних)
    sources = {
        "transactions": f"https://docs.google.com/spreadsheets/d/{budget_id}/export?format=csv&gid=33010173",
        "budget": f"https://docs.google.com/spreadsheets/d/{budget_id}/export?format=csv&gid=1626297495",
        "wishlist": f"https://docs.google.com/spreadsheets/d/{wishlist_id}/export?format=csv&gid=0"
    }

    for key, url in sources.items():
        write_log(f"Завантажую {key}...")
        res = requests.get(url, timeout=20)
        if res.status_code == 200 and "html" not in res.text.lower()[:50]:
            df = pd.read_csv(pd.io.common.StringIO(res.text))
            data[key] = df.fillna("").to_dict(orient="records")
            write_log(f"   Успішно! Рядків: {len(data[key])}")
        else:
            write_log(f"   ПОМИЛКА: Не вдалося завантажити {key} (Статус: {res.status_code})")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    write_log("Готово! data.json оновлено.")

except Exception as e:
    write_log(f"КРИТИЧНА ПОМИЛКА: {str(e)}")
