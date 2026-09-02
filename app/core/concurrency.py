import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# Dedicated shared thread pool executor for CPU-bound or blocking synchronous tasks
thread_pool = ThreadPoolExecutor(
    max_workers=settings.THREAD_POOL_WORKERS,
    thread_name_prefix="newform_worker",
)


async def run_in_threadpool[R](func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
    """Run a synchronous blocking or CPU-bound function in the dedicated thread pool."""
    loop = asyncio.get_running_loop()
    if kwargs:
        return await loop.run_in_executor(thread_pool, lambda: func(*args, **kwargs))
    return await loop.run_in_executor(thread_pool, func, *args)


def shutdown_threadpool() -> None:
    """Shutdown the thread pool executor gracefully."""
    logger.info("Shutting down ThreadPoolExecutor...")
    thread_pool.shutdown(wait=False)
