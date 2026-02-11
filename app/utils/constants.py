"""Application constants and default values.

This module centralizes all constant values used throughout the application,
including Python version options, UI frameworks, and default paths.
"""

from pathlib import Path

# Python versions supported by the application
PYTHON_VERSIONS = ["3.14", "3.13", "3.12", "3.11", "3.10", "3.9"]
DEFAULT_PYTHON_VERSION = "3.14"

# UI frameworks available for project creation
UI_FRAMEWORKS = [
    "flet",
    "PyQt6",
    "PySide6",
    "tkinter (built-in)",
    "customtkinter",
    "kivy",
    "pygame",
    "nicegui",
    "streamlit",
    "gradio",
]
DEFAULT_FRAMEWORK = "flet"

# Framework package name mappings (for uv add)
FRAMEWORK_PACKAGE_MAP = {
    "flet": "flet",
    "PyQt6": "pyqt6",
    "PySide6": "pyside6",
    "customtkinter": "customtkinter",
    "kivy": "kivy",
    "pygame": "pygame",
    "nicegui": "nicegui",
    "streamlit": "streamlit",
    "gradio": "gradio",
    "tkinter (built-in)": None,  # Built-in, no installation needed
}

# Project type package mappings (for uv add)
# Maps project type to list of required packages
PROJECT_TYPE_PACKAGE_MAP = {
    # Web Frameworks
    "django": ["django"],
    "fastapi": ["fastapi", "uvicorn"],
    "flask": ["flask"],
    "bottle": ["bottle"],
    # Data Science & ML
    "data_analysis": ["pandas", "numpy", "matplotlib", "jupyter"],
    "ml_sklearn": ["scikit-learn", "pandas", "numpy", "matplotlib"],
    "dl_pytorch": ["torch", "torchvision", "numpy"],
    "dl_tensorflow": ["tensorflow", "numpy"],
    "computer_vision": ["opencv-python", "numpy", "pillow"],
    # CLI Tools
    "cli_click": ["click"],
    "cli_typer": ["typer[all]"],
    "cli_rich": ["rich"],
    # API Development
    "api_fastapi": ["fastapi", "uvicorn", "pydantic"],
    "api_graphql": ["strawberry-graphql[fastapi]"],
    "api_grpc": ["grpcio", "grpcio-tools", "protobuf"],
    # Automation & Scraping
    "browser_automation": ["playwright"],
    "task_scheduler": ["apscheduler"],
    "scraping": ["beautifulsoup4", "httpx", "lxml"],
    # Other
    "basic_package": [],  # No packages needed
    "testing": ["pytest", "pytest-cov", "pytest-mock"],
    "async_app": ["aiohttp", "aiofiles"],
}

# Framework entry point mappings (None = no [project.scripts] section)
FRAMEWORK_ENTRY_POINT_MAP = {
    "flet": "app.main:run",
    "PyQt6": "app.main:run",
    "PySide6": "app.main:run",
    "tkinter (built-in)": "app.main:run",
    "customtkinter": "app.main:run",
    "kivy": "app.main:run",
    "pygame": "app.main:run",
    "nicegui": "app.main:run",
    "streamlit": None,  # Uses `streamlit run`
    "gradio": None,  # Uses `gradio` or `python` directly
}

# Project type entry point mappings (None = no [project.scripts] section)
PROJECT_TYPE_ENTRY_POINT_MAP = {
    # Web frameworks — have their own runners
    "django": None,
    "fastapi": None,
    "flask": None,
    "bottle": None,
    # API types — have their own runners
    "api_fastapi": None,
    "api_graphql": None,
    "api_grpc": None,
    # CLI tools — specific entry points
    "cli_click": "app.main:cli",
    "cli_typer": "app.main:app",
    "cli_rich": "app.main:main",
    # Everything else → standard main
    "data_analysis": "app.main:main",
    "ml_sklearn": "app.main:main",
    "dl_pytorch": "app.main:main",
    "dl_tensorflow": "app.main:main",
    "computer_vision": "app.main:main",
    "browser_automation": "app.main:main",
    "task_scheduler": "app.main:main",
    "scraping": "app.main:main",
    "basic_package": "app.main:main",
    "testing": "app.main:main",
    "async_app": "app.main:main",
}

# Default entry point when no framework or project type is selected
DEFAULT_ENTRY_POINT = "app.main:main"

# Configuration paths
PROJECT_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = Path(__file__).parent.parent / "config" / "templates"
UI_TEMPLATES_DIR = TEMPLATES_DIR / "ui_frameworks"
PROJECT_TYPE_TEMPLATES_DIR = TEMPLATES_DIR / "project_types"
BOILERPLATE_DIR = TEMPLATES_DIR / "boilerplate"
DOCS_DIR = Path(__file__).parent.parent / "assets" / "docs"
HELP_FILE = DOCS_DIR / "HELP.md"
GIT_CHEAT_SHEET_FILE = DOCS_DIR / "Git-Cheat-Sheet.md"

# Default paths
DEFAULT_PROJECT_ROOT = str(Path.home() / "Projects")
DEFAULT_GIT_HUB_ROOT = Path.home() / "Projects" / "git-repos"

# Default folder structure (used as final fallback)
DEFAULT_FOLDERS = ["core", "ui", "utils", "assets"]

# ============================================================================
# Dialog Data Structures
# ============================================================================

# Project type categories with metadata for dialog display
# Structure: {category_name: {icon, light_color, dark_color, items: [(label, value, description)]}}
PROJECT_TYPE_CATEGORIES = {
    "Web Frameworks": {
        "icon": "🌐",
        "light_color": "BLUE_50",
        "dark_color": "BLUE_900",
        "items": [
            (
                "Django",
                "django",
                "Full-stack web framework with ORM, admin panel, authentication, and batteries included",
            ),
            (
                "FastAPI",
                "fastapi",
                "Modern, fast async API framework with automatic OpenAPI documentation",
            ),
            (
                "Flask",
                "flask",
                "Lightweight, flexible web framework perfect for small to medium projects",
            ),
            (
                "Bottle",
                "bottle",
                "Minimalist single-file micro-framework with no dependencies",
            ),
        ],
    },
    "Data Science & ML": {
        "icon": "🤖",
        "light_color": "PURPLE_50",
        "dark_color": "PURPLE_900",
        "items": [
            (
                "Data Analysis",
                "data_analysis",
                "Complete data analysis stack with pandas, numpy, matplotlib, and Jupyter notebooks",
            ),
            (
                "Machine Learning",
                "ml_sklearn",
                "Scikit-learn based ML project with data preprocessing and model evaluation tools",
            ),
            (
                "Deep Learning (PyTorch)",
                "dl_pytorch",
                "PyTorch deep learning framework with GPU support and neural network tools",
            ),
            (
                "Deep Learning (TensorFlow)",
                "dl_tensorflow",
                "TensorFlow/Keras framework for building and training neural networks",
            ),
            (
                "Computer Vision",
                "computer_vision",
                "OpenCV-based computer vision with image processing and object detection tools",
            ),
        ],
    },
    "CLI Tools": {
        "icon": "⚙️",
        "light_color": "ORANGE_50",
        "dark_color": "ORANGE_900",
        "items": [
            (
                "Click CLI",
                "cli_click",
                "Powerful command-line interface framework with decorators and argument parsing",
            ),
            (
                "Typer CLI",
                "cli_typer",
                "Modern CLI framework with type hints, auto-completion, and beautiful help pages",
            ),
            (
                "Rich CLI",
                "cli_rich",
                "Create beautiful terminal UIs with tables, progress bars, and rich formatting",
            ),
        ],
    },
    "API Development": {
        "icon": "🔌",
        "light_color": "GREEN_50",
        "dark_color": "GREEN_900",
        "items": [
            (
                "REST API (FastAPI)",
                "api_fastapi",
                "Production-ready REST API with FastAPI, database models, and authentication",
            ),
            (
                "GraphQL API",
                "api_graphql",
                "GraphQL API with Strawberry, type-safe schemas, and resolver patterns",
            ),
            (
                "gRPC Service",
                "api_grpc",
                "High-performance gRPC service with Protocol Buffers and streaming support",
            ),
        ],
    },
    "Automation & Scraping": {
        "icon": "🔄",
        "light_color": "TEAL_50",
        "dark_color": "TEAL_900",
        "items": [
            (
                "Web Scraping",
                "scraping",
                "Web scraping toolkit with BeautifulSoup, requests, and data extraction utilities",
            ),
            (
                "Browser Automation",
                "browser_automation",
                "Playwright-based browser automation for testing and data collection",
            ),
            (
                "Task Scheduler",
                "task_scheduler",
                "APScheduler-based task scheduling with cron-like triggers and job management",
            ),
        ],
    },
    "Other": {
        "icon": "📦",
        "light_color": "GREY_50",
        "dark_color": "GREY_900",
        "items": [
            (
                "Basic Python Package",
                "basic_package",
                "Simple Python package structure with minimal dependencies",
            ),
            (
                "Testing Framework",
                "testing",
                "Comprehensive testing setup with pytest, coverage, and mocking tools",
            ),
            (
                "Async Application",
                "async_app",
                "Asyncio-based application with aiohttp for concurrent operations",
            ),
        ],
    },
}

# UI Framework details for dialog display
# Structure: [(label, value, description)]
UI_FRAMEWORK_DETAILS = [
    (
        "Flet",
        "flet",
        "Modern Flutter-based Python UI framework for cross-platform apps",
    ),
    (
        "PyQt6",
        "PyQt6",
        "Comprehensive Qt6 bindings for Python with rich widget library",
    ),
    (
        "PySide6",
        "PySide6",
        "Official Qt for Python bindings with full Qt6 feature set",
    ),
    (
        "tkinter (built-in)",
        "tkinter (built-in)",
        "Python's built-in GUI toolkit — no installation needed",
    ),
    (
        "customtkinter",
        "customtkinter",
        "Modern-looking extension of tkinter with custom widgets",
    ),
    (
        "Kivy",
        "kivy",
        "Cross-platform NUI framework for multi-touch applications",
    ),
    (
        "Pygame",
        "pygame",
        "Library for making games and multimedia applications",
    ),
    (
        "NiceGUI",
        "nicegui",
        "Easy-to-use web-based UI framework with Python",
    ),
    (
        "Streamlit",
        "streamlit",
        "Rapid prototyping framework for data apps and dashboards",
    ),
    (
        "Gradio",
        "gradio",
        "Build ML demos and web interfaces with minimal code",
    ),
]
