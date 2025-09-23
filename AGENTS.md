# Agent Guidelines for Affleego Backend

## Commands
- **Test**: `pytest` (all tests), `pytest path/to/test_file.py::test_function` (single test)
- **Lint**: `ruff check .` (check), `ruff check . --fix` (fix)
- **Format**: `ruff format .`
- **Django**: `python manage.py <command>`

## Code Style
- **Line Length**: 100 characters (ruff), 80 for flake8
- **Quotes**: Single quotes for strings
- **Imports**: Use `from typing import TYPE_CHECKING` for type-only imports
- **Docstrings**: Google style convention
- **Max Complexity**: 6 (McCabe)
- **Type Annotations**: Required, use `@final` for models, `@override` for method overrides
- **Naming**: snake_case for variables/functions, PascalCase for classes

## Django Patterns
- Models: Use mixins (`UUIDMixin`, `CreatedAtMixin`, `UpdatedAtMixin`), TextChoices for enums
- Views: DRF ViewSets with `@extend_schema` decorations, return `ApiResponse`
- Imports: Absolute imports from `server.apps.`
