import json
from collections import defaultdict


class StringMap:
    """Manage a map of string translations."""

    def __init__(self, config) -> None:
        self.config = config

        # laod the strings map file

        self.strings_map_file = config.translations_dir / "strings.json"
        if self.strings_map_file.exists():
            self.filenames = json.loads(self.strings_map_file.read_text())
        else:
            self.filenames = defaultdict(dict)  # string: {lang: string}

    def add(self, string: str, lang: str, translation: str):
        if not self.is_translated(string, lang):
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
