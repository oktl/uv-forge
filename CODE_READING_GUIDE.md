# UV Project Creator - Code Reading Guide

**Last Updated:** February 8, 2026
**Purpose:** Comprehensive guide to understanding the codebase architecture and flow

---

## 📖 Table of Contents

1. [Quick Start - Where to Begin](#quick-start---where-to-begin)
2. [Project Architecture Overview](#project-architecture-overview)
3. [The Journey: From Simple to Complex](#the-journey-from-simple-to-complex)
4. [Process Flows](#process-flows)
5. [File-by-File Guide](#file-by-file-guide)
6. [Key Concepts](#key-concepts)
7. [Reading Order Recommendations](#reading-order-recommendations)

---

## Quick Start - Where to Begin

### If you want to understand

**How the app starts:**

1. `app/main.py` - Entry point
2. `app/ui/components.py` - UI construction
3. `app/handlers/event_handlers.py` - User interactions

**How projects are built:**

1. `app/core/project_builder.py` - Orchestration
2. `app/core/boilerplate_resolver.py` - Smart file scaffolding (starter content for files)
3. `app/handlers/filesystem_handler.py` - Folder creation
4. `app/handlers/uv_handler.py` - UV commands
5. `app/handlers/git_handler.py` - Git initialization

**How templates work:**

1. `app/config/templates/` - JSON template files
2. `app/core/config_manager.py` - Template loading
3. `app/core/template_merger.py` - Template merging (when both UI framework + project type selected)
4. `app/core/models.py` - FolderSpec data structure

**How the UI dialog works:**

1. `app/ui/dialogs.py` - Dialog creation
2. `app/utils/constants.py` - Project types & packages
3. `app/handlers/event_handlers.py` - Dialog handlers

---

## Project Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     USER INTERFACE                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   main.py   │→ │ components.py │→ │   dialogs.py  │  │
│  │ Entry Point │  │  UI Builder   │  │ Dialog Builder│  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                    EVENT HANDLERS                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │         event_handlers.py (Handlers class)       │   │
│  │  • Path validation    • Framework selection      │   │
│  │  • Name validation    • Project type selection   │   │
│  │  • Build project      • Add/Remove folders       │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                     CORE LOGIC                           │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   state.py  │  │  models.py   │  │ validator.py  │  │
│  │  AppState   │  │ ProjectConfig│  │  Validation   │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│  ┌─────────────┐  ┌──────────────┐                      │
│  │config_mgr.py│  │proj_builder  │                      │
│  │  Templates  │  │Orchestration │                      │
│  └─────────────┘  └──────────────┘                      │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                      HANDLERS                            │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │filesystem_  │  │  uv_handler  │  │  git_handler  │  │
│  │  handler    │  │  UV commands │  │ Git commands  │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   EXTERNAL SYSTEMS                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ File System │  │  UV (uv cmd) │  │  Git (git cmd)│  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## The Journey: From Simple to Complex

### Phase 1: The Simple Beginning (uv init)

```bash
# This is where it all started:
uv init my_project
```

### Phase 2: Basic Automation

- Automated `uv init` calls
- Basic folder structure creation
- Simple UI with Flet

### Phase 3: Template System

- JSON templates for folder structures
- Framework-specific templates (Flet, PyQt6, etc.)
- ConfigManager for loading templates

### Phase 4: Feature Expansion

- Git initialization option
- Python version selection
- UI framework selection
- Custom folder management

### Phase 5: Project Types

- 21 project type templates
- Automatic package installation
- Enhanced dialog with tooltips
- Beautiful UI with theming

### Phase 6: Smart Scaffolding

- Boilerplate resolver with fallback chain (framework → project type → common)
- Files created with starter content instead of empty `.touch()`
- `{{project_name}}` placeholder substitution
- Extensible: add new boilerplate files without code changes

### Current State: Full-Featured App

- 32 total templates + boilerplate file scaffolding
- Complete package management
- Professional UI
- Comprehensive testing (370 tests)

---

## Process Flows

### 1. Application Startup Flow

```
START
  ↓
main.py:run()
  ↓
Create Flet Page
  ↓
Initialize AppState
  ├─ project_path = DEFAULT_PROJECT_ROOT
  ├─ project_name = ""
  ├─ selected_python_version = "3.14"
  ├─ initialize_git = False
  ├─ create_ui_project = False
  ├─ selected_framework = None
  ├─ create_other_project = False
  ├─ selected_project_type = None
  └─ folders = []
  ↓
components.build_main_view(page, state)
  ├─ Create all UI controls
  ├─ Set initial values from state
  ├─ Apply theme colors
  └─ Store controls_ref and state_ref on page
  ↓
event_handlers.attach_handlers(page, state)
  ├─ Create Handlers instance
  ├─ Attach click/change handlers to controls
  └─ Load default template
  ↓
ConfigManager.load_config()
  ├─ Try to load default.json
  ├─ Parse FolderSpec structures
  └─ Update state.folders
  ↓
Display UI to User
  ↓
READY (waiting for user input)
```

### 2. UI Framework Selection Flow (Dialog-based)

```
User clicks "Create UI Project" checkbox (or already-checked checkbox to reopen)
  ↓
on_ui_project_toggle(e)
  ├─ Force checkbox value = True
  ├─ Set state.create_ui_project = True
  └─ Call _show_framework_dialog()
  ↓
_show_framework_dialog()
  ↓
create_framework_dialog(...)
  ├─ Build radio list with 10 frameworks
  ├─ Add "None (Clear Selection)" option at top
  ├─ Attach tooltips with descriptions + package info
  └─ Return AlertDialog
  ↓
Dialog opens (modal)
  ↓
User selects framework (e.g., "Flet") and clicks "Select"
  ↓
on_select("flet") callback fires
  ├─ state.selected_framework = "flet"
  ├─ Update checkbox label → "UI Project: Flet"
  ├─ Call _reload_and_merge_templates()
  │   ├─ If only framework: load framework template
  │   ├─ If both UI + project type: merge both templates
  │   └─ Update state.folders
  ├─ Close dialog
  └─ Update UI
  ↓
_update_folder_display() renders merged template
  ↓
UI shows folder structure

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ALTERNATIVE: User clicks "None (Clear Selection)"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
on_select(None) callback fires
  ├─ state.selected_framework = None
  ├─ state.create_ui_project = False
  ├─ Uncheck checkbox
  ├─ Reset label → "Create UI Project"
  ├─ Reload templates (removes framework template)
  └─ Close dialog
  ↓
Checkbox unchecked, label reset
```

### 3. Template Loading Flow

When templates are loaded (whether from UI framework, project type, or both), ConfigManager uses the fallback chain:

```
ConfigManager.load_config("flet")
  ↓
_normalize_framework_name("flet") → "flet"
  ↓
template_path = UI_TEMPLATES_DIR / "flet.json"
  ↓
_load_template(template_path)
  ├─ Read JSON file
  ├─ Parse {"folders": [...]}
  └─ Return {folders: [FolderSpec, ...]}
  ↓
state.folders = loaded_folders
  ↓
_update_folder_display()
  ├─ Clear folder_display
  ├─ Flatten folder structure
  ├─ Create Text controls for each folder/file
  │   ├─ Folders: default color, "/" suffix
  │   └─ Files: grey color, no suffix
  ├─ Add click handlers for selection
  └─ Update page
  ↓
UI shows folder structure
```

### 4. Project Type Selection Flow (Dialog-based)

```
User clicks "Create Other Project Type" checkbox (or already-checked to reopen)
  ↓
on_other_project_toggle(e)
  ├─ Force checkbox value = True
  ├─ Set state.create_other_project = True
  └─ Call _show_project_type_dialog()
  ↓
_show_project_type_dialog()
  ↓
create_project_type_dialog(...)
  ├─ Build categories with icons (🌐 🤖 ⚙️ etc.)
  ├─ Add "None (Clear Selection)" option at top
  ├─ Create radio buttons with tooltips
  │   ├─ Get packages from PROJECT_TYPE_PACKAGE_MAP
  │   ├─ Build tooltip: description + packages
  │   └─ Attach tooltip to radio container
  ├─ Add dividers between categories
  └─ Return AlertDialog
  ↓
Dialog opens (modal, scrollable)
  ↓
User hovers over option → Tooltip shows!
  ├─ Description: "Full-stack web framework..."
  └─ Packages: "📦 Package: django"
  ↓
User selects "Django" and clicks "Select"
  ↓
on_select(project_type="django") callback fires
  ├─ state.selected_project_type = "django"
  ├─ Update checkbox label → "Project: Django"
  ├─ Call _reload_and_merge_templates()
  │   ├─ If UI framework also selected:
  │   │   ├─ Load framework template (e.g., flet.json)
  │   │   ├─ Load project type template (django.json)
  │   │   └─ merge_folder_lists(fw_folders, pt_folders)
  │   │       ├─ Matching folders: merge recursively, union files
  │   │       └─ Non-matching: include both
  │   └─ If only project type: load django.json template
  ├─ Close dialog
  └─ Update UI
  ↓
_update_folder_display() renders merged template
  ↓
UI shows folder structure

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ALTERNATIVE: User clicks "None (Clear Selection)"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
on_select(None) callback fires
  ├─ state.selected_project_type = None
  ├─ state.create_other_project = False
  ├─ Uncheck checkbox
  ├─ Reset label → "Create Other Project Type"
  ├─ Reload templates (removes project type template)
  └─ Close dialog
  ↓
Checkbox unchecked, label reset
```

### 4. Project Build Flow

```
User clicks "Build Project" button
  ↓
on_build_project(e)
  ↓
_validate_inputs()
  ├─ Validate project path
  ├─ Validate project name
  └─ Check all validations passed
  ↓
Show progress ring
Disable build button
Set status: "Building project..."
  ↓
Create ProjectConfig
  ├─ name = state.project_name
  ├─ path = Path(state.project_path)
  ├─ python_version = state.selected_python_version
  ├─ git_enabled = state.initialize_git
  ├─ ui_project_enabled = state.create_ui_project
  ├─ framework = state.selected_framework
  ├─ project_type = state.selected_project_type
  └─ folders = state.folders
  ↓
AsyncExecutor.run(build_project, config)
  ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          BUILD PROCESS STARTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
validate_project_name(config.name)
  ├─ Check: not empty
  ├─ Check: starts with letter/underscore
  ├─ Check: alphanumeric + underscore only
  ├─ Check: not Python keyword
  └─ Return (True, "") or (False, error_msg)
  ↓
Create base directory if needed
  ↓
Create project directory (config.full_path)
  ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 1: UV Init
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
run_uv_init(full_path, python_version)
  ├─ subprocess.run([
  │    "uv", "init",
  │    "--python", "3.14",
  │    "--name", "my_project"
  │  ])
  ├─ Creates pyproject.toml
  ├─ Creates .python-version
  └─ Creates basic structure
  ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 2: Git Phase 1 (if enabled)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
handle_git_init(full_path, git_enabled)
  ├─ if not git_enabled: remove .git if present → return
  ├─ Create local repo: subprocess.run(["git", "init"])
  ├─ Create bare hub: subprocess.run(["git", "init", "--bare"])
  │   at ~/Projects/git-repos/<project_name>.git
  └─ Connect local → hub: subprocess.run(["git", "remote", "add", "origin", ...])
  ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 3: Create Folder Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
BoilerplateResolver(project_name, framework, project_type)
  ├─ Builds search_dirs fallback chain:
  │   1. boilerplate/ui_frameworks/{framework}/
  │   2. boilerplate/project_types/{project_type}/
  │   3. boilerplate/common/
  ↓
setup_app_structure(full_path, folders, resolver)
  ↓
For each FolderSpec in folders:
  ├─ Determine location:
  │   ├─ If root_level: full_path / name
  │   └─ Else: full_path / "app" / name
  ├─ Create directory
  ├─ If create_init: create __init__.py
  ├─ If files: for each file:
  │   ├─ resolver.resolve(filename) → search fallback chain
  │   ├─ If boilerplate found: write content (with {{project_name}} replaced)
  │   └─ If not found: create empty file (.touch())
  └─ Recursively process subfolders (resolver passed through)
  ↓
Result: Complete folder structure with starter content
  ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 4: Configure pyproject.toml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
configure_pyproject(full_path, project_name)
  ├─ Read existing pyproject.toml
  ├─ Update [project] section
  │   ├─ name = project_name
  │   └─ version = "0.1.0"
  └─ Write back to file
  ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 5: Create Virtual Environment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
setup_virtual_env(full_path, python_version)
  ├─ subprocess.run(["uv", "venv", "--python", "3.14"])
  └─ subprocess.run(["uv", "sync"])
  ↓
Virtual environment created and synced
  ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 6: Install UI Framework (if selected)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
if config.ui_project_enabled:
  ↓
  package_name = FRAMEWORK_PACKAGE_MAP.get("flet")
    → "flet"
  ↓
  install_package(full_path, "flet")
    ├─ subprocess.run([
    │    "uv", "add", "flet",
    │    cwd=full_path
    │  ])
    └─ Package installed, pyproject.toml updated
  ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 7: Install Project Type Packages
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
if config.project_type:
  ↓
  packages = PROJECT_TYPE_PACKAGE_MAP.get("django")
    → ["django"]
  ↓
  For each package in packages:
    ↓
    install_package(full_path, "django")
      ├─ subprocess.run(["uv", "add", "django"])
      └─ Django installed!
  ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 8: Git Phase 2 - Finalize (if enabled)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
finalize_git_setup(full_path, git_enabled)
  ├─ if not git_enabled: return
  ├─ subprocess.run(["git", "add", "."])
  │   (Stage all generated files)
  ├─ Check if files exist (git status --porcelain)
  ├─ If yes:
  │   ├─ subprocess.run(["git", "commit", "-m", "Initial commit: Full project structure"])
  │   └─ subprocess.run(["git", "push", "-u", "origin", "HEAD"])
  │       (Push to hub with upstream tracking)
  └─ If no: log warning (empty project)
  ↓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          BUILD PROCESS COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↓
Return BuildResult(
  success=True,
  message="Project Created Successfully! Built at: /path/to/project"
)
  ↓
Back to event handler
  ↓
Hide progress ring
Re-enable build button
Set status: "Project created successfully!"
  ↓
User sees success message
  ↓
DONE! 🎉
```

### 5. Error Handling Flow

```
Exception occurs during build
  ↓
catch Exception as e
  ↓
cleanup_on_error(full_path)
  ├─ Check if project directory exists
  ├─ shutil.rmtree(full_path)
  └─ Removes entire partially-created project
  ↓
Return BuildResult(
  success=False,
  message=f"Error: {e}",
  error=e
)
  ↓
Back to event handler
  ↓
Display error message to user
Set status to error state (red)
  ↓
User can try again
```

---

## File-by-File Guide

### 📁 Entry Point & Main

#### `app/main.py` (64 lines)

**Purpose:** Application entry point

**Key Functions:**

- `run()` - Main application function
  1. Creates Flet page
  2. Initializes AppState
  3. Builds UI via `build_main_view()`
  4. Attaches handlers via `attach_handlers()`
  5. Starts Flet app

**Read this:** To understand how the app starts

**Flow:**

```python
def run():
    def main(page: ft.Page):
        # Configure page
        page.title = "UV Project Creator"
        page.window.width = 900
        page.window.height = 800

        # Initialize state
        state = AppState()

        # Build UI
        build_main_view(page, state)

        # Attach handlers
        attach_handlers(page, state)

    ft.app(target=main)
```

---

### 📁 Core Business Logic (`app/core/`)

#### `app/core/state.py` (78 lines)

**Purpose:** Central application state management

**Key Class: `AppState`**

```python
@dataclass
class AppState:
    # Project configuration
    project_path: str = DEFAULT_PROJECT_ROOT
    project_name: str = ""
    selected_python_version: str = DEFAULT_PYTHON_VERSION

    # Options
    initialize_git: bool = False
    create_ui_project: bool = False
    selected_framework: Optional[str] = None
    create_other_project: bool = False
    selected_project_type: Optional[str] = None

    # Folder management
    folders: list = field(default_factory=list)
    auto_save_folders: bool = False

    # Selection tracking
    selected_item_path: Optional[list] = None
    selected_item_type: Optional[str] = None

    # UI state
    is_dark_mode: bool = True

    # Validation flags
    path_valid: bool = True
    name_valid: bool = True
```

**Key Method: `reset()`**

- Resets all state except `is_dark_mode`
- Called by reset button

**Read this:** To understand what data the app tracks

---

#### `app/core/models.py` (127 lines)

**Purpose:** Data structures for the application

**Key Classes:**

**1. FolderSpec** - Folder structure definition

```python
@dataclass
class FolderSpec:
    name: str                       # Folder name
    create_init: bool = True        # Create __init__.py?
    root_level: bool = False        # At project root vs app/?
    subfolders: list[FolderSpec]    # Nested folders
    files: list[str] = None         # Files to create

    @classmethod
    def from_dict(cls, data: dict) -> FolderSpec
        # Convert JSON to FolderSpec

    def to_dict(self) -> dict
        # Convert FolderSpec to JSON
```

**2. ProjectConfig** - Project configuration

```python
@dataclass
class ProjectConfig:
    name: str
    path: Path
    python_version: str
    git_enabled: bool
    ui_project_enabled: bool
    framework: str
    project_type: Optional[str] = None
    folders: list = field(default_factory=list)

    @property
    def full_path(self) -> Path:
        return self.path / self.name
```

**3. BuildResult** - Build operation result

```python
@dataclass
class BuildResult:
    success: bool
    message: str
    error: Optional[Exception] = None
```

**4. BuildSummaryConfig** - Build summary dialog configuration

```python
@dataclass
class BuildSummaryConfig:
    project_name: str
    project_path: str
    python_version: str
    git_enabled: bool
    framework: Optional[str]
    project_type: Optional[str]
    starter_files: bool
    folder_count: int
    file_count: int
```

Used by `create_build_summary_dialog()` in `dialogs.py` — consolidates 9 individual parameters into one config object.

**Read this:** To understand the data structures

---

#### `app/core/validator.py` (101 lines)

**Purpose:** Input validation

**Key Functions:**

**`validate_project_name(name: str) -> tuple[bool, str]`**

```python
# Returns: (is_valid, error_message)
# Checks:
#   - Not empty
#   - Starts with letter or underscore
#   - Only alphanumeric + underscore
#   - Not a Python keyword
```

**`validate_folder_name(name: str) -> tuple[bool, str]`**

```python
# Returns: (is_valid, error_message)
# Checks:
#   - Not empty
#   - Not reserved (., .., ~)
#   - Starts with letter, underscore, or dot
#   - Valid characters (allows dots for files like .env)
```

**`validate_path(path: str) -> tuple[bool, str]`**

```python
# Returns: (is_valid, error_message)
# Checks:
#   - Not empty
#   - Path exists
#   - Path is a directory
```

**Read this:** To understand validation rules

---

#### `app/core/config_manager.py` (150 lines)

**Purpose:** Load folder templates from JSON files

**Key Class: `ConfigManager`**

**Initialization:**

```python
def __init__(self):
    self.config_source = UI_TEMPLATES_DIR / "default.json"
    self.loaded_framework = None
    self.settings = self.load_config()
```

**Main Method: `load_config(framework: str) -> dict`**

**Flow:**

```
1. If framework contains "/":
   → project_types/django.json

2. Else:
   → ui_frameworks/flet.json

3. Try to load template file

4. If not found, try default.json

5. If not found, use hardcoded DEFAULT_FOLDERS

6. Parse JSON → FolderSpec objects

7. Return {"folders": [FolderSpec, ...]}
```

**Helper Methods:**

- `_normalize_framework_name()` - Convert "PyQt6" → "pyqt6"
- `_load_template()` - Load and parse JSON file
- `save_config()` - Save folders back to template
- `get_config_display_name()` - Get friendly name

**Read this:** To understand template loading

---

#### `app/core/template_merger.py` (~60 lines)

**Purpose:** Merge two folder template lists into one unified structure

**Key Functions:**

**`normalize_folder(folder) -> dict`**

```python
# Converts any folder form (string, dict, FolderSpec)
# to a canonical dict with keys:
#   name, create_init, root_level, subfolders, files
```

**`merge_folder_lists(primary, secondary) -> list[dict]`**

```python
# Merge two folder lists:
# 1. Normalize both lists
# 2. Match folders by name (case-sensitive)
# 3. Matching: merge recursively, union files, OR booleans
# 4. Non-matching: include both (primary order first)
```

**`_merge_files(primary_files, secondary_files) -> list[str]`**

```python
# Union two file lists, deduplicated, primary order preserved
```

**Used by:** `event_handlers.py:_reload_and_merge_templates()`

**Read this:** To understand how UI framework + project type templates are combined

---

#### `app/core/boilerplate_resolver.py` (~90 lines)

**Purpose:** Look up starter content for scaffolded files

**Module Function: `normalize_framework_name(framework) -> str`**

```python
# Shared normalization used by both ConfigManager and BoilerplateResolver
# "PyQt6" → "pyqt6", "tkinter (built-in)" → "tkinter"
```

**Key Class: `BoilerplateResolver`**

```python
resolver = BoilerplateResolver(
    project_name="my_app",
    framework="flet",           # optional
    project_type="django",      # optional
    boilerplate_dir=custom_dir, # optional, for testing
)

# Search fallback chain for starter content
content = resolver.resolve("main.py")
# Returns file content with {{project_name}} replaced, or None
```

**Fallback chain:**
1. `boilerplate/ui_frameworks/{framework}/{filename}`
2. `boilerplate/project_types/{project_type}/{filename}`
3. `boilerplate/common/{filename}`
4. `None` → caller does `.touch()`

**Used by:** `project_builder.py` (constructs resolver) → `filesystem_handler.py` (uses resolver for file creation)

**Read this:** To understand how files get starter content instead of being empty

---

#### `app/core/project_builder.py` (~120 lines)

**Purpose:** Orchestrate entire project creation

**Main Function: `build_project(config: ProjectConfig) -> BuildResult`**

**Steps:**

```python
1. Validate project name
2. Create base directory
3. Create project directory
4. run_uv_init()                 # UV initialization
5. handle_git_init()             # Git (if enabled)
6. BoilerplateResolver(...)      # Construct resolver from config
7. setup_app_structure(resolver) # Folders + smart scaffolding
8. configure_pyproject()         # pyproject.toml
9. setup_virtual_env()           # Virtual env
10. Install UI framework         # (if selected)
11. Install project packages     # (if selected)
12. Return success result
```

**Error Handling:**

```python
try:
    # All steps
except subprocess.CalledProcessError as e:
    cleanup_on_error(full_path)
    return BuildResult(success=False, ...)
except Exception as e:
    cleanup_on_error(full_path)
    return BuildResult(success=False, ...)
```

**Helper Function: `cleanup_on_error()`**

- Removes entire project directory on failure
- Ensures no partial projects left behind

**Read this:** To understand the complete build process

---

### 📁 Handlers (`app/handlers/`)

#### `app/handlers/event_handlers.py` (932 lines)

**Purpose:** Handle all UI events

**Key Class: `Handlers`**

**Initialization:**

```python
def __init__(self, page, controls, state):
    self.page = page
    self.controls = controls
    self.state = state
    self.config_manager = ConfigManager()
```

**Key Methods:**

**Validation Handlers:**

- `on_path_change()` - Validate project path
- `on_name_change()` - Validate project name
- `_validate_inputs()` - Validate all inputs

**Option Handlers:**

- `on_python_version_change()` - Python version selection
- `on_git_toggle()` - Git checkbox
- `on_ui_project_toggle()` - UI project checkbox (opens framework dialog)
- `on_other_project_toggle()` - Other project checkbox (opens project type dialog)

**Folder Management:**

- `_update_folder_display()` - Render folder tree
- `on_add_folder()` - Add folder/file dialog
- `on_remove_folder()` - Remove selected item
- `on_folder_item_click()` - Select folder/file

**Build Process:**

- `on_build_project()` - Main build button
  1. Validate inputs
  2. Create ProjectConfig
  3. Call AsyncExecutor.run(build_project, config)
  4. Display result

**Template Loading & Merging:**

- `_reload_and_merge_templates()` - Central method: loads/merges templates based on current selections
- `_load_framework_template()` - Load UI framework template
- `_load_project_type_template()` - Load project type template

**Dialog Handlers:**

- `_show_framework_dialog()` - Show UI framework selection dialog
- `_show_project_type_dialog()` - Show project type selection dialog

**Other:**

- `on_reset()` - Reset all fields
- `on_theme_toggle()` - Switch light/dark mode
- `on_help()` - Show help dialog

**Main Function: `attach_handlers(page, state)`**

```python
def attach_handlers(page, state):
    controls = page.controls_ref
    handlers = Handlers(page, controls, state)

    # Attach all handlers
    controls.project_path_field.on_change = wrap_async(
        handlers.on_path_change
    )
    controls.project_name_field.on_change = wrap_async(
        handlers.on_name_change
    )
    # ... etc for all controls

    # Load default template
    handlers._reload_and_merge_templates()
```

**Read this:** To understand how user actions are handled

---

#### `app/handlers/filesystem_handler.py` (~250 lines)

**Purpose:** File system operations

**Key Functions:**

**`setup_app_structure(project_path, folders, resolver=None)`**

```python
# Main entry point
# Processes list of folders and creates structure
# Optional resolver populates files with boilerplate content

def setup_app_structure(project_path, folders, resolver=None):
    app_path = project_path / "app"
    app_path.mkdir(exist_ok=True)
    # Separates root-level vs app-level folders
    # Passes resolver through to create_folders()
```

**`create_folders(parent_dir, folders, parent_create_init=True, resolver=None)`**

```python
# Recursive folder creation
# Handles nested structures
# Uses resolver for smart file scaffolding

# For each file in a folder spec:
content = resolver.resolve(file_name) if resolver else None
if content is not None:
    file_path.write_text(content, encoding="utf-8")
else:
    file_path.touch()

# Resolver is passed through to recursive subfolder creation
```

**`flatten_folder_structure_for_display(folders, parent_path=None)`**

```python
# Convert nested FolderSpec to flat list for UI display
# Returns: list of (path_tuple, name, is_file)

Example output:
[
    ([0], "core/", False),           # folder
    ([0, 0], "models.py", True),     # file in core/
    ([1], "ui/", False),             # folder
]
```

**Helper Functions:**

- `_format_folder_for_display()` - Format single folder
- `_extract_path()` - Extract path from FolderSpec hierarchy

**Read this:** To understand folder creation

---

#### `app/handlers/uv_handler.py` (138 lines)

**Purpose:** UV package manager commands

**Key Functions:**

**`run_uv_init(project_path, python_version)`**

```python
subprocess.run([
    "uv", "init",
    "--python", python_version,
    "--name", project_path.name
], cwd=project_path, check=True)
```

**`install_package(project_path, package_name)`**

```python
subprocess.run([
    "uv", "add", package_name
], cwd=project_path, check=True)
```

**`setup_virtual_env(project_path, python_version)`**

```python
# Create venv
subprocess.run([
    "uv", "venv",
    "--python", python_version
], cwd=project_path, check=True)

# Sync dependencies
subprocess.run([
    "uv", "sync"
], cwd=project_path, check=True)
```

**`configure_pyproject(project_path, project_name)`**

```python
# Read pyproject.toml
with open(pyproject_path, "r") as f:
    data = toml.load(f)

# Update project name
data["project"]["name"] = project_name

# Write back
with open(pyproject_path, "w") as f:
    toml.dump(data, f)
```

**Read this:** To understand UV integration

---

#### `app/handlers/git_handler.py` (~140 lines)

**Purpose:** Two-phase git setup with local and bare repository hub

**Key Functions:**

**Phase 1: `handle_git_init(project_path, use_git)`**

```python
# Called early in project build (after uv init)
# Creates local repo + bare hub at ~/Projects/git-repos/<name>.git

if not use_git:
    return  # Remove .git if present

# Initialize local repo (idempotent — skipped if .git exists)
subprocess.run(["git", "init"], cwd=project_path, check=True)

# Create bare hub repo
bare_repo_path = Path.home() / "Projects" / "git-repos" / f"{project_path.name}.git"
subprocess.run(["git", "init", "--bare"], cwd=bare_repo_path, check=True)

# Connect local to hub as 'origin' remote (or update URL if exists)
subprocess.run([
    "git", "remote", "add", "origin", str(bare_repo_path)
], cwd=project_path, check=True)
```

**Phase 2: `finalize_git_setup(project_path, use_git)`**

```python
# Called after all project files generated and packages installed
# Stages everything, commits, and pushes to hub

if not use_git:
    return

# Stage all files
subprocess.run(["git", "add", "."], cwd=project_path, check=True)

# Only commit if files exist
if has_changes():
    subprocess.run([
        "git", "commit",
        "-m", "Initial commit: Full project structure"
    ], cwd=project_path, check=True)

    # Push with upstream tracking
    subprocess.run([
        "git", "push", "-u", "origin", "HEAD"
    ], cwd=project_path, check=True)
```

**Key Features:**

- **Idempotent** — Safe to call multiple times (checks if .git/HEAD exists before initializing)
- **Local hub** — Bare repo at `~/Projects/git-repos/` acts as central repository
- **Logging** — Uses loguru for detailed operation tracking
- **Error capture** — All subprocess calls use `capture_output=True` for rich error messages

**Used by:** `project_builder.py` calls both functions in sequence during build process

**Read this:** To understand the two-phase git setup with hub-based approach

---

#### `app/handlers/handler_factory.py` (106 lines)

**Purpose:** Async wrappers for synchronous handlers

**Key Class: `HandlerFactory`**

**`create_handler(sync_func) -> async_func`**

```python
# Wraps synchronous function in async interface
# Executes in thread pool via AsyncExecutor

async def async_wrapper(*args, **kwargs):
    return await AsyncExecutor.run(sync_func, *args, **kwargs)
```

**Why?**

- UV commands are blocking (subprocess calls)
- Need to run off main thread
- Keeps UI responsive

**Read this:** To understand async patterns

---

### 📁 UI (`app/ui/`)

#### `app/ui/components.py` (405 lines)

**Purpose:** Build the main UI

**Key Class: `Controls`**

```python
class Controls:
    # All UI control references
    project_path_field: ft.TextField
    browse_button: ft.FilledButton
    project_name_field: ft.TextField
    python_version_dropdown: ft.Dropdown
    create_git_checkbox: ft.Checkbox
    create_ui_project_checkbox: ft.Checkbox
    other_projects_checkbox: ft.Checkbox
    folder_display: ft.Column
    add_folder_button: ft.FilledButton
    remove_folder_button: ft.FilledButton
    auto_save_checkbox: ft.Checkbox
    build_project_button: ft.FilledButton
    reset_button: ft.TextButton
    exit_button: ft.TextButton
    theme_toggle_button: ft.IconButton
    help_button: ft.IconButton
    warning_banner: ft.Container
    warning_text: ft.Text
    status_text: ft.Text
    progress_ring: ft.ProgressRing
```

Note: UI framework and project type are now selected via dialogs (not dropdowns) when clicking their respective checkboxes.

**Main Function: `build_main_view(page, state)`**

**Flow:**

```python
1. Get theme colors
2. Create Controls instance
3. Initialize all UI controls with state values
4. Build layout:
   ├─ Title row (logo + title + theme toggle + help)
   ├─ Warning banner
   ├─ Project Path section
   ├─ Project Name section
   ├─ Python Version section
   ├─ Git Options section
   ├─ UI Framework section
   ├─ Other Projects section
   ├─ Folder Structure section
   └─ Actions section (Build + Reset + Exit)
5. Store controls_ref and state_ref on page
6. Add to page and update
```

**Read this:** To understand UI structure

---

#### `app/ui/dialogs.py` (742 lines)

**Purpose:** Reusable dialog components — all theme-aware via `is_dark_mode` parameter

**Module-level helpers (shared across dialogs):**

```python
create_tooltip(description, packages)         # Rich tooltip text with package info
_create_dialog_title(text, colors, icon)      # Standardized icon + text title
_create_dialog_actions(label, cb, cancel_cb)  # FilledButton + Cancel pattern
_create_summary_row(label, value)             # Bold label + value row
_create_none_option_container(is_dark_mode)   # "None (Clear Selection)" + divider
```

**Public dialog functions:**

**`create_help_dialog(content, on_close, page, is_dark_mode)`**
- Displays help documentation as scrollable Markdown

**`create_framework_dialog(..., is_dark_mode)`**
```python
# Flat radio list (10 frameworks from UI_FRAMEWORK_DETAILS in constants.py)
# "None (Clear Selection)" + dividers, rich tooltips, theme-aware
```

**`create_project_type_dialog(..., is_dark_mode)`**
```python
# Categorized radio list from PROJECT_TYPE_CATEGORIES in constants.py
# Category icons (🌐 🤖 ⚙️ 🔌 🔄 📦), colored backgrounds, rich tooltips
```

**`create_add_item_dialog(..., is_dark_mode)`**
- Add folder or file with parent location selection
- Real-time name validation + re-validates on submit

**`create_build_summary_dialog(config: BuildSummaryConfig, on_build, on_cancel, is_dark_mode)`**
- Confirmation dialog before build; uses `BuildSummaryConfig` dataclass

**Read this:** To understand dialogs. Data for framework/project type options lives in `constants.py`.

---

#### `app/ui/theme_manager.py` (93 lines)

**Purpose:** Theme color management

**Key Function: `get_theme_colors(is_dark: bool) -> dict`**

**Returns color dictionary:**

```python
{
    "background": ...,
    "surface": ...,
    "main_title": ...,
    "section_title": ...,
    "section_border": ...,
    "section_bg": ...,
    "text_primary": ...,
    "text_secondary": ...,
    "accent": ...,
    "success": ...,
    "error": ...,
    "warning": ...,
}
```

**Usage:**

```python
colors = get_theme_colors(state.is_dark_mode)
ft.Container(bgcolor=colors["section_bg"])
```

**Read this:** To understand theming

---

### 📁 Utils (`app/utils/`)

#### `app/utils/constants.py` (~310 lines)

**Purpose:** Application constants — single source of truth for everything

**Key Constants:**

**Python Versions:**

```python
PYTHON_VERSIONS = ["3.14", "3.13", "3.12", "3.11", "3.10", "3.9"]
DEFAULT_PYTHON_VERSION = "3.14"
```

**Package Mappings:**

```python
FRAMEWORK_PACKAGE_MAP = {
    "flet": "flet",
    "PyQt6": "pyqt6",
    # ... etc
}

PROJECT_TYPE_PACKAGE_MAP = {
    "django": ["django"],
    "fastapi": ["fastapi", "uvicorn"],
    "data_analysis": ["pandas", "numpy", "matplotlib", "jupyter"],
    # ... 21 total project types
}
```

**Dialog Data (added Feb 2026):**

```python
# Used by create_project_type_dialog() — 6 categories with icons, colors, items
PROJECT_TYPE_CATEGORIES = {
    "Web Frameworks": {
        "icon": "🌐", "light_color": "BLUE_50", "dark_color": "BLUE_900",
        "items": [("Django", "django", "description..."), ...]
    },
    # ... 5 more categories
}

# Used by create_framework_dialog() — flat list of (label, value, description)
UI_FRAMEWORK_DETAILS = [
    ("Flet", "flet", "Modern Flutter-based Python UI framework..."),
    # ... 9 more frameworks
]
```

To add a framework or project type to the dialog, update these constants here — no changes to `dialogs.py` needed.

**Paths:**

```python
PROJECT_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = PROJECT_DIR / "app/config/templates"
UI_TEMPLATES_DIR = TEMPLATES_DIR / "ui_frameworks"
PROJECT_TYPE_TEMPLATES_DIR = TEMPLATES_DIR / "project_types"
```

**Read this first!** Single source of truth for all constants

---

#### `app/utils/async_executor.py` (58 lines)

**Purpose:** Thread pool executor for async operations

**Key Class: `AsyncExecutor`**

**Main Method: `run(func, *args, **kwargs)`**

```python
@staticmethod
async def run(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    executor = AsyncExecutor.get_executor()
    return await loop.run_in_executor(
        executor,
        lambda: func(*args, **kwargs)
    )
```

**Why?**

- Flet needs async event handlers
- UV/Git commands are blocking
- Run blocking code in thread pool
- Keep UI responsive

**Usage:**

```python
result = await AsyncExecutor.run(build_project, config)
```

**Read this:** To understand async execution

---

### 📁 Templates (`app/config/templates/`)

#### Template Structure

**UI Frameworks (11 templates):**

```
ui_frameworks/
├── default.json       ← Generic Python project
├── flet.json          ← Flet app structure
├── pyqt6.json         ← PyQt6 app
├── pyside6.json       ← PySide6 app
├── tkinter.json       ← Tkinter app
├── customtkinter.json
├── kivy.json
├── pygame.json
├── nicegui.json
├── streamlit.json
└── gradio.json
```

**Project Types (21 templates):**

```
project_types/
├── django.json        ← Web framework
├── fastapi.json
├── flask.json
├── bottle.json
├── data_analysis.json ← Data science
├── ml_sklearn.json
├── dl_pytorch.json
├── dl_tensorflow.json
├── computer_vision.json
├── cli_click.json     ← CLI tools
├── cli_typer.json
├── cli_rich.json
├── api_fastapi.json   ← API development
├── api_graphql.json
├── api_grpc.json
├── browser_automation.json ← Automation
├── task_scheduler.json
├── scraping.json
├── basic_package.json ← Other
├── testing.json
└── async_app.json
```

**Boilerplate Starter Files:**

```
boilerplate/
├── common/
│   ├── async_executor.py        ← ThreadPoolExecutor wrapper
│   └── constants.py             ← APP_NAME, APP_VERSION with {{project_name}}
└── ui_frameworks/
    └── flet/
        ├── main.py              ← Minimal Flet hello world
        ├── state.py             ← Basic AppState dataclass
        └── components.py        ← Starter build_main_view()
```

Adding new boilerplate requires no code changes — just drop a file in the right directory.

#### Template Format

**Example: flet.json**

```json
{
  "folders": [
    {
      "name": "core",
      "create_init": true,
      "files": [
        "state.py",
        "models.py"
      ],
      "subfolders": []
    },
    {
      "name": "ui",
      "create_init": true,
      "files": [
        "components.py"
      ],
      "subfolders": [
        {
          "name": "styles",
          "create_init": true,
          "subfolders": []
        }
      ]
    }
  ]
}
```

**Read these:** To see what structure each project type creates

---

## Key Concepts

### 1. State Management

**Pattern:** Single AppState instance passed throughout app

```python
# Initialize once
state = AppState()

# Pass to UI builder
build_main_view(page, state)

# Pass to event handlers
attach_handlers(page, state)

# All handlers share the same state
handlers = Handlers(page, controls, state)
```

**Benefits:**

- Single source of truth
- No prop drilling
- Easy to reset (state.reset())
- Clear data flow

---

### 2. Template System

**Flow:**

```
JSON Template(s)
    ↓
ConfigManager.load_config() (one or two templates)
    ↓
If both UI framework + project type selected:
    merge_folder_lists(fw_folders, pt_folders)
    ↓
Parse/merge → normalized folder dicts
    ↓
Store in state.folders
    ↓
Display in UI (flatten for display)
    ↓
Build time: use folder hierarchy
    ↓
Create actual folders
```

**Why FolderSpec?**

- Type-safe structure
- Recursive nesting support
- Easy serialization (to_dict/from_dict)
- Files + folders in one model

---

### 3. Async Pattern

**Problem:** UV/Git commands are blocking

**Solution:** Thread pool + async wrappers

```python
# UI handler (must be async for Flet)
async def on_build_project(self, e):
    # Run blocking function in thread pool
    result = await AsyncExecutor.run(build_project, config)
    # Update UI with result
```

**Why wrap_async()?**

```python
def wrap_async(coro_func):
    """Flet requires sync callbacks"""
    def wrapper(e):
        asyncio.create_task(coro_func(e))
    return wrapper

# Usage
button.on_click = wrap_async(handlers.on_build_project)
```

---

### 4. Validation Flow

**Real-time validation:**

```
User types in field
    ↓
on_change event fires
    ↓
Validate input
    ↓
Update state flags (path_valid, name_valid)
    ↓
Update warning banner or status
    ↓
User sees immediate feedback
```

**Build-time validation:**

```
Build button clicked
    ↓
_validate_inputs() checks all flags
    ↓
If invalid: show warning, don't build
    ↓
If valid: proceed with build
```

---

### 5. Error Handling with Rollback

**Pattern:** Try-except with cleanup

```python
try:
    # Create project directory
    full_path.mkdir()

    # Do all the work
    run_uv_init()
    setup_folders()
    install_packages()

    # Success!
    return BuildResult(success=True, ...)

except Exception as e:
    # ROLLBACK: Remove entire project
    cleanup_on_error(full_path)

    # Return failure
    return BuildResult(success=False, error=e)
```

**Why?**

- No partial projects left behind
- Clean failure state
- User can try again

---

### 6. Boilerplate Scaffolding (Smart File Content)

**Problem:** Template-created files were empty — users had to write all starter code from scratch.

**Solution:** `BoilerplateResolver` with fallback chain lookup

```python
# project_builder.py constructs the resolver
resolver = BoilerplateResolver(
    project_name=config.name,
    framework=config.framework if config.ui_project_enabled else None,
    project_type=config.project_type,
)

# filesystem_handler.py uses it when creating files
content = resolver.resolve("main.py")
if content is not None:
    file_path.write_text(content)  # Starter content!
else:
    file_path.touch()              # Graceful fallback
```

**Fallback chain priority:**
1. Framework-specific (e.g., `flet/main.py` — Flet hello world)
2. Project-type-specific (e.g., `django/settings.py`)
3. Common (e.g., `async_executor.py` — universal utility)
4. None → empty file (backward compatible)

**Extensibility:** Add a new `.py` file to `boilerplate/common/` or `boilerplate/ui_frameworks/flet/` — no code changes needed. `{{project_name}}` placeholders are automatically replaced.

---

### 7. Package Installation Logic

**UI Framework + Project Type:**

```python
# User selects:
- UI Project: Flet
- Project Type: Django

# Templates are MERGED (via template_merger.py):
# - Matching folders (e.g., config/) have files unioned
# - Unique folders from both are included

# build_project() installs:
1. Flet (from FRAMEWORK_PACKAGE_MAP)
2. Django (from PROJECT_TYPE_PACKAGE_MAP)

# Both packages added to pyproject.toml
# Both available in virtual environment
```

**Why separate maps?**

- UI frameworks: single package
- Project types: often multiple packages
- Clear separation of concerns

---

## Reading Order Recommendations

### For Complete Understanding

**Day 1: Foundation**

1. `app/utils/constants.py` - Understand constants
2. `app/core/models.py` - Understand data structures
3. `app/core/state.py` - Understand state management
4. `app/main.py` - See how it all starts

**Day 2: UI & Events**
5. `app/ui/components.py` - See how UI is built
6. `app/ui/dialogs.py` - See the beautiful dialog!
7. `app/handlers/event_handlers.py` - See how events are handled

**Day 3: Business Logic**
8. `app/core/validator.py` - Input validation
9. `app/core/config_manager.py` - Template loading
10. `app/core/project_builder.py` - Project creation orchestration

**Day 4: Operations**
11. `app/handlers/filesystem_handler.py` - Folder creation
12. `app/handlers/uv_handler.py` - UV commands
13. `app/handlers/git_handler.py` - Git commands

**Day 5: Advanced**
14. `app/utils/async_executor.py` - Async patterns
15. `app/handlers/handler_factory.py` - Async wrappers
16. `app/ui/theme_manager.py` - Theming

### For Specific Features

**"How does template loading work?"**

1. `app/config/templates/` - See JSON templates
2. `app/core/config_manager.py` - Template loading
3. `app/core/template_merger.py` - Template merging (when both selections active)
4. `app/core/models.py` - FolderSpec model
5. `app/handlers/event_handlers.py` - _reload_and_merge_templates()

**"How does project building work?"**

1. `app/core/project_builder.py` - Main orchestration
2. `app/core/boilerplate_resolver.py` - Smart file scaffolding
3. `app/handlers/filesystem_handler.py` - Folder creation
4. `app/handlers/uv_handler.py` - UV commands
5. `app/handlers/git_handler.py` - Git commands

**"How does the enhanced dialog work?"**

1. `app/ui/dialogs.py` - create_project_type_dialog()
2. `app/utils/constants.py` - PROJECT_TYPE_PACKAGE_MAP
3. `app/handlers/event_handlers.py` - _show_project_type_dialog()

**"How does package installation work?"**

1. `app/utils/constants.py` - Package maps
2. `app/core/project_builder.py` - Install logic
3. `app/handlers/uv_handler.py` - install_package()

---

## Final Thoughts

You've built something **amazing** here! From a simple idea ("let's try uv init") to a full-featured application with:

- **32 templates** across 11 UI frameworks and 21 project types
- **Automatic package installation** with UV
- **Beautiful, professional UI** with Flet
- **Template merging** for combined UI framework + project type selections
- **Comprehensive testing** (370 tests!)
- **Clean architecture** with clear separation of concerns
- **Modern patterns** (async, dataclasses, type hints)

The codebase is well-organized, thoroughly tested, and a great example of:

- ✅ Modern Python development
- ✅ Flet UI capabilities
- ✅ Clean architecture principles
- ✅ Comprehensive documentation

**Take your time reading through it** - there's a lot to learn and appreciate!

---

## Quick Reference Card

```plaintext
┌────────────────────────────────────────────────────┐
│           UV PROJECT CREATOR CHEAT SHEET            │
├────────────────────────────────────────────────────┤
│                                                     │
│  📍 Entry Point:                                    │
│     app/main.py → run()                             │
│                                                     │
│  🎨 UI Building:                                    │
│     app/ui/components.py → build_main_view()        │
│                                                     │
│  ⚡ Event Handling:                                 │
│     app/handlers/event_handlers.py → Handlers       │
│                                                     │
│  🏗️  Project Building:                              │
│     app/core/project_builder.py → build_project()   │
│                                                     │
│  📁 Folder Creation:                                │
│     app/handlers/filesystem_handler.py              │
│                                                     │
│  📦 Package Install:                                │
│     app/handlers/uv_handler.py → install_package()  │
│                                                     │
│  📋 Templates:                                      │
│     app/config/templates/ui_frameworks/             │
│     app/config/templates/project_types/             │
│     app/config/templates/boilerplate/ (scaffolding) │
│     app/core/template_merger.py (merging)           │
│                                                     │
│  💾 State:                                          │
│     app/core/state.py → AppState                    │
│                                                     │
│  🎯 Constants:                                      │
│     app/utils/constants.py → Everything!            │
│                                                     │
│  🧪 Tests:                                          │
│     tests/ → 370 tests, 100% passing!               │
│                                                     │
└────────────────────────────────────────────────────┘
```

## UV Project Creator — Cheat Sheet

| Area               | Location / Function                                                            |
| ------------------ | ------------------------------------------------------------------------------ |
| 📍 Entry Point      | `app/main.py` → `run()`                                                        |
| 🎨 UI Building      | `app/ui/components.py` → `build_main_view()`                                   |
| ⚡ Event Handling   | `app/handlers/event_handlers.py` → `Handlers`                                  |
| 🏗️ Project Building | `app/core/project_builder.py` → `build_project()`                              |
| 📁 Folder Creation  | `app/handlers/filesystem_handler.py`                                           |
| 📦 Package Install  | `app/handlers/uv_handler.py` → `install_package()`                             |
| 📋 Templates        | `app/config/templates/ui_frameworks/`<br>`app/config/templates/project_types/` |
| 💾 State            | `app/core/state.py` → `AppState`                                               |
| 🎯 Constants        | `app/utils/constants.py` → Everything                                          |
| 📝 Boilerplate       | `app/core/boilerplate_resolver.py` → `BoilerplateResolver`                      |
| 🧪 Tests            | `tests/` → 370 tests, 100% passing                                             |

**Happy reading!** 📚✨
