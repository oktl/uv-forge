"""Template merging utilities for combining folder structures.

Provides functions to normalize folder representations and merge two
folder template lists (e.g., a UI framework template and a project type
template) into a single unified structure.
"""

from typing import Any

from app.core.models import FolderSpec

# Folder specs arrive as strings, dicts (from JSON), or FolderSpec instances.
type FolderInput = str | dict[str, Any] | FolderSpec


def normalize_folder(
    folder: FolderInput, parent_create_init: bool = True
) -> dict[str, Any]:
    """Convert any folder form to a canonical dict.

    Args:
        folder: A string name, dict, or FolderSpec instance.
        parent_create_init: Parent folder's create_init value. String subfolders
            inherit this instead of defaulting to True, matching the behavior
            of create_folders() in filesystem_handler.py.

    Returns:
        Dict with keys: name, create_init, root_level, subfolders, files.
    """
    if isinstance(folder, str):
        return {
            "name": folder,
            "create_init": parent_create_init,
            "root_level": False,
            "subfolders": [],
            "files": [],
        }

    if isinstance(folder, FolderSpec):
        create_init = folder.create_init
        return {
            "name": folder.name,
            "create_init": create_init,
            "root_level": folder.root_level,
            "subfolders": [
                normalize_folder(sf, create_init) for sf in (folder.subfolders or [])
            ],
            "files": list(folder.files) if folder.files else [],
        }

    # dict
    create_init = folder.get("create_init", True)
    return {
        "name": folder.get("name", ""),
        "create_init": create_init,
        "root_level": folder.get("root_level", False),
        "subfolders": [
            normalize_folder(sf, create_init)
            for sf in folder.get("subfolders", []) or []
        ],
        "files": list(folder.get("files", []) or []),
    }


def _merge_files(primary_files: list[str], secondary_files: list[str]) -> list[str]:
    """Union two file lists, preserving primary order, deduplicating.

    Args:
        primary_files: Files from the primary template.
        secondary_files: Files from the secondary template.

    Returns:
        Merged file list with no duplicates.
    """
    seen = set(primary_files)
    result = list(primary_files)
    for f in secondary_files:
        if f not in seen:
            seen.add(f)
            result.append(f)
    return result


def _merge_single_folder(
    primary: dict[str, Any], secondary: dict[str, Any]
) -> dict[str, Any]:
    """Merge two normalized folder dicts with the same name.

    Args:
        primary: Primary folder dict.
        secondary: Secondary folder dict.

    Returns:
        Merged folder dict.
    """
    return {
        "name": primary["name"],
        "create_init": primary["create_init"] or secondary["create_init"],
        "root_level": primary["root_level"] or secondary["root_level"],
        "subfolders": merge_folder_lists(
            primary["subfolders"], secondary["subfolders"]
        ),
        "files": _merge_files(primary["files"], secondary["files"]),
    }


def merge_folder_lists(
    primary: list[FolderInput], secondary: list[FolderInput]
) -> list[dict[str, Any]]:
    """Merge two folder lists into one.

    Matching folders (by name, case-sensitive) are merged recursively:
    subfolders are merged, files are unioned, booleans are OR'd.
    Non-matching folders from both lists are included (primary order first,
    then secondary-only folders appended).

    Assumes folder names are unique within each list. If duplicates exist,
    only the last occurrence in secondary is used for matching.

    Args:
        primary: Primary folder list (its order takes precedence).
        secondary: Secondary folder list.

    Returns:
        Merged list of normalized folder dicts.
    """
    norm_primary = [normalize_folder(f) for f in primary]
    norm_secondary = [normalize_folder(f) for f in secondary]

    # Index secondary by name for lookup
    secondary_by_name: dict[str, dict[str, Any]] = {}
    for folder in norm_secondary:
        secondary_by_name[folder["name"]] = folder

    merged: list[dict[str, Any]] = []
    used_secondary_names: set[str] = set()

    for p_folder in norm_primary:
        name = p_folder["name"]
        if name in secondary_by_name:
            # Merge the two folders
            s_folder = secondary_by_name[name]
            used_secondary_names.add(name)
            merged.append(_merge_single_folder(p_folder, s_folder))
        else:
            merged.append(p_folder)

    # Append secondary-only folders
    for s_folder in norm_secondary:
        if s_folder["name"] not in used_secondary_names:
            merged.append(s_folder)

    return merged
