"""Tests for BuildHandlersMixin static helpers: _open_in_file_manager, _open_in_terminal."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from app.handlers.build_handlers import BuildHandlersMixin


class TestOpenInFileManager:
    """Tests for BuildHandlersMixin._open_in_file_manager."""

    def test_macos_uses_open(self, tmp_path):
        with patch("sys.platform", "darwin"), patch(
            "subprocess.Popen"
        ) as mock_popen:
            BuildHandlersMixin._open_in_file_manager(tmp_path)
        mock_popen.assert_called_once_with(["open", str(tmp_path)])

    def test_windows_uses_explorer(self, tmp_path):
        with patch("sys.platform", "win32"), patch(
            "subprocess.Popen"
        ) as mock_popen:
            BuildHandlersMixin._open_in_file_manager(tmp_path)
        mock_popen.assert_called_once_with(["explorer", str(tmp_path)])

    def test_linux_uses_xdg_open(self, tmp_path):
        with patch("sys.platform", "linux"), patch(
            "subprocess.Popen"
        ) as mock_popen:
            BuildHandlersMixin._open_in_file_manager(tmp_path)
        mock_popen.assert_called_once_with(["xdg-open", str(tmp_path)])


class TestOpenInTerminal:
    """Tests for BuildHandlersMixin._open_in_terminal."""

    def test_macos_uses_open_terminal(self, tmp_path):
        with patch("sys.platform", "darwin"), patch(
            "subprocess.Popen"
        ) as mock_popen:
            BuildHandlersMixin._open_in_terminal(tmp_path)
        mock_popen.assert_called_once_with(
            ["open", "-a", "Terminal", str(tmp_path)]
        )

    def test_windows_uses_cmd(self, tmp_path):
        with patch("sys.platform", "win32"), patch(
            "subprocess.Popen"
        ) as mock_popen, patch.object(
            subprocess, "CREATE_NEW_CONSOLE", 16, create=True
        ):
            BuildHandlersMixin._open_in_terminal(tmp_path)
        call_kwargs = mock_popen.call_args
        assert call_kwargs[0][0] == ["cmd"]
        assert call_kwargs[1]["cwd"] == str(tmp_path)

    def test_linux_tries_gnome_terminal_first(self, tmp_path):
        with patch("sys.platform", "linux"), patch(
            "subprocess.Popen"
        ) as mock_popen:
            BuildHandlersMixin._open_in_terminal(tmp_path)
        # First call should be gnome-terminal
        first_call_cmd = mock_popen.call_args_list[0][0][0]
        assert first_call_cmd[0] == "gnome-terminal"

    def test_linux_falls_through_to_next_terminal_on_not_found(self, tmp_path):
        call_count = [0]

        def popen_side_effect(cmd, **kwargs):
            call_count[0] += 1
            if cmd[0] == "gnome-terminal":
                raise FileNotFoundError
            return Mock()

        with patch("sys.platform", "linux"), patch(
            "subprocess.Popen", side_effect=popen_side_effect
        ):
            BuildHandlersMixin._open_in_terminal(tmp_path)

        # gnome-terminal failed, konsole succeeded
        assert call_count[0] == 2

    def test_linux_tries_all_terminals_silently_if_none_found(self, tmp_path):
        """If all terminals raise FileNotFoundError, no exception is propagated."""
        with patch("sys.platform", "linux"), patch(
            "subprocess.Popen", side_effect=FileNotFoundError
        ):
            BuildHandlersMixin._open_in_terminal(tmp_path)  # should not raise
