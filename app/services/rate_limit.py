from fastapi import HTTPException

from app.core.config import settings
from app.queues.redis_queue import get_redis


def _rate_limit_key(user_id: str) -> str:
    return f"rl:user:{user_id}"


async def enforce_user_rate_limit(user_id: str) -> None:
    redis = await get_redis()
    key = _rate_limit_key(user_id)

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, settings.rate_limit_window_seconds)

    if count <= settings.rate_limit_max_requests:
        return

    ttl = await redis.ttl(key)
    retry_after = ttl if isinstance(ttl, int) and ttl > 0 else settings.rate_limit_window_seconds
    raise HTTPException(
        status_code=429,
        detail="Rate limit exceeded",
        headers={"Retry-After": str(retry_after)},
    )

