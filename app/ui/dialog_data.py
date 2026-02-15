"""Dialog display data and UI label constants.

This module holds presentation metadata used by dialogs and UI handlers:
category structures with icons, colors, and descriptions for framework
and project type selection dialogs, plus checkbox label strings.
"""

# Checkbox label constants
UI_PROJECT_CHECKBOX_LABEL = "Create UI Project"
OTHER_PROJECT_CHECKBOX_LABEL = "Create Other Project Type"

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

# UI Framework categories for dialog display
# Structure: {category_name: {icon, light_color, dark_color, items: [(label, value, description)]}}
UI_FRAMEWORK_CATEGORIES = {
    "Desktop GUI": {
        "icon": "🖥️",
        "light_color": "GREEN_50",
        "dark_color": "GREEN_900",
        "items": [
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
        ],
    },
    "Web & Data": {
        "icon": "🌐",
        "light_color": "BLUE_50",
        "dark_color": "BLUE_900",
        "items": [
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
        ],
    },
    "Game & Multimedia": {
        "icon": "🎮",
        "light_color": "ORANGE_50",
        "dark_color": "ORANGE_900",
        "items": [
            (
                "Pygame",
                "pygame",
                "Library for making games and multimedia applications",
            ),
        ],
    },
}
