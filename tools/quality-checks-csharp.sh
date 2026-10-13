#!/usr/bin/env bash
# Steps of the reusable workflow .gitea/workflows/quality-checks-csharp.yml
# (ADR-0008). The workflow checks out the calling repository, fetches this file
# into shared-scripts/ and runs one command per step:
#
#   quality-checks-csharp.sh validate   check the inputs, before anything is installed
#   quality-checks-csharp.sh install    install the exact .NET SDK version
#   quality-checks-csharp.sh run        run dotnet format and dotnet build on the project
#
# Settings come from the environment, never from interpolated expressions:
#   WORKING_DIRECTORY, PROJECT, DOTNET_SDK_VERSION, DOTNET_ROOT (and
#   QC_DOTNET_INSTALL_SCRIPT, QC_DOTNET for tests).
# Every failure is printed as ::error::[category] message.

DOTNET_INSTALL_URL="https://dot.net/v1/dotnet-install.sh"

validate_inputs() {
  set -u
  case "$WORKING_DIRECTORY" in
    "" | /* | .. | ../* | */.. | */../*)
      echo "::error::[configuration] working-directory must be a relative path inside the repository."
      exit 1
      ;;
  esac
  case "$PROJECT" in
    /* | .. | ../* | */.. | */../*)
      echo "::error::[configuration] project must be a relative path inside the working directory."
      exit 1
      ;;
  esac
  # An exact stable version of the .NET SDK, 10 or later (no channel, no range).
  if ! [[ "$DOTNET_SDK_VERSION" =~ ^([1-9][0-9]+)\.[0-9]+\.[0-9]+$ ]] || [ "${BASH_REMATCH[1]}" -lt 10 ]; then
    echo "::error::[configuration] dotnet-sdk-version '$DOTNET_SDK_VERSION' is not an exact stable version 10 or later, such as 10.0.401."
    exit 1
  fi
  echo "Checking C# in ${WORKING_DIRECTORY} with .NET SDK ${DOTNET_SDK_VERSION}"
}

install_sdk() {
  set -eu
  local script="${QC_DOTNET_INSTALL_SCRIPT:-}"
  if [ -z "$script" ]; then
    script="$(mktemp)"
    curl -fsSL "$DOTNET_INSTALL_URL" -o "$script"
  fi
  bash "$script" --version "$DOTNET_SDK_VERSION" --install-dir "$DOTNET_ROOT" --no-path
  "$DOTNET_ROOT/dotnet" --version
}

run_checks() {
  set -u
  if [ ! -d "$WORKING_DIRECTORY" ]; then
    echo "::error::[configuration] working-directory '$WORKING_DIRECTORY' does not exist."
    exit 1
  fi
  cd "$WORKING_DIRECTORY"
  local dotnet="${QC_DOTNET:-$DOTNET_ROOT/dotnet}"

  local sources
  mapfile -t sources < <(git ls-files -- '*.cs')
  if [ "${#sources[@]}" -eq 0 ]; then
    echo "::notice::No C# files in '$WORKING_DIRECTORY'; nothing was checked."
    echo "All selected checks passed."
    exit 0
  fi

  local target="$PROJECT" candidates
  if [ -z "$target" ]; then
    mapfile -t candidates < <(git ls-files -- '*.sln' '*.slnx')
    if [ "${#candidates[@]}" -eq 0 ]; then
      mapfile -t candidates < <(git ls-files -- '*.csproj')
    fi
    case "${#candidates[@]}" in
      0)
        echo "::error::[configuration] C# files exist but no solution or project was found in '$WORKING_DIRECTORY'; add one or set the input project."
        exit 1
        ;;
      1) target="${candidates[0]}" ;;
      *)
        echo "::error::[configuration] Several solutions or projects were found (${candidates[*]}); set the input project."
        exit 1
        ;;
    esac
  elif [ ! -f "$target" ]; then
    echo "::error::[configuration] project '$target' does not exist in '$WORKING_DIRECTORY'."
    exit 1
  fi
  echo "Checking $target"

  export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
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

  run_tool "dotnet format --verify-no-changes" "$dotnet" format "$target" --verify-no-changes
  run_tool "dotnet build -warnaserror" "$dotnet" build "$target" --nologo -warnaserror

  if [ "${#failed[@]}" -gt 0 ]; then
    echo "::error::Quality checks failed: ${failed[*]}"
    exit 1
  fi
  echo "All selected checks passed."
}

case "${1:-}" in
  validate) validate_inputs ;;
  install) install_sdk ;;
  run) run_checks ;;
  *)
    echo "::error::[configuration] usage: quality-checks-csharp.sh validate|install|run" >&2
    exit 2
    ;;
esac
