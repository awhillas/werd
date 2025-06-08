# Development Workflow

## Daily Development

### Setting Up Your Environment

```bash
# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
make update

# Verify installation
python -m pip check
```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding guidelines in `CLAUDE.md`

3. **Run tests frequently**
   ```bash
   pytest
   ```

4. **Format and lint code**
   ```bash
   black werd/ tests/
   pylint werd/
   ```

## Testing Strategy

### Running Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_cli.py

# Run tests with coverage
pytest --cov=werd
```

### Writing Tests
- Use Click's `CliRunner` for CLI testing
- Leverage `isolated_filesystem()` for file system tests
- Follow existing test patterns in `tests/` directory

### Test Structure
```python
from click.testing import CliRunner
from werd.cli import cli

def test_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["command", "--option"])
        assert result.exit_code == 0
```

## Dependency Management

### Adding Dependencies

1. **Add to pyproject.toml**
   ```toml
   dependencies = [
       "new-package",
   ]
   ```

2. **Update requirements**
   ```bash
   make requirements
   ```

3. **Install updated dependencies**
   ```bash
   make init
   ```

### Development Dependencies

Add to `[project.optional-dependencies]` section:
```toml
dev = ["pytest", "pylint", "black", "new-dev-tool"]
```

## Code Quality Checks

### Pre-commit Checklist
- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black werd/ tests/`
- [ ] No linting errors: `pylint werd/`
- [ ] Type hints are correct
- [ ] Documentation is updated

### Continuous Integration
The project uses GitHub Actions for:
- Running tests on multiple Python versions
- Code quality checks
- Dependency security scanning

## Release Process

### Version Management
- Update version in `pyproject.toml`
- Update `__version__` in `werd/__init__.py`
- Create git tag: `git tag v0.1.0`

### Building Distribution
```bash
python -m build
python -m twine check dist/*
```

## Common Tasks

### Adding a New CLI Command

1. **Create command function**
   ```python
   @cli.command(name="new-command")
   @click.option("--option", help="Command option")
   @click.pass_context
   def new_command(ctx: click.Context, option: str) -> None:
       """Command description."""
       # Implementation
   ```

2. **Add business logic** in separate module
3. **Write tests** for the new command
4. **Update documentation**

### Debugging

- Use `click.echo()` for debug output
- Set breakpoints with `import pdb; pdb.set_trace()`
- Check configuration loading with verbose logging
- Test CLI commands in isolation with `CliRunner`

### Performance Profiling

```python
import cProfile
import pstats

# Profile a function
cProfile.run('your_function()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```