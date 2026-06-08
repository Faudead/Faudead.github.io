import json
import os
import pandas as pd
import requests
from io import BytesIO

BUDGET_ID = "1D11kd5byyB17kJ88mUGvBdhkLOX8IKsPn6CcGKK0COU"
WISHLIST_ID = "1Wgs2XgmamRKgoEd_R4Z2tbOa21h8t6UjlslB62hAtYs"

base_path = os.getcwd()
log_path = os.path.join(base_path, "debug_log.txt")
json_path = os.path.join(base_path, "data.json")


def write_log(msg):
    print(msg)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def clean_df(df):
    # прибираємо NaN і Timestamp проблеми
    df = df.fillna("")

    def convert(x):
        if isinstance(x, pd.Timestamp):
            return x.isoformat()
        return str(x)

    return df.map(convert)


def load_sheet_xlsx(sheet_id, name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

    write_log(f"\n===== {name} =====")
    write_log(f"URL: {url}")

    try:
        res = requests.get(url, timeout=20)

        write_log(f"HTTP статус: {res.status_code}")
        write_log(f"Content-Type: {res.headers.get('Content-Type')}")

        if res.status_code != 200:
            write_log("❌ HTTP помилка")
            write_log(res.text[:300])
            return {}

        xls = pd.ExcelFile(BytesIO(res.content))

        write_log(f"📄 Вкладки: {xls.sheet_names}")

        result = {}

        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)

            df = clean_df(df)

            data = df.to_dict(orient="records")
            result[sheet] = data

            write_log(f"   ✅ {sheet}: {len(data)} рядків")

        return result

    except Exception as e:
        write_log("❌ КРИТИЧНА ПОМИЛКА")
        write_log(str(e))
        return {}


# ===== INIT LOG =====
with open(log_path, "w", encoding="utf-8") as f:
    f.write("Початок синхронізації...\n")


data = {
    "budget": {},
    "transactions": [],
    "wishlist": []
}

# ===== BUDGET SHEET =====
budget_sheets = load_sheet_xlsx(BUDGET_ID, "BUDGET")

data["transactions"] = budget_sheets.get("Транзакції", [])
data["budget"] = budget_sheets.get("Бюджет", [])
data["dovidnyky"] = budget_sheets.get("Довідники", [])

# ===== WISHLIST SHEET =====
wishlist_sheets = load_sheet_xlsx(WISHLIST_ID, "WISHLIST")

# зазвичай Sheet1 або Лист1
data["wishlist"] = wishlist_sheets.get("Sheet1") or wishlist_sheets.get("Лист1") or []

# ===== SAVE JSON =====
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

write_log("\n===== ГОТОВО =====")