from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.orders import create_order as create_order_repo
from app.models import Order


async def create_order(
    session: AsyncSession,
    *,
    user_id: str,
    amount: Decimal,
) -> Order:
    return await create_order_repo(session, user_id=user_id, amount=amount)
