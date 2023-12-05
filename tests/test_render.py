import os
import shutil
from pathlib import Path

from werd.config import BlogPost, ConfigModel, Page
from werd.render import find_template_file, render_content

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
        "translations_dir": "_translations",
    }
)


def test_render_content(tmp_path: Path):
    # Copy the tests/content directory to _translations/en
    content_dir = Path("tests/content").absolute()
    template_dir = Path("tests/themes/default").absolute()
    os.chdir(tmp_path)
    for source, dest in [
        (content_dir, tmp_path / "_translations" / "en"),
        (template_dir, tmp_path / "themes" / "default"),
    ]:
        (dest).mkdir(parents=True)
        shutil.copytree(source, dest, dirs_exist_ok=True)

    # render the langauge content

    render_content(CONFIG)

    # Check the output directory


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
