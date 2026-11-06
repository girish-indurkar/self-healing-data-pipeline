"""Clean sample data banata hai: data/clean_orders.csv"""
import random
import pandas as pd
from pathlib import Path

def generate(n=200, path="data/clean_orders.csv"):
    random.seed(42)
    cities = ["Nashik", "Pune", "Mumbai", "Nagpur", "Thane"]
    df = pd.DataFrame({
        "order_id": range(1, n + 1),
        "customer_id": [random.randint(1000, 1100) for _ in range(n)],
        "amount": [round(random.uniform(100, 5000), 2) for _ in range(n)],
        "order_date": pd.date_range("2026-01-01", periods=n, freq="D").strftime("%Y-%m-%d"),
        "city": [random.choice(cities) for _ in range(n)],
    })
    Path(path).parent.mkdir(exist_ok=True, parents=True)
    df.to_csv(path, index=False)
    return path

if __name__ == "__main__":
    print("Created", generate())
