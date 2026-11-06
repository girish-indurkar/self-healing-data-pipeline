"""Clean data ko jaan-bujhkar kharab karta hai -> data/incoming/orders.csv"""
import random
import pandas as pd
from pathlib import Path

SCENARIOS = {
    "none": "Clean data (no failure)",
    "column_rename": "Upstream ne 'amount' ka naam 'total_amount' kar diya",
    "type_change": "'amount' ab '₹1,200' jaisa string aa raha hai",
    "null_values": "customer_id me NULL values aa gayi",
    "duplicates": "order_id duplicate rows aa gayi",
}

def inject(scenario, src="data/clean_orders.csv", dst="data/incoming/orders.csv"):
    random.seed(1)
    df = pd.read_csv(src)
    if scenario == "column_rename":
        df = df.rename(columns={"amount": "total_amount"})
    elif scenario == "type_change":
        df["amount"] = df["amount"].apply(lambda x: f"₹{x:,.2f}")
    elif scenario == "null_values":
        idx = random.sample(range(len(df)), 15)
        df.loc[idx, "customer_id"] = None
    elif scenario == "duplicates":
        df = pd.concat([df, df.sample(10, random_state=1)], ignore_index=True)
    Path(dst).parent.mkdir(exist_ok=True, parents=True)
    df.to_csv(dst, index=False)
    return dst
