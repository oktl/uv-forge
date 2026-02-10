"""Async executor utilities.

This module provides utilities for running synchronous (blocking) functions
in a thread pool executor to avoid blocking the async event loop.
"""

import asyncio
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class AsyncExecutor:
    """Manages background task execution in thread pool.

    Provides utilities to run synchronous functions in a thread pool
    executor without blocking the async event loop.
    """

    @staticmethod
    async def run(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Run a synchronous function in a thread pool executor.

        Use this for CPU-bound or blocking I/O operations that would
        otherwise block the async event loop (e.g., API calls, file I/O).

        Args:
            func: The synchronous function to run
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The return value from the function

        Example:
            result = await AsyncExecutor.run(
                some_blocking_function,
                arg1,
                arg2,
                key=value
            )
        """
        loop = asyncio.get_event_loop()

        # If function has kwargs, wrap in lambda
        if kwargs:
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

        # If just args, can pass directly
        if args:
            return await loop.run_in_executor(None, lambda: func(*args))

        # No args, call directly
        return await loop.run_in_executor(None, func)


# Convenience alias for shorter syntax
run_async = AsyncExecutor.run
