from unittest.mock import patch

from typer.testing import CliRunner

from aeos.cli import REQUIRED_TOOLS, app

runner = CliRunner()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_doctor_all_present() -> None:
    with patch("aeos.cli.shutil.which", return_value="/usr/bin/tool"):
        result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    for tool in REQUIRED_TOOLS:
        assert tool in result.output
    assert "MISSING" not in result.output


def test_doctor_some_missing() -> None:
    def _which(cmd: str) -> str | None:
        return None if cmd in ("docker", "pnpm") else "/usr/bin/tool"

    with patch("aeos.cli.shutil.which", side_effect=_which):
        result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 1
    assert "docker" in result.output
    assert "pnpm" in result.output
    assert "MISSING" in result.output
