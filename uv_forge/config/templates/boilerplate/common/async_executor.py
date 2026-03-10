"""Async executor for running blocking operations off the UI thread."""

import asyncio
from concurrent.futures import ThreadPoolExecutor


class AsyncExecutor:
    """Runs blocking functions in a thread pool to keep the UI responsive."""

    _executor = ThreadPoolExecutor(max_workers=4)

    @classmethod
    async def run(cls, func, *args, **kwargs):
        """Execute a blocking function in the thread pool.

        Args:
            func: The blocking callable to run.
            *args: Positional arguments for func.
            **kwargs: Keyword arguments for func.

        Returns:
            The return value of func.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(cls._executor, lambda: func(*args, **kwargs))
