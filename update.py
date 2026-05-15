import pandas as pd

SHEET_URL = "https://docs.google.com/spreadsheets/d/1Wgs2XgmamRKgoEd_R4Z2tbOa21h8t6UjlslB62hAtYs/export?format=csv&gid=0"

df = pd.read_csv(SHEET_URL)

df = df.fillna("")

df.to_json(
    "data.json",
    orient="records",
    indent=2,
    force_ascii=False
)

print("updated")
