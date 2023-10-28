from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, validator

"""
Example:

site_name:
  en: Data Ninja
  jp: データ忍者
  ko: 데이터 닌자
  de: Daten-Ninja

language:
  default: en
  source: en
  output:
  - en
  - jp
  - ko
  - de

theme_name: something
content_dir: content
translations_dir: _translations
"""


class LanguageConfig(BaseModel):
    default: str
    source: str
    output: list[str]


class ConfigModel(BaseModel):
    site_name: dict[str, str]
    language: LanguageConfig
    index_page: str = "home"
    content_dir: Path = Path("content")
    output_dir: Path = Path("output")
    theme_dir: Path = Path("themes/default")
    translations_dir: Path = Path("_translations")

    @validator("content_dir", "translations_dir", "theme_dir")
    def validate_dir(cls, v):
        dir_path = Path(v)
        if not dir_path.exists():
            print(f"Creating {dir_path}")
            (Path.cwd() / dir_path).mkdir(parents=True, exist_ok=True)

        return dir_path


class Page(BaseModel):
    content_file: Path
    output_file: Path
    href: str
    lang: str
    title: str


class BlogPost(Page):
    date: datetime
