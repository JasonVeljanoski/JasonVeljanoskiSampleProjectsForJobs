import asyncio
import datetime as dt
import json
from enum import Enum, IntEnum, auto

import redis
import sqlalchemy as sql
from broadcaster import Broadcast
from starlette.concurrency import run_until_first_complete

from app import config


class Socket_Group(IntEnum):
    INVESTIGATION = auto()
    ACTION = auto()
    NOTIFICATION = auto()


# ----------------------------------------------------------------------------------------------------------------

if config.DEV_MODE:
    broadcast = Broadcast("memory://")
else:
    broadcast = Broadcast("redis://redis:6379")

data_cache = redis.Redis(host="redis", port=6379, db=1, decode_responses=True)

# ----------------------------------------------------------------------------------------------------------------


async def startup():
    await broadcast.connect()

    data_cache.flushdb()


async def shutdown():
    await broadcast.disconnect()


# ----------------------------------------------------------------------------------------------------------------


async def __socket_receiver__(websocket):
    async for _ in websocket.iter_text():
        pass


async def __socket_sender__(websocket, channel):
    async with broadcast.subscribe(channel=channel) as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)


# ----------------------------------------------------------------------------------------------------------------


async def add_websocket(websocket, user_id):
    await websocket.accept()

    current = int(data_cache.get(user_id) or 0)
    data_cache.set(user_id, current + 1)

    await run_until_first_complete(
        (__socket_receiver__, {"websocket": websocket}),
        (__socket_sender__, {"websocket": websocket, "channel": f"{user_id}"}),
    )

    current = int(data_cache.get(user_id) or 0)
    if current > 1:
        data_cache.set(user_id, current - 1)
    else:
        data_cache.delete(user_id)

    try:
        await websocket.close()
    except:
        pass


# ----------------------------------------------------------------------------------------------------------------


def send(user_id: int, group: Socket_Group, data):
    json_data = json.dumps(data, cls=CustomEncoder)

    wrapped_data = f'{{ "group": "{group.name}", "data": {json_data} }}'
    channel = f"{user_id}"

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(broadcast.publish(channel=channel, message=wrapped_data))
    else:
        asyncio.run(__publish_wrapper__(wrapped_data, channel))


async def __publish_wrapper__(data, channel):
    asyncio.create_task(broadcast.publish(channel=channel, message=data))


# ----------------------------------------------------------------------------------------------------------------


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Enum, Enum)):
            return obj.name
        if isinstance(obj, (Enum, IntEnum)):
            return obj.name
        if isinstance(obj, (dt.date, dt.datetime)):
            return obj.isoformat()
        if isinstance(obj, sql.orm.state.InstanceState):
            return None

        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            return obj.__dict__
