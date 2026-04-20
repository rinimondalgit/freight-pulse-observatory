import pandas as pd
import random
from datetime import datetime, timedelta

carriers = ["FedEx", "UPS", "DHL", "XPO", "Old Dominion"]
modes = ["Ground", "Air", "LTL", "FTL"]
states = ["TX", "CA", "IL", "GA", "NJ"]

rows = []

for i in range(1, 10001):
    ship_date = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 364))
    promised_days = random.randint(2, 7)
    actual_days = max(1, promised_days + random.choice([-1, 0, 1, 2]))
    delivery_date = ship_date + timedelta(days=actual_days)

    rows.append({
        "shipment_id": f"SHP{i:05d}",
        "ship_date": ship_date.date(),
        "delivery_date": delivery_date.date(),
        "carrier": random.choice(carriers),
        "mode": random.choice(modes),
        "origin_state": random.choice(states),
        "destination_state": random.choice(states),
        "distance_miles": random.randint(100, 2000),
        "promised_days": promised_days,
        "actual_days": actual_days,
        "delayed_flag": 1 if actual_days > promised_days else 0,
        "shipping_cost": round(random.uniform(100, 2000), 2)
    })

df = pd.DataFrame(rows)
df.to_csv("data/raw/shipments_sample.csv", index=False)

print("✅ Data generated successfully!")