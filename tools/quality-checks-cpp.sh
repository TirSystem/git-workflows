#!/usr/bin/env bash
# Steps of the reusable workflow .gitea/workflows/quality-checks-cpp.yml
# (ADR-0008). The workflow checks out the calling repository, fetches this file
# into shared-scripts/ and runs one command per step:
#
#   quality-checks-cpp.sh validate   check the inputs, before anything is installed
#   quality-checks-cpp.sh install    install the exact clang tool versions into a venv
#   quality-checks-cpp.sh run        run clang-format and clang-tidy on the tracked files
#
# Settings come from the environment, never from interpolated expressions:
#   WORKING_DIRECTORY, STD, COMPILE_COMMANDS_DIR, CLANG_FORMAT_VERSION,
#   CLANG_TIDY_VERSION, QC_VENV (and QC_BIN for tests).
# Every failure is printed as ::error::[category] message.

C_STANDARD="${C_STANDARD:-c17}"

validate_inputs() {
  set -u
  case "$WORKING_DIRECTORY" in
    "" | /* | .. | ../* | */.. | */../*)
      echo "::error::[configuration] working-directory must be a relative path inside the repository."
      exit 1
      ;;
  esac
  if ! [[ "$STD" =~ ^(c\+\+|gnu\+\+)[0-9]{2}$ ]]; then
    echo "::error::[configuration] std '$STD' is not a C++ standard such as c++20 or gnu++20."
    exit 1
  fi
  case "$COMPILE_COMMANDS_DIR" in
    /* | .. | ../* | */.. | */../*)
      echo "::error::[configuration] compile-commands-dir must be a relative path inside the repository."
      exit 1
      ;;
  esac
  local name version
  for name in CLANG_FORMAT_VERSION CLANG_TIDY_VERSION; do
    version="${!name}"
    if ! [[ "$version" =~ ^[0-9]+(\.[0-9]+){1,3}$ ]]; then
      echo "::error::[configuration] ${name,,} '$version' is not an exact version such as 23.1.3."
      exit 1
    fi
  done
  echo "Checking C and C++ in ${WORKING_DIRECTORY} with std ${STD}"
}

install_tools() {
  set -eu
  python3 -m venv "$QC_VENV"
  "$QC_VENV/bin/pip" install --quiet \
    "clang-format==${CLANG_FORMAT_VERSION}" "clang-tidy==${CLANG_TIDY_VERSION}"
}

# A .clang-format must exist in the working directory or above it, up to the
# top of the repository: clang-format finds its style the same way.
find_clang_format_config() {
  local top dir parent
  top="$(cd "$(git rev-parse --show-toplevel)" && pwd -P)"
  dir="$(pwd -P)"
  while true; do
    if [ -f "$dir/.clang-format" ] || [ -f "$dir/_clang-format" ]; then
      return 0
    fi
    parent="$(dirname "$dir")"
    # stop at the top of the repository, or at the file system root
    if [ "$dir" = "$top" ] || [ "$parent" = "$dir" ]; then
      return 1
    fi
    dir="$parent"
  done
}

run_checks() {
  set -u
  QC_BIN="${QC_BIN:-$QC_VENV/bin}"
  if [ ! -d "$WORKING_DIRECTORY" ]; then
    echo "::error::[configuration] working-directory '$WORKING_DIRECTORY' does not exist."
    exit 1
  fi
  cd "$WORKING_DIRECTORY"

  local all_files cpp_files c_files
  mapfile -t all_files < <(git ls-files -- '*.c' '*.cc' '*.cpp' '*.cxx' '*.h' '*.hh' '*.hpp' '*.hxx')
  if [ "${#all_files[@]}" -eq 0 ]; then
    echo "::notice::No C or C++ files in '$WORKING_DIRECTORY'; nothing was checked."
    echo "All selected checks passed."
    exit 0
  fi
  if ! find_clang_format_config; then
    echo "::error::[configuration] No .clang-format found in '$WORKING_DIRECTORY' or above it; add the style of the project."
    exit 1
  fi
  if [ -n "$COMPILE_COMMANDS_DIR" ] && [ ! -f "$COMPILE_COMMANDS_DIR/compile_commands.json" ]; then
    echo "::error::[configuration] compile-commands-dir '$COMPILE_COMMANDS_DIR' has no compile_commands.json; build it before the call."
    exit 1
  fi

  # .c files are C; everything else (including headers) is checked as C++.
  mapfile -t c_files < <(git ls-files -- '*.c')
  mapfile -t cpp_files < <(git ls-files -- '*.cc' '*.cpp' '*.cxx' '*.h' '*.hh' '*.hpp' '*.hxx')

  local failed=()
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

  run_tool "clang-format" "$QC_BIN/clang-format" --dry-run -Werror "${all_files[@]}"

  if [ -n "$COMPILE_COMMANDS_DIR" ]; then
    run_tool "clang-tidy" "$QC_BIN/clang-tidy" --quiet -p "$COMPILE_COMMANDS_DIR" "${all_files[@]}"
  else
    if [ "${#cpp_files[@]}" -gt 0 ]; then
      run_tool "clang-tidy (C++)" "$QC_BIN/clang-tidy" --quiet "${cpp_files[@]}" -- "-std=${STD}"
    fi
    if [ "${#c_files[@]}" -gt 0 ]; then
      run_tool "clang-tidy (C)" "$QC_BIN/clang-tidy" --quiet "${c_files[@]}" -- "-std=${C_STANDARD}"
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
    echo "::error::[configuration] usage: quality-checks-cpp.sh validate|install|run" >&2
    exit 2
    ;;
esac
