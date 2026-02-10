# Set up mutual capability for UI and other project types

Yesterday we added a new feature to the app created in this project - we added a
  checkox control other_projects_checkbox - which is created at line 210 in
  @app/ui/components.py. Clicking the checkbox opens an AlertDialog that gives us the
  opportunity to choose a project type other than the UI frameworks we originally had.
  We set it up so that each checkbox is mutually exclusive - only one can be chosen.
  But after thinking about it I think it would be better if we can choose both a UI
  framework and other project type so,for instance , we can create a web-scraping app
  that has a flet UI. Can you look into how to make that change? . Let me know pros and cons
   and how difficult it would be.
  ⎿  Read app/ui/components.py (406 lines)

⏺ Let me explore the current implementation to understand how the mutual exclusivity works
  and what would need to change.

⏺ Explore(Explore other_projects_checkbox implementation)
  ⎿  Done (15 tool uses · 60.7k tokens · 46s)

⏺ Excellent research. Here's my analysis:

## Current Implementation

  The mutual exclusivity is enforced in two places in `event_handlers.py`:

- `on_ui_project_toggle` (~line 425): When UI project is checked, it unchecks other project,
  clears selected_project_type
- `on_other_project_toggle` (~line 474): When other project is checked, it unchecks UI
  project, clears selected_framework, disables the framework dropdown

  Each path has its own independent state fields, templates, and package maps:
  Column 1: State
  UI Project: `create_ui_project`, selected_framework
  Other Project Type: `create_other_project`, selected_project_type
  ────────────────────────────────────────
  Column 1: Templates
  UI Project: `ui_frameworks/*.json`
  Other Project Type: `project_types/*.json`
  ────────────────────────────────────────
  Column 1: Packages
  UI Project: `FRAMEWORK_PACKAGE_MAP`
  Other Project Type: `PROJECT_TYPE_PACKAGE_MAP`
  Pros of Allowing Both

  1. Real-world usefulness - Your example is spot-on: a web scraper with a Flet UI, a data
  analysis project with a Streamlit dashboard, a Django project with PyQt admin tools, etc.
  2. More flexible project creation - Users get combined folder structures and all relevant
  packages installed
  3. No loss of functionality - Everything that works today still works; you're just removing
   a restriction

  Cons / Challenges

  1. Template merging - This is the main complexity. Both selections load a template that
  replaces state.folders. You'd need a merge strategy to combine two folder structures (e.g.,
   a Flet template + a FastAPI template). Conflicts are possible (both might define core/,
  utils/, tests/).
  2. Package conflicts - Two package sets get installed, which could have version
  incompatibilities (unlikely but possible).
  3. Confusing folder display - The merged structure could be large and harder for the user
  to understand at a glance.
  4. Build logic changes - project_builder.py currently installs UI framework packages OR
  project type packages. It would need to install both.

  Difficulty Assessment

  Moderate. The main pieces:

  1. Remove mutual exclusivity (~5 min) - Delete the unchecking logic in both toggle
  handlers. Trivial.
  2. Template merging (~1-2 hours) - Write a merge_folder_specs() function that intelligently
   combines two folder trees (merge matching folder names, concatenate files lists, recurse
  into subfolders). This is the bulk of the work.
  3. Build logic (~15 min) - Update project_builder.py to install both framework packages AND
   project type packages when both are selected.
  4. UI tweaks (~15 min) - Re-enable the framework dropdown even when other project is
  checked, and vice versa.
  5. Tests (~30 min) - Add tests for the merge logic and the combined build path.

  The template merging is the only non-trivial part. Everything else is straightforward. Want
   me to plan out the implementation?

## Plan: Allow Both UI Framework + Other Project Type Selection

 Context

 Currently create_ui_project_checkbox and other_projects_checkbox are mutually exclusive —
 checking one unchecks the other and clears its state. This prevents useful combinations
 like a web scraper with a Flet UI, or a data analysis project with a Streamlit dashboard.

 The build logic in project_builder.py (lines 85-94) already supports both — framework and
 project type packages are installed via independent if blocks. The only barriers are: (1)
 the mutual exclusivity enforcement in the UI handlers, and (2) template loading overwrites
 state.folders instead of merging.

 Files to Change
 File: `app/core/template_merger.py`
 Action: CREATE
 Description: Pure merge functions (~60 lines)
 ────────────────────────────────────────
 File: `app/handlers/event_handlers.py`
 Action: MODIFY
 Description: Remove mutual exclusivity, add unified template reload
 ────────────────────────────────────────
 File: `tests/core/test_template_merger.py`
 Action: CREATE
 Description: ~25 tests for merge logic
 ────────────────────────────────────────
 File: `tests/handlers/test_event_handlers.py`
 Action: MODIFY
 Description: Rewrite 3 tests, add ~8 new tests
 No changes needed to: state.py, models.py, project_builder.py, components.py,
 config_manager.py, constants.py.

 Implementation Steps

 Step 1: Create `app/core/template_merger.py`

 Pure utility module with no UI/state dependencies. Three public functions:

- `normalize_folder(folder)` — Converts any folder form (string, dict, FolderSpec) to a
 canonical dict with keys: name, create_init, root_level, subfolders (list), files (list).
- `merge_folder_lists(primary, secondary)` — Merges two folder lists:
  - Normalize both lists
  - Match folders by name (case-sensitive) at each level
  - Matching folders: recursively merge subfolders, union files (deduplicated), OR booleans
  (root_level, create_init)
  - Non-matching: include both (primary order first, secondary-only appended)
  - Returns list of dicts
- `_merge_files(primary_files, secondary_files)` — Union two file lists, deduplicated,
 primary order preserved.

 Step 2: Modify `app/handlers/event_handlers.py`

 2a. Add new method `_reload_and_merge_templates()`

 Central method that all template-changing code paths call:

 `def _reload_and_merge_templates(self) -> None:`
     1. If framework selected → load framework template folders
     2. If project type selected → load project type template folders
     3. If both → merge_folder_lists(framework_folders, project_type_folders)
     4. If only one → use that one
     5. If neither → load default template
     6. Clear selected_item_path/type (folder structure changed)
     7. Call_update_folder_display()

 When both are merged, set a status message like "Merged templates: flet + Django".

 2b. Remove mutual exclusivity from `on_ui_project_toggle` (lines 433-437)

 Delete these lines:

 ```python
 if self.state.create_ui_project:
     self.state.create_other_project = False
     self.controls.other_projects_checkbox.value = False
     self.state.selected_project_type = None
```

 Replace `_load_framework_template()` calls (lines 448, 453) with
 `_reload_and_merge_templates()`.

 2c. Remove mutual exclusivity from `on_other_project_toggle` (lines 482-488)

 Delete these lines:

 ```python
 self.state.create_ui_project = False
 self.controls.create_ui_project_checkbox.value = False
 self.state.selected_framework = None
 self.controls.ui_framework_dropdown.value = None
 self.controls.ui_framework_dropdown.disabled = True
```

 Replace `_load_project_type_template(None)` call (line 499) with
 `_reload_and_merge_templates()`.

 2d. Update `on_framework_change` (line 467)

 Replace `_load_framework_template(framework)` with`_reload_and_merge_templates()`.

 2e. Update `_show_project_type_dialog.on_select` (line 511)

 Replace `_load_project_type_template(project_type)` with `_reload_and_merge_templates()`.

 2f. Update `on_reset` (line 812)

 Replace `_load_framework_template(None)` with `_reload_and_merge_templates()`.

 2g. Keep `_load_framework_template` and `load_project_type_template` as-is

 They still serve as simple helpers. _reload_and_merge_templates will replicate their
 loading logic internally (calling config_manager.load_config directly) rather than
 delegating to them, since it needs the raw folder lists before deciding whether to merge.

### Step 3: Create `tests/core/test_template_merger.py`

 ~25 tests across 3 classes:

- TestNormalizeFolder (~7 tests): string, minimal dict, full dict, nested subfolders,
 FolderSpec, None→empty list for subfolders/files
- TestMergeFiles (~5 tests): disjoint, identical, partial overlap, empty primary, both
 empty
- TestMergeFolderLists (~13 tests): empty inputs, no overlap, full overlap, partial
 overlap, primary order preserved, root_level/create_init OR logic, recursive subfolders,
 files union, mixed string+dict types, real template integration test (load flet.json +
 django.json and verify merge)

 Step 4: Update tests/handlers/test_event_handlers.py

 Rewrite 3 existing tests:

 1. test_on_other_project_toggle_checked (line 544) — Remove assertions that UI project
 state was cleared (lines 559-563). Instead assert UI project state is unchanged.
 2. test_on_other_project_toggle_mutual_exclusion (line 608) — Rewrite to test that checking
  Other does NOT uncheck UI. Assert state.create_ui_project remains True, selected_framework
  remains "flet".
 3. test_ui_project_toggle_unchecks_other_project (line 728) — Rewrite to test that checking
  UI does NOT uncheck Other. Assert state.create_other_project remains True,
 selected_project_type remains "django".

 Add ~8 new tests:

- Both checkboxes can be checked simultaneously
- _reload_and_merge_templates with both selected (mocked config_manager, verify
 merge_folder_lists is called)
- _reload_and_merge_templates with only framework selected
- _reload_and_merge_templates with only project type selected
- _reload_and_merge_templates with neither selected (loads default)
- Framework change triggers merge when both selected
- Reset works correctly with both checked
- _reload_and_merge_templates clears selected_item_path/selected_item_type

 Step 5: Run full test suite

- pytest — all existing tests + new tests should pass
- Verify no regressions in the 184+ existing tests

#### Edge Cases Handled

- One selected, other not yet chosen: _reload_and_merge_templates uses whichever template
 is available, no merge needed
- Both templates define same folder (e.g. core/, tests/): merged recursively, files unioned
- root_level conflict: OR logic — if either template wants root level, merged result is
 root level
- User adds/removes folders manually then changes selection: folders are reloaded from
 templates (matches current behavior)
- Dialog cancelled with no selection: existing on_close logic unchecks the checkbox,
 _reload_and_merge_templates not called

### Verification

 1. Run pytest — all tests pass (existing + new)
 2. Launch app with uv run create_project
 3. Check "Create UI Project", select Flet → folder display shows Flet template
 4. Check "Create Other Project Type", select Django → folder display shows merged Flet +
 Django folders
 5. Verify merged display has folders from both templates, no duplicates for common folders
 like core/
 6. Uncheck UI project → folder display reverts to Django-only template
 7. Re-check UI project, select a different framework → display updates with new merge
 8. Click Reset → both checkboxes unchecked, default template loaded
 9. Build a project with both selected → verify both framework package and project type
 packages are installed
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

 Claude has written up a plan and is ready to execute. Would you like to proceed?

 ❯ 1. Yes, clear context and auto-accept edits (shift+tab)
   2. Yes, auto-accept edits
   3. Yes, manually approve edits
   4. Type here to tell Claude what to change

## Summary

### Files Created

- app/core/template_merger.py — Pure utility module (~60 lines) with three functions:
  - normalize_folder() — Converts string, dict, or FolderSpec to a canonical dict
  - _merge_files() — Unions two file lists with deduplication
  - merge_folder_lists() — Recursively merges two folder lists by name, OR'ing booleans and
   unioning files
- tests/core/test_template_merger.py — 25 tests across 3 test classes covering all merge
  logic

### Files Modified

- app/handlers/event_handlers.py:
  - Added import for merge_folder_lists
  - Added _reload_and_merge_templates() method — central method that loads one or both
  templates and merges them when both are active
  - Removed mutual exclusivity from on_ui_project_toggle (deleted 4 lines that cleared
  other project state)
  - Removed mutual exclusivity from on_other_project_toggle (deleted 5 lines that cleared
  UI project state)
  - Updated on_framework_change, _show_project_type_dialog.on_select, and on_reset to use
  _reload_and_merge_templates()
- tests/handlers/test_event_handlers.py:
  - Rewrote 3 tests: removed assertions about mutual exclusivity, replaced with assertions
  that the other checkbox state is unchanged
  - Added 8 new tests: both-checked state, merge behavior with various selections,
  framework change triggers merge, reset with both checked, selection clearing

### Test Results

- 276 tests collected, 251 passed, 25 failed (all pre-existing async plugin issues,
  unrelated to this change)
- All 33 new tests pass
- No regressions in existing tests

## CLAUDE.md has been updated across all relevant sections

- Header: Version bumped to 0.2.2, date to February 8, 2026
- Key Features: Added combined selection with template merging
- Current Status: Updated template system description and test count (276)
- Working UI Features: Updated checkbox/dropdown descriptions to reflect
  non-mutual-exclusivity
- Recent Work: Added new entry for the combined selection feature
- Directory Structure: Added template_merger.py and test_template_merger.py, updated test
  counts
- Core Modules: Added template_merger.py description
- Handlers description: Added _reload_and_merge_templates() and
  _load_project_type_template()
- Template System: Added new "Template Merging" subsection with merge logic explanation
- Test Directory: Updated counts (122 core, 84 handlers, 13 test files)
- Test Coverage: Updated to 276 tests / 251 passing
- Test Highlights: Added test_template_merger.py, updated test_event_handlers.py count and
  description
- Code Coverage: Added template_merger.py (100%) to excellent coverage list
- File Statistics: Updated to 32 app files, 13 test files, 276 tests
- Version History: Added v0.2.2 entry, demoted v0.2.1 from "Current"
- All clean. Both files are updated. Here's a summary of what changed:

  FINAL_SUMMARY.md:
  - Date updated to February 8, 2026
  - Added "Template merging" bullet under Automatic Package Installation
  - Test count updated from 243 to 276 (in 4 locations)
  - File count updated from 41 to 45
  - Added "Template Merging" milestone (#8) to the journey

  CODE_READING_GUIDE.md:
  - Date updated to February 8, 2026
  - Added template_merger.py to "How templates work" quick start
  - Updated Template Loading Flow to show _reload_and_merge_templates() with merge branching
  - Updated Project Type Selection Flow to note no longer mutually exclusive, and show merge
  path
  - Added full template_merger.py file-by-file guide section (after config_manager.py)
  - Updated event_handlers description: added_reload_and_merge_templates() to Template
  Loading section
  - Updated attach_handlers code example to use_reload_and_merge_templates()
  - Updated Template System key concept flow diagram to include merge step
  - Updated Package Installation Logic to mention template merging
  - Updated "How does template loading work?" reading order to include template_merger.py
  - Updated all test count references from 243 to 276
  - Added template merging to the final summary bullet list
  - Added template_merger.py to the cheat sheet
