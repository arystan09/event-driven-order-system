from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order, OrderStatus


async def create_order(
    session: AsyncSession,
    *,
    user_id: str,
    amount: Decimal,
) -> Order:
    order = Order(
        user_id=user_id,
        amount=amount,
        status=OrderStatus.pending,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order
