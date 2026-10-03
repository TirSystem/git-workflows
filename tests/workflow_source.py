"""Helpers that read workflow files and the Python embedded in them."""

import re
import textwrap
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIRS = (
    REPO_ROOT / ".gitea" / "scoped_workflows",
    REPO_ROOT / ".gitea" / "workflows",
)
SYNC_WORKFLOW = WORKFLOW_DIRS[0] / "sync-github-metadata.yml"

_HEREDOC = re.compile(
    r"^[ \t]*python3 - <<'PY'\r?\n(?P<code>.*?)^[ \t]*PY[ \t]*\r?$",
    re.DOTALL | re.MULTILINE,
)


def workflow_files() -> list[Path]:
    """Return every workflow file in the known workflow directories."""
    files: list[Path] = []
    for directory in WORKFLOW_DIRS:
        if directory.is_dir():
            files += sorted(directory.glob("*.yml")) + sorted(directory.glob("*.yaml"))
    return files


def embedded_python(path: Path) -> list[str]:
    """Return the source of each `python3 - <<'PY'` heredoc in a workflow."""
    text = path.read_text(encoding="utf-8")
    return [
        textwrap.dedent(match.group("code").replace("\r\n", "\n"))
        for match in _HEREDOC.finditer(text)
    ]


def load_sync_module(name: str = "embedded_sync") -> dict[str, Any]:
    """Execute the embedded sync script without running `main`."""
    (source,) = embedded_python(SYNC_WORKFLOW)
    namespace: dict[str, Any] = {"__name__": name}
    exec(compile(source, str(SYNC_WORKFLOW), "exec"), namespace)
    return namespace
