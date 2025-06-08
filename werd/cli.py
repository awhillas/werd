import os
from typing import Optional

import click
from dotenv import load_dotenv

from .config import ConfigModel

load_dotenv(os.getcwd() + "/.env")

CONFIG: Optional[ConfigModel] = None


def check_env() -> None:
    """Check for environment variables."""
    if not os.getenv("OPENAI_API_KEY", False):
        raise Exception("OPENAI_API_KEY not found in environment variables?")


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx: click.Context) -> None:
    "CLI tool for static website generation with a focus on translation to any number of lnaguages via  AI"
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand != "init":
        try:
            # TODO: Optioanlly pass a config file path
            ctx.obj["config"] = ConfigModel.load()
        except FileNotFoundError:
            click.echo("config.yaml file not found. Try running `werd init`")
            exit(1)


@cli.command(name="init")
def init() -> None:
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
def translate(ctx: click.Context, all: bool, langs: Optional[str]) -> None:
    "Translate the source markdown files into the target languages."
    from werd.translate import translate_content

    langs_list: list[str] = []
    if langs:
        langs_list = langs.split(",")
        click.echo(f"Translating into {langs_list}")

    if all:
        click.echo("Translating all content files.")

    translate_content(ctx.obj["config"], all, langs_list)


@cli.command(name="render")
@click.pass_context
def render_content(ctx: click.Context) -> None:
    """Render the translated markdown files into HTML."""
    from werd.render import render_content

    render_content(ctx.obj["config"])
