#!/usr/bin/env bash
# Steps of the composite action actions/connect-tailscale/action.yml.
#
#   connect-tailscale.sh mask   print ::add-mask:: for every secret input
#   connect-tailscale.sh up     install tailscale if needed, start tailscaled and join the tailnet
#   connect-tailscale.sh down   log the node out and stop tailscaled
#
# Settings come from the environment, never from interpolated expressions:
#   TS_AUTHKEY, TS_OAUTH_SECRET, TS_TAGS, TS_HOSTNAME, TS_VERSION, TS_USERSPACE,
#   TS_SHA256, TS_ARGS, TS_TIMEOUT, TS_HEALTH_CHECK_HOST. TS_TAILSCALE,
#   TS_TAILSCALED, TS_SUDO, TS_STATE_DIR, TS_START_WAIT (tries) and
#   TS_WAIT_INTERVAL (seconds) name the commands, the work folder and the waits,
#   for the tests.
# The auth key is passed to tailscale in a file of mode 600, never on a command
# line. Every failure is printed as ::error::[category] message.

TS_TAILSCALE="${TS_TAILSCALE:-tailscale}"
TS_TAILSCALED="${TS_TAILSCALED:-tailscaled}"
# sudo is used only when the job is not root: a job container runs as root and
# often has no sudo. TS_SUDO overrides it (empty for none).
if [ -n "${TS_SUDO+x}" ]; then
  SUDO="$TS_SUDO"
elif [ "$(id -u)" = "0" ]; then
  SUDO=""
else
  SUDO="sudo"
fi
STATE_DIR="${TS_STATE_DIR:-${RUNNER_TEMP:-/tmp}/tailscale}"

fail() {
  echo "::error::[$1] $2"
  exit 1
}

mask_secrets() {
  local value
  for value in "${TS_AUTHKEY:-}" "${TS_OAUTH_SECRET:-}"; do
    [ -n "$value" ] && echo "::add-mask::$value"
  done
  return 0
}

validate_inputs() {
  if [ -n "${TS_AUTHKEY:-}" ] && [ -n "${TS_OAUTH_SECRET:-}" ]; then
    fail configuration "give authkey or oauth-secret, not both."
  fi
  if [ -z "${TS_AUTHKEY:-}" ] && [ -z "${TS_OAUTH_SECRET:-}" ]; then
    fail configuration "give authkey or oauth-secret."
  fi
  if [ -n "${TS_OAUTH_SECRET:-}" ] && [ -z "${TS_TAGS:-}" ]; then
    fail configuration "tags is required with oauth-secret (for example tag:ci)."
  fi
  if [ -n "${TS_TAGS:-}" ]; then
    [[ "$TS_TAGS" =~ ^tag:[a-zA-Z0-9-]+(,tag:[a-zA-Z0-9-]+)*$ ]] ||
      fail configuration "tags must look like tag:ci or tag:ci,tag:deploy."
  fi
  [[ "$TS_TIMEOUT" =~ ^[0-9]+$ ]] ||
    fail configuration "timeout must be a number of seconds."
  [[ "$TS_VERSION" =~ ^([0-9]+\.[0-9]+\.[0-9]+)?$ ]] ||
    fail configuration "version must be an exact version like 1.80.2."
  [[ "${TS_SHA256:-}" =~ ^([0-9a-fA-F]{64})?$ ]] ||
    fail configuration "sha256 must be 64 hexadecimal digits."
  case "$TS_USERSPACE" in
    true | false) ;;
    *) fail configuration "userspace-networking must be true or false." ;;
  esac
  [[ "${TS_HOSTNAME:-}" =~ ^[a-zA-Z0-9-]*$ ]] ||
    fail configuration "hostname may hold letters, digits and hyphens only."
}

machine_arch() {
  case "$(uname -m)" in
    x86_64 | amd64) echo amd64 ;;
    aarch64 | arm64) echo arm64 ;;
    *) fail environment "no Tailscale build for $(uname -m)." ;;
  esac
}

install_tools() {
  command -v "$TS_TAILSCALE" >/dev/null 2>&1 && command -v "$TS_TAILSCALED" >/dev/null 2>&1 && return 0
  [ -n "$TS_VERSION" ] ||
    fail configuration "tailscale is not on the runner; set version (for example 1.80.2) so it can be installed."
  local arch url tmp
  arch="$(machine_arch)"
  url="https://pkgs.tailscale.com/stable/tailscale_${TS_VERSION}_${arch}.tgz"
  echo "Installing Tailscale $TS_VERSION"
  tmp="$(mktemp -d)"
  curl -fsSL "$url" -o "$tmp/tailscale.tgz" ||
    fail environment "could not download $url."
  if [ -n "${TS_SHA256:-}" ]; then
    echo "${TS_SHA256}  $tmp/tailscale.tgz" | sha256sum -c --quiet - ||
      fail environment "the downloaded archive does not match sha256."
  fi
  tar -xzf "$tmp/tailscale.tgz" -C "$tmp" --strip-components=1 ||
    fail environment "could not unpack the Tailscale archive."
  $SUDO install -m 755 "$tmp/tailscale" "$tmp/tailscaled" /usr/local/bin/ ||
    fail environment "could not install tailscale (root or sudo is needed)."
  rm -rf "$tmp"
}

daemon_answers() {
  "$TS_TAILSCALE" version --daemon >/dev/null 2>&1
}

start_daemon() {
  # a daemon that already runs belongs to the host; this action would log it out
  if daemon_answers; then
    fail environment "a tailscaled already runs on this runner; the action starts its own and must not take over the host's. Use it on a job container."
  fi
  local args=(--state=mem:)
  if [ "$TS_USERSPACE" = "true" ]; then
    args+=(--tun=userspace-networking --socks5-server=localhost:1055)
  fi
  mkdir -p "$STATE_DIR"
  $SUDO nohup "$TS_TAILSCALED" "${args[@]}" >"$STATE_DIR/tailscaled.log" 2>&1 &
  : >"$STATE_DIR/started-by-action"
  wait_for_daemon
}

# wait_for_daemon: tailscaled needs a moment to create its socket
wait_for_daemon() {
  local tries="${TS_START_WAIT:-30}" i
  for ((i = 0; i < tries; i++)); do
    daemon_answers && return 0
    sleep "${TS_WAIT_INTERVAL:-1}"
  done
  fail connection "tailscaled did not answer in $tries tries; the last lines of its log: $(tail -n 5 "$STATE_DIR/tailscaled.log" 2>/dev/null | tr '
' ' ')"
}

# write_key_file: the auth key in a file of mode 600; prints its path
write_key_file() {
  local file="$STATE_DIR/authkey" key
  if [ -n "${TS_OAUTH_SECRET:-}" ]; then
    key="${TS_OAUTH_SECRET}?ephemeral=true&preauthorized=true"
  else
    key="$TS_AUTHKEY"
  fi
  mkdir -p "$STATE_DIR"
  (umask 077 && printf '%s' "$key" >"$file")
  echo "$file"
}

tailnet_up() {
  validate_inputs
  install_tools
  start_daemon
  local keyfile up_args extra
  keyfile="$(write_key_file)"
  up_args=("--auth-key=file:$keyfile" "--timeout=${TS_TIMEOUT}s")
  [ -z "${TS_HOSTNAME:-}" ] || up_args+=("--hostname=$TS_HOSTNAME")
  [ -z "${TS_TAGS:-}" ] || up_args+=("--advertise-tags=$TS_TAGS")
  # TS_ARGS is split on spaces on purpose: it holds flags, never a secret
  # shellcheck disable=SC2206
  extra=(${TS_ARGS:-})
  if ! $SUDO "$TS_TAILSCALE" up "${up_args[@]}" "${extra[@]}"; then
    rm -f "$keyfile"
    fail connection "tailscale up failed; the last lines of tailscaled: $(tail -n 5 "$STATE_DIR/tailscaled.log" 2>/dev/null | tr '\n' ' ')"
  fi
  rm -f "$keyfile"
  if [ -n "${TS_HEALTH_CHECK_HOST:-}" ]; then
    "$TS_TAILSCALE" ping --c 3 --timeout 10s "$TS_HEALTH_CHECK_HOST" >/dev/null 2>&1 ||
      fail connection "health-check-host '$TS_HEALTH_CHECK_HOST' does not answer on the tailnet."
  fi
  echo "Tailscale is up."
}

tailnet_down() {
  # only a daemon this action started is logged out and stopped
  if [ ! -f "$STATE_DIR/started-by-action" ]; then
    echo "This action did not start tailscaled on this runner; nothing to do."
    return 0
  fi
  $SUDO "$TS_TAILSCALE" logout 2>/dev/null || echo "The node was not logged in."
  $SUDO "$TS_TAILSCALE" down 2>/dev/null || true
  $SUDO pkill -x "$(basename "$TS_TAILSCALED")" 2>/dev/null || true
  rm -rf "$STATE_DIR"
  echo "Tailscale is down."
}

main() {
  set -uo pipefail
  TS_USERSPACE="${TS_USERSPACE:-false}"
  TS_TIMEOUT="${TS_TIMEOUT:-60}"
  TS_VERSION="${TS_VERSION:-}"
  case "${1:-}" in
    mask) mask_secrets ;;
    up) tailnet_up ;;
    down) tailnet_down ;;
    *) fail configuration "unknown command '${1:-}'; use mask, up or down." ;;
  esac
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  main "$@"
fi
