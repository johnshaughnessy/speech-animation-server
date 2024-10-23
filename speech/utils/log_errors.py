# Usage:
#
# @log_errors
# async def my_async_function():
#    raise Exception("This will be logged")
#
# @log_errors
# def my_sync_function():
#   raise Exception("This will be logged")
#
# The reason we want this decorator is because by default, exceptions in async functions are swallowed by the event loop.


from functools import wraps
import traceback
import asyncio
from speech.utils.log import log


def log_errors(f):
    @wraps(f)
    def sync_wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            log.error(f"Error in {f.__name__}:", str(e))
            log.error("Traceback:", "".join(traceback.format_tb(e.__traceback__)))
            raise e

    @wraps(f)
    async def async_wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except Exception as e:
            log.error(f"Error in {f.__name__}:", str(e))
            log.error("Traceback:", "".join(traceback.format_tb(e.__traceback__)))
            raise e

    if asyncio.iscoroutinefunction(f):
        return async_wrapper
    return sync_wrapper
