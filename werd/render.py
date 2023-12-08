import json
import os
from collections import defaultdict
from datetime import datetime
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from markdown import markdown

from werd import PACKAGEDIR
from werd.data import (
    BlogPost,
    ContentIndexPage,
    ContentPage,
    FileSystemNode,
    IndexPage,
    Page,
    Visitor,
)
from werd.strings_map import StringMap


def find_template_file(config: dict, rel_file: Path):
    """
    Schema is from most specfic to least specific:

    Examples:

    content/en/pages/about.md
    content/en/pages/index.md
    content/blog/2023-10-06/index.md

    We look for the following files in the theme directory:

    1. themes/<theme>/<category>/<name>.j2
    2. themes/<theme>/<category>/index.j2
    3. themes/<theme>/<category>.j2
    4. themes/<theme>/<name>.j2
    5. themes/<theme>/index.j2
    """

    def get_stems(stem: str, parent: str) -> list[str]:
        return [f"{stem}.j2", "index.j2"] + ([f"{parent}.j2"] if parent else [])

    # Most specific to least
    candidates = []
    for parent in rel_file.parents:
        candidates += [parent / c for c in get_stems(rel_file.stem, parent.name)]

    # Find the first one that exists
    for c in candidates:
        theme_file = config.theme_dir / c
        if theme_file.exists():
            break

    return theme_file.relative_to(config.theme_dir)


def copy_static_assets(config: dict):
    """
    Copy all static assets from the theme directory to the output directory.
    """

    def copy_assets(src_dir: Path, dest_dir: Path):
        for file in (src_dir / "assets").glob("**/*"):
            if file.is_file():
                rel_path = file.relative_to(src_dir)
                save_path = dest_dir / rel_path
                save_path.parent.mkdir(parents=True, exist_ok=True)
                save_path.write_bytes(file.read_bytes())

    print("Copying theme static assets...")
    copy_assets(config.theme_dir, config.output_dir)
    print("Copying content static assets...")
    copy_assets(config.content_dir, config.output_dir)


def get_layout_content(lang, config: dict):
    """Looks for a _layout dir and renders it as HTML from markdown."""
    root = config.translations_dir / lang / "_layout"
    if root.exists():
        return {
            child.stem: markdown(child.read_text())
            for child in root.iterdir()
            if child.is_file()
        }
    else:
        return {}


def get_languages():
    """
    Get a map of 2 letter language codes to language names in the given language.
    """
    return json.loads((PACKAGEDIR / "langs.json").read_text())


class PageTree(Visitor):
    """
    Build a tree of Page objects from a given content directory.
    Should encapsulate the logical view of the website so ideally use many different
    renderer classes to produce different formats as output.
    """

    def __init__(self, lang, config: dict, string_map: StringMap):
        self.lang = lang
        self.config = config
        self.string_map = string_map

    def find_index_subpage(self, subpages: list[FileSystemNode]):
        """Search the given subpages for an spcially named index page."""
        try:
            # Find the index replacement page in subpages if it exists
            return next(
                s for s in subpages if s.filepath.stem == self.config.index_page
            )
        except StopIteration:
            return False

    def visit(self, node: FileSystemNode, subpages: list[Page] = []):
        # Skip special directories
        if "_layout" in node.path.parts or node.path.name in [
            "assets",
        ]:
            return None

        title = self.string_map.get_title(self.lang, node.path)

        if node.is_folder():
            home_page = self.find_index_subpage(subpages)
            if home_page:
                # subpages.remove(home_page)
                return ContentIndexPage(
                    filepath=node.path,
                    title=home_page.title,
                    href=str(
                        node.path.relative_to(self.config.translations_dir)
                        / "index.html"
                    ),
                    lang=self.lang,
                    content=home_page.content,
                    subpages=subpages,
                )
            else:
                # Not a special index page, so just return a normal index page
                return IndexPage(
                    filepath=node.path,
                    title=title,
                    href=str(
                        node.path.relative_to(self.config.translations_dir)
                        / "index.html"
                    ),
                    lang=self.lang,
                    subpages=[s for s in subpages if s is not None],
                )
        else:
            if node.path.suffix == ".md":
                content = markdown(node.path.read_text())

                if node.is_a("blog"):
                    return BlogPost(
                        title=title,
                        href=str(
                            node.path.parent.relative_to(self.config.translations_dir)
                            / node.path.stem
                            / "index.html"
                        ),
                        lang=self.lang,
                        content=content,
                        filepath=node.path,
                        date=datetime.strptime(node.path.parent.name, "%Y-%m-%d"),
                    )
                else:
                    return ContentPage(
                        title=title,
                        href=str(
                            node.path.relative_to(
                                self.config.translations_dir
                            ).with_suffix(".html")
                        ),
                        lang=self.lang,
                        content=content,
                        filepath=node.path,
                    )


class HtmlPageRenderer(Visitor):
    """Transverses a Page tree and renders each Page as a HTML file."""

    def __init__(self, lang, config, root: Page, layout_content: dict[str, str]):
        self.config = config
        self.lang = lang
        self.all_languages = get_languages()
        self.root = root
        self.layout_content = layout_content
        self.env = Environment(loader=FileSystemLoader(config.theme_dir))

    def visit(self, page: Page):
        """
        Can do matching here and handle each of the Page types differently.
        """
        theme_file = find_template_file(self.config, page.filepath)
        template = self.env.get_template(str(theme_file))

        site_name = (
            self.config.site_name[self.lang]
            if self.lang in self.config.site_name
            else self.config.site_name[self.config.language.default]
        )

        # Render the HTML

        html = template.render(
            page=page,
            subpages=page.subpages if hasattr(page, "subpages") else [],
            config=self.config,
            site_name=site_name,
            home=self.root,
            pages=self.root.subpages,
            lang=self.lang,
            languages=self.all_languages,
            supported_languages=self.config.language.output,
            layout=self.layout_content,
        )

        # Save the HTML

        html = BeautifulSoup(html, "html.parser").prettify(formatter="html5")
        save_path = self.config.output_dir / page.href
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(html)


class RssRenderer(Visitor):
    """Render the RSS feed for everything."""

    ...


def render_content(config: dict):
    """Translates content and renders HTML."""
    # assert config.theme_dir.exists(), f"Theme directory '{config.theme_dir}' not found?"

    for lang in config.language.output:
        # Build the page tree

        root = config.translations_dir / lang
        root_node = FileSystemNode(root)
        page_tree = root_node.accept(PageTree(lang, config, StringMap(config)))

        # Get the layout content

        layout_content = get_layout_content(lang, config)

        # Render the HTML

        page_tree.accept(HtmlPageRenderer(lang, config, page_tree, layout_content))

    # Static assets

    copy_static_assets(config)

    # Landing page

    env = Environment(loader=FileSystemLoader(config.theme_dir))
    template = env.get_template("landing.j2")
    html = template.render(
        title=config.site_name[config.language.default],
        lang=config.language.default,
        config=config,
        languages=get_languages(),
        supported_languages=config.language.output,
        layout=layout_content,
    )
    (config.output_dir / "index.html").write_text(html)
