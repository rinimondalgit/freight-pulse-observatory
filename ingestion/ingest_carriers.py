import json
if __name__ == "__main__":
    rows = json.load(open("carrier_reference_sample.json"))
    print(rows[:2])
    print(f"records: {len(rows)}")
