import random
import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.shop
orders = db.orders

orders.delete_many({})

sample_orders = [
    {
        "_id": 2001,
        "customer": {"name": "Linh", "city": "Hanoi"},
        "status": "paid",
        "items": [
            {"sku": "BK-01", "qty": 1, "price": 12.5}
        ]
    },
    {
        "_id": 2002,
        "customer": {"name": "Nam", "city": "HCM"},
        "status": "shipped",
        "discount": 5,
        "items": [
            {"sku": "BK-02", "qty": 2, "price": 15.0},
            {"sku": "BK-01", "qty": 1, "price": 12.5}
        ]
    },
    {
        "_id": 2003,
        "email": "test@test.com",
        "status": "paid",
        "items": [
            {"sku": "BK-03", "qty": 5, "price": 20.0}
        ]
    },
    {
        "_id": 2004,
        "customer": {"city": "Da Nang"},
        "coupon": "SUMMER",
        "items": [
            {"sku": "BK-01", "qty": 3, "price": 12.5}
        ]
    },
    {
        "_id": 2005,
        "note": "Giao hang nhanh",
        "items": [
            {"sku": "BK-04", "qty": 1, "price": 10.0}
        ]
    }
]

orders.insert_many(sample_orders)

bk01_orders = orders.find({"items.sku": "BK-01"})
for order in bk01_orders:
    print(f"{order['_id']}")

pipeline = [
    {"$match": {"customer.city": {"$exists": True}}},
    {"$unwind": "$items"},
    {
        "$group": {
            "_id": "$customer.city",
            "totalRevenue": {
                "$sum": {"$multiply": ["$items.qty", "$items.price"]}
            }
        }
    },
    {"$sort": {"totalRevenue": -1}}
]

revenue_by_city = orders.aggregate(pipeline)
df = pd.DataFrame(list(revenue_by_city))
if not df.empty:
    df.rename(columns={"_id": "City", "totalRevenue": "Revenue"}, inplace=True)
    print(df.to_string(index=False))

big_data_col = db.big_data
big_data_col.delete_many({})
big_data_col.drop_indexes()

mock_docs = []
for i in range(10000):
    mock_docs.append({
        "ref_id": i,
        "status": "active" if i % 2 == 0 else "inactive",
        "value": random.randint(1, 100)
    })
big_data_col.insert_many(mock_docs)

explain_before = big_data_col.find({"ref_id": 8888}).explain()
print(explain_before.get("queryPlanner", {}).get("winningPlan", {}).get("stage", "N/A"))
print(explain_before.get("executionStats", {}).get("totalDocsExamined", "N/A"))

big_data_col.create_index([("ref_id", 1)])

explain_after = big_data_col.find({"ref_id": 8888}).explain()
stage_after = explain_after.get("queryPlanner", {}).get("winningPlan", {}).get("stage", "N/A")
if stage_after == "FETCH":
    input_stage = explain_after.get("queryPlanner", {}).get("winningPlan", {}).get("inputStage", {}).get("stage", "N/A")
    stage_after = f"{stage_after} -> {input_stage}"
print(stage_after)
print(explain_after.get("executionStats", {}).get("totalDocsExamined", "N/A"))