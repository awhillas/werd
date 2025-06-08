# Coding Guidelines for werd Project

## Language & Dependencies
- **Python 3.8+** minimum requirement
- Uses **Click** for CLI framework
- **Pydantic** for data validation/models
- **Jinja2** for templating
- **PyYAML** for configuration

## Code Style & Quality
- **Black** for code formatting
- **Pylint** for linting  
- **pytest** for testing
- Type hints used throughout (`typing`, `Optional`, `list[str]`)

## Project Structure
- Package-based structure with `werd/` as main module
- CLI commands imported from separate modules (e.g., `from werd.translate import translate_content`)
- Configuration validation using Pydantic models
- Path handling with `pathlib.Path` objects

## Key Patterns
- **Click context passing** for configuration sharing
- **Environment variable validation** (OPENAI_API_KEY checks)
- **Lazy imports** in CLI commands to improve startup time
- **Configuration-driven** architecture with `config.yaml`
- **Path validation** with automatic directory creation

## Testing
- Uses **pytest** framework
- **Click.testing.CliRunner** for CLI testing
- Test isolation with `isolated_filesystem()`

## Development Workflow
- **Makefile** for common tasks
- **uv** for dependency management (uv.lock present)

## Documentation
- Type hints for all function parameters
- Docstrings follow standard Python conventions
- CLI help text integrated with Click decorators