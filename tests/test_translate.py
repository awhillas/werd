import os
import shutil
from pathlib import Path

import pytest
import responses
from click.testing import CliRunner
from dotenv import load_dotenv

from werd.cli import cli
from werd.config import ConfigModel
from werd.translate import translate_content


def setup_std_test_env_dir(tmp_path: Path):
    """Copy all the test files accross to the temp directory."""
    shutil.copyfile(Path.cwd() / "tests/.env", tmp_path / ".env")
    shutil.copyfile(Path.cwd() / "werd/templates/config.yaml", tmp_path / "config.yaml")
    shutil.copytree(Path.cwd() / "tests/content", tmp_path / "content")
    os.chdir(tmp_path)
    load_dotenv(tmp_path / ".env")
    return tmp_path


def test_translate_command(tmp_path: Path):
    """Test the translate CLI command."""
    setup_std_test_env_dir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["translate"])
    assert result.exit_code == 0


def test_translate_function(tmp_path: Path):
    """Test just the translate command."""
    setup_std_test_env_dir(tmp_path)

    config = ConfigModel(
        **{
            "site_name": {
                "en": "My Mulitlingual Website",
            },
            "language": {
                "default": "en",
                "source": "en",
                "output": ["en", "jp", "de"],
            },
        }
    )
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.POST,
            "https://api.openai.com/v1/chat/completions",
            json={
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "gpt-3.5-turbo-0613",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Hello there, how may I assist you today?",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 9,
                    "completion_tokens": 12,
                    "total_tokens": 21,
                },
            },
        )
        translate_content(config)

    for lang in config.language.output:
        assert (config.translations_dir / lang / "about_us.md").exists()
        assert (config.translations_dir / lang / "pages" / "a-team.md").exists()
        assert (
            config.translations_dir / lang / "blog" / "2023-01-01" / "today_we_begin.md"
        ).exists()

    Path(".hash").unlink(missing_ok=True)
    shutil.rmtree("_translations")
