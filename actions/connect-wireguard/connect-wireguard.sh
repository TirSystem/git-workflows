#!/usr/bin/env bash
# Steps of the composite action actions/connect-wireguard/action.yml.
#
#   connect-wireguard.sh mask   print ::add-mask:: for every secret input
#   connect-wireguard.sh up     write the configuration and bring the tunnel up
#   connect-wireguard.sh down   take the tunnel down and delete the configuration
#
# Settings come from the environment, never from interpolated expressions:
#   WG_CONFIG, WG_PRIVATE_KEY, WG_ADDRESS, WG_PEER_PUBLIC_KEY, WG_ENDPOINT,
#   WG_ALLOWED_IPS, WG_PRESHARED_KEY, WG_DNS, WG_KEEPALIVE, WG_INTERFACE,
#   WG_HEALTH_CHECK_HOST. WG_DIR is the configuration directory (/etc/wireguard
#   by default); WG_QUICK, WG_SUDO and WG_PING name the commands, for the tests.
# Every failure is printed as ::error::[category] message. A key is never printed.

WG_DIR="${WG_DIR:-/etc/wireguard}"
WG_QUICK="${WG_QUICK:-wg-quick}"
WG_PING="${WG_PING:-ping}"
# sudo is used only when the job is not root: a job container runs as root and
# often has no sudo. WG_SUDO overrides it (empty for none).
if [ -n "${WG_SUDO+x}" ]; then
  SUDO="$WG_SUDO"
elif [ "$(id -u)" = "0" ]; then
  SUDO=""
else
  SUDO="sudo"
fi
# variables that must reach wg-quick through sudo, which resets the environment
WG_QUICK_ENV=()

fail() {
  echo "::error::[$1] $2"
  exit 1
}

mask_secrets() {
  local value line key
  for value in "${WG_PRIVATE_KEY:-}" "${WG_PRESHARED_KEY:-}"; do
    [ -n "$value" ] && echo "::add-mask::$value"
  done
  # a full configuration: mask the value of every PrivateKey and PresharedKey
  # line, and nothing else, so the rest of the log stays readable
  while IFS= read -r line; do
    line="${line//$''/}"
    key="${line%%=*}"
    key="${key//[[:space:]]/}"
    case "${key,,}" in
      privatekey | presharedkey)
        value="${line#*=}"
        value="${value#"${value%%[![:space:]]*}"}"
        value="${value%"${value##*[![:space:]]}"}"
        [ -n "$value" ] && echo "::add-mask::$value"
        ;;
    esac
  done <<<"${WG_CONFIG:-}"
  return 0
}

check_interface() {
  [[ "$WG_INTERFACE" =~ ^[a-zA-Z0-9_=+.-]{1,15}$ ]] ||
    fail configuration "interface '$WG_INTERFACE' is not a valid interface name."
}

# render_config: the wg-quick configuration on stdout
render_config() {
  if [ -n "${WG_CONFIG:-}" ]; then
    printf '%s\n' "$WG_CONFIG"
    return 0
  fi
  local name
  for name in WG_PRIVATE_KEY WG_ADDRESS WG_PEER_PUBLIC_KEY WG_ENDPOINT WG_ALLOWED_IPS; do
    [ -n "${!name:-}" ] ||
      fail configuration "set config, or all of private-key, address, peer-public-key, endpoint and allowed-ips ($name is empty)."
  done
  for name in WG_PRIVATE_KEY WG_ADDRESS WG_PEER_PUBLIC_KEY WG_ENDPOINT WG_ALLOWED_IPS WG_PRESHARED_KEY WG_DNS; do
    # a line break would add directives (PostUp runs as root) to the file
    [[ "${!name:-}" != *[[:cntrl:]]* ]] ||
      fail configuration "$name must be one line without control characters."
  done
  [[ "$WG_KEEPALIVE" =~ ^[0-9]+$ ]] ||
    fail configuration "persistent-keepalive must be a number of seconds."
  printf '[Interface]\nPrivateKey = %s\nAddress = %s\n' "$WG_PRIVATE_KEY" "$WG_ADDRESS"
  [ -z "${WG_DNS:-}" ] || printf 'DNS = %s\n' "$WG_DNS"
  printf '\n[Peer]\nPublicKey = %s\nEndpoint = %s\nAllowedIPs = %s\nPersistentKeepalive = %s\n' \
    "$WG_PEER_PUBLIC_KEY" "$WG_ENDPOINT" "$WG_ALLOWED_IPS" "$WG_KEEPALIVE"
  [ -z "${WG_PRESHARED_KEY:-}" ] || printf 'PresharedKey = %s\n' "$WG_PRESHARED_KEY"
}

install_tools() {
  command -v "$WG_QUICK" >/dev/null 2>&1 && return 0
  echo "Installing wireguard-tools"
  if ! { $SUDO apt-get update -qq &&
    $SUDO apt-get install -y -qq wireguard-tools resolvconf iproute2 iputils-ping; }; then
    fail environment "wireguard-tools is not installed and could not be installed (a Debian or Ubuntu runner with root is needed)."
  fi
}

# Use the user-space implementation when the kernel has no WireGuard module,
# which is the usual case in a Gitea runner container.
choose_implementation() {
  if $SUDO ip link add dev "wgprobe$$" type wireguard 2>/dev/null; then
    $SUDO ip link delete dev "wgprobe$$" 2>/dev/null || true
    return 0
  fi
  if command -v wireguard-go >/dev/null 2>&1 || $SUDO apt-get install -y -qq wireguard-go 2>/dev/null; then
    WG_QUICK_ENV=(WG_QUICK_USERSPACE_IMPLEMENTATION=wireguard-go)
    echo "No kernel WireGuard module; using wireguard-go."
  else
    fail environment "the runner has no WireGuard kernel module and wireguard-go could not be installed; the runner container needs NET_ADMIN and /dev/net/tun (see guides/vpn-wireguard.md)."
  fi
}

tunnel_up() {
  check_interface
  local conf="$WG_DIR/$WG_INTERFACE.conf" rendered
  # on failure the captured output is the ::error:: line, which must be shown
  rendered="$(render_config)" || {
    echo "$rendered"
    exit 1
  }
  install_tools
  choose_implementation
  $SUDO install -d -m 700 "$WG_DIR"
  (umask 077 && printf '%s\n' "$rendered" | $SUDO tee "$conf" >/dev/null)
  $SUDO chmod 600 "$conf"
  # env keeps the userspace variable through sudo; the file holds the key, so
  # it is removed when the interface does not come up
  if ! $SUDO env ${WG_QUICK_ENV[@]+"${WG_QUICK_ENV[@]}"} "$WG_QUICK" up "$WG_INTERFACE"; then
    $SUDO rm -f "$conf"
    fail connection "wg-quick could not bring $WG_INTERFACE up."
  fi
  if [ -n "${WG_HEALTH_CHECK_HOST:-}" ]; then
    "$WG_PING" -c 3 -W 5 "$WG_HEALTH_CHECK_HOST" >/dev/null 2>&1 ||
      fail connection "health-check-host '$WG_HEALTH_CHECK_HOST' does not answer through the tunnel."
  fi
  echo "WireGuard interface $WG_INTERFACE is up."
}

tunnel_down() {
  check_interface
  local conf="$WG_DIR/$WG_INTERFACE.conf"
  $SUDO "$WG_QUICK" down "$WG_INTERFACE" 2>/dev/null || echo "Interface $WG_INTERFACE was not up."
  $SUDO rm -f "$conf"
  echo "WireGuard interface $WG_INTERFACE is down."
}

main() {
  set -uo pipefail
  WG_INTERFACE="${WG_INTERFACE:-wg0}"
  WG_KEEPALIVE="${WG_KEEPALIVE:-25}"
  case "${1:-}" in
    mask) mask_secrets ;;
    up) tunnel_up ;;
    down) tunnel_down ;;
    *) fail configuration "unknown command '${1:-}'; use mask, up or down." ;;
  esac
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  main "$@"
fi
