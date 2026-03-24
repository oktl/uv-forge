# Presets

Presets let you save a full project configuration as a named template for one-click reuse. Open Presets from the overflow menu (**...**) in the app bar, or use the quick-select dropdown in the main window.

![Presets dialog](../assets/images/presets-dialog.png){ .img-sm }

## Built-in presets

UV Forger ships with 4 starter presets so you can build immediately without configuring anything:

| Preset                   | Framework / Type | Packages                                     |
| ------------------------ | ---------------- | -------------------------------------------- |
| **Flet Desktop App**     | Flet (UI)        | flet + pytest, ruff (dev)                    |
| **FastAPI Backend**      | FastAPI          | fastapi, uvicorn + pytest, ruff, httpx (dev) |
| **Data Science Starter** | Data Analysis    | pandas, numpy, matplotlib, jupyter           |
| **CLI Tool (Typer)**     | CLI (Typer)      | typer[all] + pytest, ruff (dev)              |

Built-in presets use Python 3.13, git enabled, starter files enabled, and MIT license. They appear with a teal **Built-in** badge and cannot be deleted.

## Saving a preset

1. Configure your project the way you want it
2. Click **Save as Preset** in the Project Structure section (or press ++cmd+s++ / ++ctrl+s++), or open the Presets dialog from the overflow menu
3. Enter a name and click **Save Current**

This captures everything: Python version, git and starter file settings, UI framework, project type, folder structure, all packages (including dev), and project metadata.

Saving with an existing name overwrites the previous preset. There's no limit on user presets.

!!! tip "Customize first, then save"
    Before saving, you can go well beyond the template defaults:

    - **Add custom folders and files** — add anything the template doesn't include, or import existing files/directories from disk
    - **Edit file content** — right-click a file and choose *Edit Content...* to open the code editor; press ++cmd+s++ to save your edits as a [user template](templates.md#file-content-editing)
    - **Add, remove, or reorder packages** — mark any package as a dev dependency
    - **Set metadata** — author, license, description

    Everything above is captured when you click **Save Current**, so a single preset can reproduce your entire customized setup.

!!! info "Presets + user templates = full reproducibility"
    Presets capture your folder structure and packages, while user templates capture your edited file content. Because user templates sit at the top of the [boilerplate fallback chain](templates.md#file-content-editing), any content you saved from the editor (++cmd+s++) is automatically used whenever that file path is created — even in a different project. Together, a preset and your saved user templates reproduce the complete setup without any manual steps.

### Workflow example

1. Select a UI framework (e.g., Flet) and a project type (e.g., FastAPI)
2. Add a custom `docker/` folder with a `Dockerfile`
3. Edit `main.py` with your preferred boilerplate and save (++cmd+s++)
4. Add `httpx` and mark `pytest` as dev
5. Set your author name and MIT license
6. Click **Save as Preset** (or ++cmd+s++) → name it "My Full-Stack Starter" → **Save Current**
7. Next project: apply the preset, change the name, and build — done

## Applying a preset

**From the Presets dialog:** Click a preset to select it, then click **Apply**.

**From the quick-select dropdown:** The dropdown in the main window (below Python version) lists all presets. Selecting one applies it immediately.

Applying a preset populates all configuration fields but leaves your project name and path unchanged, so you can reuse the same stack across different projects.

!!! note
    Any post-build packages from Settings (e.g., `pre-commit`) are automatically merged in when applying a preset.

## Deleting a preset

Select a preset in the dialog and click **Delete**. The dialog stays open so you can continue managing presets. Built-in presets cannot be deleted. If you save a user preset with the same name as a built-in, the user preset takes priority.
