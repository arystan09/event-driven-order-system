from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.orders import create_order
from app.services.rate_limit import enforce_user_rate_limit

router = APIRouter()


class OrderCreateRequest(BaseModel):
    user_id: str
    amount: Decimal


class OrderCreateResponse(BaseModel):
    id: int


@router.post("/orders", response_model=OrderCreateResponse)
async def create_order_endpoint(
    payload: OrderCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> OrderCreateResponse:
    await enforce_user_rate_limit(payload.user_id)
    order = await create_order(
        session=session,
        user_id=payload.user_id,
        amount=payload.amount,
    )
    return OrderCreateResponse(id=order.id)

