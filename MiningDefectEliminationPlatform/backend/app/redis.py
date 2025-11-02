import redis


def get_redis(db=2):
    return redis.Redis(host="redis", port=6379, db=db, decode_responses=True)
