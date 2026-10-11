#!/usr/bin/env bash
# Steps of the reusable workflow .gitea/workflows/quality-checks.yml (ADR-0005).
# The workflow checks out the calling repository, fetches this file into
# shared-scripts/ and runs one command per step:
#
#   quality-checks.sh validate   check the inputs, before anything is installed
#   quality-checks.sh install    install the pinned tools into a virtual environment
#   quality-checks.sh run        run every selected tool on the tracked files
#
# Settings come from the environment, never from interpolated expressions:
#   LANGUAGES, WORKING_DIRECTORY, RUFF_VERSION, MYPY_VERSION,
#   SHELLCHECK_PY_VERSION, SHFMT_PY_VERSION, QC_VENV (and QC_BIN for tests).
# Every failure is printed as ::error::[category] message.

validate_inputs() {
  set -u
  IFS=',' read -ra langs <<< "${LANGUAGES// /}"
  if [ "${#langs[@]}" -eq 0 ]; then
    echo "::error::[configuration] languages is empty; use python, shell or both, comma separated."
    exit 1
  fi
  for lang in "${langs[@]}"; do
    case "$lang" in
      python | shell) ;;
      *)
        echo "::error::[configuration] Unknown language '$lang'; use python and shell, comma separated."
        exit 1
        ;;
    esac
  done
  case "$WORKING_DIRECTORY" in
    "" | /* | .. | ../* | */.. | */../*)
      echo "::error::[configuration] working-directory must be a relative path inside the repository."
      exit 1
      ;;
  esac
  echo "Checking ${LANGUAGES} in ${WORKING_DIRECTORY}"
}

install_tools() {
  set -eu
  IFS=',' read -ra langs <<< "${LANGUAGES// /}"
  packages=()
  for lang in "${langs[@]}"; do
    case "$lang" in
      python) packages+=("ruff==${RUFF_VERSION}" "mypy==${MYPY_VERSION}") ;;
      shell) packages+=("shellcheck-py==${SHELLCHECK_PY_VERSION}" "shfmt-py==${SHFMT_PY_VERSION}") ;;
    esac
  done
  python3 -m venv "$QC_VENV"
  "$QC_VENV/bin/pip" install --quiet "${packages[@]}"
}

run_checks() {
  set -u
  QC_BIN="${QC_BIN:-$QC_VENV/bin}"
  if [ ! -d "$WORKING_DIRECTORY" ]; then
    echo "::error::[configuration] working-directory '$WORKING_DIRECTORY' does not exist."
    exit 1
  fi
  cd "$WORKING_DIRECTORY"

  failed=()
  run_tool() {
    local name="$1"
    shift
    echo "::group::$name"
    if "$@"; then
      echo "::endgroup::"
      echo "PASS $name"
    else
      echo "::endgroup::"
      echo "FAIL $name"
      failed+=("$name")
    fi
  }
  wanted() {
    local lang
    IFS=',' read -ra langs <<< "${LANGUAGES// /}"
    for lang in "${langs[@]}"; do
      [ "$lang" = "$1" ] && return 0
    done
    return 1
  }

  if wanted python; then
    mapfile -t files < <(git ls-files -- '*.py')
    if [ "${#files[@]}" -eq 0 ]; then
      echo "::notice::No python files in '$WORKING_DIRECTORY'; nothing was checked."
    else
      run_tool "ruff check" "$QC_BIN/ruff" check "${files[@]}"
      run_tool "ruff format --check" "$QC_BIN/ruff" format --check "${files[@]}"
      run_tool "mypy --strict" "$QC_BIN/mypy" --strict "${files[@]}"
    fi
  fi

  if wanted shell; then
    mapfile -t files < <(git ls-files -- '*.sh')
    if [ "${#files[@]}" -eq 0 ]; then
      echo "::notice::No shell files in '$WORKING_DIRECTORY'; nothing was checked."
    else
      run_tool "shellcheck" "$QC_BIN/shellcheck" "${files[@]}"
      run_tool "shfmt -d" "$QC_BIN/shfmt" -d "${files[@]}"
    fi
  fi

  if [ "${#failed[@]}" -gt 0 ]; then
    echo "::error::Quality checks failed: ${failed[*]}"
    exit 1
  fi
  echo "All selected checks passed."
}

case "${1:-}" in
  validate) validate_inputs ;;
  install) install_tools ;;
  run) run_checks ;;
  *)
    echo "::error::[configuration] usage: quality-checks.sh validate|install|run" >&2
    exit 2
    ;;
esac
