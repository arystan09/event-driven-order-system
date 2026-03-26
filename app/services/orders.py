from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.orders import create_order as create_order_repo
from app.models import Order
from app.queues.redis_queue import enqueue_order_id


async def create_order(
    session: AsyncSession,
    *,
    user_id: str,
    amount: Decimal,
) -> Order:
    order = await create_order_repo(session, user_id=user_id, amount=amount)
    await enqueue_order_id(order.id)
    return order
