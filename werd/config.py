from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, validator

"""
Example:

site_name:
  en: Data Ninja

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
    theme_dir: Path = Path("theme")
    translations_dir: Path = Path("_translations")

    @validator("content_dir", "translations_dir", "theme_dir")
    def validate_dir(cls, v):
        dir_path = Path(v)
        if not dir_path.exists():
            print(f"Creating {dir_path}")
            (Path.cwd() / dir_path).mkdir(parents=True, exist_ok=True)

        return dir_path

    @classmethod
    def get_file_path(cls, path: str):
        if path is None:
            path = Path("config.yaml")

        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"{path} not found.")

        return Path(path)

    @classmethod
    def load(cls, path: Optional[str] = None):
        filepath = cls.get_file_path(path)
        return ConfigModel(**yaml.safe_load(filepath.read_text()))

    def save(self, path: Optional[str] = None):
        filepath = ConfigModel.get_file_path(path)
        filepath.write_text(yaml.dump(self.model_dump()))
