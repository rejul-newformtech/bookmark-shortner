import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# Lazy‑initialized shared thread pool executor for CPU‑bound or blocking sync tasks
_thread_pool: ThreadPoolExecutor | None = None


def get_thread_pool() -> ThreadPoolExecutor:
    """Return a live ThreadPoolExecutor, creating one if needed.

    The executor may have been shut down by ``shutdown_threadpool``; in that case a
    fresh instance is created so that subsequent ``run_in_threadpool`` calls keep
    working, even after the FastAPI lifespan cycle ends (e.g., during repeated
    test clients).
    """
    global _thread_pool
    if _thread_pool is None or getattr(_thread_pool, "_shutdown", False):
        _thread_pool = ThreadPoolExecutor(
            max_workers=settings.THREAD_POOL_WORKERS,
            thread_name_prefix="newform_worker",
        )
    return _thread_pool


async def run_in_threadpool[R](func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
    """Run a synchronous blocking or CPU‑bound function in the dedicated thread pool.

    The function is dispatched via ``loop.run_in_executor`` using the lazily
    created ``_thread_pool``. Keyword arguments are wrapped in a ``lambda`` to keep
    the signature compatible with ``run_in_executor``.
    """
    loop = asyncio.get_running_loop()
    pool = get_thread_pool()
    if kwargs:
        return await loop.run_in_executor(pool, lambda: func(*args, **kwargs))
    return await loop.run_in_executor(pool, func, *args)


def shutdown_threadpool() -> None:
    """Gracefully shut down the thread pool and clear the cached reference.

    ``ThreadPoolExecutor.shutdown`` marks the executor as unusable. By resetting
    ``_thread_pool`` to ``None`` we allow ``get_thread_pool`` to lazily recreate a
    fresh executor when needed.
    """
    global _thread_pool
    if _thread_pool is not None:
        logger.info("Shutting down ThreadPoolExecutor…")
        _thread_pool.shutdown(wait=False)
        _thread_pool = None
