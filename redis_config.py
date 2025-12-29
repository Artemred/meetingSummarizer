from redis import asyncio
from config import settings

pool = asyncio.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)


async def get_redis_connection():
    return await asyncio.Redis(connection_pool=pool)
