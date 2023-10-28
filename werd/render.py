import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markdown import markdown

from werd import PACKAGEDIR
from werd.config import BlogPost, Page
from werd.strings_map import StringMap


def get_languages(config: dict):
    """
    Get a map of 2 letter language codes to language names in the given language.
    """
    return json.loads((PACKAGEDIR / "langs.json").read_text())


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


def render_html_content(
    lang: str,
    config: dict,
    theme_file: Path,
    content: str,
    pages: dict[str, Page],
    blog_posts: list[BlogPost],
    all_languages: dict[str, str],
):
    """
    Render the HTML for the given file using the given theme file.
    """
    env = Environment(loader=FileSystemLoader(config.theme_dir))
    template = env.get_template(str(theme_file))
    return template.render(
        config=config,
        content=content,
        site_name=config.site_name,
        title=config.site_name[lang]
        if lang in config.site_name
        else config.site_name[config.language.default],
        lang=lang,
        pages=pages,
        blog_posts=blog_posts,
        languages=all_languages,
    )


def get_page_list(config: dict):
    """
    Get a list of all pages in the content directory excluding blog posts.
    """
    pages = defaultdict(list)
    for lang in config.language.output:
        for file in (config.content_dir).glob(f"**/*"):
            if file.is_file() and file.suffix == ".md" and "blog" not in file.parts:
                rel_path = file.relative_to(config.content_dir)

                if rel_path.stem == config.index_page:
                    pages[lang].append(
                        Page(
                            content_file=rel_path,
                            output_file=Path(f"/{lang}")
                            / rel_path.parent
                            / "index.html",
                            href=str(Path(f"/{lang}") / rel_path.parent / "index.html"),
                            lang=lang,
                            title=file.stem.replace("_", " "),
                        )
                    )
                else:
                    pages[lang].append(
                        Page(
                            content_file=rel_path,
                            output_file=Path(f"/{lang}")
                            / rel_path.with_suffix(".html"),
                            href=str(Path(f"/{lang}") / rel_path.with_suffix(".html")),
                            lang=lang,
                            title=file.stem.replace("_", " "),
                        )
                    )

    return pages


def get_blog_posts(config: dict):
    """
    Get a list of all blog posts in the 'blog' content dir. ordered by date.
    i.e. content/blog/<year>-<month>-<day>/<name>.md
    """
    posts = defaultdict(list)
    for lang in config.language.output:
        for file in (config.content_dir / "blog").glob(f"**/*"):
            if file.is_file() and file.suffix == ".md":
                rel_path = file.relative_to(config.content_dir)
                output_file = Path(f"/{lang}") / rel_path.with_suffix(".html")
                posts[lang].append(
                    BlogPost(
                        content_file=rel_path,
                        output_file=output_file,
                        href=str(output_file),
                        lang=lang,
                        title=file.stem.replace("_", " "),
                        date=datetime.strptime(file.parent.name, "%Y-%m-%d"),
                    )
                )
        posts[lang] = sorted(posts[lang], key=lambda p: p.date, reverse=True)
    return posts


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


def render_content(config: dict):
    """
    Find the theme file jinja2 template that applies to each file in the content directory.
    Render out it's content to the output directory.
    Save it to the output directory.
    """
    print("Rendering HTML...")
    pages_list = get_page_list(config)
    blog_posts = get_blog_posts(config)
    all_languages = get_languages(config)  # Well, a lot of them anyway
    string_map = StringMap(config)

    for lang in config.language.output:
        print(f"Rendering {lang}...")
        translated_pages = {
            string_map.lookup(lang, page.title): page for page in pages_list[lang]
        }
        for file in (config.translations_dir / lang).glob(f"**/*"):
            if file.is_file() and file.suffix == ".md":
                print(f"\t{file}")
                # Find the theme file that applies to this file
                rel_path = file.relative_to(config.translations_dir / lang)
                theme_file = find_template_file(config, rel_path).relative_to(
                    config.theme_dir
                )
                html_content = markdown(file.read_text())
                html = render_html_content(
                    lang=lang,
                    config=config,
                    theme_file=theme_file,
                    content=html_content,
                    pages=translated_pages,
                    blog_posts=blog_posts[lang],
                    all_languages=all_languages,
                )

                if rel_path.stem == config.index_page:
                    save_path = (
                        config.output_dir / lang / rel_path.parent / "index.html"
                    )
                else:
                    save_path = config.output_dir / lang / rel_path.with_suffix(".html")

                save_path.parent.mkdir(parents=True, exist_ok=True)
                save_path.write_text(html)

                print(f"\t\t{save_path}")

    # Jinja2 environment for rendering landing page
    env = Environment(loader=FileSystemLoader(config.theme_dir))

    # Landing page

    if (config.theme_dir / "landing.j2").exists():
        template = env.get_template(str("landing.j2"))
        html = template.render(
            title=config.site_name[config.language.default],
            lang=config.language.default,
            supported_languages=config.language.output,
            languages=all_languages,
        )
        save_path = config.output_dir / "index.html"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(html)
        print(f"\t\t{save_path}")
    else:
        print("No landing page found.")

    # Blog index
    # Use the blog_index.j2 template if it exists and generate a blog index page in the /blog directory

    if (config.theme_dir / "blog_index.j2").exists():
        template = env.get_template(str("blog_index.j2"))
        html = template.render(
            config=config,
            title=config.site_name[config.language.default],
            lang=config.language.default,
            blog_posts=blog_posts[config.language.default],
            languages=all_languages,
        )
        save_path = config.output_dir / "blog" / "index.html"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(html)
        print(f"\t\t{save_path}")

    # Static assets

    copy_static_assets(config)
