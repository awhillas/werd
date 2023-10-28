import os
from pathlib import Path

import click
import yaml
from dotenv import load_dotenv

from .config import ConfigModel

load_dotenv(os.getcwd() + "/.env")


def check_env():
    """Check for environment variables."""
    if not os.getenv("OPENAI_API_KEY", False):
        raise Exception("OPENAI_API_KEY not found in environment variables?")


def check_config() -> ConfigModel:
    """Check for config file."""
    if not Path("config.yaml").exists():
        raise FileNotFoundError("config.yaml file not found.")

    with open("config.yaml", "r") as f:
        config = ConfigModel(**yaml.safe_load(f))

    return config


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    "CLI tool for static website generation with a focus on translationt to any number of lnaguages via AI"

    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    if ctx.invoked_subcommand != "init":
        ctx.ensure_object(dict)
        try:
            ctx.obj["config"] = check_config()
        except FileNotFoundError as e:
            click.echo("config.yaml file not found. Try running `werd init`")
            exit(1)


@cli.command(name="init")
@click.pass_context
def init(ctx):
    "Create a config.yaml file."
    from werd.init import inti_command

    inti_command()


@cli.command(name="translate")
@click.option(
    "-a",
    "--all",
    is_flag=True,
    help="All translation even if the source file has not changed.",
)
@click.pass_context
def translate(ctx, all: bool):
    "Translate the source markdown files into the target languages."
    from werd.translate import translate_content

    translate_all = False
    if all:
        click.echo("Translating all files.")
        translate_all = True

    translate_content(ctx["config"], translate_all)


def render_content(ctx):
    from werd.render import render_content

    render_content(ctx["config"])
