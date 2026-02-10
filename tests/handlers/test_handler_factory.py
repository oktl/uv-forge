"""Test suite for handler_factory.py"""

import asyncio
import time
from unittest.mock import MagicMock, patch
import pytest

from app.handlers.handler_factory import HandlerFactory, async_handler


class TestHandlerFactoryClass:
    """Tests for HandlerFactory class methods"""

    def test_create_async_handler_creates_callable(self):
        """Test create_async_handler creates callable handler"""
        async def test_async_func():
            return "test"

        handler = HandlerFactory.create_async_handler(test_async_func)
        assert callable(handler)

    def test_handler_has_correct_name(self):
        """Test handler has descriptive name"""
        async def my_async_function():
            return "result"

        handler = HandlerFactory.create_async_handler(my_async_function)
        assert handler.__name__ == "my_async_function"

    def test_handler_with_args_has_descriptive_name(self):
        """Test handler with args has descriptive name"""
        async def process_data(value):
            return value

        handler = HandlerFactory.create_async_handler(process_data, "test_arg")
        assert "process_data" in handler.__name__
        assert "test_arg" in handler.__name__

    def test_handler_accepts_event_parameter(self):
        """Test handler accepts event parameter"""
        async def sample_handler():
            return "done"

        handler = HandlerFactory.create_async_handler(sample_handler)

        # Mock ControlEvent
        mock_event = MagicMock()

        with patch('asyncio.create_task') as mock_create_task:
            handler(mock_event)
            # Should create a task
            assert mock_create_task.called

    def test_handler_passes_args_to_coroutine(self):
        """Test handler passes arguments to coroutine"""
        call_args = []

        async def capture_args(*args, **kwargs):
            call_args.extend(args)
            for k, v in kwargs.items():
                call_args.append(f"{k}={v}")
            return "captured"

        handler = HandlerFactory.create_async_handler(
            capture_args,
            "arg1", "arg2",
            key1="value1"
        )

        mock_event = MagicMock()

        with patch('asyncio.create_task') as mock_create_task:
            handler(mock_event)

            # Check that create_task was called with a coroutine
            assert mock_create_task.called
            # The coroutine is the first argument
            coro = mock_create_task.call_args[0][0]
            assert asyncio.iscoroutine(coro)
            # Clean up the coroutine
            coro.close()

    def test_create_handler_with_arg_convenience_method(self):
        """Test create_handler_with_arg convenience method"""
        async def single_arg_func(value):
            return value * 2

        handler = HandlerFactory.create_handler_with_arg(single_arg_func, 42)
        assert callable(handler)

    def test_multiple_handlers_are_independent(self):
        """Test multiple handlers are independent"""
        async def func_a():
            return "A"

        async def func_b():
            return "B"

        handler_a = HandlerFactory.create_async_handler(func_a)
        handler_b = HandlerFactory.create_async_handler(func_b)

        assert handler_a.__name__ != handler_b.__name__


class TestAsyncHandlerFunction:
    """Tests for async_handler convenience function"""

    def test_async_handler_creates_callable(self):
        """Test async_handler creates callable"""
        async def test_func():
            return "test"

        handler = async_handler(test_func)
        assert callable(handler)

    def test_async_handler_with_args_and_kwargs(self):
        """Test async_handler with args and kwargs"""
        async def multi_arg_func(a, b, c=None):
            return f"{a}-{b}-{c}"

        handler = async_handler(multi_arg_func, "x", "y", c="z")
        assert callable(handler)

    def test_async_handler_equivalent_to_factory(self):
        """Test async_handler equivalent to HandlerFactory.create_async_handler"""
        async def comparison_func():
            return "same"

        handler1 = async_handler(comparison_func)
        handler2 = HandlerFactory.create_async_handler(comparison_func)

        assert handler1.__name__ == handler2.__name__


class TestHandlerExecution:
    """Tests for handler execution behavior"""

    def test_handler_creates_task_when_called(self):
        """Test handler creates task on execution"""
        executed = []

        async def track_execution():
            executed.append(True)
            return "executed"

        handler = HandlerFactory.create_async_handler(track_execution)
        mock_event = MagicMock()

        with patch('asyncio.create_task') as mock_create_task:
            handler(mock_event)

            assert mock_create_task.call_count == 1

            # Clean up the coroutine
            coro = mock_create_task.call_args[0][0]
            if asyncio.iscoroutine(coro):
                coro.close()

    def test_handler_returns_immediately(self):
        """Test handler returns immediately (doesn't await)"""
        async def slow_function():
            await asyncio.sleep(10)
            return "slow"

        handler = HandlerFactory.create_async_handler(slow_function)
        mock_event = MagicMock()

        start = time.time()

        with patch('asyncio.create_task') as mock_create_task:
            handler(mock_event)
            elapsed = time.time() - start

            # Clean up
            coro = mock_create_task.call_args[0][0]
            if asyncio.iscoroutine(coro):
                coro.close()

            # Should return almost immediately (not wait 10 seconds)
            assert elapsed < 0.1

    def test_handler_returns_none(self):
        """Test handler returns None (event handlers should)"""
        async def return_value_func():
            return "some value"

        handler = HandlerFactory.create_async_handler(return_value_func)
        mock_event = MagicMock()

        with patch('asyncio.create_task'):
            result = handler(mock_event)
            assert result is None
