import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "learnneo4j"))
driver = GraphDatabase.driver(URI, auth=AUTH)

def run_query(query, **params):
    records, summary, keys = driver.execute_query(query, **params)
    return records


run_query('''
    MERGE (linh:Person {name: "Linh", city: "Hanoi"})
    MERGE (p1:Person {name: "Hoang", city: "Hanoi"})
    MERGE (p2:Person {name: "Kien", city: "Da Nang"})
    MERGE (p3:Person {name: "Trang", city: "Hanoi"})
    MERGE (p4:Person {name: "Duy", city: "Hanoi"})
    MERGE (p5:Person {name: "Ly", city: "HCM"})
    MERGE (linh)-[:FRIEND]->(p1)
    MERGE (p1)-[:FRIEND]->(p2)
    MERGE (p1)-[:FRIEND]->(p3)
    MERGE (p1)-[:FRIEND]->(p4)
    MERGE (p2)-[:FRIEND]->(p5)
''')

result_1 = run_query('''
    MATCH (me:Person {name: "Linh"})-[:FRIEND*2]-(fof:Person)
    WHERE fof.city = "Hanoi" AND fof <> me
    RETURN DISTINCT fof.name AS name
''')
print("Bạn của bạn của Linh ở Hà Nội:")
for r in result_1:
    print(r["name"])



# Tạo dữ liệu mẫu nếu chưa có
run_query('''
    MERGE (mai:Person {name: "Mai"})
    MERGE (b1:Book {title: "Python Basics", price: 120000})
    MERGE (b2:Book {title: "Data Viz", price: 135000})
    MERGE (b3:Book {title: "SQL in Practice", price: 150000})
    MERGE (mai)-[:BOUGHT]->(b1)
    MERGE (mai)-[:BOUGHT]->(b2)
''')


result_2a = run_query('''
    MATCH (me:Person {name: "Mai"})-[:FRIEND]-(friend:Person)-[:BOUGHT]->(book:Book)
    WHERE NOT (me)-[:BOUGHT]->(book)
    RETURN book.title AS recommendation, count(*) AS score
    ORDER BY score DESC
''')
print("Gợi ý sách cho Mai:")
for r in result_2a:
    print(r["recommendation"])

result_2b = run_query('''
    MATCH (p:Person)-[:BOUGHT]->(b:Book)
    RETURN p.name AS person, sum(b.price) AS total_spent
    ORDER BY total_spent DESC
''')
print("\nTổng chi tiêu mỗi người:")
for r in result_2b:
    print(f"{r['person']}: {r['total_spent']} VNĐ")



run_query('''
    MERGE (s1:Station {name: "Ga A"})
    MERGE (s2:Station {name: "Ga B"})
    MERGE (s3:Station {name: "Ga C"})
    MERGE (s4:Station {name: "Ga D"})
    MERGE (s1)-[:NEXT {minutes: 5}]->(s2)
    MERGE (s2)-[:NEXT {minutes: 3}]->(s3)
    MERGE (s3)-[:NEXT {minutes: 4}]->(s4)
    MERGE (s1)-[:NEXT {minutes: 15}]->(s4)
''')

result_3 = run_query('''
    MATCH (start:Station {name: "Ga A"}), (end:Station {name: "Ga D"})
    MATCH path = shortestPath((start)-[:NEXT*]-(end))
    RETURN [n IN nodes(path) | n.name] AS route, length(path) AS stops
''')
print("Tuyến đi qua ít ga nhất từ Ga A đến Ga D:")
for r in result_3:
    print(f"Lộ trình: {' -> '.join(r['route'])} (Số chặng: {r['stops']})")

driver.close()