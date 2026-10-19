"""Offline tests for the composite action actions/connect-wireguard.

The shell script is run with stub commands (no sudo, no wg-quick, no network),
so the generated configuration, the masking and the failure messages are
checked without touching the runner.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

from workflow_source import REPO_ROOT

ACTION_DIR = REPO_ROOT / "actions" / "connect-wireguard"
ACTION = ACTION_DIR / "action.yml"
SCRIPT = ACTION_DIR / "connect-wireguard.sh"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="bash is needed to run the action script")

KEY = "PRIVATEKEYPRIVATEKEYPRIVATEKEYPRIVATEKEY00="


@pytest.fixture(scope="module")
def document() -> dict:
    return yaml.safe_load(ACTION.read_text(encoding="utf-8"))


def run(tmp_path: Path, command: str, **env: str) -> subprocess.CompletedProcess:
    """Run the script with a stub wg-quick that records its arguments."""
    stub = tmp_path / "wg-quick"
    stub.write_text('#!/usr/bin/env bash\necho "$*" >> "$STUB_LOG"\n', encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    ping = tmp_path / "ping"
    ping.write_text("#!/usr/bin/env bash\nexit ${PING_EXIT:-0}\n", encoding="utf-8")
    ping.chmod(ping.stat().st_mode | stat.S_IXUSR)
    (tmp_path / "etc").mkdir(exist_ok=True)
    full = {
        "PATH": os.environ["PATH"],
        "WG_DIR": str(tmp_path / "etc"),
        "WG_QUICK": str(stub),
        "WG_PING": str(ping),
        "WG_SUDO": "",
        "STUB_LOG": str(tmp_path / "log"),
        # pretend the kernel has WireGuard and the tools are present
        "WG_INTERFACE": "wg0",
        **env,
    }
    # `ip link add` fails in the test environment, so wireguard-go must exist
    go = tmp_path / "wireguard-go"
    go.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    go.chmod(go.stat().st_mode | stat.S_IXUSR)
    full["PATH"] = f"{tmp_path}:{full['PATH']}"
    return subprocess.run(
        [BASH, str(SCRIPT), command], env=full, capture_output=True, text=True, check=False
    )


FIELDS = {
    "WG_PRIVATE_KEY": KEY,
    "WG_ADDRESS": "10.8.0.2/32",
    "WG_PEER_PUBLIC_KEY": "PEERPUBLICKEY=",
    "WG_ENDPOINT": "vpn.example.org:51820",
    "WG_ALLOWED_IPS": "10.8.0.0/24",
}


class TestDefinition:
    def test_is_a_composite_action(self, document):
        assert document["runs"]["using"] == "composite"

    def test_inputs_are_the_contract(self, document):
        assert set(document["inputs"]) == {
            "action", "config", "private-key", "address", "peer-public-key", "endpoint",
            "allowed-ips", "preshared-key", "dns", "persistent-keepalive", "interface",
            "health-check-host",
        }

    def test_uses_gitea_contexts_only(self):
        text = ACTION.read_text(encoding="utf-8")
        assert "gitea.action_path" in text
        assert "github." not in text

    def test_no_secret_is_interpolated_into_a_run_line(self, document):
        for step in document["runs"]["steps"]:
            assert "inputs." not in step["run"]


class TestUp:
    def test_writes_a_private_config_and_brings_the_interface_up(self, tmp_path):
        result = run(tmp_path, "up", **FIELDS)
        assert result.returncode == 0, result.stdout + result.stderr
        conf = tmp_path / "etc" / "wg0.conf"
        text = conf.read_text(encoding="utf-8")
        assert f"PrivateKey = {KEY}" in text
        assert "AllowedIPs = 10.8.0.0/24" in text
        assert "PersistentKeepalive = 25" in text
        if os.name != "nt":  # Windows has no POSIX file modes
            assert stat.S_IMODE(conf.stat().st_mode) == 0o600
        assert (tmp_path / "log").read_text(encoding="utf-8").strip() == "up wg0"

    def test_a_full_config_is_used_as_given(self, tmp_path):
        result = run(tmp_path, "up", WG_CONFIG="[Interface]\nPrivateKey = abc\n")
        assert result.returncode == 0, result.stdout
        assert (tmp_path / "etc" / "wg0.conf").read_text(encoding="utf-8").startswith("[Interface]")

    def test_the_key_is_never_printed(self, tmp_path):
        result = run(tmp_path, "up", **FIELDS)
        assert KEY not in result.stdout + result.stderr

    def test_a_missing_field_fails_with_its_name(self, tmp_path):
        fields = {k: v for k, v in FIELDS.items() if k != "WG_ENDPOINT"}
        result = run(tmp_path, "up", **fields)
        assert result.returncode == 1
        assert "::error::[configuration]" in result.stdout
        assert "WG_ENDPOINT" in result.stdout

    def test_a_bad_interface_name_fails(self, tmp_path):
        result = run(tmp_path, "up", **{**FIELDS, "WG_INTERFACE": "../etc"})
        assert result.returncode == 1
        assert "interface" in result.stdout

    def test_a_failing_health_check_fails_the_step(self, tmp_path):
        result = run(tmp_path, "up", **FIELDS, WG_HEALTH_CHECK_HOST="10.8.0.1", PING_EXIT="1")
        assert result.returncode == 1
        assert "::error::[connection]" in result.stdout


def make_exec(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class TestEnvironment:
    def test_the_userspace_variable_reaches_wg_quick_through_sudo(self, tmp_path):
        # a sudo that resets the environment, as the real one does
        sudo = make_exec(
            tmp_path / "sudo-reset",
            '#!/usr/bin/env bash\nexec env -i "PATH=$PATH" "STUB_LOG=$STUB_LOG" "$@"\n',
        )
        quick = make_exec(
            tmp_path / "quick-env",
            '#!/usr/bin/env bash\necho "$WG_QUICK_USERSPACE_IMPLEMENTATION $*" >> "$STUB_LOG"\n',
        )
        result = run(tmp_path, "up", **FIELDS, WG_SUDO=str(sudo), WG_QUICK=str(quick))
        assert result.returncode == 0, result.stdout + result.stderr
        assert "wireguard-go up wg0" in (tmp_path / "log").read_text(encoding="utf-8")

    def test_a_field_with_a_line_break_is_refused(self, tmp_path):
        result = run(tmp_path, "up", **{**FIELDS, "WG_ALLOWED_IPS": "10.8.0.0/24\nPostUp = id"})
        assert result.returncode == 1
        assert "WG_ALLOWED_IPS must be one line" in result.stdout
        assert not (tmp_path / "etc" / "wg0.conf").exists()

    def test_the_key_file_is_removed_when_wg_quick_fails(self, tmp_path):
        failing = make_exec(tmp_path / "quick-fail", "#!/usr/bin/env bash\nexit 1\n")
        result = run(tmp_path, "up", **FIELDS, WG_QUICK=str(failing))
        assert result.returncode == 1
        assert not (tmp_path / "etc" / "wg0.conf").exists()


class TestDownAndMask:
    def test_down_removes_the_config(self, tmp_path):
        run(tmp_path, "up", **FIELDS)
        result = run(tmp_path, "down")
        assert result.returncode == 0
        assert not (tmp_path / "etc" / "wg0.conf").exists()

    def test_mask_prints_every_secret(self, tmp_path):
        result = run(tmp_path, "mask", WG_PRIVATE_KEY=KEY, WG_CONFIG="[Interface]\nPrivateKey = abc")
        assert f"::add-mask::{KEY}" in result.stdout
        assert "::add-mask::abc" in result.stdout
        assert "[Interface]" not in result.stdout  # only the key values are masked

    def test_unknown_command_fails(self, tmp_path):
        assert run(tmp_path, "sideways").returncode == 1
