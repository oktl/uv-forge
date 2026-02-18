"""Check project name availability on PyPI."""

import re

import httpx


def normalize_pypi_name(name: str) -> str:
    """Normalize a name per PEP 503 (PyPI simple repository spec).

    PyPI treats hyphens, underscores, and dots as equivalent, and
    names are case-insensitive. E.g. "My_Cool.App" -> "my-cool-app".
    """
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
            return True
        if response.status_code == 200:
            return False
        return None
    except httpx.HTTPError:
        return None
