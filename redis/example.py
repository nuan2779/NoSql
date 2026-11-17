import json
import time
import redis
import uuid
from concurrent.futures import ThreadPoolExecutor


r = redis.Redis(host="localhost", port=6379, decode_responses=True)

print("Xóa dữ liệu cũ...")
r.flushdb()


r.set("user:42:name", "Linh")
print("GET user:42:name ->", r.get("user:42:name"))

r.incr("page:home:views")
print("Sau INCR (1 lần) ->", r.get("page:home:views"))
r.incrby("page:home:views", 10)
print("Sau INCRBY 10 ->", r.get("page:home:views"))

# Thời gian hết hạn (TTL)
r.set("otp:linh", "834512", ex=60)
print("TTL của otp:linh ->", r.ttl("otp:linh"), "giây")






r.hset("user:42", mapping={"name": "Linh", "city": "Hanoi", "age": 21})
print("HGET city ->", r.hget("user:42", "city"))
print("HGETALL ->", r.hgetall("user:42"))

r.lpush("jobs", "resize:img1", "resize:img2")
print("RPOP từ jobs ->", r.rpop("jobs"))


r.sadd("tags:post1", "python", "data", "ai")
r.sadd("tags:post2", "python", "web")
print("SINTER (Giao của 2 set) ->", r.sinter("tags:post1", "tags:post2"))


r.zadd("board", {"linh": 1200, "nam": 950, "mai": 1430})
print("ZREVRANGE (Top 3 từ cao xuống) ->", r.zrevrange("board", 0, 2, withscores=True))
print("ZRANK (Thứ hạng của 'nam' từ dưới lên) ->", r.zrank("board", "nam"))



def slow_query(product_id: int) -> dict:
    time.sleep(1)  # Giả lập truy vấn DB chậm
    return {"id": product_id, "title": "Python Basics", "price": 12.5}

def get_product(product_id: int) -> dict:
    key = f"product:{product_id}"
    cached = r.get(key)
    if cached is not None:
        return json.loads(cached)                   
    product = slow_query(product_id)               
    r.set(key, json.dumps(product), ex=300)         
    return product

start = time.perf_counter()
get_product(7)
print(f"Lần gọi đầu (Cache Miss): {time.perf_counter() - start:.3f}s")

start = time.perf_counter()
get_product(7)
print(f"Lần gọi thứ hai (Cache Hit): {time.perf_counter() - start:.3f}s")




def allow(user: str, limit: int = 5) -> bool:
    key = f"rate:{user}:{int(time.time() // 60)}"   # Một bộ đếm cho mỗi phút
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)
    return count <= limit

print("Gửi 6 request liên tiếp:")
print([allow("test_user") for _ in range(6)])