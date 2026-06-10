import time
import asyncio
import functools
import logging

logger = logging.getLogger("retry_utility")

def with_retry(max_attempts=3, backoff_factor=2.0, exceptions=None):
    if exceptions is None:
        from requests.exceptions import RequestException
        exceptions = (RequestException, IOError, TimeoutError)
    else:
        exceptions = tuple(exceptions)

    def decorator(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            attempt = 0
            delay = 1.0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"Failed {func.__name__} after {max_attempts} attempts. Error: {e}")
                        raise
                    logger.warning(f"Error in {func.__name__}: {e}. Retrying in {delay}s... (Attempt {attempt}/{max_attempts})")
                    time.sleep(delay)
                    delay *= backoff_factor

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempt = 0
            delay = 1.0
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"Failed {func.__name__} after {max_attempts} attempts. Error: {e}")
                        raise
                    logger.warning(f"Error in {func.__name__}: {e}. Retrying in {delay}s... (Attempt {attempt}/{max_attempts})")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
