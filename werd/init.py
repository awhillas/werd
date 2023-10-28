import shutil
from pathlib import Path

import click

from werd import PACKAGEDIR
from werd.config import ConfigModel


def inti_command():
    """Create a config.yaml file in the current working directory."""

    shutil.copyfile(PACKAGEDIR / "templates" / "config.yaml", "config.yaml")
    click.echo("Created config.yaml file in current directory.")

    # # Check `content` dir exists
    # content_dir = Path("content")
    # content_dir.mkdir(exist_ok=True)
