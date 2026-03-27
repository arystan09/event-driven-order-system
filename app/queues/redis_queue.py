import asyncio
from typing import Optional

from redis.asyncio import Redis

from app.core.config import settings

_redis: Optional[Redis] = None
_lock = asyncio.Lock()


async def get_redis() -> Redis:
    global _redis
    if _redis is not None:
        return _redis

    async with _lock:
        if _redis is not None:
            return _redis

        _redis = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )
        return _redis


async def close_redis() -> None:
    global _redis
    if _redis is None:
        return

    await _redis.close()
    _redis = None


async def enqueue_order_id(order_id: int) -> None:
    redis = await get_redis()
    await redis.rpush(settings.redis_order_queue, str(order_id))


async def dequeue_order_id(*, timeout_seconds: int = 5) -> int | None:
    redis = await get_redis()
    item = await redis.blpop(settings.redis_order_queue, timeout=timeout_seconds)
    if item is None:
        return None

    _, value = item
    try:
        return int(value)
    except ValueError:
        return None
