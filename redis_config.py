from redis import Redis, ConnectionPool
from config import settings

pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)


def get_redis_connection():
    return Redis(connection_pool=pool)
