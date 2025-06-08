# Developer Setup

## Prerequisites

- Python 3.8 or higher
- pip and pip-tools
- OpenAI API key (for translation features)

## Installation

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd werd
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

Using the Makefile (recommended):

```bash
make init
```

Or manually:

```bash
python -m pip install --upgrade pip wheel
python -m pip install --upgrade -r requirements/main.txt -r requirements/dev.txt -e .
python -m pip check
```

### 3. Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Development Tools

### Code Quality

- **Black**: Code formatting
- **Pylint**: Linting and code analysis
- **pytest**: Testing framework

### Dependency Management

The project uses `pip-tools` for dependency management:

```bash
# Update dependencies
make requirements

# Full update (dependencies + install)
make update
```

### Testing

Run tests with:

```bash
pytest
```

Tests are located in the `tests/` directory and use Click's testing utilities for CLI testing.

## Project Structure

```
werd/
├── werd/           # Main package
│   ├── cli.py      # Click CLI commands
│   ├── config.py   # Pydantic configuration models
│   ├── translate.py # Translation functionality
│   ├── render.py   # HTML rendering
│   └── ...
├── tests/          # Test suite
├── requirements/   # Pinned dependencies
├── docs/           # Documentation
└── pyproject.toml  # Project configuration
```

## Configuration

The tool requires a `config.yaml` file in your working directory. Initialize one with:

```bash
werd init
```

This creates a configuration file that defines:
- Site name (multilingual)
- Language settings (source, output languages)
- Directory paths for content, themes, and output