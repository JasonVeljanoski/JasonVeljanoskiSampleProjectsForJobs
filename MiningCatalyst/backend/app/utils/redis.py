import json

import redis


def get_redis(db=2):
    return redis.Redis(host="redis", port=6379, db=db, decode_responses=True)


def append_to_key(redis, key, to_append):
    if redis.exists(key):
        prev = json.loads(redis.get(key))
        prev.append(to_append)
        redis.set(key, json.dumps(prev))
    else:
        redis.set(key, json.dumps([to_append]))
