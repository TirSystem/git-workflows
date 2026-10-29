"""Steps of the scoped workflow .gitea/scoped_workflows/sync-milestones.yml (ADR-0018).

The workflow checks out the repository, fetches this file into shared-scripts/
and runs one command per step:

  sync_milestones.py check       decide from docs/milestones/ whether there is
                                 anything to publish (output found=true|false)
                                 and verify the two secrets when there is
  sync_milestones.py framework   make framework/ available: the project's own
                                 submodule, or the pinned release
  sync_milestones.py publish     run framework/scripts/ci-publish-milestones.sh,
                                 which always passes --accepted-only

Settings come from the environment:
  TOKEN_FOR_GITEA_REPO    reads the repositories (the project and the framework)
  TOKEN_FOR_GITEA_ISSUES  publishes issues and milestones
  DRY_RUN                 "true" previews the plan; any other value applies
  GITHUB_OUTPUT           file the check step writes its output to

A token is only handed to the called processes through their environment; it is
never on a command line and never printed. Every failure is printed as
::error::[category] message.
"""

import os
import subprocess
import sys
from pathlib import Path

FRAMEWORK_TAG = "v0.18.0"
FRAMEWORK_URL = "https://git.tirsystem.com/TirSystem/sqa-qc-framework.git"
FRAMEWORK_DIR = "framework"
PUBLISH_SCRIPT = "framework/scripts/ci-publish-milestones.sh"
MILESTONES_DIR = "docs/milestones"
REPO_TOKEN = "TOKEN_FOR_GITEA_REPO"
ISSUES_TOKEN = "TOKEN_FOR_GITEA_ISSUES"
SSH_PREFIX = "ssh://git@git.tirsystem.com:10022/"
HTTPS_PREFIX = "https://git.tirsystem.com/"


def fail(category: str, message: str) -> None:
    """Print a categorised error and exit with code 1."""
    print(f"::error::[{category}] {message}")
    sys.exit(1)


def require_secret(name: str) -> str:
    """Return the value of the secret ``name``; an empty or missing one is a configuration error."""
    value = os.environ.get(name, "")
    if not value:
        fail("configuration", f"{name} is missing or empty.")
    return value


def write_output(name: str, value: str) -> None:
    """Append ``name=value`` to the step output file when the runner provides one."""
    target = os.environ.get("GITHUB_OUTPUT")
    if not target:
        return
    with open(target, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{name}={value}\n")


def check() -> None:
    """Record whether docs/milestones/ exists and, when it does, verify both secrets."""
    found = Path(MILESTONES_DIR).is_dir()
    write_output("found", "true" if found else "false")
    if not found:
        print("No docs/milestones folder in this repository; nothing to publish.")
        return
    require_secret(REPO_TOKEN)
    require_secret(ISSUES_TOKEN)


def git_environment(token: str) -> dict[str, str]:
    """Return the environment that lets git use HTTPS with ``token``; the token stays out of the command line."""
    environment = dict(os.environ)
    environment.update(
        {
            "GIT_CONFIG_COUNT": "2",
            "GIT_CONFIG_KEY_0": f"url.{HTTPS_PREFIX}.insteadOf",
            "GIT_CONFIG_VALUE_0": SSH_PREFIX,
            "GIT_CONFIG_KEY_1": "http.extraheader",
            "GIT_CONFIG_VALUE_1": f"Authorization: token {token}",
        }
    )
    return environment


def run_git(command: list[str], environment: dict[str, str], what: str) -> None:
    """Run a git command; a failure is a tool error that names ``what`` and never the environment."""
    try:
        completed = subprocess.run(command, env=environment, check=False)
    except OSError as error:
        fail("tool", f"git cannot be started: {error}")
    if completed.returncode != 0:
        fail("tool", f"{what} failed with exit code {completed.returncode}.")


def describe_framework(environment: dict[str, str]) -> str:
    """Return the tag or commit of the framework checkout."""
    try:
        completed = subprocess.run(
            ["git", "-C", FRAMEWORK_DIR, "describe", "--tags", "--always"],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        fail("tool", f"git cannot be started: {error}")
    if completed.returncode != 0:
        fail("tool", f"git describe in {FRAMEWORK_DIR} failed with exit code {completed.returncode}.")
    return completed.stdout.strip()


def framework() -> None:
    """Use the project's framework submodule when it has the script, otherwise the pinned release."""
    token = require_secret(REPO_TOKEN)
    environment = git_environment(token)
    if Path(PUBLISH_SCRIPT).is_file():
        run_git(
            ["git", "submodule", "update", "--init", "--recursive", "--depth=1"],
            environment,
            "The submodule update",
        )
        print(f"Framework source: project submodule at {describe_framework(environment)}")
        return
    run_git(
        ["git", "clone", "--depth", "1", "--branch", FRAMEWORK_TAG, FRAMEWORK_URL, FRAMEWORK_DIR],
        environment,
        f"The clone of the framework release {FRAMEWORK_TAG}",
    )
    print(f"Framework source: release {FRAMEWORK_TAG}")


def publish() -> None:
    """Publish the accepted milestones; the script applies --accepted-only and never closes or deletes."""
    require_secret(ISSUES_TOKEN)
    environment = dict(os.environ)
    for step in ("ensure-tools", "publish"):
        try:
            completed = subprocess.run(["bash", PUBLISH_SCRIPT, step], env=environment, check=False)
        except OSError as error:
            fail("tool", f"bash cannot be started: {error}")
        if completed.returncode != 0:
            fail("tool", f"{PUBLISH_SCRIPT} {step} failed with exit code {completed.returncode}.")


def main(argv: list[str]) -> None:
    commands = {"check": check, "framework": framework, "publish": publish}
    if len(argv) != 2 or argv[1] not in commands:
        fail("configuration", "usage: sync_milestones.py check|framework|publish")
    commands[argv[1]]()


if __name__ == "__main__":
    main(sys.argv)
