# UV Project Creator Help

This application helps you create new Python projects using UV with automatic folder structure generation, template management, and package installation.

## Getting Started

### 1. **Project Name**
Enter a valid Python package name:
- Must start with a letter or underscore
- Can contain letters, numbers, and underscores
- Cannot be a Python keyword (e.g., `class`, `def`, `import`)
- Cannot already exist at the target location

A live path preview appears below the name field showing the full resolved project path as you type.

**PyPI Name Check:** Click the globe icon (🌐) next to the name field to check if your project name is available on PyPI. The button is enabled once the name passes local validation. Results appear below the field:
- **Green** — name is available on PyPI
- **Red** — name is already taken (names are normalized per PEP 503, so `my_app` and `my-app` are treated as the same package)
- **Orange** — could not reach PyPI (check your internet connection)

### 2. **Set Project Path**
Browse or enter the directory where you want to create your project. This is where your project folder will be created. The default path is pre-filled and rarely needs changing.

### 3. **Python Version**
Select the Python version for your project:
- Default: 3.14
- Supported versions: 3.9 through 3.14
- The selected version will be configured in `.python-version` and `pyproject.toml`

### 4. **Git Repository** (Optional)
Check this option to initialize a Git repository in your project with automatic hub-based setup. This uses a two-phase approach:

**Phase 1 (During Project Creation):**
- Creates a local Git repository in your project directory
- Creates a bare "hub" repository at `~/Projects/git-repos/<project_name>.git`
- Connects the local repo to the hub as the `origin` remote

**Phase 2 (After Build Completion):**
- Automatically stages all generated project files (`git add .`)
- Creates an initial commit with message "Initial commit: Full project structure"
- Pushes to the hub with upstream tracking (`git push -u origin HEAD`)

**Result:** Your project is git-ready immediately—no manual first push needed! The hub acts as a central repository for your projects stored locally on your machine.

### 5. **UI Project** (Optional)
Check this option if you're creating a user interface application.
- A dialog will open letting you select from 10 UI frameworks organized by category:

**Desktop GUI:**
- Flet, PyQt6, PySide6, tkinter, customtkinter, Kivy

**Web & Data:**
- NiceGUI, Streamlit, Gradio

**Game & Multimedia:**
- Pygame
- **Selecting "None (Clear Selection)"** unchecks the option and clears your choice
- **Click the checkbox again** to reopen the dialog and change your selection
- The framework package will be automatically installed in your project

### 6. **Project Type** (Optional)
Check this option to create a specialized project type. This is independent of UI projects — you can use both together!

A dialog will open with 21 project type options organized by category:

**Web Frameworks:**
- Django, FastAPI, Flask, Bottle

**Data Science & ML:**
- Data Analysis, Machine Learning (scikit-learn), Deep Learning (PyTorch/TensorFlow), Computer Vision

**CLI Tools:**
- Click CLI, Typer CLI, Rich CLI

**API Development:**
- REST API (FastAPI), GraphQL (Strawberry), gRPC

**Automation & Scraping:**
- Web Scraping (BeautifulSoup), Browser Automation (Playwright), Task Scheduling (APScheduler)

**Other:**
- Basic Python Package, Testing Framework, Async Applications

Each option shows:
- 📦 **Packages** - What will be automatically installed
- 📋 **Description** - What the template includes

Features:
- **Selecting "None (Clear Selection)"** unchecks the option and clears your choice
- **Click the checkbox again** to reopen the dialog and change your selection
- Required packages are automatically installed

### 7. **Folders & Files**
The folder and file structure is automatically loaded from templates based on your selections:
- **Folders** - Displayed with "/" suffix in default color
- **Files** - Displayed in grey color
- **Starter Content** - Key files come pre-populated with boilerplate starter code (e.g., `main.py`, `state.py`, `components.py`) instead of being empty, with `{{project_name}}` placeholders automatically replaced as a formatted title (e.g. `my_app` → `My App`)

**Smart Scaffolding Fallback Chain:**
Files are populated from boilerplate in this priority order:
1. Framework-specific (e.g., Flet's `main.py`)
2. Project-type-specific (e.g., Django templates)
3. Common utilities (e.g., `async_executor.py`)
4. Empty file (if no boilerplate found)

You can customize the structure by:
- **Add Folder/File** - Add custom folders or files at any level
- **Remove Folder/File** - Select an item and click Remove to delete it
- **Auto-save Folder Changes** - Optionally save your custom structure back to the template

### 8. **Build Project**
Click "Build Project" to create your project with all configured settings. The builder will:

1. Create the project directory
2. Initialize UV with `uv init`
3. Initialize Git Phase 1 (if enabled): Create local repo + hub, set origin remote
4. Create the folder structure from templates
5. Populate key files with starter boilerplate content
6. Configure pyproject.toml
7. Create virtual environment with `uv venv`
8. Install selected UI framework (if any)
9. Install selected project type packages (if any)
10. Finalize Git Phase 2 (if enabled): Stage, commit, and push to hub

A **confirmation dialog** will appear showing a summary of your project settings. Before confirming, you can choose post-build actions:
- **Open project folder after build** — Opens the created project in Finder/Explorer (checked by default)
- **Open in VS Code** — Opens the project in VS Code immediately after creation (checked by default; requires VS Code to be installed)
- **Open terminal at project root** — Opens a terminal window in the project directory

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `⌘Enter` / `Ctrl+Enter` | Build project (when inputs are valid) |
| `⌘F` / `Ctrl+F` | Open Add Folder/File dialog |
| `⌘P` / `Ctrl+P` | Open Add Packages dialog |
| `⌘R` / `Ctrl+R` | Reset all fields (opens confirmation) |
| `Esc` | Close current dialog / Exit application |

## Tips & Tricks

- **Reset Button** (`⌘R`) - Restore all settings to defaults (preserves dark/light mode preference)
- **Theme Toggle** - Click the sun/moon icon to switch between light and dark mode
- **Help Button** - Click the "?" icon to view this help documentation
- **About Button** - Click the "i" icon to view app info, tech stack, and features (with links back to Help and Git Cheat Sheet)
- **Real-time Validation** - The app shows validation status with ✓ (valid) and ✗ (invalid) icons
- **Warning Banner** - Any issues are displayed below the project name field
- **Status Messages** - See what's happening in the status bar during build

## Combining UI Framework + Project Type

You can select **both** a UI framework and a project type! The templates will be intelligently merged:
- Matching folders are combined (files from both are included)
- Unique folders from both templates are included
- All dependencies are installed
- Perfect for creating full-stack applications (e.g., Flet UI + FastAPI backend)

## More Information

- **UV Documentation**: [uv](https://docs.astral.sh/uv/) https://docs.astral.sh/uv/
- **Python Documentation**: [Python](https://docs.python.org/) https://docs.python.org/
- **Flet Documentation**: [Flet](https://flet.dev/) https://flet.dev/
- **Project Management**: See individual framework/project type documentation for detailed setup guides

## Troubleshooting

**"Project already exists at this location"**
- Choose a different project name or location

**"UV command not found"**
- Install UV: [Astral uv](https://docs.astral.sh/uv/getting-started/installation/)

**"Git command not found"**
- Install Git: [Git](https://git-scm.com/)

**Build fails mid-way**
- Check your internet connection (for package installation)
- Ensure you have disk space
- The partial project will be automatically cleaned up

---

## See Also

- [About UV Project Creator](app://about) — App info, tech stack, and features
- [Git Cheat Sheet](app://git-cheat-sheet) — Quick reference for common Git commands
