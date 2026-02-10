# Manual Testing Guide - Add/Remove Folder Feature

## Quick Test Checklist

Follow these steps to verify the Add/Remove functionality works correctly.

### Setup

```bash
cd /Users/tim/Projects/for-launch/create-project
uv run create_project
```

---

## Test 1: Select Items

**Steps:**
1. Launch the application
2. Look at the "App Subfolders" section
3. Click on any folder in the list (e.g., "core/")

**Expected:**
- Item should highlight with blue border and background
- Status bar shows "Selected folder: core"

**Cleanup:** Click another item or continue to next test

---

## Test 2: Add Folder at Root

**Steps:**
1. Click "Add Folder" button
2. Dialog opens
3. Enter name: "custom"
4. Keep "Folder" selected
5. Keep "Root" as parent
6. Click "Add"

**Expected:**
- Dialog closes
- New folder "custom/" appears in the list
- Status shows "Folder 'custom' added."

---

## Test 3: Add Subfolder

**Steps:**
1. Click "Add Folder" button
2. Enter name: "helpers"
3. Keep "Folder" selected
4. Select parent: "core/" (or any existing folder)
5. Click "Add"

**Expected:**
- New folder "helpers/" appears indented under "core/"
- Status shows "Folder 'helpers' added."

---

## Test 4: Add File

**Steps:**
1. Click "Add Folder" button
2. Enter name: "config.py"
3. Select "File" (radio button)
4. Select parent: "core/" (must not be "Root")
5. Click "Add"

**Expected:**
- New file "config.py" appears in grey under "core/"
- File is indented one level from parent
- Status shows "File 'config.py' added."

---

## Test 5: Remove Item

**Steps:**
1. Click on the "helpers/" folder (or any item) to select it
2. Item highlights with blue border
3. Click "Remove Folder" button

**Expected:**
- Item disappears from list
- Selection is cleared
- Status shows "Folder 'helpers' removed."

---

## Test 6: Validation - Invalid Name

**Steps:**
1. Click "Add Folder"
2. Enter name: "bad folder" (with space)
3. Select "Folder"
4. Click "Add"

**Expected:**
- Orange warning banner appears
- Message: "Name can only contain letters, numbers, hyphens, underscores, and periods."
- Dialog stays open

**Cleanup:** Click "Cancel" to close dialog

---

## Test 7: Validation - Empty Name

**Steps:**
1. Click "Add Folder"
2. Leave name field empty
3. Click "Add"

**Expected:**
- Orange warning banner appears
- Message: "Name cannot be empty."

**Cleanup:** Click "Cancel"

---

## Test 8: Validation - File at Root

**Steps:**
1. Click "Add Folder"
2. Enter name: "test.txt"
3. Select "File"
4. Keep parent as "Root"
5. Click "Add"

**Expected:**
- Orange warning banner appears
- Message: "Files must be added inside a folder."

**Cleanup:** Click "Cancel"

---

## Test 9: Remove Without Selection

**Steps:**
1. Make sure nothing is selected (or reset app)
2. Click "Remove Folder" button

**Expected:**
- Status bar shows: "No item selected. Click an item to select it first."
- No changes to folder list

---

## Test 10: Theme Toggle Preserves Selection

**Steps:**
1. Select any folder/file (it highlights)
2. Click the theme toggle button (moon/sun icon)
3. Theme switches (dark ↔ light)

**Expected:**
- Selection highlighting still visible
- Blue colors adjust to theme
- Selected item remains selected

---

## Test 11: Reset Clears Selection

**Steps:**
1. Select any folder/file
2. Click "Reset" button

**Expected:**
- All fields reset to defaults
- Folder display clears
- Selection is cleared (no highlight)
- Status shows "All fields reset."

---

## Test 12: Deep Nesting

**Steps:**
1. Add folder "level1" at Root
2. Add folder "level2" inside "level1"
3. Add folder "level3" inside "level2"
4. Add file "deep.txt" inside "level3"

**Expected:**
- Each level appears with correct indentation
- File shows in grey at deepest level
- Can select and remove any level

---

## Test 13: Framework Template Loading

**Steps:**
1. Check "UI Project" checkbox
2. Select framework "flet" from dropdown
3. Folder display updates with Flet template

**Expected:**
- Template structure loads (e.g., "core/", "ui/", "utils/")
- Can click and select any folder/file
- Can add custom folders to the template
- Can remove folders from the template

---

## Test 14: Project Creation with Custom Folders

**Steps:**
1. Set project name: "test_custom"
2. Add a custom folder "data" at root
3. Add file "config.json" in "data" folder
4. Click "Build Project" button

**Expected:**
- Project creates successfully
- Custom "data/" folder exists in project
- "config.json" file exists inside "data/"

**Verify:**
```bash
ls test_custom/app/data/
# Should show: config.json
```

---

## Visual Indicators Reference

### Selection State
- **Selected:** Blue background (`#1565C0`) + blue border
- **Unselected:** No background, no border
- **Hover:** Clickable cursor

### Item Types
- **Folders:** Default text color, ends with `/`
- **Files:** Grey text (`#BDBDBD`), no trailing `/`

### Status Messages
- **Info:** Blue text
- **Success:** Green text
- **Error/Warning:** Red/Orange text

---

## Cleanup After Testing

To remove test projects:
```bash
rm -rf test_custom
rm -rf /path/to/any/test/projects
```

To reset the app:
- Click "Reset" button in the app

---

## Known Limitations

1. **No undo** - Removed items cannot be recovered (use Reset to reload template)
2. **No drag-and-drop** - Items cannot be reordered visually
3. **No rename** - Must remove and re-add to change names
4. **Auto-save not wired** - Checkbox exists but doesn't persist changes yet

---

## Bug Reporting

If you encounter issues, note:
- What you clicked
- What happened vs what you expected
- Error messages in status bar or warning banner
- Console output (if running from terminal)

Check `app/assets/docs/ADD_REMOVE_IMPLEMENTATION.md` for technical details.
