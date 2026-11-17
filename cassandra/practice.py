from cassandra.cluster import Cluster
from datetime import datetime

cluster = Cluster(["127.0.0.1"])
session = cluster.connect()

session.execute('''
    CREATE KEYSPACE IF NOT EXISTS practice
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
''')
session.set_keyspace('practice')

session.execute('''
    CREATE TABLE IF NOT EXISTS customer_orders (
        customer_id text,
        order_ts timestamp,
        order_id text,
        total double,
        PRIMARY KEY ((customer_id), order_ts)
    ) WITH CLUSTERING ORDER BY (order_ts DESC)
''')

session.execute('''
    CREATE TABLE IF NOT EXISTS orders_by_day (
        order_date date,
        order_ts timestamp,
        order_id text,
        total double,
        PRIMARY KEY ((order_date), order_ts)
    ) WITH CLUSTERING ORDER BY (order_ts DESC)
''')

session.execute('''
    CREATE TABLE IF NOT EXISTS sensor_readings_monthly (
        sensor_id text,
        month text,
        ts timestamp,
        temperature double,
        PRIMARY KEY ((sensor_id, month), ts)
    ) WITH CLUSTERING ORDER BY (ts DESC)
''')

try:
    session.execute("SELECT * FROM iot.readings_by_sensor WHERE temperature > 30")
except Exception as e:
    print(type(e).__name__, e)

cluster.shutdown()