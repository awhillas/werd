import json
import os
from collections import defaultdict
from pathlib import Path
from string import Template

import openai

from werd.content_tracker import ContentTracker
from werd.strings_map import StringMap

INPUT_TEMPLATE = """lang: ${source_lang}
---
${content}
"""
OUTPUT_TEMPLATE = """lang: ${target_lang}
---"""


def write_content_with_path(
    file: Path, targe_dir: Path, content: str, content_dir: Path
):
    """
    Write the content to the file path relative to the target path recreating
    all the subdirectories infront of the file in the target path.
    Remove the content_dir from the beginning of the path.
    """
    # Remove the content_dir from the beginning of the path
    file = file.relative_to(content_dir)

    target_dir = targe_dir / file.parent

    target_dir.mkdir(parents=True, exist_ok=True)

    (targe_dir / file).write_text(content)


def translate_string(
    content: str, source_lang: str, target_lang: str, no_markdown=False
):
    """Translate content to lang."""
    response = openai.ChatCompletion.create(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful translation assistant. Translate the markdown into the target language preserving the markdown formating."
                if no_markdown
                else "You are a helpful translation assistant. Translate the text into the target language. Do not translate the markdown formating.",
            },
            {
                "role": "user",
                "content": Template(INPUT_TEMPLATE).substitute(
                    content=content, source_lang=source_lang
                ),
            },
            {
                "role": "user",
                "content": Template(OUTPUT_TEMPLATE).substitute(
                    target_lang=target_lang
                ),
            },
        ],
    )
    return response.choices[0]["message"]["content"]


def translate_content(config: dict, translate_all: bool = False):
    """
    Generate static site from content and theme.
    """
    print("Translating!")

    tracker = ContentTracker(".hash")
    strings_map = StringMap(config)

    config.translations_dir.mkdir(parents=True, exist_ok=True)

    for file in config.content_dir.glob("**/*"):
        if (
            file.is_file()
            and file.suffix == ".md"
            and (translate_all or tracker.has_changed(str(file)))
        ):
            content = file.read_text()
            tracker.update(file)

            for lang in config.language.output:
                # Translate the filename

                string = file.stem.replace("_", " ")
                if config.language.source != lang:
                    if not strings_map.is_translated(string, lang):
                        print(f"Translating '{string}' into {lang}")
                        translation = translate_string(
                            string, config.language.source, lang
                        )
                        strings_map.add(string, lang, translation)
                else:
                    strings_map.add(string, lang, string)

                # Translate the content

                lang_dir = config.translations_dir / lang

                if lang != config.language.source:
                    print(f"Translating {file} into {lang}...")
                    translated_content = translate_string(
                        content, config.language.source, lang
                    )
                    write_content_with_path(
                        file, lang_dir, translated_content, config.content_dir
                    )

                else:
                    # Just copy the file
                    print(f"Copying {file}...")
                    write_content_with_path(file, lang_dir, content, config.content_dir)

    strings_map.save()
