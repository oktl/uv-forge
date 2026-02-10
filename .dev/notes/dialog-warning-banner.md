# Plan: Add Warning Banner to Add Folder/File Dialog

  Current Issues

  1. Validation errors from validate_folder_name() show in main window's warning_banner (line 489)
  2. Other errors ("Cannot add items inside a file", "Files must be added inside a folder") also show in main
   window
  3. Warnings persist even after successful folder/file addition
  4. User has to look away from the dialog to see what went wrong

  Proposed Solution

  1. Update create_add_item_dialog in dialogs.py (Lines 162-267)

  Add a warning banner Text control inside the dialog:

- Position it prominently between the input fields and action buttons
- Style with orange color (ft.Colors.ORANGE_600) for visibility
- Initially empty/hidden
- Store reference as dialog.warning_text attribute for callback access

  Changes:

# Add warning banner control

  warning_text = ft.Text(
      value="",
      color=ft.Colors.ORANGE_600,
      size=13,
      visible=False,  # Hidden when empty
      weight=ft.FontWeight.W_500,
  )

# Insert into the Column before actions

  content=ft.Column(
      [
          name_field,
          ft.Container(height=10),
          ft.Text("Type:", size=14),
          type_radio,
          ft.Container(height=10),
          parent_dropdown,
          ft.Container(height=15),  # Spacing
          warning_text,              # NEW: Warning banner
      ],
      tight=True,
  )

# Store reference on dialog object

  dialog = ft.AlertDialog(...)
  dialog.warning_text = warning_text  # NEW: Add reference
  return dialog

  1. Update on_add_folder in event_handlers.py (Lines 478-580)

  Modify the add_item nested function to use the dialog's warning banner:

  Changes:

- Replace self._set_warning(error, update=True) with dialog warning updates
- Clear dialog warning on success before closing
- Keep main window status messages for success feedback

  async def add_item(name: str, item_type: str, parent_path: list | None):
      """Add folder or file to state."""
      # Validate name
      valid, error = validate_folder_name(name)
      if not valid:
          # NEW: Show in dialog's warning banner
          dialog.warning_text.value = error
          dialog.warning_text.visible = True
          self.page.update()
          return

      # ... rest of validation logic ...

      if some_error:
          # NEW: Show in dialog's warning banner
          dialog.warning_text.value = "Error message here"
          dialog.warning_text.visible = True
          self.page.update()
          return

      # On success - clear dialog warning and close
      dialog.warning_text.value = ""      # NEW: Clear warning
      dialog.warning_text.visible = False  # NEW: Hide warning
      dialog.open = False

      # Update display and show success in main window
      self._update_folder_display()
      self._set_status(
          f"{item_type.title()} '{name}' added.", "success", update=True
      )

  3. Clear Main Window Warning on Dialog Open (Optional enhancement)

  Clear any existing warnings in main window when opening the add dialog:

# Before opening dialog

  self._set_warning("", update=False)
  self.page.overlay.append(dialog)
  dialog.open = True
  self.page.update()

  Benefits

  1. ✅ Errors appear immediately where user is looking (in the dialog)
  2. ✅ No need to look back at main window for validation feedback
  3. ✅ Warnings automatically cleared on success
  4. ✅ Better separation: dialog warnings in dialog, status messages in main window
  5. ✅ Consistent UX pattern for future dialogs

  Files to Modify

- app/ui/dialogs.py - Add warning banner to dialog (lines 162-267)
- app/handlers/event_handlers.py - Update error handling in on_add_folder (lines 478-580)

  Testing Plan

  1. Open Add Folder dialog
  2. Enter invalid name (e.g., "my folder" with space) → Warning should appear in dialog
  3. Fix name → Warning should remain until successful add
  4. Add successfully → Dialog closes, warning gone, success message in main window
  5. Reopen dialog → No stale warnings
  6. Test all error cases (empty name, reserved names, file in root, etc.)

  Would you like me to proceed with this implementation?

## Changes Made

  1. app/ui/dialogs.py (Lines 207-280)

- Added a warning banner Text control (warning_text) styled in orange
- Positioned it at the bottom of the dialog content, above the action buttons
- Initially hidden (visible=False) until an error occurs
- Stored reference as dialog.warning_text attribute for callback access

  1. app/handlers/event_handlers.py (Lines 478-585)

  Updated the on_add_folder method's add_item function to:

- Show validation errors in the dialog's warning banner instead of main window
- Updated 3 error cases:
  - Invalid folder/file name → Shows in dialog
  - "Cannot add items inside a file" → Shows in dialog
  - "Files must be added inside a folder" → Shows in dialog
- Clear the dialog's warning banner on successful addition
- Clear main window's warning banner when opening the dialog (prevents stale warnings)

  Benefits

  ✅ Immediate feedback - Errors appear right where the user is looking
  ✅ Better UX - No need to look back at main window for validation errors
  ✅ Auto-cleanup - Warnings automatically cleared on success
  ✅ Separation of concerns - Dialog errors in dialog, status messages in main window

  Testing

  You can test this by:

  1. Run the app: uv run create_project
  2. Click "Add Folder" button
  3. Try entering invalid names:
     - my folder (space) → Warning appears in dialog
     - 123abc (starts with number) → Warning appears in dialog
     - Empty name → Warning appears in dialog
  4. Try adding a file at root level → Warning appears in dialog
  5. Enter a valid name → Warning clears, dialog closes, success message in main window

  The implementation is complete and ready to test!

## Summary of What We Implemented

  ✅ Dialog Warning Banner - Errors show directly in the Add Folder/File dialog instead of the main window
  ✅ Real-time Validation - Warnings appear/disappear as you type, just like the project name field
  ✅ Automatic Cleanup - Warnings clear on success and when opening a new dialog
  ✅ Stricter Validation - Both folders and files now require starting with letter/underscore for Python
  package compatibility

  The UX is much cleaner now - users get immediate feedback right where they're working, and the warnings
  don't persist after successful operations. Perfect for maintaining good Python naming conventions
  throughout the project structure!
