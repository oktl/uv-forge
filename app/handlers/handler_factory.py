"""Handler factory for creating event handler wrappers.

This module provides utilities for creating properly wrapped event handlers
that integrate with asyncio, improving debugging and code clarity.
"""

import asyncio
from typing import Any, Awaitable, Callable

import flet as ft


class HandlerFactory:
    """Factory for creating wrapped event handlers.

    Provides methods to wrap async handler functions with proper event
    handling and task creation, eliminating the need for inline lambdas.
    """

    @staticmethod
    def create_async_handler(
        coro_func: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[ft.ControlEvent], None]:
        """Create an event handler that runs an async function as a task.

        This wraps an async function to be used as a Flet event handler,
        creating a task to run the coroutine without blocking.

        Args:
            coro_func: The async function to call
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            An event handler function that creates a task

        Example:
            button.on_click = HandlerFactory.create_async_handler(
                handlers.on_summarize,
                "claude"
            )
        """

        def handler(e: ft.ControlEvent) -> None:
            """Event handler that creates a task for the coroutine."""
            asyncio.create_task(coro_func(*args, **kwargs))

        # Set a descriptive name for better debugging
        func_name = getattr(coro_func, "__name__", "unknown")
        if args:
            args_str = "_".join(str(arg) for arg in args)
            handler.__name__ = f"{func_name}_with_{args_str}"
        else:
            handler.__name__ = func_name

        return handler

    @staticmethod
    def create_handler_with_arg(
        coro_func: Callable[[Any], Awaitable[Any]],
        arg: Any,
    ) -> Callable[[ft.ControlEvent], None]:
        """Create an event handler for an async function with one argument.

        Convenience method for the common case of a handler with a single argument.

        Args:
            coro_func: The async function to call
            arg: The argument to pass to the function

        Returns:
            An event handler function

        Example:
            button.on_click = HandlerFactory.create_handler_with_arg(
                handlers.on_select_word_count,
                100
            )
        """
        return HandlerFactory.create_async_handler(coro_func, arg)


# Convenience function for shorter syntax
def async_handler(
    coro_func: Callable[..., Awaitable[Any]],
    *args: Any,
    **kwargs: Any,
) -> Callable[[ft.ControlEvent], None]:
    """Convenience function to create an async event handler.

    Shorter alternative to HandlerFactory.create_async_handler.

    Args:
        coro_func: The async function to call
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        An event handler function

    Example:
        button.on_click = async_handler(handlers.on_summarize, "claude")
    """
    return HandlerFactory.create_async_handler(coro_func, *args, **kwargs)
