from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

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


async def get_order_by_id(session: AsyncSession, order_id: int) -> Order | None:
    result = await session.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def update_order_status(
    session: AsyncSession,
    *,
    order: Order,
    status: OrderStatus,
) -> Order:
    order.status = status
    await session.commit()
    await session.refresh(order)
    return order


async def try_mark_order_processing(session: AsyncSession, order_id: int) -> bool:
    stmt = (
        update(Order)
        .where(Order.id == order_id)
        .where(Order.status.in_([OrderStatus.pending, OrderStatus.failed]))
        .values(status=OrderStatus.processing)
    )
    result = await session.execute(stmt)
    if result.rowcount and result.rowcount > 0:
        await session.commit()
        return True

    await session.rollback()
    return False
