import json

import redis


class Redis_Client:
    __redis_handle = redis.Redis(host="redis", port=6379, db=0)

    def get(self, key):
        value = self.__redis_handle.get(key)
        if value != None:
            value = json.loads(value)

        return value

    def get_all(self):
        iterator = self.__redis_handle.scan_iter()
        return {key.decode("utf-8"): self.get(key) for key in iterator}

    def exists(self, key):
        return self.__redis_handle.exists(key)

    def set(self, key, value):
        self.__redis_handle.set(key, json.dumps(value, default=str))

    def init(self, key, value):
        if not self.__redis_handle.get(key):
            self.set(key, value)

    def append(self, key, value):
        arr = self.get(key)
        if arr:
            arr.append(value)
            self.set(key, arr)
        else:
            self.set(key, [value])

    def clear_all(self):
        self.__redis_handle.flushdb()
