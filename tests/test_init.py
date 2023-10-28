import os
from pathlib import Path

from click.testing import CliRunner

from werd.cli import cli


def test_init_command(tmp_path: Path):
    os.chdir(tmp_path)

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init"])

        assert Path("./config.yaml").exists(), "Should create a config.yaml file."

        assert result.exit_code == 0
        assert result.output.startswith("Created config.yaml")
