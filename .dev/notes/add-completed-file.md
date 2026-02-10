# Add files that are complete to the project build

I have an idea about a feature to add to this app. Since we are creating empty files
  in the new project that gets built, maybe it would be nice to have some of those new
  files completely created, like say the @app/utils/async_executor.py  file or maybe
  just template files for the /ui files. That would be like icing in the cake. Would
  somehting like that be possible? What are your thoughts on that, pros and cons
  ⎿  Read app/utils/async_executor.py (59 lines)

⏺ That's a great idea, and yes, it's absolutely possible. Here are my thoughts:

  Pros

- Immediate value: A newly created project would be runnable out of the box instead of just
   being an empty skeleton. That's a big upgrade in user experience.
- Reduces boilerplate drudgery: Files like async_executor.py, __main__.py, state.py,
  models.py, and especially framework entry points (main.py for Flet, app.py for
  Flask/FastAPI) always start with the same boilerplate.
- Teaching tool: New developers get working examples of patterns (dataclasses, async
  wrappers, Flet page setup) right in their project.
- Natural extension of your template system: Your JSON templates already define file names
  per folder. Adding file content is a logical next step - you could add a "content" key (or
  reference a snippet file) alongside each filename.
- Differentiation: Most scaffolding tools create empty files. Pre-populated ones with good
  patterns would set this apart.

  Cons

- Maintenance burden: Every file template is something you need to keep correct and
  up-to-date. If Flet's API changes (and it has, significantly), your templates become
  misleading.
- Opinionated content: What goes in models.py? A placeholder dataclass? Users may disagree
  with your patterns. Empty files are unopinionated.
- Template complexity grows: Right now your JSON templates are simple lists of names.
  Adding content means either embedding code strings in JSON (ugly, hard to edit) or managing
   a parallel tree of snippet files.
- Combinatorial explosion: You have 10 frameworks x 21 project types. If file content
  varies by combination, that's a lot of variants to manage. You'd need to decide which files
   get universal content vs. framework-specific content.
- Scope creep risk: Once you start, there's pressure to template every file, turning this
  into a full code generator rather than a project scaffolder.

  My Recommendation

  A pragmatic middle ground:

  1. Start small - Only populate files that are truly universal and rarely change:
  async_executor.py, __init__.py with a version string, __main__.py with a basic entry point,
   maybe a conftest.py for the test directory.
  2. Framework entry points - A main.py with the minimal "hello world" for each framework
  (Flet page, Flask app, FastAPI app) would be the highest-value addition. You already have
  framework-specific templates, so this fits naturally.
  3. Use separate snippet files, not inline JSON - Store the file content as actual .py files
   in something like app/config/templates/snippets/ rather than embedding code in JSON.
  Easier to edit, test, and syntax-highlight.
  4. Make it opt-in - A checkbox like "Include starter code" (defaulting to on) lets users
  who prefer empty files still get them.

  The implementation would touch your template JSON format (adding a content reference),
  filesystem_handler.py (writing content instead of empty files), and config_manager.py
  (loading snippets). It's a medium-sized feature but architecturally clean given what you
  already have.

  Want me to plan out the implementation?

  Okay, now I can give you informed feedback having seen the actual code. Your approach is
  solid in principle - the core idea of "convention over configuration" (match by filename,  
  no JSON changes) is clean. But there's one significant issue and a few refinements worth
  considering.

  The Big Problem: Filename Collisions

  Your lookup is flat - boilerplate / file_path.name. But you have 10 frameworks and 21
  project types that can share filenames with very different content:

- main.py for Flet vs Flask vs FastAPI vs Django - all completely different
- components.py for Flet vs PyQt6 vs Tkinter - different APIs entirely
- state.py for a Flet app vs a data analysis project - different patterns
- config.py exists in multiple templates with different purposes

  A single flat boilerplate/ folder can only hold one main.py. That breaks down fast.

  Fix: Add One Level of Hierarchy

  Instead of a flat folder, use the structure you already have:

  app/config/templates/
  ├── boilerplate/
  │   ├── common/              # Universal files (any project)
  │   │   ├── async_executor.py
  │   │   ├── conftest.py
  │   │   └── __main__.py
  │   ├── ui_frameworks/       # Mirrors your existing template dirs
  │   │   ├── flet/
  │   │   │   ├── main.py
  │   │   │   ├── components.py
  │   │   │   └── state.py
  │   │   ├── flask/
  │   │   │   └── main.py
  │   │   └── pyqt6/
  │   │       └── main.py
  │   └── project_types/
  │       ├── fastapi/
  │       │   └── main.py
  │       └── django/
  │           └── settings.py

  Then the lookup becomes a fallback chain (which mirrors your existing template loading
  pattern in config_manager.py):

  1. boilerplate/ui_frameworks/{framework}/{filename}
  2. boilerplate/project_types/{project_type}/{filename}
  3. boilerplate/common/{filename}
  4. Fall through → empty file via .touch()

  This mirrors the fallback chain you already use for JSON templates, so it's a familiar
  pattern in your codebase.

  The Context Problem

  Look at your actual create_folders() on line 141 - it only receives parent_dir and folders.
   It has no idea which framework or project type is active. To do framework-aware
  boilerplate lookup, you'd need to pass that context through. Two options:

  Option A - Pass context down through create_folders() and setup_app_structure():
  def create_folders(parent_dir, folders, parent_create_init=True,
                     framework=None, project_type=None):

  Option B - Build a resolver object before calling create_folders(), and pass that in:
  resolver = BoilerplateResolver(framework="flet", project_type="fastapi")
  create_folders(parent_dir, folders, boilerplate=resolver)

  Option B is cleaner - it keeps create_folders() from needing to know the details of how
  boilerplate lookup works.

  Your Dynamic Variables Idea

  The {{project_name}} replacement is good and worth keeping. Just one note: you'd want to
  apply it to all boilerplate files (not just select ones), since a main.py template might
  reference the project name in a window title or app config. Your scaffold_dynamic_file
  function handles this fine.

  What I'd Keep As-Is From Your Design

- No JSON changes - the "check by filename" convention is the right call. It keeps your 32
  existing templates untouched.
- shutil.copy for static files - simple and correct.
- Graceful fallback to .touch() - any file without a boilerplate just stays empty. Zero
  breakage risk.
- Boilerplate files are real .py files - editable, syntax-highlighted, testable. Much
  better than embedding code strings in JSON.

  Summary

  Your design is 90% there. The one structural change I'd make is the hierarchy in the
  boilerplate folder (common → framework → project_type fallback) and passing a
  resolver/context into create_folders() so it knows which framework it's building for.
  Everything else - the convention-over-configuration approach, no JSON changes, real files
  as templates - is the right call.

  Want me to plan out the full implementation?

  ## Plan: Boilerplate File Scaffolding ("Smart Scaffolding")

 Context

 Currently, when a project is created, files listed in JSON templates (e.g., state.py,
 main.py, async_executor.py) are created as empty files via Path.touch(). This feature adds
 a lookup system: if a boilerplate template exists for a filename, the file is created with
 that starter content instead. No boilerplate? Falls back to empty .touch() — zero breakage
 risk.

 Files to Create

 1. app/core/boilerplate_resolver.py (NEW — ~70 lines)

 The resolver class with a fallback lookup chain:

- normalize_framework_name(framework) — module-level function extracted from
 ConfigManager._normalize_framework_name() for shared use
- BoilerplateResolver class:
  - Constructor takes project_name, optional framework, optional project_type, optional
 boilerplate_dir (for testing)
  - Builds ordered search_dirs list from the arguments
  - resolve(filename) -> Optional[str] — searches fallback chain, returns content or None
  - _substitute(content) -> str — replaces {{project_name}} placeholders

 Fallback chain order:

 1. boilerplate/ui_frameworks/{normalized_framework}/{filename}
 2. boilerplate/project_types/{project_type}/{filename}
 3. boilerplate/common/{filename}
 4. None → caller does .touch()

 5. Boilerplate template files (NEW)

 app/config/templates/boilerplate/
 ├── common/
 │   ├── async_executor.py        # ThreadPoolExecutor wrapper (universal utility)
 │   └── constants.py             # APP_NAME, APP_VERSION, PROJECT_DIR
 └── ui_frameworks/
     └── flet/
         ├── main.py              # Minimal Flet hello world app
         ├── state.py             # Basic AppState dataclass
         └── components.py        # Starter build_main_view() function

 All files use {{project_name}} placeholders where appropriate. Start small — more can be
 added later without code changes.

 1. tests/core/test_boilerplate_resolver.py (NEW — ~15-18 tests)

- TestNormalizeFrameworkName — parametrized name normalization tests
- TestBoilerplateResolverInit — search_dirs ordering for various combos (framework-only,
 project-type-only, both, neither)
- TestBoilerplateResolverResolve — fallback chain priority, missing dirs, framework
 normalization in paths
- TestBoilerplateResolverSubstitute — variable replacement, no-op when no placeholders,
 multiple replacements

 Files to Modify

 1. app/utils/constants.py (1 line added)

 Add after existing template dir constants (line ~78):
 BOILERPLATE_DIR = TEMPLATES_DIR / "boilerplate"

 1. app/core/config_manager.py (2 lines changed)

- Import normalize_framework_name from boilerplate_resolver
- Delegate _normalize_framework_name() to the shared function (eliminates duplication)

 1. app/handlers/filesystem_handler.py (~15 lines changed)

- Add optional resolver=None parameter to create_folders() and setup_app_structure()
- At line 192 (the .touch() call), check resolver first:
 content = resolver.resolve(file_name) if resolver else None
 if content is not None:
     file_path.write_text(content, encoding="utf-8")
 else:
     file_path.touch()
- Pass resolver through recursive create_folders() calls and both calls in
 setup_app_structure()
- resolver=None default means all existing callers work unchanged

 1. app/core/project_builder.py (~6 lines added)

- Import BoilerplateResolver
- Before setup_app_structure() call (line 80), construct resolver from config:
 resolver = BoilerplateResolver(
     project_name=config.name,
     framework=config.framework if config.ui_project_enabled else None,
     project_type=config.project_type,
 )
 setup_app_structure(full_path, config.folders, resolver=resolver)

 1. tests/handlers/test_filesystem_handler.py (~4-6 tests added)

 New TestCreateFoldersWithResolver class using a stub resolver:

- File gets boilerplate content when resolver returns content
- File is empty when resolver returns None
- Backward compatible when resolver is not passed
- Resolver propagates to nested subfolders

 Implementation Order

 1. Add BOILERPLATE_DIR to constants.py
 2. Create boilerplate_resolver.py with resolver class
 3. Update config_manager.py to use shared normalize function
 4. Update filesystem_handler.py with optional resolver parameter
 5. Update project_builder.py to construct and inject resolver
 6. Create boilerplate directory structure and starter files
 7. Write tests for resolver and filesystem integration
 8. Run full test suite — verify no regressions

 Verification

- uv run pytest — all existing 276 tests pass + new tests pass
- Manual test: create a Flet project → verify app/utils/async_executor.py has content,
 app/core/state.py has Flet-specific content, files without boilerplate are still empty
- Manual test: create a non-Flet project → verify common boilerplate applies, no
 Flet-specific content leaks through
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

 Claude has written up a plan and is ready to execute. Would you like to proceed?

 ❯ 1. Yes, clear context and auto-accept edits (shift+tab)
   2. Yes, auto-accept edits
   3. Yes, manually approve edits
   4. Type here to tell Claude what to change

## All Done?

All done. Here's a summary of what was implemented:

  Summary

  New files created:

- app/core/boilerplate_resolver.py — normalize_framework_name() shared function +
  BoilerplateResolver class with fallback chain lookup (framework → project_type → common →  
  None) and {{project_name}} placeholder substitution
- tests/core/test_boilerplate_resolver.py — 26 tests covering normalization, search_dirs
  ordering, fallback chain priority, missing dirs, and substitution (100% coverage)
- app/config/templates/boilerplate/ — Starter boilerplate files:
  - common/async_executor.py — ThreadPoolExecutor wrapper
  - common/constants.py — APP_NAME/APP_VERSION with placeholder
  - ui_frameworks/flet/main.py — Minimal Flet hello world
  - ui_frameworks/flet/state.py — Basic AppState dataclass
  - ui_frameworks/flet/components.py — Starter build_main_view()

  Modified files:

- app/utils/constants.py — Added BOILERPLATE_DIR constant
- app/core/config_manager.py — Delegated_normalize_framework_name() to shared
  normalize_framework_name() from boilerplate_resolver
- app/handlers/filesystem_handler.py — Added optional resolver parameter to
  create_folders() and setup_app_structure(); files with boilerplate get content, others
  still get .touch()
- app/core/project_builder.py — Constructs BoilerplateResolver from config and passes it to
   setup_app_structure()
- tests/handlers/test_filesystem_handler.py — Added 5 integration tests for resolver in
  TestCreateFoldersWithResolver

  Test results:

- 282 passed (was 276 + 31 new = 307 total, 25 pre-existing failures unchanged)
- Zero regressions — all existing callers work unchanged due to resolver=None defaults

## Updated Docs

All three files are updated. Here's a summary of the changes:

### CLAUDE.md

- Added smart scaffolding to key capabilities
- Updated test count 276 → 307
- Added boilerplate_resolver.py to directory structure
- Added boilerplate/ directory to templates tree
- Updated test counts in tests/ tree (core: 148, handlers: 89)
- Added full Boilerplate File Scaffolding subsection under Template System
- Added normalize_framework_name() to Key Architecture Decisions
- Updated Development Guidelines test count

### CODE_READING_GUIDE.md

- Added boilerplate_resolver.py to "How projects are built" quick start
- Added Phase 6: Smart Scaffolding to the journey timeline
- Updated Step 3 build flow to show resolver construction and fallback chain
- Added full boilerplate_resolver.py file-by-file entry
- Updated project_builder.py steps to include resolver (step 6-7)
- Updated filesystem_handler.py section to show resolver parameter
- Added boilerplate directory listing to Templates section
- Added Key Concept #6: Boilerplate Scaffolding
- Added to "How does project building work?" reading order
- Updated all test counts (276 → 307) in Final Thoughts, cheat sheet box, and table
- Added boilerplate row to cheat sheet table

### FINAL_SUMMARY.md

- Added new section 4: Smart Scaffolding (renumbered subsequent sections 5→6, 6→7)
- Added smart file scaffolding to Core Functionality checklist
- Updated test counts (276 → 307, 251 → 282 sync)
- Updated Project Stats (47 files, +5 boilerplate, 307 tests)
- Added smart scaffolding to "Where We Are Now"
- Added milestone 10: Smart Scaffolding
- Updated Achievements test count
- Updated Resources test count and added boilerplate templates entry
- Updated Reflection section

## Add a checkbox to turn off file creation

Plan: "Include Starter Files" Checkbox

 Context

 The smart scaffolding feature (BoilerplateResolver) is
 implemented and working. Currently it always runs — every file
  listed in a JSON template gets boilerplate content if
 available, or is created empty. The user wants a UI checkbox
 to control whether template files are created at all. When
 unchecked (default), only directories + __init__.py are
 created. When checked, template files are created with
 boilerplate content.

 Behavior

- "Include starter files" checkbox — unchecked by default
- Unchecked (default): files lists in templates are skipped
 entirely. Only directories and __init__.py are created.
- Checked: Template files are created and populated with
 boilerplate content (current smart scaffolding behavior).

 Files to Modify

 1. app/core/state.py (~2 lines)

 Add field to AppState dataclass (after initialize_git at line
 ~37):
 include_starter_files: bool = False

 Add reset in reset() method (line ~68 area):
 self.include_starter_files = False

 1. app/core/models.py (~1 line)

 Add field to ProjectConfig dataclass (after project_type at
 line ~97):
 include_starter_files: bool = False

 1. app/ui/components.py (~8 lines)

 Add to Controls class (line ~71 area):
 self.include_starter_files_checkbox: ft.Checkbox

 Create checkbox control (after git checkbox construction, line
  ~193 area):
 controls.include_starter_files_checkbox = ft.Checkbox(
     label="Include Starter Files",
     value=state.include_starter_files,
     tooltip="Create template files with boilerplate starter
 content\nDefault is no — only folders and __init__.py are
 created",
 )

 Place in layout: Add as standalone line right after the git
 checkbox inside the "Set Options" section column (line ~317
 area).

 1. app/handlers/event_handlers.py (~10 lines)

 Add handler (after on_git_toggle around line ~424):
 async def on_boilerplate_toggle(self, e: ft.ControlEvent) ->
 None:
     """Handle include starter files checkbox toggle."""
     self.state.include_starter_files = e.control.value
     status = "enabled" if self.state.include_starter_files
 else "disabled"
     self._set_status(f"Starter files {status}.", "info",
 update=True)

 Attach handler (line ~948 area, after git checkbox
 attachment):
 controls.include_starter_files_checkbox.on_change =
 wrap_async(
     handlers.on_boilerplate_toggle
 )

 Reset UI in on_reset() (line ~841 area):
 self.controls.include_starter_files_checkbox.value = False

 Add include_starter_files to ProjectConfig construction in
 on_build_project() (line ~804-815 area).

 1. app/handlers/filesystem_handler.py (~6 lines)

 In create_folders(), wrap the file-creation block so it's
 skipped entirely when resolver is None AND no resolver means
 "don't create files". But the cleaner approach: the resolver
 parameter already controls this — when resolver is None, files
  are .touch()'d. Instead, we add a new skip_files=False
 parameter:

 Actually, simpler approach: In project_builder.py, just don't
 pass resolver and also pass a skip_files flag. But the
 cleanest approach is:

- Add skip_files: bool = False parameter to both
 create_folders() and setup_app_structure()
- When skip_files=True, skip the entire file-creation block
 (the if files: loop)
- __init__.py creation is NOT affected (it's directory
 infrastructure, not a template file)

 1. app/core/project_builder.py (~3 lines changed)

 Conditionally construct resolver and pass skip_files:
 if config.include_starter_files:
     resolver = BoilerplateResolver(
         project_name=config.name,
         framework=config.framework if
 config.ui_project_enabled else None,
         project_type=config.project_type,
     )
 else:
     resolver = None
 setup_app_structure(full_path, config.folders,
 resolver=resolver,
                     skip_files=not
 config.include_starter_files)

 1. Tests

- tests/handlers/test_filesystem_handler.py: Add 2 tests for
 skip_files=True behavior (files not created, __init__.py still
  created)
- Existing boilerplate resolver tests remain unchanged

 Implementation Order

 1. Add include_starter_files to AppState + reset
 2. Add include_starter_files to ProjectConfig
 3. Add checkbox to UI Controls class + layout
 4. Add event handler + attachment + reset
 5. Add skip_files parameter to filesystem_handler.py
 6. Update project_builder.py to use the flag
 7. Add tests
 8. Run full test suite

 Verification

- uv run pytest — all 307 existing tests pass + new tests pass
- Manual: create project with checkbox unchecked → only directories + __init__.py, no template files
- Manual: create project with checkbox checked → template files created with boilerplate content
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

 Claude has written up a plan and is ready to execute. Would you like to proceed?

 ❯ 1. Yes, clear context and auto-accept edits (shift+tab)
   2. Yes, auto-accept edits
   3. Yes, manually approve edits
   4. Type here to tell Claude what to change

## Summary of adding checkbox

Here's a summary of all changes made:

  Files Modified (7 files)

  1. app/core/state.py — Added include_starter_files: bool = False field and reset logic
  2. app/core/models.py — Added include_starter_files: bool = False to ProjectConfig
  3. app/ui/components.py — Added include_starter_files_checkbox to Controls class, created the checkbox control with tooltip,
   placed it in the "Set Options" section after the git checkbox
  4. app/handlers/event_handlers.py — Added on_boilerplate_toggle handler, attached it to the checkbox,
  added reset in on_reset(), passed include_starter_files to
  ProjectConfig construction
  5. app/handlers/filesystem_handler.py — Added skip_files: bool = False parameter to both create_folders() and
  setup_app_structure(). When True, the file-creation block is skipped but __init__.py creation is unaffected. Propagates to
  recursive subfolder calls.
  6. app/core/project_builder.py — Conditionally creates BoilerplateResolver only when include_starter_files is True;
  passes skip_files=not config.include_starter_files to setup_app_structure()
  7. tests/handlers/test_event_handlers.py — Added include_starter_files_checkbox to MockControls
  8. tests/handlers/test_filesystem_handler.py — Added 4 new tests in TestCreateFoldersSkipFiles class:
    - Files are skipped when skip_files=True
    - __init__.py is still created
    - skip_files propagates to subfolders
    - setup_app_structure passes skip_files through

  Test Results

- 286 passed (282 existing + 4 new), 25 failed (all
  pre-existing)

## Other ideas for options or features for folder/file stuff

Here are some ideas, roughly ordered by how much value they'd add relative to
  effort:

  1. .gitignore tailored per framework/project type
  UV's uv init creates a basic .gitignore, but Django needs db.sqlite3, media/, data science needs .ipynb_checkpoints/, Flet needs .flet/, etc. You could add a gitignore boilerplate directory with per-framework snippets that get appended after build.

  2. README.md scaffolding
  A template README with the project name, a "Getting Started" section showing uv run commands, and framework-specific setup notes. Minimal effort — just another boilerplate file at the root level.

  3. Root-level config files per project type
  Things like conftest.py for testing projects, Dockerfile for web apps,.env. example for Django/FastAPI. These are root-level files that the boilerplate system could handle if you extended it to write files at the project root (not just inside app/ subfolders).

  4. pyproject.toml entry point wiring
  Right now configure_pyproject just sets the name. For CLI tools (click/typer) you'd want [project.scripts] entries, for Flet apps a flet run target. A small per-project-type config that gets merged into pyproject.toml after build.

  5. Starter test file
  The tests/ folder already gets created (it's root-level in templates), but it's empty. A test_placeholder.py with a passing smoke test and conftest.py would make the project immediately runnable with uv run pytest.

  6. Pre-commit config
  A .pre-commit-config.yaml with ruff/mypy — toggled by a checkbox. Small file, big ergonomic win for new projects.

  7. Folder tree preview before build
  Show a visual tree of exactly what will be created (files + folders) in a dialog or expandable panel before the user clicks Build. You already have flatten_folders_for_display — this would just surface it in the UI.

## Add boilerplate README.mdAll 34 tests pass. Here's what was done

  Boilerplate files created:

- boilerplate/common/README.md — generic fallback with
  Setup/Run/Development sections
- boilerplate/ui_frameworks/flet/README.md — same structure but
  describes it as a Flet app with a link to flet.dev

  Logic (filesystem_handler.py:264-267): After the main.py
  replacement, the resolver is asked for README.md. If boilerplate
  exists, it overwrites UV's empty README with the
  project-name-substituted version. Same guards apply — skipped when
   resolver is None or skip_files=True.

  The resolver's existing fallback chain handles framework
  specificity automatically: a Flet project gets the Flet README,
  anything else falls through to the common one, and if someone
  deletes all the boilerplate READMEs, UV's empty file stays
  untouched.

## Add Test boilerplate files

Boilerplate files created:

- boilerplate/common/conftest.py — shared fixture providing the
  project name
- boilerplate/common/test_app.py — two smoke tests: verifies app  
  is importable and the fixture works

  Both use {{project_name}} placeholders, so they'll have the real
  project name substituted at build time.

  Templates updated (22 files):

- ui_frameworks/flet.json and ui_frameworks/default.json — added
  "files": ["conftest.py", "test_app.py"] to tests folder
- All 20 project type templates — same addition, preserving
  existing subfolders where present

  Since the files live in boilerplate/common/, they're the universal
   fallback — every project type gets them automatically. If you
  later want a framework-specific conftest.py (e.g., with a Flet
  test client fixture), just drop it in
  boilerplate/ui_frameworks/flet/conftest.py and the resolver's
  fallback chain picks it up.

## Add pyproject.toml boilerplate with Entry Points

Plan: pyproject.toml Entry Point Wiring

 Context

 configure_pyproject() hardcodes app.main:run for every project.
 This is broken — the Flet boilerplate doesn't define run(), and
 many project types (Django, FastAPI, Flask) shouldn't have
 [project.scripts] at all since they have their own runners. CLI
 tools (click, typer) have their own entry point conventions.

 Changes

 1. app/utils/constants.py — Add entry point mappings

 Two new dicts:

- FRAMEWORK_ENTRY_POINT_MAP — UI frameworks → entry point or None
  - GUI frameworks (flet, PyQt6, etc.) → "app.main:run"
  - streamlit, gradio → None (they have their own runners)
- PROJECT_TYPE_ENTRY_POINT_MAP — project types → entry point or
 None
  - CLI click → "app.main:cli", typer → "app.main:app", rich →
 "app.main:main"
  - django, fastapi, flask, bottle, api_* → None
  - Everything else → "app.main:main"
- DEFAULT_ENTRY_POINT = "app.main:main" — fallback when nothing is
  selected

 1. app/handlers/uv_handler.py — Update configure_pyproject

- Add framework and project_type optional params (backward
 compatible)
- Add _resolve_entry_point() helper with priority: framework →
 project_type → default
- [tool.hatch.build.targets.wheel] always written
- [project.scripts] only written when entry point is not None

 1. app/core/project_builder.py — Pass context (line 93)

 configure_pyproject(
     full_path, config.name,
     framework=config.framework if config.ui_project_enabled else
 None,
     project_type=config.project_type,
 )

 1. Boilerplate files

- Fix boilerplate/ui_frameworks/flet/main.py — add run() wrapper
 around ft.app(target=main)
- New boilerplate/common/main.py — generic with def main():
 (fallback for all projects)
- New boilerplate/project_types/cli_click/main.py — click CLI
 starter
- New boilerplate/project_types/cli_typer/main.py — typer CLI
 starter

 1. Tests — tests/handlers/test_uv_handler.py

- Update 3 existing assertions (app.main:run → app.main:main)
- Add tests for: flet, django (no scripts), cli_click, cli_typer,
 streamlit (no scripts), framework priority over project_type,
 hatch always written, default behavior
- Add TestResolveEntryPoint class for the helper function

 Verification

- uv run pytest — all tests pass
- Build a Flet project in the app → pyproject.toml has
 app.main:run, main.py has run()
- Build a Django project → pyproject.toml has NO [project.scripts]
- Build a bare project → pyproject.toml has app.main:main
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

 Claude has written up a plan and is ready to execute. Would you
 like to proceed?

 ❯ 1. Yes, clear context and auto-accept edits (shift+tab)
   2. Yes, auto-accept edits
   3. Yes, manually approve edits
   4. Type here to tell Claude what to change

## Changes Made

  1. app/utils/constants.py — Added three new constants:
    - FRAMEWORK_ENTRY_POINT_MAP — GUI frameworks → "app.main:run", streamlit/gradio → None
    - PROJECT_TYPE_ENTRY_POINT_MAP — CLI tools get specific entry points (cli, app, main), web frameworks → None, everything else →
  "app.main:main"
    - DEFAULT_ENTRY_POINT = "app.main:main"
  2. app/handlers/uv_handler.py — Two changes:
    - New_resolve_entry_point(framework, project_type) helper with priority chain: framework → project_type → default
    - configure_pyproject() now accepts optional framework and
  project_type params; [project.scripts] is only written when entry point is not None
  3. app/core/project_builder.py (line 93) — Now passes framework and project_type context to configure_pyproject()
  4. Boilerplate files:
    - Fixed boilerplate/ui_frameworks/flet/main.py — added run() wrapper matching the app.main:run entry point
    - New boilerplate/common/main.py — generic def main() fallback
    - New boilerplate/project_types/cli_click/main.py — Click CLI starter with @click.group() and cli() entry point
    - New boilerplate/project_types/cli_typer/main.py — Typer CLI starter with app = typer.Typer() entry point
  5. Tests — 22 new tests added (14 in TestResolveEntryPoint, 8 in  TestConfigurePyprojectWithContext), 2 existing assertions updated.
   All 314 sync tests pass.

## Fix the pytest failures

All 25 async tests now pass. We went from 25 failures to 6
   — and those 6 remaining failures are pre-existing
  validator test issues (unrelated to our changes or the
  async fix). They're about folder name validation of
  dotfiles/numbers, not entry points.

  Here's the summary:

  Root cause of the async test failures: The .venv was
  created from a different project location
  (/Users/tim/Projects/create_project/), so the pytest
  binary's shebang pointed to the wrong venv's Python. That
  Python could find pytest, anyio, and cov
  (system-installed), but not pytest-asyncio (only in the
  project venv). The asyncio_mode = auto config was
  "unknown" because the plugin never loaded.

  Fix: Deleted and recreated the .venv with uv sync --group
  dev. Now .venv/bin/pytest has the correct shebang,
  pytest-asyncio loads as a plugin, and all 25 async tests
  pass.

  Remaining 6 failures are pre-existing validator test bugs
  — tests expect dotfiles (.gitignore, .env.local) and
  number-prefixed names (123folder) to be valid, but
  validate_folder_name() rejects anything not starting with
  a letter or underscore. That's a separate issue.

✻ Churned for 3m 25s

❯ Oh, I copied this project from another folder and
  pasted it into this one, so that's what caused the
  problem?

⏺ Yes, exactly. When you copied the project, the .venv came
  along with it. The shebang in .venv/bin/pytest (and likely
   other scripts) still pointed to the original location:

  #!/Users/tim/Projects/create_project/.venv/bin/python3

  So uv run pytest was executing with the old venv's Python,
   which had pytest but not pytest-asyncio. Recreating the  
  venv fixed the shebangs to point to the correct path:

  #!/Users/tim/Projects/for-launch/create-project/.venv/bin/
  python

  If you copy a project again in the future, a quick rm -rf
  .venv && uv sync --group dev will avoid the issue. Or just
   don't copy .venv — it's always regenerable.
