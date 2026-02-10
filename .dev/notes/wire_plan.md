# Wire up the controls

 Plan: Wire Up UI Controls with Event Handlers and State Management

 Overview

 Connect the UI controls defined in components.py with event handlers in
 event_handlers.py and state management in state.py, following the pattern
 established in .dev/yt_event_handlers.py.

 Files to Modify/Create

 1. app/core/state.py - Define AppState Attributes

 Pattern from: app/core/state example.py

 @dataclass
 class AppState:
     # Path and project settings
     project_path: str = "/Users/tim/Projects"  # Default from
 DEFAULT_PROJECT_ROOT
     project_name: str = ""  # Name of the project to create

     # Options
     selected_python_version: str = "3.14"  # Default from constants
     initialize_git: bool = False  # Whether to create git repo
     create_ui_project: bool = False  # Whether it's a UI project
     selected_framework: Optional[str] = None  # Selected UI framework

     # Folder management
     folders: list = field(default_factory=list)  # Current folder
 structure
     auto_save_folders: bool = False  # Auto-save folder changes to config

     # UI state
     is_dark_mode: bool = True

     # Validation state
     path_valid: bool = False
     name_valid: bool = False

     def reset(self) -> None:
         """Reset to initial values (preserve is_dark_mode)."""

 2. app/core/__init__.py - Export AppState

 from app.core.state import AppState
 __all__ = ["AppState"]

 1. app/handlers/__init__.py - Export attach_handlers

 from app.handlers.event_handlers import attach_handlers
 __all__ = ["attach_handlers"]

 1. app/handlers/event_handlers.py - Implement Event Handlers

 Structure (following .dev/yt_event_handlers.py pattern):

 class Handlers:
     def __init__(self, page: ft.Page, controls: Controls, state:
 AppState):
         self.page = page
         self.controls = controls
         self.state = state
         self.config_manager = ConfigManager()

     # --- Path & Name Handlers ---
     async def on_browse_click(self, e): ...
     async def on_path_change(self, e): ...
     async def on_project_name_change(self, e): ...

     # --- Options Handlers ---
     async def on_python_version_change(self, e): ...
     async def on_git_toggle(self, e): ...
     async def on_ui_project_toggle(self, e): ...
     async def on_framework_change(self, e): ...

     # --- Folder Management Handlers ---
     async def on_add_folder(self, e): ...
     async def on_remove_folder(self, e): ...
     async def on_auto_save_toggle(self, e): ...

     # --- Main Actions ---
     async def on_build_project(self, e): ...
     async def on_reset(self, e): ...
     async def on_exit(self, e): ...

     # --- UI Feature Handlers ---
     async def on_theme_toggle(self, e): ...
     async def on_help_click(self, e): ...

     # --- Helper Methods ---
     def _set_status(self, message, status_type, update=False): ...
     def _update_folder_display(self): ...
     def _validate_inputs(self) -> bool: ...

 def attach_handlers(page: ft.Page, state: AppState) -> None:
     controls = page.controls_ref
     handlers = Handlers(page, controls, state)

     # Attach all handlers to controls
     controls.browse_button.on_click = handlers.on_browse_click
     controls.project_path_input.on_change = handlers.on_path_change
     # ... etc

 5. app/ui/components.py - Update build_main_view Signature

 Change line 95 from:
 def build_main_view(page: ft.Page) -> ft.Control:
 To:
 def build_main_view(page: ft.Page, state: AppState) -> ft.Control:

 Also need to:

- Set initial values from state (dropdown values, checkbox values)
- Set project_path_input.value = state.project_path (default:
 /Users/tim/Projects)
- Set python_version_dropdown.value = state.selected_python_version
 (default: "3.14")
- Set ui_framework_dropdown.disabled = True initially (enabled when UI
 project checked)
- Store state reference on page: page.state_ref = state
- Add FilePicker to page overlay for Browse functionality:
 controls.file_picker = ft.FilePicker()
 page.overlay.append(controls.file_picker)

 1. app/ui/components.py - Add file_picker to Controls class

 Add to Controls class (around line 34):
 self.file_picker: ft.FilePicker

 1. app/main.py - Fix Import Paths

 Current (broken):
 from core import AppState
 from handlers import attach_handlers
 from ui.components import build_main_view

 Should be:
 from app.core.state import AppState
 from app.handlers.event_handlers import attach_handlers
 from app.ui.components import build_main_view

 Implementation Order

 Phase 1: State Foundation

 1. app/core/state.py - Define all AppState attributes
 2. app/core/init.py - Add export

 Phase 2: Event Handlers Skeleton

 1. app/handlers/event_handlers.py - Create Handlers class with all methods
  (stubs first)
 2. app/handlers/init.py - Add export

 Phase 3: Wire Up Components

 1. app/ui/components.py - Update signature, set initial values from state
 2. app/main.py - Fix imports

 Phase 4: Implement Handlers (one at a time)

 1. Path/name input validation handlers (browse, path change, name change)
 2. Options dropdown/checkbox handlers (python version, git, UI project,
 framework)
 3. Folder display helper method (_update_folder_display)
 4. Build project handler (main action)
 5. Reset, exit, theme, help handlers
 6. Stub add/remove folder handlers (defer implementation)

 Control → Handler Mapping
 ┌────────────────────────────┬───────────┬──────────────────────────┐
 │          Control           │   Event   │      Handler Method      │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ browse_button              │ on_click  │ on_browse_click          │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ project_path_input         │ on_change │ on_path_change           │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ project_name_input         │ on_change │ on_project_name_change   │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ python_version_dropdown    │ on_change │ on_python_version_change │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ create_git_checkbox        │ on_change │ on_git_toggle            │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ create_ui_project_checkbox │ on_change │ on_ui_project_toggle     │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ ui_framework_dropdown      │ on_change │ on_framework_change      │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ add_folder_button          │ on_click  │ on_add_folder            │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ remove_folder_button       │ on_click  │ on_remove_folder         │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ auto_save_folder_changes   │ on_change │ on_auto_save_toggle      │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ build_project_button       │ on_click  │ on_build_project         │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ reset_button               │ on_click  │ on_reset                 │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ exit_button                │ on_click  │ on_exit                  │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ help_button                │ on_click  │ on_help_click            │
 ├────────────────────────────┼───────────┼──────────────────────────┤
 │ theme_toggle_button        │ on_click  │ on_theme_toggle          │
 └────────────────────────────┴───────────┴──────────────────────────┘
 Key Dependencies to Use

- Validation: app/core/validator.py - validate_project_name(),
 validate_path()
- Template Loading: app/core/config_manager.py -
 ConfigManager.load_config(framework)
- Async Wrapper: app/handlers/handler_factory.py - async_handler() for
 handlers with args
- Project Building: app/core/project_builder.py - Main build orchestration
- Constants: app/utils/constants.py - PYTHON_VERSIONS, UI_FRAMEWORKS,
 DEFAULT_PROJECT_ROOT
- Theme: app/ui/theme_manager.py - get_theme_colors(is_dark)

 Folder Display Logic

 When on_framework_change or on_ui_project_toggle fires:

 1. Load template via ConfigManager.load_config(framework)
 2. Parse folder structure from settings["folders"]
 3. Create Row controls for each folder (with indentation for subfolders)
 4. Update controls.subfolders_container.content.controls
 5. Call page.update()

 Verification

 1. Run uv run python -m app.main - App should launch without import errors
 2. Enter project path → status should show validation result
 3. Enter project name → status should show validation result
 4. Toggle "Create UI Project" → framework dropdown should enable/disable
 5. Change framework → folder list should update
 6. Click "Build Project" with valid inputs → project should be created
 7. Click "Reset" → all fields should clear
 8. Click "Exit" → app should close

 Decisions Made

 1. Default path: /Users/tim/Projects - TextField shows this initially,
 Browse button opens FilePicker to change it
 2. Add/Remove folders: Deferred - stub handlers now, implement interaction
  pattern later
 3. Browse button: Uses ft.FilePicker.get_directory_path_async() to open
 directory picker dialog

 Deferred for Later

- Add folder button interaction (dialog or inline)
- Remove folder button interaction (selection mechanism)
- Auto-save folder changes functionality
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

 Claude has written up a plan and is ready to execute. Would you like to
 proceed?

 ❯ 1. Yes, clear context and auto-accept edits (shift+tab)
   2. Yes, auto-accept edits
   3. Yes, manually approve edits
   4. Type here to tell Claude what to change

## Summary

All components are wired up correctly. Here's a summary of what was
  implemented:

  Implementation Summary

  Files Modified/Created:

  1. app/core/state.py - Defined AppState with all required attributes:
    - project_path, project_name, selected_python_version
    - initialize_git, create_ui_project, selected_framework
    - folders, auto_save_folders, is_dark_mode
    - path_valid, name_valid
    - reset() method
  2. app/core/__init__.py - Added AppState export
  3. app/handlers/__init__.py - Added attach_handlers export
  4. app/handlers/event_handlers.py - Full implementation with:
    - Handlers class with all handler methods
    - Path/name validation handlers
    - Options dropdown/checkbox handlers
    - Framework template loading
    - Build project with async execution
    - Reset, exit, theme toggle, help handlers
    - Folder display helper method
    - attach_handlers() function to wire up all controls
  5. app/ui/components.py - Updated to:
    - Accept state parameter in build_main_view()
    - Initialize all controls with values from state
    - Add file_picker to Controls class and page overlay
    - Store state_ref on page
    - Add theme toggle button to appbar
  6. app/main.py - Fixed imports to use absolute paths
  7. Additional import fixes in:
    - app/core/config_manager.py
    - app/core/project_builder.py
    - app/core/ui_state_sync.py
    - app/ui/dialogs.py

  Control → Handler Mapping:

  All 15 controls are wired to their respective handlers as specified in the
   plan.

  Deferred Features:

- Add/remove folder functionality (stub handlers implemented)
- Auto-save folder changes to config (handler implemented, functionality
  deferred)
