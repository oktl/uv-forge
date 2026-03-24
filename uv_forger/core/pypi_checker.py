"""Check project name availability on PyPI."""

import re

import httpx


def normalize_pypi_name(name: str) -> str:
    """Normalize a name per PEP 503 (PyPI simple repository spec).

    PyPI treats hyphens, underscores, and dots as equivalent, and
    names are case-insensitive.

    Args:
        name: The package name to normalize.

    Returns:
        Lowercased name with all separators replaced by hyphens.
    """
    return re.sub(r"[-_.]+", "-", name).lower()


def extract_package_name(package_spec: str) -> str:
    """Extract the bare package name from a versioned spec string.

    Strips version specifiers (>=, ==, !=, ~=, <, >) and extras ([postgres])
    so the name can be looked up on PyPI.

    Args:
        package_spec: Package spec as entered by user, e.g. 'httpx>=0.25'
            or 'django[postgres]'.

    Returns:
        Bare package name suitable for a PyPI lookup.
    """
    match = re.match(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?", package_spec)
    return match.group(0) if match else package_spec


def validate_package_format(package_spec: str) -> str | None:
    """Validate package spec format. Returns error message or None if valid."""
    if " " in package_spec.strip():
        return f"Invalid: '{package_spec}' contains spaces"
    if not re.match(
        r"^[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9]?(\[.*\])?(([><=!~]=?|===?).*)?$",
        package_spec,
    ):
        return f"Invalid format: '{package_spec}'"
    return None


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
