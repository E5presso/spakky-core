import subprocess
from typing import Any

import toml


def get_current_branch() -> str:
    # pylint: disable=subprocess-run-check
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        stdout=subprocess.PIPE,
    )
    return result.stdout.decode("utf-8").strip()


def get_version_from_pyproject() -> str | None:
    with open("pyproject.toml", "r", encoding="utf-8") as f:
        pyproject: dict[str, Any] = toml.load(f)
    return pyproject["tool"]["poetry"].get("version", None)


def add_git_tag(version: str) -> None:
    # pylint: disable=subprocess-run-check
    result = subprocess.run(
        ["git", "tag", "--list", version],
        stdout=subprocess.PIPE,
    )
    if version in result.stdout.decode("utf-8").strip().split("\n"):
        print(f"Tag {version} already exists.")
        return
    subprocess.run(["git", "tag", version])
    print(f"Tag {version} created.")


def main() -> None:
    current_branch: str = get_current_branch()
    print(f"[GIT TAG] Current branch: {current_branch}")
    if current_branch == "main":
        latest_version: str | None = get_version_from_pyproject()
        if latest_version is not None:
            add_git_tag(latest_version)
            return
        print("[GIT TAG] No version found in pyproject.toml")
        return
    print(f"[GIT TAG] Not on main branch (current: {current_branch})")
    return


if __name__ == "__main__":
    main()
