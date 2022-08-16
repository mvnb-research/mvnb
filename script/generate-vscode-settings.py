from json import dumps
from pathlib import Path
from sys import executable

vscode = Path(".vscode")

gitignore = vscode / ".gitignore"

settings_json = vscode / "settings.json"

settings = {
    "coverage-gutters.showLineCoverage": True,
    "explorer.excludeGitIgnore": False,
    "python.linting.flake8Enabled": True,
    "python.testing.pytestEnabled": True,
    "python.defaultInterpreterPath": executable,
}

if __name__ == "__main__":
    # create .vscode
    vscode.mkdir(exist_ok=True)

    # create .vscode/.gitignore
    gitignore.write_text("*")

    # create .vscode/settings.json
    settings_json.write_text(dumps(settings, indent=2))
