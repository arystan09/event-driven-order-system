from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.init import init_db
from app.queues.redis_queue import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.app_env == "development":
        await init_db()
    yield
    await close_redis()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(api_router)
    return app


app = create_app()
