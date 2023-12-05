import json
import os
from collections import defaultdict
from datetime import datetime
from functools import partial
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markdown import markdown

from werd import PACKAGEDIR
from werd.data import BlogPost, FileSystemNode, IndexPage, Page, PageTreeNode, Visitor
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

    return theme_file


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


class LayoutContentRenderer(Visitor):
    """Looks for a _layout dir and renders it as HTML from markdown."""

    def __init__(self, lang, config: dict):
        self.lang = lang
        self.config = config

    def visit(self, node: FileSystemNode, subpages: list[Page] = []):
        if not node.is_folder():
            return node.path.stem, markdown(node.path.read_text())


class PageTree(Visitor):
    """Build a tree of Page objects from a given content directory."""

    def __init__(self, lang, config: dict, string_map: StringMap):
        self.lang = lang
        self.config = config
        self.string_map = string_map

    def visit(self, node: FileSystemNode, subpages: list[Page] = []):
        if node.is_folder() and not node.path.name.startswith("_"):
            return IndexPage(
                title=self.string_map.get_title(self.lang, node.path),
                href=str(
                    node.path.relative_to(self.config.translations_dir) / "index.html"
                ),
                lang=self.lang,
                subpages=[s for s in subpages if s is not None],
            )
        else:
            if node.path.suffix == ".md":
                content = markdown(node.path.read_text())
                if node.is_a("blog"):
                    return BlogPost(
                        title=self.string_map.get_title(self.lang, node.path),
                        href=str(
                            node.path.parent.relative_to(self.config.translations_dir)
                            / node.path.stem
                            / "index.html"
                        ),
                        lang=self.lang,
                        content=content,
                        content_file=node.path,
                        date=datetime.strptime(node.path.parent.name, "%Y-%m-%d"),
                    )
                else:
                    return Page(
                        title=self.string_map.get_title(self.lang, node.path),
                        href=str(
                            node.path.relative_to(
                                self.config.translations_dir
                            ).with_suffix(".html")
                        ),
                        lang=self.lang,
                        content=content,
                        content_file=node.path,
                    )


class HtmlPageRenderer(Visitor):
    """Transverses a Page tree and renders each Page as a HTML file."""

    def __init__(
        self, lang, config, root: PageTreeNode, layout_content: dict[str, str]
    ):
        self.config = config
        self.lang = lang
        self.all_languages = self.get_languages()
        self.root = root
        self.layout_content = layout_content
        self.env = Environment(loader=FileSystemLoader(config.theme_dir))

    def get_languages():
        """
        Get a map of 2 letter language codes to language names in the given language.
        """
        return json.loads((PACKAGEDIR / "langs.json").read_text())

    def visit(self, node: PageTreeNode):
        theme_file = find_template_file(self.config, node.path)

        template = self.env.get_template(str(theme_file))

        site_name = (
            self.config.site_name[self.lang]
            if self.lang in self.config.site_name
            else self.config.site_name[self.config.language.default]
        )

        html = template.render(
            page=node,
            config=self.config,
            site_name=site_name,
            home=self.root,
            pages=self.root.subpages,
            lang=self.lang,
            languages=self.all_languages,
            supported_languages=self.config.language.output,
            layout=self.layout_content,
        )


def render_content(config: dict):
    """Translates content and renders HTML."""
    for lang in config.language.output:
        # Build the page tree

        root = config.translations_dir / lang
        root_node = FileSystemNode(root)
        page_tree = root_node.accept(PageTree(lang, config, StringMap(config)))

        # Get the layout content

        layout_content_dir = root / "_layout"
        if layout_content_dir.exists():
            layout_content = FileSystemNode(layout_content_dir).accept(
                LayoutContentRenderer(lang, config)
            )
        else:
            layout_content = {}

        # Render the HTML

        root_node.accept(HtmlPageRenderer(lang, config, page_tree, layout_content))

    # Static assets

    copy_static_assets(config)
