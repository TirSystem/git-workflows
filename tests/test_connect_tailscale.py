"""Offline tests for the composite action actions/connect-tailscale.

The shell script is run with stub tailscale and tailscaled commands (no sudo,
no network), so the arguments, the key file, the masking and the failure
messages are checked without touching the runner.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

from workflow_source import REPO_ROOT

ACTION_DIR = REPO_ROOT / "actions" / "connect-tailscale"
ACTION = ACTION_DIR / "action.yml"
SCRIPT = ACTION_DIR / "connect-tailscale.sh"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="bash is needed to run the action script")

AUTHKEY = "tskey-auth-SECRETSECRETSECRET"
OAUTH = "tskey-client-SECRETSECRETSECRET"

# the stub records its arguments and, for `up`, the content of the key file
TAILSCALE_STUB = """#!/usr/bin/env bash
echo "$*" >> "$STUB_LOG"
case "$1" in
  up)
    for a in "$@"; do
      case "$a" in --auth-key=file:*) cat "${a#--auth-key=file:}" > "$STUB_KEY" ;; esac
    done
    exit "${UP_EXIT:-0}" ;;
  ping) exit "${PING_EXIT:-0}" ;;
  version)
    # the daemon answers only after tailscaled was started, and after DAEMON_DELAY calls
    [ -f "$STUB_DAEMON" ] || exit 1
    n=$(( $(cat "$STUB_DAEMON") + 1 )); echo "$n" > "$STUB_DAEMON"
    [ "$n" -gt "${DAEMON_DELAY:-0}" ] ;;
esac
"""


@pytest.fixture(scope="module")
def document() -> dict:
    return yaml.safe_load(ACTION.read_text(encoding="utf-8"))


def make_stub(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def run(tmp_path: Path, command: str, **env: str) -> subprocess.CompletedProcess:
    make_stub(tmp_path / "tailscale", TAILSCALE_STUB)
    make_stub(
        tmp_path / "tailscaled",
        '#!/usr/bin/env bash\necho "$*" >> "$STUB_LOG"\necho 0 > "$STUB_DAEMON"\n',
    )
    full = {
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "TS_SUDO": "",
        "TS_STATE_DIR": str(tmp_path / "state"),
        "STUB_LOG": str(tmp_path / "log"),
        "STUB_KEY": str(tmp_path / "key"),
        "STUB_DAEMON": str(tmp_path / "daemon"),
        "TS_WAIT_INTERVAL": "0.05",
        "TS_START_WAIT": "100",
        **env,
    }
    return subprocess.run(
        [BASH, str(SCRIPT), command], env=full, capture_output=True, text=True, check=False
    )


def log(tmp_path: Path) -> str:
    return (tmp_path / "log").read_text(encoding="utf-8")


class TestDefinition:
    def test_is_a_composite_action(self, document):
        assert document["runs"]["using"] == "composite"

    def test_inputs_are_the_contract(self, document):
        assert set(document["inputs"]) == {
            "action", "authkey", "oauth-secret", "tags", "hostname", "version",
            "sha256", "userspace-networking", "args", "timeout", "health-check-host",
        }

    def test_uses_gitea_contexts_only(self):
        text = ACTION.read_text(encoding="utf-8")
        assert "gitea.action_path" in text
        assert "github." not in text.replace("tailscale/github-action", "").replace("GitHub", "")

    def test_no_input_is_interpolated_into_a_run_line(self, document):
        for step in document["runs"]["steps"]:
            assert "inputs." not in step["run"]


class TestUp:
    def test_joins_with_an_auth_key_file_not_the_key_on_the_command_line(self, tmp_path):
        result = run(tmp_path, "up", TS_AUTHKEY=AUTHKEY, TS_TAGS="tag:ci", TS_HOSTNAME="ci-1")
        assert result.returncode == 0, result.stdout + result.stderr
        calls = log(tmp_path)
        assert AUTHKEY not in calls
        assert AUTHKEY not in result.stdout + result.stderr
        assert (tmp_path / "key").read_text(encoding="utf-8") == AUTHKEY
        assert "--advertise-tags=tag:ci" in calls
        assert "--hostname=ci-1" in calls
        assert not (tmp_path / "state" / "authkey").exists()

    def test_an_oauth_secret_becomes_an_ephemeral_preauthorized_key(self, tmp_path):
        result = run(tmp_path, "up", TS_OAUTH_SECRET=OAUTH, TS_TAGS="tag:ci")
        assert result.returncode == 0, result.stdout
        assert (tmp_path / "key").read_text(encoding="utf-8") == f"{OAUTH}?ephemeral=true&preauthorized=true"

    def test_userspace_networking_starts_the_daemon_without_a_tun_device(self, tmp_path):
        run(tmp_path, "up", TS_AUTHKEY=AUTHKEY, TS_USERSPACE="true")
        assert "--tun=userspace-networking --socks5-server=localhost:1055" in log(tmp_path)

    def test_extra_args_are_passed(self, tmp_path):
        run(tmp_path, "up", TS_AUTHKEY=AUTHKEY, TS_ARGS="--accept-routes --shields-up")
        assert "--accept-routes --shields-up" in log(tmp_path)

    @pytest.mark.parametrize(
        ("env", "message"),
        [
            ({}, "give authkey or oauth-secret"),
            ({"TS_AUTHKEY": AUTHKEY, "TS_OAUTH_SECRET": OAUTH}, "not both"),
            ({"TS_OAUTH_SECRET": OAUTH}, "tags is required"),
            ({"TS_AUTHKEY": AUTHKEY, "TS_TAGS": "ci"}, "tags must look like"),
            ({"TS_AUTHKEY": AUTHKEY, "TS_TIMEOUT": "soon"}, "timeout"),
            ({"TS_AUTHKEY": AUTHKEY, "TS_VERSION": "1.x"}, "version"),
            ({"TS_AUTHKEY": AUTHKEY, "TS_VERSION": "latest"}, "version"),
            ({"TS_AUTHKEY": AUTHKEY, "TS_SHA256": "abc"}, "sha256"),
            ({"TS_AUTHKEY": AUTHKEY, "TS_USERSPACE": "yes"}, "userspace-networking"),
            ({"TS_AUTHKEY": AUTHKEY, "TS_HOSTNAME": "bad name"}, "hostname"),
        ],
    )
    def test_bad_inputs_fail_before_anything_starts(self, tmp_path, env, message):
        result = run(tmp_path, "up", **env)
        assert result.returncode == 1
        assert "::error::[configuration]" in result.stdout
        assert message in result.stdout
        assert not (tmp_path / "log").exists()

    def test_a_failing_up_fails_and_deletes_the_key_file(self, tmp_path):
        result = run(tmp_path, "up", TS_AUTHKEY=AUTHKEY, UP_EXIT="1")
        assert result.returncode == 1
        assert "::error::[connection]" in result.stdout
        assert not (tmp_path / "state" / "authkey").exists()
        assert AUTHKEY not in result.stdout

    def test_a_failing_health_check_fails_the_step(self, tmp_path):
        result = run(tmp_path, "up", TS_AUTHKEY=AUTHKEY, TS_HEALTH_CHECK_HOST="db", PING_EXIT="1")
        assert result.returncode == 1
        assert "health-check-host" in result.stdout


class TestDaemon:
    def test_waits_until_the_daemon_answers(self, tmp_path):
        result = run(tmp_path, "up", TS_AUTHKEY=AUTHKEY, DAEMON_DELAY="5")
        assert result.returncode == 0, result.stdout
        assert "up --auth-key" in log(tmp_path)

    def test_a_daemon_that_never_answers_fails_before_up(self, tmp_path):
        result = run(tmp_path, "up", TS_AUTHKEY=AUTHKEY, DAEMON_DELAY="1000", TS_START_WAIT="3")
        assert result.returncode == 1
        assert "::error::[connection] tailscaled did not answer" in result.stdout
        assert "up --auth-key" not in log(tmp_path)

    def test_a_daemon_of_the_host_is_not_taken_over(self, tmp_path):
        (tmp_path / "daemon").write_text("0", encoding="utf-8")
        result = run(tmp_path, "up", TS_AUTHKEY=AUTHKEY)
        assert result.returncode == 1
        assert "::error::[environment] a tailscaled already runs" in result.stdout
        calls = log(tmp_path)  # only the probe ran: no second daemon, no up
        assert "--state=mem:" not in calls
        assert "up --auth-key" not in calls

    def test_down_leaves_a_daemon_it_did_not_start(self, tmp_path):
        (tmp_path / "daemon").write_text("0", encoding="utf-8")
        result = run(tmp_path, "down")
        assert result.returncode == 0
        assert "nothing to do" in result.stdout
        assert not (tmp_path / "log").exists()

    def test_without_tailscale_a_version_is_required(self, tmp_path):
        result = run(tmp_path, "up", TS_AUTHKEY=AUTHKEY, TS_TAILSCALE="no-such-tailscale")
        assert result.returncode == 1
        assert "::error::[configuration] tailscale is not on the runner; set version" in result.stdout


class TestDownAndMask:
    def test_down_logs_out_and_removes_the_state(self, tmp_path):
        run(tmp_path, "up", TS_AUTHKEY=AUTHKEY)
        result = run(tmp_path, "down")
        assert result.returncode == 0
        assert "logout" in log(tmp_path)
        assert not (tmp_path / "state").exists()

    def test_mask_prints_every_secret(self, tmp_path):
        result = run(tmp_path, "mask", TS_AUTHKEY=AUTHKEY, TS_OAUTH_SECRET=OAUTH)
        assert f"::add-mask::{AUTHKEY}" in result.stdout
        assert f"::add-mask::{OAUTH}" in result.stdout

    def test_unknown_command_fails(self, tmp_path):
        assert run(tmp_path, "sideways").returncode == 1
