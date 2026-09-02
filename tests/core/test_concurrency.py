import asyncio
import time

import pytest

from app.core.concurrency import run_in_threadpool


def synchronous_task(val: int) -> int:
    time.sleep(0.01)
    return val * 2


class TestConcurrency:
    """Test cases for thread pool execution."""

    @pytest.mark.asyncio
    async def test_run_in_threadpool_execution(self):
        """Test running a synchronous function in threadpool."""
        result = await run_in_threadpool(synchronous_task, 21)
        assert result == 42

    @pytest.mark.asyncio
    async def test_run_in_threadpool_parallel(self):
        """Test running multiple synchronous tasks concurrently in threadpool."""
        tasks = [run_in_threadpool(synchronous_task, i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        assert results == [i * 2 for i in range(10)]
