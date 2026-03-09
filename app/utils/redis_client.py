import redis
import os

redis_client = redis.Redis(
    host = os.getenv("REDIS_HOST"),
    port = int(os.getenv("REDIS_PORT")),
    db = 0,
    decode_responses= True
)