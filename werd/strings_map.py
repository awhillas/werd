import json
from collections import defaultdict
from pathlib import Path


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class StringMap(metaclass=Singleton):
    """Manage a map of string translations."""

    def __init__(self, config) -> None:
        self.config = config

        # load the strings map file

        self.strings_map_file = config.translations_dir / "strings.json"
        if self.strings_map_file.exists():
            self.filenames = json.loads(self.strings_map_file.read_text())
        else:
            self.filenames = defaultdict(dict)  # string: {lang: string}

    def add(self, string: str, lang: str, translation: str):
        if not self.is_translated(string, lang):
            if not string in self.filenames:
                self.filenames[string] = {}
            self.filenames[string][lang] = translation

    def is_translated(self, string: str, lang: str):
        return string in self.filenames and lang in self.filenames[string]

    def save(self):
        self.strings_map_file.write_text(
            json.dumps(self.filenames, indent=4, ensure_ascii=False), "utf8"
        )

    def lookup(self, lang: str, string: str):
        if string in self.filenames and lang in self.filenames[string]:
            return self.filenames[string][lang]
        else:
            return string

    @classmethod
    def to_title(self, file: Path):
        return file.stem.replace("_", " ").strip().title()

    def get_title(self, lang: str, file: Path):
        return self.lookup(lang, self.to_title(file))