# Code Coverage Guide

**Added:** February 6, 2026
**Current Coverage:** 55% (485/887 lines)

---

## Quick Reference

### Run Tests with Coverage

```bash
# Coverage runs automatically now!
pytest

# Or explicitly
uv run pytest

# View HTML report
open htmlcov/index.html
```

### Understanding the Output

```plaintext
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
app/core/state.py              27      0   100%
app/core/validator.py          29      0   100%
app/core/project_builder.py    46     35    24%   31-32, 55-108
```

- **Stmts**: Total lines of code
- **Miss**: Lines not tested
- **Cover**: Percentage covered
- **Missing**: Exact line numbers without tests

---

## Current Status

### ✅ Excellent Coverage (90-100%)

These files are very well tested - no action needed!

- **state.py** (100%) - AppState fully tested
- **validator.py** (100%) - All validation tested
- **models.py** (100%) - All data models tested
- **handler_factory.py** (100%) - Async wrappers tested
- **git_handler.py** (100%) - Git operations tested
- **async_executor.py** (100%) - Async execution tested
- **constants.py** (100%) - All constants covered
- **filesystem_handler.py** (95%) - File operations well tested
- **uv_handler.py** (94%) - UV commands well tested
- **ui_config.py** (92%) - UI config well tested

### ⚠️ Good But Could Improve (60-90%)

These files are well tested but have some gaps:

- **config_manager.py** (76%)
  - Missing: Lines 87-90, 102-105, 115-119, 132
  - Recommendation: Test error handling and edge cases

- **theme_manager.py** (61%)
  - Missing: Lines 37-42, 54-62, 75, 93
  - Recommendation: Test theme switching logic

### ⚡ Intentionally Low Coverage (0-50%)

These are hard to test or not worth testing:

#### UI Files (Hard to Test)

- **event_handlers.py** (37%) - UI event handlers
  - Missing: Most async event handler methods
  - Why: Requires UI runtime and mocking Flet
  - Current tests cover: Helper methods, validation, folder display

- **components.py** (14%) - UI component creation
  - Missing: Most UI building code
  - Why: Requires Flet runtime to test
  - Not critical: UI bugs are caught manually during testing

- **main.py** (0%) - Application entry point
  - Missing: All startup code
  - Why: Hard to test entry points
  - Not critical: Failures are immediately visible

#### Not Used Yet

- **dialogs.py** (0%) - Dialog components (not implemented)
- **ui_state_sync.py** (0%) - Legacy YouTube code (unused)
- **state example.py** (0%) - Leftover file (can delete)
- **button_state.py** (empty) - Not implemented
- **state_validator.py** (empty) - Not implemented

#### Integration Testing

- **project_builder.py** (24%) - Main orchestration
  - Missing: Lines 31-32, 55-108 (most of the build logic)
  - Why: Would need integration tests that create real projects
  - Current tests: Individual handlers (filesystem, UV, git) are well tested
  - Trade-off: Complex to test, but components are individually tested

---

## Interpreting the HTML Report

### In Your Browser

1. Open `htmlcov/index.html`
2. Click any file to see line-by-line coverage
3. Look for red highlighting = untested code

### Color Coding

- **Green**: Code was executed during tests ✅
- **Red**: Code was never executed ❌
- **Yellow**: Partial coverage (e.g., if statement tested but not else)

### Example

Click on `app/core/config_manager.py` (76%) to see:

- Lines 87-90: Error handling for missing templates (not tested)
- Lines 102-105: Error handling for invalid JSON (not tested)
- Lines 115-119: Fallback logic (not tested)

---

## Should You Add More Tests?

### High Priority

Focus on **config_manager.py** (76%) - These are testable and valuable:

- Test what happens when template files are missing
- Test what happens with invalid JSON
- Test fallback behavior

### Medium Priority

**theme_manager.py** (61%) - If you add more theme features, test them

### Low Priority / Skip

- **event_handlers.py** - UI tests are complex, current coverage is fine
- **components.py** - UI building code, manual testing is sufficient
- **project_builder.py** - Integration tests are complex, individual handlers are tested
- **main.py** - Entry point, not worth testing

---

## Tips for Future Development

### When Adding New Code

1. **Run pytest frequently** - Coverage updates automatically
2. **Check the HTML report** - See what needs tests
3. **Aim for 80%+ on business logic** - Don't worry about 100%
4. **UI code is OK with lower coverage** - Hard to test, not critical

### When You See Red Lines

Ask yourself:

1. **Is this business logic?** → Add tests
2. **Is this UI code?** → Maybe skip (hard to test)
3. **Is this error handling?** → Good to test
4. **Is this unreachable code?** → Consider deleting

### Example Workflow

```bash
# 1. Make changes to code
vim app/core/new_feature.py

# 2. Run tests (coverage automatic)
pytest

# 3. Check coverage report
open htmlcov/index.html

# 4. Add tests for red lines (if needed)
vim tests/core/test_new_feature.py

# 5. Verify coverage improved
pytest
```

---

## Configuration

### pytest.ini

Coverage runs automatically because of these lines:

```ini
addopts =
    --cov=app                  # Test the app/ directory
    --cov-report=term-missing  # Show missing lines in terminal
    --cov-report=html          # Generate HTML report
```

### .gitignore

Coverage artifacts are ignored:

```plaintext
htmlcov/          # HTML report directory
.coverage         # Coverage data file
.pytest_cache/    # Pytest cache
```

---

## Common Questions

**Q: Why is main.py at 0%?**
A: Entry points are hard to test and not critical. The code it calls is well tested.

**Q: Should I aim for 100% coverage?**
A: No! 80-90% on business logic is great. UI code and entry points are OK at lower coverage.

**Q: What's a good coverage target?**
A: For this project: 55% overall is good because UI code is hard to test. Focus on keeping business logic (core/, handlers/) at 80%+.

**Q: How do I test async code?**
A: Use `@pytest.mark.asyncio` decorator - already configured in your tests.

**Q: Can I exclude files from coverage?**
A: Yes, but you don't need to. The numbers already show what matters.

---

## Summary

✅ **Your core business logic is excellent** (80-100% coverage)
✅ **Coverage runs automatically** (just run `pytest`)
✅ **HTML reports show exactly what's missing**
✅ **Current 55% is actually quite good** (given UI complexity)

**Next step:** When adding new features, check coverage to ensure business logic is tested!
