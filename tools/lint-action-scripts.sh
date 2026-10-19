#!/usr/bin/env bash
# Lint the shell scripts of the composite actions (MIL-012 task 6): shellcheck,
# and shfmt in the format .editorconfig sets (two spaces, indented case labels).
# validate-workflows.yml runs it on every pull request and push to main.
#
# Usage:   lint-action-scripts.sh [<directory>]     (default: actions)
# Env:     SHELLCHECK, SHFMT  the commands to run (default: from the PATH)
# Exit:    0 every script is clean (or there is none); 1 at least one finding or
#          a missing tool
# Needs:   bash, find, shellcheck, shfmt

SHELLCHECK="${SHELLCHECK:-shellcheck}"
SHFMT="${SHFMT:-shfmt}"

main() {
  set -u
  local dir="${1:-actions}" failed=0 tool
  for tool in "$SHELLCHECK" "$SHFMT"; do
    command -v "$tool" >/dev/null 2>&1 || {
      echo "::error::[environment] $tool is not installed."
      exit 1
    }
  done
  local files=()
  while IFS= read -r file; do
    files+=("$file")
  done < <(find "$dir" -name '*.sh' -type f | sort)
  if [ "${#files[@]}" -eq 0 ]; then
    echo "::notice::No shell scripts under '$dir'; nothing was checked."
    exit 0
  fi
  "$SHELLCHECK" "${files[@]}" || {
    echo "::error::[lint] shellcheck found problems."
    failed=1
  }
  "$SHFMT" -d "${files[@]}" || {
    echo "::error::[lint] shfmt would change a script; run shfmt -w."
    failed=1
  }
  [ "$failed" -eq 0 ] && echo "Checked ${#files[@]} script(s): clean."
  exit "$failed"
}

main "$@"
