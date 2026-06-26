from pathlib import Path

from aeos.generators.basic import generate
from aeos.generators.python import generate as generate_python


def test_basic_generator_creates_structure(tmp_path: Path) -> None:
    name = "test-project"
    project = tmp_path / name
    project.mkdir()

    created = generate(project, name)

    readme = (project / "README.md").read_text()
    assert readme == f"# {name}\n\nGenerated with AEOS.\n"
    assert ".venv/" in (project / ".gitignore").read_text()
    assert (project / "aeos.toml").exists()
    for sub in [
        "governance/adr",
        "governance/rfc",
        "governance/dec",
        "governance/standards",
        "governance/playbooks",
        "docs",
        "src",
        "tests",
    ]:
        assert (project / sub).is_dir()
    assert f"{name}/" in created
    assert len(created) > 0


def test_python_generator_creates_structure(tmp_path: Path) -> None:
    name = "demo-api"
    pkg = "demo_api"
    project = tmp_path / name
    project.mkdir()

    created = generate_python(project, name)

    assert (project / "pyproject.toml").exists()
    assert (
        project / "src" / pkg / "version.py"
    ).read_text() == '__version__ = "0.1.0"\n'
    assert (project / "src" / pkg / "__init__.py").exists()
    assert (project / "tests" / "unit" / "test_version.py").exists()
    assert (project / "governance" / "adr").is_dir()
    assert (project / "README.md").read_text() == f"# {name}\n\nGenerated with AEOS.\n"
    assert "dist/" in (project / ".gitignore").read_text()
    assert f"{name}/" in created
    assert len(created) > 0
