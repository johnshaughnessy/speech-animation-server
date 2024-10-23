import asyncio
from speech.utils.log import log


def log_task_error(task):
    try:
        result = task.result()
        exc = task.exception()
        if exc:
            log.error("Task error:", str(exc))
            # If you want the full traceback:
            # import traceback
            # log.error("Traceback:", "".join(traceback.format_tb(exc.__traceback__)))
    except asyncio.CancelledError:
        log.warn("Task was cancelled")
    except Exception as e:
        log.error("Task error:", str(e))


def create_task(arg):
    task = asyncio.create_task(arg)
    task.add_done_callback(log_task_error)
    return task
