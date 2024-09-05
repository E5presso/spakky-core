import subprocess

import toml


def get_current_branch() -> str:
    # pylint: disable=subprocess-run-check
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        stdout=subprocess.PIPE,
    )
    return result.stdout.decode("utf-8").strip()


def get_version_from_pyproject() -> str:
    with open("pyproject.toml", "r", encoding="utf-8") as f:
        pyproject = toml.load(f)
    return pyproject["tool"]["poetry"]["version"]


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


if __name__ == "__main__":
    current_branch: str = get_current_branch()
    if current_branch == "main":
        latest_version = get_version_from_pyproject()
        if latest_version:
            add_git_tag(latest_version)
        else:
            print("No version found in pyproject.toml.")
    else:
        print(f"Not on main branch (current: {current_branch}). Skipping tag creation.")
