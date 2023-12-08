import json
import os
from collections import defaultdict
from pathlib import Path
from string import Template

import tiktoken
from openai import OpenAI

from werd.content_tracker import ContentTracker
from werd.strings_map import StringMap

INPUT_TEMPLATE = """lang: ${source_lang}
---
${content}
"""
OUTPUT_TEMPLATE = """lang: ${target_lang}
---"""


def count_tokens(messages, model="gpt-3.5-turbo"):
    """
    Return the number of tokens used by a list of messages.
    From" https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        # print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return count_tokens(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        # print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return count_tokens(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""count_tokens() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


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

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful translation assistant. "
                "Translate the text into the target language. "
                "Do not translate the markdown formating."
                if no_markdown
                else "You are a helpful translation assistant. "
                "Translate the markdown into the target language preserving the markdown formating."
            ),
        },
        {
            "role": "user",
            "content": Template(INPUT_TEMPLATE).substitute(
                content=content, source_lang=source_lang
            ),
        },
        {
            "role": "user",
            "content": Template(OUTPUT_TEMPLATE).substitute(target_lang=target_lang),
        },
    ]

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-32k",
        messages=messages,
        max_tokens=count_tokens(messages, model="gpt-4-32k")
        * 2,  # I guess this ratio depends on the two languages?
    )
    return response.choices[0].message.content


def translate_content(config: dict, translate_all: bool = False, langs: list = []):
    """
    Generate static site from content and theme.
    """
    print("Translating!")

    tracker = ContentTracker(".hash")
    strings_map = StringMap(config)

    config.translations_dir.mkdir(parents=True, exist_ok=True)

    # Bits and pieces

    languages = langs if langs else config.language.output

    for lang in languages:
        if lang != config.language.source:
            for string in ["blog", config.site_name[config.language.source]]:
                if not strings_map.is_translated(string, lang):
                    print(f"Translating '{string}' into {lang}...")
                    translation = translate_string(
                        string, config.language.source, lang, no_markdown=True
                    )
                    print("\r" + translation)
                    strings_map.add(string, lang, translation)

    # Content files

    for file in config.content_dir.glob("**/*"):
        if (
            file.is_file()
            and file.suffix == ".md"
            and (translate_all or langs or tracker.has_changed(str(file)))
        ):
            content = file.read_text()
            tracker.update(file)

            for lang in languages:
                # Translate the filename

                string = StringMap.to_title(file)
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
                    print(f"Translating file {file} into {lang}...")
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
