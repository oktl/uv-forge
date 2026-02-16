# PyPI Name Availability Checker — Implementation Plan

**Feature:** A small button next to the project name field that checks whether the name is available on PyPI.

**Design principle:** Manual trigger (button click), not automatic. Keeps the app offline-first — the network call only happens when the user explicitly asks for it.

---

## 1. Add `httpx` Dependency

```bash
uv add httpx
```

**Why httpx over requests:** Native async support (`httpx.AsyncClient`) — fits directly into the existing `wrap_async()` / async handler pattern without needing `AsyncExecutor.run()` to offload a blocking call.

---

## 2. New Module: `app/core/pypi_checker.py`

Small, focused module — one public function:

```python
"""Check project name availability on PyPI."""

import httpx

# PyPI normalizes names: lowercase, hyphens/underscores/dots all become hyphens
# e.g. "My_App" and "my-app" are the same package
def normalize_pypi_name(name: str) -> str:
    """Normalize a name per PEP 503 (PyPI simple repository spec)."""
    import re
    return re.sub(r"[-_.]+", "-", name).lower()


async def check_pypi_availability(name: str, timeout: float = 5.0) -> bool | None:
    """Check if a package name is available on PyPI.

    Args:
        name: The project name to check.
        timeout: Request timeout in seconds.

    Returns:
        True  — name is available (404 from PyPI)
        False — name is taken (200 from PyPI)
        None  — check failed (network error, timeout, unexpected status)
    """
    normalized = normalize_pypi_name(name)
    url = f"https://pypi.org/pypi/{normalized}/json"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout, follow_redirects=True)

        if response.status_code == 404:
            return True   # Available
        if response.status_code == 200:
            return False  # Taken
        return None       # Unexpected status
    except (httpx.HTTPError, httpx.TimeoutException):
        return None       # Network problem
```

**Key decisions:**
- Uses PEP 503 normalization so `my_app` and `my-app` are correctly treated as the same name
- Returns a tri-state (`True`/`False`/`None`) so the UI can show "available", "taken", or "check failed"
- 5-second timeout — generous but won't hang the UI
- No caching needed (manual trigger, user won't spam it)

---

## 3. UI Changes: `app/ui/components.py`

Add a new control to the `Controls` class and place it in a `Row` with the project name input.

### 3a. New control on the Controls class (~line 55 area)

```python
controls.check_pypi_button = ft.IconButton(
    icon=ft.Icons.TRAVEL_EXPLORE,
    tooltip="Check name availability on PyPI",
    disabled=True,  # Enabled only when name is valid
    icon_size=20,
)

controls.pypi_status_text = ft.Text(
    value="",
    size=UIConfig.TEXT_SIZE_SMALL,
    italic=True,
)
```

### 3b. Layout change (~line 379-383)

Replace the bare `controls.project_name_input` with a `Row`:

```python
# Before:
controls.project_name_label,
controls.project_name_input,

# After:
controls.project_name_label,
ft.Row(
    controls=[
        controls.project_name_input,
        controls.check_pypi_button,
    ],
    vertical_alignment=ft.CrossAxisAlignment.CENTER,
),
controls.pypi_status_text,
```

The `pypi_status_text` sits below the row and shows the result (e.g., "✓ Available on PyPI" / "✗ Name taken on PyPI" / "⚠ Could not reach PyPI").

### 3c. Visual states for `pypi_status_text`

| State | Text | Color |
|-------|------|-------|
| Available | `"✓ 'name' is available on PyPI"` | `UIConfig.COLOR_SUCCESS` (green) |
| Taken | `"✗ 'name' is taken on PyPI"` | `UIConfig.COLOR_ERROR` (red) |
| Error | `"⚠ Could not check PyPI (offline?)"` | `UIConfig.COLOR_WARNING` (orange) |
| Checking | `"Checking PyPI..."` | `UIConfig.COLOR_INFO` (blue) |
| Idle | `""` (empty) | — |

---

## 4. Handler: `app/handlers/input_handlers.py`

### 4a. New async handler method on `InputHandlersMixin`

```python
async def on_check_pypi(self, e: ft.ControlEvent) -> None:
    """Check PyPI availability for the current project name."""
    name = self.state.project_name
    if not name or not self.state.name_valid:
        return

    # Show "checking" state
    self.controls.pypi_status_text.value = "Checking PyPI..."
    self.controls.pypi_status_text.color = UIConfig.COLOR_INFO
    self.controls.check_pypi_button.disabled = True
    await self.page.update_async()

    result = await check_pypi_availability(name)

    normalized = normalize_pypi_name(name)
    if result is True:
        self.controls.pypi_status_text.value = f"✓ '{normalized}' is available on PyPI"
        self.controls.pypi_status_text.color = UIConfig.COLOR_SUCCESS
    elif result is False:
        self.controls.pypi_status_text.value = f"✗ '{normalized}' is taken on PyPI"
        self.controls.pypi_status_text.color = UIConfig.COLOR_ERROR
    else:
        self.controls.pypi_status_text.value = "⚠ Could not check PyPI (offline?)"
        self.controls.pypi_status_text.color = UIConfig.COLOR_WARNING

    self.controls.check_pypi_button.disabled = False
    await self.page.update_async()
```

### 4b. Enable/disable the button based on name validity

In the existing `on_project_name_change` handler, after updating `self.state.name_valid`:

```python
# Clear previous PyPI status when name changes
self.controls.pypi_status_text.value = ""
# Enable check button only when name is valid
self.controls.check_pypi_button.disabled = not self.state.name_valid
```

This ensures:
- Button is disabled until the name passes local validation
- Previous PyPI result clears when the user types a new name (prevents stale info)

---

## 5. Wiring: `app/handlers/ui_handler.py`

In `attach_handlers()`, add the event binding:

```python
controls.check_pypi_button.on_click = wrap_async(handlers.on_check_pypi)
```

---

## 6. Reset Handling: `app/handlers/build_handlers.py`

In the existing `on_reset` handler, clear the PyPI status:

```python
self.controls.pypi_status_text.value = ""
self.controls.check_pypi_button.disabled = True
```

---

## 7. Tests: `tests/core/test_pypi_checker.py`

```python
"""Tests for PyPI name availability checker."""

import pytest
import httpx

from app.core.pypi_checker import check_pypi_availability, normalize_pypi_name


class TestNormalizePypiName:
    def test_lowercase(self):
        assert normalize_pypi_name("MyApp") == "myapp"

    def test_underscores_to_hyphens(self):
        assert normalize_pypi_name("my_cool_app") == "my-cool-app"

    def test_dots_to_hyphens(self):
        assert normalize_pypi_name("my.app") == "my-app"

    def test_consecutive_separators(self):
        assert normalize_pypi_name("my__app") == "my-app"

    def test_mixed_separators(self):
        assert normalize_pypi_name("My_Cool.App") == "my-cool-app"


class TestCheckPypiAvailability:
    @pytest.mark.asyncio
    async def test_available_returns_true(self, monkeypatch):
        """404 from PyPI means name is available."""
        mock_response = httpx.Response(404, request=httpx.Request("GET", "https://pypi.org"))

        async def mock_get(self, url, **kwargs):
            return mock_response

        monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
        result = await check_pypi_availability("nonexistent-package-xyz")
        assert result is True

    @pytest.mark.asyncio
    async def test_taken_returns_false(self, monkeypatch):
        """200 from PyPI means name is taken."""
        mock_response = httpx.Response(200, request=httpx.Request("GET", "https://pypi.org"))

        async def mock_get(self, url, **kwargs):
            return mock_response

        monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
        result = await check_pypi_availability("requests")
        assert result is False

    @pytest.mark.asyncio
    async def test_network_error_returns_none(self, monkeypatch):
        """Network errors return None."""
        async def mock_get(self, url, **kwargs):
            raise httpx.ConnectError("No internet")

        monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
        result = await check_pypi_availability("anything")
        assert result is None

    @pytest.mark.asyncio
    async def test_timeout_returns_none(self, monkeypatch):
        """Timeouts return None."""
        async def mock_get(self, url, **kwargs):
            raise httpx.TimeoutException("Timed out")

        monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
        result = await check_pypi_availability("anything")
        assert result is None

    @pytest.mark.asyncio
    async def test_unexpected_status_returns_none(self, monkeypatch):
        """Non-200/404 status returns None."""
        mock_response = httpx.Response(500, request=httpx.Request("GET", "https://pypi.org"))

        async def mock_get(self, url, **kwargs):
            return mock_response

        monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
        result = await check_pypi_availability("anything")
        assert result is None

    @pytest.mark.asyncio
    async def test_normalizes_name_before_check(self, monkeypatch):
        """Should normalize the name (PEP 503) before querying."""
        captured_urls = []

        async def mock_get(self, url, **kwargs):
            captured_urls.append(str(url))
            return httpx.Response(404, request=httpx.Request("GET", url))

        monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
        await check_pypi_availability("My_Cool_App")
        assert "my-cool-app" in captured_urls[0]
```

---

## 8. Files Changed Summary

| File | Change |
|------|--------|
| `pyproject.toml` | Add `httpx` to dependencies |
| `app/core/pypi_checker.py` | **New** — `normalize_pypi_name()`, `check_pypi_availability()` |
| `app/ui/components.py` | Add `check_pypi_button` + `pypi_status_text` controls, update layout |
| `app/handlers/input_handlers.py` | Add `on_check_pypi()` handler, update `on_project_name_change()` to enable/disable button and clear status |
| `app/handlers/ui_handler.py` | Wire `check_pypi_button.on_click` |
| `app/handlers/build_handlers.py` | Clear PyPI status on reset |
| `tests/core/test_pypi_checker.py` | **New** — tests for normalization and availability check |

---

## 9. Future Enhancements (Not in Scope)

- **GitHub check** — could add a second button/status, but GitHub search is noisy and less definitive
- **Auto-check on focus loss** — could fire automatically when the user tabs out of the name field
- **Cache results** — not needed for manual trigger, but would help if we switch to auto-check
- **Show package details** — if taken, could show a link to the existing PyPI package
