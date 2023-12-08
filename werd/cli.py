import os
from pathlib import Path

import click
import yaml
from dotenv import load_dotenv

from .config import ConfigModel

load_dotenv(os.getcwd() + "/.env")

CONFIG = None


def check_env():
    """Check for environment variables."""
    if not os.getenv("OPENAI_API_KEY", False):
        raise Exception("OPENAI_API_KEY not found in environment variables?")


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    "CLI tool for static website generation with a focus on translation to any number of lnaguages via  AI"
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand != "init":
        try:
            # TODO: Optioanlly pass a config file path
            ctx.obj["config"] = ConfigModel.load()
        except FileNotFoundError as e:
            click.echo("config.yaml file not found. Try running `werd init`")
            exit(1)


@cli.command(name="init")
def init():
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
@click.option(
    "-l",
    "--langs",
    is_flag=False,
    type=click.STRING,
    required=False,
    help="Force translate a comma seperated list of languages.",
)
@click.pass_context
def translate(ctx, all: bool, langs: str):
    "Translate the source markdown files into the target languages."
    from werd.translate import translate_content

    if langs:
        langs = langs.split(",")
        click.echo(f"Translating into {langs}")
    else:
        langs = []

    translate_all = False
    if all:
        click.echo("Translating all content files.")
        translate_all = True

    translate_content(ctx.obj["config"], translate_all, langs)


@cli.command(name="render")
@click.pass_context
def render_content(ctx):
    """Render the translated markdown files into HTML."""
    from werd.render import render_content

    render_content(ctx.obj["config"])
