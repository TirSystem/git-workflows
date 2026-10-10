"""Helpers that read workflow files and the Python embedded in them."""

import importlib.util
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
SYNC_SCRIPT = REPO_ROOT / "tools" / "sync_github_metadata.py"
PUBLISH_WORKFLOW = WORKFLOW_DIRS[0] / "publish-wiki.yml"

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


class ModuleView:
    """A script module, readable and writable by item and by attribute.

    Tests write `sync["request_json"] = fake` or `module.request_json = fake`;
    both set the attribute of the real module, so the functions of the script
    see the replacement.
    """

    def __init__(self, module: Any) -> None:
        object.__setattr__(self, "_module", module)

    def __getitem__(self, name: str) -> Any:
        return getattr(self._module, name)

    def __setitem__(self, name: str, value: Any) -> None:
        setattr(self._module, name, value)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._module, name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._module, name, value)


def load_script(path: Path, name: str) -> ModuleView:
    """Import a script file without running its `main` (its name is not `__main__`)."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return ModuleView(module)


def load_sync_module(name: str = "sync_github_metadata") -> ModuleView:
    """Import tools/sync_github_metadata.py."""
    return load_script(SYNC_SCRIPT, name)


class ScriptNamespace(dict):
    """The globals of an embedded script, readable and writable as attributes.

    Functions of the script look names up in this dict, so a test that sets
    `namespace.request_json = fake` changes what the script calls.
    """

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def load_publish_module(name: str = "embedded_publish") -> ScriptNamespace:
    """Execute the embedded publish script without running `main`."""
    (source,) = embedded_python(PUBLISH_WORKFLOW)
    namespace = ScriptNamespace({"__name__": name})
    exec(compile(source, str(PUBLISH_WORKFLOW), "exec"), namespace)
    return namespace
