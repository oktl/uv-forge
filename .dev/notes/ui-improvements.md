# UI Improvements

Can you think of any other UI improvements/niceties that might be good to have?

⏺ Here are a few ideas that come to mind, keeping the scope reasonable:

  1. Build button stays disabled until inputs are valid — Right now you can click Build with an empty project name and it validates after the click. Disabling the button (and maybe graying it out with a tooltip like "Enter a project name") until both path and name are valid gives instant feedback and prevents wasted clicks.
  2. Confirmation summary before build — A quick dialog showing "About to create my-project at /Users/tim/Projects with Flet, git init, 8 folders, 12 files — proceed?" Prevents accidental builds and lets the user sanity-check everything in one glance.
  3. Snackbar for success/error instead of just status text — The status bar at the bottom is easy to miss. A Flet SnackBar that pops up briefly for "Project created successfully!"
  (green) or errors (red) would be more noticeable for important outcomes.
  4. Folder/file count in the folder display header — Change "App Subfolders:" to something like "App Subfolders: 6 folders, 14 files" so the user can see at a glance how big the scaffold will be, especially after template merging.
  5. Visual indicator on the path/name fields for validation state — A green checkmark icon or red X suffix on the text fields as you type, rather than only showing a warning banner after focus leaves the field.
  6. Keyboard shortcut for Build — Something like Enter (when not in a text field) or a visible shortcut hint on the button. Small but speeds up repeated use.

  Any of those catch your eye, or would you rather go a different direction?

## Plan: 6 UI Improvements for UV Project Creator

 Context

 The app works well functionally but has some UX gaps: the Build button is always clickable even with invalid inputs, there's no
 build confirmation, status messages are easy to miss, folder counts aren't visible, text fields lack validation indicators, and
 there are no keyboard shortcuts. These 6 improvements address each gap.

 ---
 Implementation Order

 Features are ordered by dependency: 4 → 5 → 1 → 2 → 3 → 6

 ---
 Feature 4: Folder/File Count in Subfolders Label

 Change "App Subfolders:" to "App Subfolders: 6 folders, 14 files"

 app/handlers/event_handlers.py

- Add _count_folders_and_files(folders) static method to Handlers — recursively counts folders and files from state.folders
 (handles both FolderSpec objects and dicts)
- Modify _update_folder_display() (line 207) — after building controls, update self.controls.app_subfolders_label.value with
 counts

 tests/handlers/test_event_handlers.py

- Add app_subfolders_label = MockText() to MockControls
- Add tests for _count_folders_and_files (empty, flat, nested, FolderSpec)

 ---
 Feature 5: Validation Icons on Path/Name Fields

 Green checkmark when valid, red X when invalid, nothing when empty

 app/handlers/event_handlers.py

- Add _set_validation_icon(field, is_valid) static method — sets field.suffix to ft.Icon(CHECK_CIRCLE, GREEN), ft.Icon(CANCEL,
 RED), or None
- Modify on_path_change() (line 359) — call _set_validation_icon after validation: None when empty, True/False otherwise
- Modify on_project_name_change() (line 382) — same pattern, including the "already exists" case
- Modify on_browse_click() (line 337) — call _set_validation_icon after path validation
- Modify on_reset() — set path icon to True (default path is valid), name icon to None (empty)

 tests/handlers/test_event_handlers.py

- Add suffix attribute to MockControl
- Add tests for the icon helper and that handlers set icons correctly

 ---
 Feature 1: Build Button Disabled Until Inputs Valid

 Button starts disabled/dimmed; enables when both path and name are valid

 app/ui/components.py

- Update build_project_button constructor (line 256) — add disabled=True, opacity=0.5

 app/handlers/event_handlers.py

- Add _update_build_button_state() method — sets disabled, opacity (0.5/1.0), and tooltip based on state.path_valid and
 state.name_valid
- Call from: on_path_change(), on_project_name_change(), on_browse_click(), on_reset(), end of _execute_build() (replacing the
 existing button.disabled = False)
- Call from attach_handlers() (after line 970) for initial state

 tests/handlers/test_event_handlers.py

- Add opacity and tooltip attributes to MockControl
- Add tests for _update_build_button_state (both valid, name invalid, path invalid)

 ---
 Feature 2: Confirmation Summary Dialog Before Build

 Show project details for user review before building

 app/ui/dialogs.py

- Add create_build_summary_dialog(...) factory function — displays project name, path, python version, git, framework, project
 type, starter files, folder/file counts. Build + Cancel buttons.

 app/handlers/event_handlers.py

- Extract build logic from on_build_project() into new _execute_build() async method
- Move wrap_async from inside attach_handlers() to module level (line ~29) so both attach_handlers and on_build_project can use it
- Rewrite on_build_project() to: validate → count folders/files → show confirmation dialog → on Build click call _execute_build(),
  on Cancel close dialog

 tests/ (both handler and dialog test files)

- Add tests for create_build_summary_dialog (basic, with framework, with project type)
- Add tests for dialog flow in on_build_project

 ---
 Feature 3: SnackBar for Success/Error After Build

 Auto-dismissing notification for build outcomes

 app/handlers/event_handlers.py

- Add _show_snackbar(message, is_error) method — creates ft.SnackBar with GREEN_600 or RED_600 bgcolor, calls
 self.page.open(snackbar) (Flet 0.80+ API)
- Call from _execute_build() after build completes (both success and error paths)

 tests/handlers/test_event_handlers.py

- Add open() method and opened_controls list to MockPage
- Add tests for snackbar creation and correct bgcolor

 ---
 Feature 6: Keyboard Shortcut (Ctrl+Enter / Cmd+Enter)

 Trigger build via keyboard when inputs are valid

 app/handlers/event_handlers.py

- Add on_keyboard_event(e) async method to Handlers — checks e.key == "Enter" and (e.ctrl or e.meta), verifies both inputs valid AND button not already disabled (prevents double-trigger during build), then calls on_build_project(e)
- In attach_handlers(), add: page.on_keyboard_event = wrap_async(handlers.on_keyboard_event)
- Build button tooltip (in _update_build_button_state) already includes "(Ctrl+Enter)" hint when enabled

 tests/handlers/test_event_handlers.py

- Add tests: Ctrl+Enter triggers build, Cmd+Enter triggers build, ignored when invalid, ignored when button disabled, other keys
 ignored

 ---
 Files Modified (summary)
 ┌───────────────────────────────────────┬─────────────────────────────────────────────────────────────────────┐
 │                 File                  │                               Changes                               │
 ├───────────────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
 │ app/handlers/event_handlers.py        │ 6 new methods, 6 modified methods, wrap_async moved to module level │
 ├───────────────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
 │ app/ui/dialogs.py                     │ 1 new function (create_build_summary_dialog)                        │
 ├───────────────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
 │ app/ui/components.py                  │ 2 lines added to build button constructor                           │
 ├───────────────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
 │ tests/handlers/test_event_handlers.py │ Mock updates + ~20-25 new tests                                     │
 └───────────────────────────────────────┴─────────────────────────────────────────────────────────────────────┘
 No changes to app/main.py or app/core/state.py.

 ---
 Existing Code to Reuse

- _set_status() / _set_warning() — keep as-is, SnackBar is supplementary
- _validate_inputs() — still called first in on_build_project
- state.path_valid / state.name_valid — already tracked, just not consumed by the button
- Dialog pattern: page.overlay.append(dialog) + dialog.open = True + page.update()
- FolderSpec dataclass (app/core/models.py:13) — .files, .subfolders, .name attributes
- get_theme_colors() from app/ui/theme_manager.py — for dialog theming
- UIConfig from app/ui/ui_config.py — for dialog sizing constants

 ---
 Verification

 1. uv run pytest — all existing tests pass + new tests pass
 2. Manual: launch app (uv run create_project), verify:

- Build button starts dimmed/disabled
- Type a valid name → button enables, name field gets green checkmark
- Type invalid name → button stays disabled, name field gets red X
- Clear name → button disables, icon clears
- Click Build → confirmation dialog shows correct summary
- Click Cancel in dialog → nothing happens
- Click Build in dialog → project builds, green SnackBar appears
- Press Ctrl+Enter with valid inputs → same as clicking Build
- Click Reset → button disables, icons clear, labels reset
- Folder label shows accurate counts after template load/change
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

 Claude has written up a plan and is ready to execute. Would you like to proceed?

 ❯ 1. Yes, clear context and auto-accept edits (shift+tab)
   2. Yes, auto-accept edits
   3. Yes, manually approve edits
   4. Type here to tell Claude what to change

## UI Improvement Results

All 6 features are implemented. Here's a summary of what was done:

__Files modified:__
  File: `app/handlers/event_handlers.py`
  Changes: 6 new methods (`_count_folders_and_files`, `_set_validation_icon`,`_update_build_button_state`, `_show_snackbar`, `_execute_build, on_keyboard_event`), `wrap_async` moved to module level, `on_build_project` refactored to show confirmation dialog, validation icons + build button state calls added to 5 existing handlers
  ────────────────────────────────────────
  File: `app/ui/dialogs.py`
  Changes: 1 new function (`create_build_summary_dialog`)
  ────────────────────────────────────────
  File: `app/ui/components.py`
  Changes: Build button starts `disabled=True, opacity=0.5`
  ────────────────────────────────────────
  File: tests/handlers/test_event_handlers.py
  Changes: Mock classes updated (suffix, opacity, tooltip, page.open()), app_subfolders_label added to MockControls, 25 new tests
  Test results: 362 passed (55 new tests added across all files), 6 pre-existing failures in validator tests (unchanged).

## Feature summary

  1. Build button disabled until both path and name are valid (dimmed at 50% opacity with tooltip hint)
  2. Confirmation dialog shows project summary (name, path, python version, git, framework, type, folder/file counts) before build
  3. SnackBar notifications auto-dismiss green/red for build success/error
  4. Folder/file counts displayed in the "App Subfolders: 6 folders, 14 files" label
  5. Validation icons — green checkmark when valid, red X when invalid, cleared when empty
  6. Ctrl+Enter / Cmd+Enter keyboard shortcut triggers build (tooltip shows hint when button is enabled)
