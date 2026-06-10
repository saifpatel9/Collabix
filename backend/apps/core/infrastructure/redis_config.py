from django.conf import settings


def get_redis_url():
    return settings.REDIS_URL


def get_redis_client(db=0, decode_responses=True):
    import redis

    from urllib.parse import urlparse

    parsed = urlparse(settings.REDIS_URL)
    pool = redis.ConnectionPool(
        host=parsed.hostname or "127.0.0.1",
        port=parsed.port or 6379,
        db=parsed.path.lstrip("/") if parsed.path else db,
        password=parsed.password or None,
        decode_responses=decode_responses,
    )
    return redis.Redis(connection_pool=pool)


def get_channel_layer_config():
    return settings.CHANNEL_LAYERS


def get_cache_config():
    return settings.CACHES
