#!/usr/bin/env bash
# Steps of the reusable workflow .gitea/workflows/code-metrics.yml (ADR-0010).
# The workflow checks out the calling repository, fetches this file into
# shared-scripts/ and runs one command per step:
#
#   code-metrics.sh validate   check the inputs, before anything is counted
#   code-metrics.sh measure    count the code, read the coverage report and
#                              write the badge files (count_loc.py, badges.py)
#   code-metrics.sh publish    commit the badge files to the badges branch,
#                              and nothing when none of them changed
#
# Settings come from the environment, never from interpolated expressions:
#   WORKING_DIRECTORY, EXCLUDE, COVERAGE_REPORT, COVERAGE_WARN, COVERAGE_GOOD,
#   BADGES_BRANCH, BADGES_OUT (the directory of the badge files; a temporary
#   directory under RUNNER_TEMP by default).
# Every failure is printed as ::error::[category] message.

TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="${BADGES_OUT:-${RUNNER_TEMP:-/tmp}/code-metrics}"
ALLOWED_FILES='^(code-files\.svg|code-lines\.svg|coverage\.svg|code-metrics\.json)$'
COMMIT_MESSAGE="Update code metrics badges [skip ci]"

fail() {
  echo "::error::[configuration] $1"
  exit 1
}

relative_path() {
  case "$1" in
    "" | /* | .. | ../* | */.. | */../*) return 1 ;;
  esac
}

validate_inputs() {
  set -u
  relative_path "$WORKING_DIRECTORY" ||
    fail "working-directory must be a relative path inside the repository."
  [ -d "$WORKING_DIRECTORY" ] ||
    fail "working-directory '$WORKING_DIRECTORY' does not exist."
  if [ -n "$COVERAGE_REPORT" ]; then
    relative_path "$COVERAGE_REPORT" ||
      fail "coverage-report must be a relative path inside the repository."
  fi
  case "$BADGES_BRANCH" in
    main | master | HEAD | "") fail "badges-branch '$BADGES_BRANCH' must not be a default branch." ;;
  esac
  git check-ref-format --branch "$BADGES_BRANCH" > /dev/null 2>&1 ||
    fail "badges-branch '$BADGES_BRANCH' is not a valid branch name."
  echo "Counting ${WORKING_DIRECTORY}; badges go to the branch ${BADGES_BRANCH}"
}

measure() {
  set -eu
  metrics="$(mktemp)"
  python3 "$TOOLS_DIR/count_loc.py" \
    --directory "$WORKING_DIRECTORY" --exclude "$EXCLUDE" --output "$metrics"
  rm -rf "$OUT_DIR"
  python3 "$TOOLS_DIR/badges.py" \
    --metrics "$metrics" --output-dir "$OUT_DIR" \
    --coverage-report "$COVERAGE_REPORT" \
    --coverage-warn "$COVERAGE_WARN" --coverage-good "$COVERAGE_GOOD"
  rm -f "$metrics"
}

# Copy the badge files into the worktree and stage them; return 0 when
# something differs from the branch.
stage_files() {
  local worktree="$1" file
  for file in "$OUT_DIR"/*; do
    cp "$file" "$worktree/$(basename "$file")"
  done
  git -C "$worktree" add -- .
  ! git -C "$worktree" diff --cached --quiet
}

commit_files() {
  git -C "$1" -c user.name="code-metrics" -c user.email="code-metrics@invalid" \
    commit --quiet -m "$COMMIT_MESSAGE"
}

publish() {
  set -eu
  [ -d "$OUT_DIR" ] || fail "no badge files in '$OUT_DIR'; run measure first."
  local worktree exists=0 committed=0 attempt
  worktree="$(mktemp -d)"
  if git fetch --quiet origin "+refs/heads/$BADGES_BRANCH:refs/remotes/origin/$BADGES_BRANCH" 2> /dev/null; then
    exists=1
    if git ls-tree -r --name-only "origin/$BADGES_BRANCH" | grep -qvE "$ALLOWED_FILES"; then
      fail "branch '$BADGES_BRANCH' holds files that are not badge files; it is not a badges branch."
    fi
    git worktree add --quiet --detach "$worktree" "origin/$BADGES_BRANCH"
  else
    git worktree add --quiet --detach "$worktree" HEAD
    git -C "$worktree" checkout --quiet --orphan "$BADGES_BRANCH"
    git -C "$worktree" rm -rfq --ignore-unmatch .
  fi

  for attempt in 1 2; do
    if [ "$committed" -eq 0 ]; then
      if stage_files "$worktree"; then
        commit_files "$worktree"
        committed=1
      elif [ "$exists" -eq 1 ]; then
        echo "Badges are current; nothing to commit."
        break
      fi
    fi
    if git -C "$worktree" push --quiet origin "HEAD:refs/heads/$BADGES_BRANCH"; then
      echo "Published the badges to the branch ${BADGES_BRANCH}."
      break
    fi
    [ "$attempt" -lt 2 ] || fail "the push to '$BADGES_BRANCH' failed twice."
    if git fetch --quiet origin "+refs/heads/$BADGES_BRANCH:refs/remotes/origin/$BADGES_BRANCH" 2> /dev/null; then
      git -C "$worktree" reset --quiet --hard "origin/$BADGES_BRANCH"
      exists=1
      committed=0
    fi
  done
  git worktree remove --force "$worktree"
}

case "${1:-}" in
  validate) validate_inputs ;;
  measure) measure ;;
  publish) publish ;;
  *)
    echo "::error::[configuration] usage: code-metrics.sh validate|measure|publish" >&2
    exit 2
    ;;
esac
