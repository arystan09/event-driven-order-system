import asyncio

from app.db.session import SessionLocal
from app.models import OrderStatus
from app.queues.redis_queue import close_redis, dequeue_order_id
from app.repositories.orders import get_order_by_id, update_order_status


async def process_order(order_id: int) -> None:
    async with SessionLocal() as session:
        order = await get_order_by_id(session, order_id)
        if order is None:
            return

        try:
            await update_order_status(session, order=order, status=OrderStatus.processing)
            await asyncio.sleep(0.5)
            await update_order_status(session, order=order, status=OrderStatus.done)
        except Exception:
            await update_order_status(session, order=order, status=OrderStatus.failed)


async def run_worker() -> None:
    while True:
        order_id = await dequeue_order_id(timeout_seconds=5)
        if order_id is None:
            continue

        await process_order(order_id)


if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    finally:
        try:
            asyncio.run(close_redis())
        except RuntimeError:
            pass
