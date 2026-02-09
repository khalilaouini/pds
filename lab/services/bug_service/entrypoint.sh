#!/bin/sh
set -eu

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

echo "$(ts) [INFO] bug_service: starting up..." 1>&2

if [ -z "${REQUIRED_ENV:-}" ]; then
  echo "$(ts) [ERROR] bug_service: REQUIRED_ENV is missing (misconfiguration)" 1>&2
  echo "$(ts) [ERROR] bug_service: exiting with code 1" 1>&2
  exit 1
fi

echo "$(ts) [INFO] bug_service: REQUIRED_ENV is set, running normally" 1>&2
while true; do
  echo "$(ts) [INFO] bug_service: running tick" 1>&2
  sleep 1
done

