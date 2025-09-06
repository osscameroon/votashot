#!/usr/bin/env bash

# Ensure dev environment is set up, then run Django tests.
# - Starts run_dev_mode.sh in the background to set up env/migrations
# - Activates the virtualenv in .venv
# - Runs `python manage.py test`

set -euo pipefail

# Resolve project root (directory containing this script)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DEV_SCRIPT="$PROJECT_ROOT/run_dev_mode.sh"
VENV_DIR="$PROJECT_ROOT/.venv"

if [[ ! -f "$RUN_DEV_SCRIPT" ]]; then
  echo "Error: $RUN_DEV_SCRIPT not found" >&2
  exit 1
fi

# Start dev setup (migrations + server) in background so we can proceed to tests
"$RUN_DEV_SCRIPT" >/dev/null 2>&1 &
DEV_PID=$!

# Always clean up background server if it's still running when we exit
cleanup() {
  if kill -0 "$DEV_PID" >/dev/null 2>&1; then
    kill "$DEV_PID" >/dev/null 2>&1 || true
    # Give it a moment to terminate gracefully
    sleep 1 || true
    if kill -0 "$DEV_PID" >/dev/null 2>&1; then
      kill -9 "$DEV_PID" >/dev/null 2>&1 || true
    fi
  fi
}
trap cleanup EXIT

# Activate the virtual environment
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Error: virtual environment not found at $VENV_DIR" >&2
  echo "Run setup first or ensure .venv exists." >&2
  exit 1
fi

source "$VENV_DIR/bin/activate"

cd "$PROJECT_ROOT"

# Run Django test suite
python manage.py test core.tests.test_vote.VoteApiViewTests
python manage.py test core.tests.test_votingpaperresult.VotingPaperResultViewTests
python manage.py test core.tests.test_authentication.AuthenticateApiViewTests
python manage.py test core.tests.test_poll_office_stats.PollOfficeStatsViewTests
python manage.py test core.tests.test_poll_office_results.PollOfficeResultsViewTests
