# Frameworks & Project Types

## UI Frameworks

UV Forger includes templates for 10 UI frameworks, organized by category.

### Desktop GUI

| Framework         | Package         | Description                                   |
| ----------------- | --------------- | --------------------------------------------- |
| **Flet**          | `flet`          | Cross-platform apps with Flutter, from Python |
| **PyQt6**         | `pyqt6`         | Python bindings for Qt 6                      |
| **PySide6**       | `pyside6`       | Official Qt for Python bindings               |
| **tkinter**       | *(stdlib)*      | Python's built-in GUI toolkit                 |
| **customtkinter** | `customtkinter` | Modern-looking tkinter widgets                |
| **Kivy**          | `kivy`          | Cross-platform NUI framework                  |

### Web & Data

| Framework     | Package     | Description                   |
| ------------- | ----------- | ----------------------------- |
| **NiceGUI**   | `nicegui`   | Web-based UI with Python      |
| **Streamlit** | `streamlit` | Data apps and dashboards      |
| **Gradio**    | `gradio`    | ML model demos and interfaces |

### Game & Multimedia

| Framework  | Package  | Description                     |
| ---------- | -------- | ------------------------------- |
| **Pygame** | `pygame` | Game and multimedia development |

---

## Project Types

21 project types are available, each with its own template and package set.

### Web Frameworks

| Type        | Key Packages         | Description                       |
| ----------- | -------------------- | --------------------------------- |
| **Django**  | `django`             | Full-featured web framework       |
| **FastAPI** | `fastapi`, `uvicorn` | Modern async API framework        |
| **Flask**   | `flask`              | Lightweight web framework         |
| **Bottle**  | `bottle`             | Minimal single-file web framework |

### Data Science & ML

| Type                           | Key Packages                      | Description                        |
| ------------------------------ | --------------------------------- | ---------------------------------- |
| **Data Analysis**              | `pandas`, `numpy`, `matplotlib`   | Data exploration and visualization |
| **Machine Learning**           | `scikit-learn`, `pandas`, `numpy` | Classical ML with scikit-learn     |
| **Deep Learning (PyTorch)**    | `torch`, `torchvision`            | Neural networks with PyTorch       |
| **Deep Learning (TensorFlow)** | `tensorflow`                      | Neural networks with TensorFlow    |
| **Computer Vision**            | `opencv-python`, `pillow`         | Image processing and CV            |

### CLI Tools

| Type          | Key Packages | Description                          |
| ------------- | ------------ | ------------------------------------ |
| **Click CLI** | `click`      | CLI with Click                       |
| **Typer CLI** | `typer[all]` | CLI with Typer (Click-based, modern) |
| **Rich CLI**  | `rich`       | Rich terminal output                 |

### API Development

| Type         | Key Packages             | Description                 |
| ------------ | ------------------------ | --------------------------- |
| **REST API** | `fastapi`, `uvicorn`     | RESTful API with FastAPI    |
| **GraphQL**  | `strawberry-graphql`     | GraphQL API with Strawberry |
| **gRPC**     | `grpcio`, `grpcio-tools` | gRPC services               |

### Automation & Scraping

| Type                   | Key Packages              | Description                        |
| ---------------------- | ------------------------- | ---------------------------------- |
| **Web Scraping**       | `beautifulsoup4`, `httpx` | Web scraping with BeautifulSoup    |
| **Browser Automation** | `playwright`              | Browser automation with Playwright |
| **Task Scheduling**    | `apscheduler`             | Scheduled tasks with APScheduler   |

### Other

| Type                     | Key Packages         | Description                   |
| ------------------------ | -------------------- | ----------------------------- |
| **Basic Python Package** | —                    | Minimal package structure     |
| **Testing Framework**    | `pytest`             | Test suite setup              |
| **Async Applications**   | `asyncio` *(stdlib)* | Async/await project structure |

---

## Combining frameworks and project types

You can select **both** a UI framework and a project type. Their templates are [merged intelligently](../guide/templates.md#template-merging) — matching folders are combined, unique folders from both are included, and all packages are installed.

Example combinations:

- **Flet + FastAPI** — Desktop app with an API backend
- **Streamlit + Data Analysis** — Data dashboard with analysis tooling
- **PyQt6 + Machine Learning** — GUI for an ML pipeline
