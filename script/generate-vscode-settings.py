from json import dumps
from pathlib import Path
from sys import executable

vscode = Path(".vscode")

gitignore = vscode / ".gitignore"

settings_json = vscode / "settings.json"

python = executable

pflake8 = str(Path(executable).parent / "pflake8")

settings = {
    "coverage-gutters.showLineCoverage": True,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "explorer.excludeGitIgnore": False,
    "python.defaultInterpreterPath": executable,
    "python.linting.flake8Enabled": True,
    "python.linting.flake8Path": pflake8,
    "python.testing.pytestEnabled": True,
}

if __name__ == "__main__":
    # create .vscode
    vscode.mkdir(exist_ok=True)

    # create .vscode/.gitignore
    gitignore.write_text("*")

    # create .vscode/settings.json
    settings_json.write_text(dumps(settings, indent=2))
