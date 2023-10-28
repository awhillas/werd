import os
from pathlib import Path

from werd.config import BlogPost, ConfigModel, Page
from werd.render import find_template_file, get_blog_posts, get_page_list

CONFIG = ConfigModel(
    **{
        "site_name": {
            "en": "Data Ninja",
            "jp": "データ忍者",
        },
        "language": {
            "default": "en",
            "source": "en",
            "output": ["en", "jp"],
        },
    }
)


def test_render_find_template_file(tmp_path: Path):
    os.chdir(tmp_path)

    (tmp_path / "themes" / "default").mkdir(parents=True)
    Path("themes/default/index.j2").write_text("{{ content }}")

    for example in [
        "pages/index.md",
        "pages/about.md",
        "blog/2023-01-01/index.md",
    ]:
        template_path = find_template_file(CONFIG, Path(example))
        assert template_path == Path(
            "themes/default/index.j2"
        ), "Should use the most general 'index' template"

    # Pages

    (tmp_path / "themes" / "default" / "pages").mkdir(parents=True)

    # General pages template

    Path("themes/default/pages/index.j2").write_text("{{ content }}")
    for example in [
        "pages/index.md",
        "pages/about.md",
    ]:
        template_path = find_template_file(CONFIG, Path(example))
        assert template_path == Path(
            "themes/default/pages/index.j2"
        ), "Should use the more specific 'pages' template"
    template_path = find_template_file(
        CONFIG, Path("content/ko/blog/2023-01-01/index.md")
    )
    assert template_path == Path(
        "themes/default/index.j2"
    ), "Should use the most general 'index' template still"

    # Specific about page template

    Path("themes/default/pages/about.j2").write_text("{{ content }}")
    template_path = find_template_file(CONFIG, Path("pages/about.md"))
    assert template_path == Path(
        "themes/default/pages/about.j2"
    ), "Should use the more specific 'about' page template"

    # Blog

    (tmp_path / "themes" / "default" / "blog").mkdir(parents=True)
    Path("themes/default/blog/index.j2").write_text("{{ content }}")
    for example in [
        "blog/2233-03-22/index.md",
        "blog/2233-03-22/something.md",
        "blog/2233-03-22/kirk_is_born.md",
    ]:
        template_path = find_template_file(CONFIG, Path(example))
        assert template_path == Path(
            "themes/default/blog/index.j2"
        ), "Should use the more specific 'blog' template"

    # Specific blog page template

    Path("themes/default/blog/kirk_is_born.j2").write_text("{{ content }}")
    template_path = find_template_file(CONFIG, Path("blog/2233-03-22/kirk_is_born.md"))
    assert template_path == Path(
        "themes/default/blog/kirk_is_born.j2"
    ), "Should use the more specific 'kirk_is_born' blog template"


def test_render_get_page_list(tmp_path: Path):
    config = CONFIG.copy(update={"content_dir": Path("tests/content")})

    pages_list = get_page_list(config)

    assert len(pages_list) == 2, "Should have 2 pages"
    for lang in pages_list:
        assert len(pages_list) == len(
            CONFIG.language.output
        ), "Should have same number of sets of pages as languages"
        for p in pages_list[lang]:
            assert isinstance(p, Page), "Should be a Page object"
            assert str(p.href).startswith(f"/{lang}"), "Should have the language prefix"


def test_render_get_blog_posts(tmp_path: Path):
    config = CONFIG.copy(update={"content_dir": Path("tests/content")})

    blog_posts = get_blog_posts(config)

    for lang in blog_posts:
        assert len(blog_posts) == len(
            CONFIG.language.output
        ), "Should have same number of sets of pages as languages"
        for p in blog_posts[lang]:
            assert isinstance(p, BlogPost), "Should be a BlogPost object"
            assert p.href.startswith(f"/{lang}"), "Should have the language prefix"
