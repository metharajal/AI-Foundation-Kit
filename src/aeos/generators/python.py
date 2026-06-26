from pathlib import Path

from aeos.generators.base import write_common_files


def generate(project: Path, name: str) -> list[str]:
    pkg = name.replace("-", "_")

    dirs = [
        project / "governance" / "adr",
        project / "governance" / "rfc",
        project / "governance" / "dec",
        project / "governance" / "standards",
        project / "governance" / "playbooks",
        project / "docs",
        project / "src" / pkg,
        project / "tests" / "unit",
    ]
    for d in dirs:
        d.mkdir(parents=True)

    write_common_files(project, name)

    (project / ".gitignore").write_text(
        ".venv/\n__pycache__/\n.DS_Store\ndist/\n*.egg-info/\n"
    )

    (project / "pyproject.toml").write_text(
        "[build-system]\n"
        'requires = ["hatchling"]\n'
        'build-backend = "hatchling.build"\n'
        "\n[project]\n"
        f'name = "{name}"\n'
        'version = "0.1.0"\n'
        'requires-python = ">=3.12"\n'
        "\n[tool.uv]\n"
        'dev-dependencies = ["pytest>=8.0"]\n'
        "\n[tool.hatch.build.targets.wheel]\n"
        f'packages = ["src/{pkg}"]\n'
        "\n[tool.pytest.ini_options]\n"
        'testpaths = ["tests"]\n'
    )

    (project / "src" / pkg / "__init__.py").write_text(
        f'from {pkg}.version import __version__\n\n__all__ = ["__version__"]\n'
    )

    (project / "src" / pkg / "version.py").write_text('__version__ = "0.1.0"\n')

    (project / "tests" / "unit" / "test_version.py").write_text(
        f"from {pkg}.version import __version__\n"
        "\n\n"
        "def test_version() -> None:\n"
        '    assert __version__ == "0.1.0"\n'
    )

    return [
        f"{name}/",
        f"{name}/README.md",
        f"{name}/aeos.toml",
        f"{name}/.gitignore",
        f"{name}/pyproject.toml",
        f"{name}/governance/",
        f"{name}/docs/",
        f"{name}/src/{pkg}/",
        f"{name}/src/{pkg}/__init__.py",
        f"{name}/src/{pkg}/version.py",
        f"{name}/tests/unit/",
        f"{name}/tests/unit/test_version.py",
    ]
