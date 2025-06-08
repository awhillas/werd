# Project Architecture

## Overview

Werd is a CLI tool for static website generation with AI-powered translation capabilities. The architecture follows a modular design with clear separation of concerns.

## Core Components

### CLI Layer (`cli.py`)
- **Framework**: Click for command-line interface
- **Context Management**: Passes configuration between commands
- **Lazy Loading**: Commands import modules only when needed
- **Environment Validation**: Checks for required environment variables

### Configuration (`config.py`)
- **Validation**: Pydantic models for type-safe configuration
- **Auto-creation**: Automatically creates missing directories
- **YAML-based**: Human-readable configuration files

### Content Management
- **`content_tracker.py`**: Tracks file changes and translation status
- **`content_tree.py`**: Manages hierarchical content structure
- **`data.py`**: Data models and utilities

### Translation System (`translate.py`)
- **AI Integration**: OpenAI API for content translation
- **Incremental Updates**: Only translates changed content
- **Multi-language Support**: Configurable target languages

### Rendering Engine (`render.py`)
- **Template Engine**: Jinja2 for HTML generation
- **Visitor Pattern**: Modular rendering system
- **Theme Support**: Customizable templates

## Data Flow

```
1. Content (Markdown) → Content Tracker
2. Configuration → Validation → Config Model
3. Translation → OpenAI API → Translated Content
4. Rendering → Jinja2 Templates → Static HTML
```

## File Structure Patterns

### Content Organization
```
content/
├── _layout/        # Layout elements
├── pages/          # Static pages
└── blog/           # Blog posts
```

### Translation Structure
```
_translations/
├── en/             # English translations
├── de/             # German translations
└── jp/             # Japanese translations
```

### Theme Structure
```
theme/
├── base.j2         # Base template
├── index.j2        # Home page template
└── blog/           # Blog-specific templates
```

## Key Design Patterns

### Configuration-Driven Architecture
- All behavior controlled through `config.yaml`
- Pydantic models ensure type safety
- Automatic validation and defaults

### Visitor Pattern (Rendering)
- Modular approach to HTML generation
- Easy to extend with new content types
- Clean separation of rendering logic

### Lazy Loading
- CLI commands import modules on-demand
- Faster startup times
- Reduced memory footprint

### Path Abstraction
- `pathlib.Path` used throughout
- Platform-independent file handling
- Automatic directory creation

## Extension Points

### Adding New Commands
1. Create command function with Click decorators
2. Add to CLI group in `cli.py`
3. Implement business logic in separate module

### Custom Renderers
1. Extend visitor pattern in `render.py`
2. Add new template types
3. Update configuration schema if needed

### Translation Providers
1. Abstract translation interface
2. Implement new provider class
3. Update configuration to support provider selection