# Migration Guide

This document outlines the changes made during the `refactor/quality-upgrade` process.

## Summary of Changes

### Code Style and Quality
- **Tooling**: Added `ruff` for fast linting and formatting.
- **Configuration**: Added `.editorconfig`, `ruff.toml`, and `.pre-commit-config.yaml` to enforce coding standards.
- **Formatting**: The entire codebase has been formatted according to the `ruff` configuration (compatible with `black`).
- **Imports**: Optimized imports across the project.

### Testing
- **Framework**: Standard Django `TestCase`.
- **New Tests**: Added initial tests for `patients` application covering:
  - Model logic (`Patient` creation, nurse/doctor assignment).
  - Basic Views (`PatientDetailView`).
- **CI**: Added GitHub Actions workflow (`.github/workflows/ci.yml`) to run tests and linting on every push and PR.

### Environment
- **Configuration**: Standardized `settings.py` to use `environs` for environment variable management.
- **Typo Fix**: Fixed a typo in `DATABSE_URL` to `DATABASE_URL` in `settings.py`.

### Documentation
- Updated `README.md` with clearer instructions for setup, development, and testing.
- Added this migration guide.

## How to Maintain

1. **Linting**: Run `ruff check .` before committing.
2. **Formatting**: Run `ruff format .` to ensure consistent style.
3. **Testing**: Write tests for new features and ensure existing tests pass (`python manage.py test`).
4. **CI**: Ensure the GitHub Actions pipeline stays green.
