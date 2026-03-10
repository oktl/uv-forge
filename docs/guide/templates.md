# Templates

UV Forge uses a JSON-based template system to define project structures. Templates live in `uv_forge/config/templates/` and determine which folders, files, and packages are created for each project.

## Template directory layout

```
uv_forge/config/templates/
├── ui_frameworks/        # One JSON per UI framework
│   ├── flet.json
│   ├── pyqt6.json
│   ├── default.json      # Fallback template
│   └── ...
├── project_types/        # One JSON per project type
│   ├── django.json
│   ├── fastapi.json
│   └── ...
└── boilerplate/          # Starter file content
    ├── common/           # Shared across all project types
    │   ├── async_executor.py
    │   └── constants.py
    └── ui_frameworks/    # Framework-specific starter code
        └── flet/
            ├── main.py
            ├── state.py
            └── components.py
```

## Template format

Each template is a JSON file defining a list of `FolderSpec` structures:

```json
[
  {
    "name": "core",
    "create_init": true,
    "root_level": false,
    "subfolders": [],
    "files": ["state.py", "models.py"]
  },
  {
    "name": "tests",
    "create_init": true,
    "root_level": true,
    "subfolders": [],
    "files": []
  }
]
```

| Field          | Type     | Description                                         |
| -------------- | -------- | --------------------------------------------------- |
| `name`         | string   | Folder name                                         |
| `create_init`  | boolean  | Whether to create `__init__.py` in this folder      |
| `root_level`   | boolean  | `true` = created at project root, `false` = inside `app/` |
| `subfolders`   | array    | Nested `FolderSpec` objects                         |
| `files`        | array    | Filenames to create in this folder                  |

## Loading fallback chain

When you select a UI framework, templates are loaded in this order:

1. **Framework-specific template** — e.g., `ui_frameworks/flet.json`
2. **Default template** — `ui_frameworks/default.json`
3. **Hardcoded defaults** — `DEFAULT_FOLDERS` in `constants.py`

The first one found is used. Project type templates follow the same pattern with their own directory.

## Template merging

When you select **both** a UI framework and a project type, UV Forge merges their templates:

- **Matching folders** (same name) are merged recursively — files are unioned, `create_init` and `root_level` are OR'd, subfolders are merged the same way
- **Unmatched folders** from both templates are included as-is
- The UI framework template takes priority for ordering

This means selecting "Flet" + "FastAPI" gives you a project with the folder structures from both, intelligently combined rather than duplicated.

## Smart scaffolding (boilerplate)

When files are created during a build, UV Forge looks for starter content instead of creating empty files. The lookup follows a fallback chain:

1. `boilerplate/ui_frameworks/{framework}/{filename}` — framework-specific (e.g., Flet's `main.py`)
2. `boilerplate/project_types/{project_type}/{filename}` — project-type-specific
3. `boilerplate/common/{filename}` — shared utilities
4. Empty file — if no boilerplate exists (zero breakage risk)

Boilerplate files can use `{{project_name}}` as a placeholder. At build time, it's replaced with a title-case version of the project name (e.g., `my_app` becomes `My App`).

## Adding a new template

### New UI framework

1. Add the framework name to `UI_FRAMEWORKS` in `uv_forge/core/constants.py`
2. Add its package to `FRAMEWORK_PACKAGE_MAP` in the same file
3. Add a display entry to `UI_FRAMEWORK_CATEGORIES` in `uv_forge/ui/dialog_data.py`
4. Create `uv_forge/config/templates/ui_frameworks/<name>.json`
5. Optionally add boilerplate files to `uv_forge/config/templates/boilerplate/ui_frameworks/<name>/`

### New project type

1. Add the type and its packages to `PROJECT_TYPE_PACKAGE_MAP` in `uv_forge/core/constants.py`
2. Add a display entry to `PROJECT_TYPE_CATEGORIES` in `uv_forge/ui/dialog_data.py`
3. Create `uv_forge/config/templates/project_types/<name>.json`
4. Optionally add boilerplate files to `uv_forge/config/templates/boilerplate/project_types/<name>/`

!!! tip
    Adding boilerplate is just dropping files into the right directory — no code changes needed. Look at existing templates for reference.
