import asyncio

from app.db.session import SessionLocal
from app.models import OrderStatus
from app.queues.redis_queue import (
    clear_attempt,
    close_redis,
    dequeue_order_id,
    enqueue_dead_letter,
    enqueue_order_id,
    increment_attempt,
)
from app.repositories.orders import (
    get_order_by_id,
    try_mark_order_processing,
    update_order_status,
)


async def process_order(order_id: int) -> bool:
    async with SessionLocal() as session:
        order = await get_order_by_id(session, order_id)
        if order is None:
            await clear_attempt(order_id)
            return True

        if order.status == OrderStatus.done:
            await clear_attempt(order_id)
            return True

        try:
            claimed = await try_mark_order_processing(session, order_id)
            if not claimed:
                return True

            await asyncio.sleep(0.5)
            await update_order_status(session, order=order, status=OrderStatus.done)
            await clear_attempt(order_id)
            return True
        except Exception:
            await update_order_status(session, order=order, status=OrderStatus.failed)
            return False


async def run_worker() -> None:
    max_attempts = 3
    while True:
        order_id = await dequeue_order_id(timeout_seconds=5)
        if order_id is None:
            continue

        ok = await process_order(order_id)
        if ok:
            continue

        attempt = await increment_attempt(order_id)
        if attempt < max_attempts:
            await enqueue_order_id(order_id)
            continue

        await enqueue_dead_letter(order_id)
        await clear_attempt(order_id)


if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    finally:
        try:
            asyncio.run(close_redis())
        except RuntimeError:
            pass
