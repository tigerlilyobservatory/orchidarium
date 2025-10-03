#! /usr/bin/env bash
# Start the service.


set -eo pipefail


if [ -z "$PASS_GPG_KEY_ID" ]; then
    printf "ERROR: PASS_GPG_KEY_ID is not defined. Please provide a valid private GPG key ID.\\n" >&2
    exit 1
fi

# Start the service.
if [ -n "$(poetry env info -p)" ]; then
    poetry run orchidarium "$@"
else
    passoperator "$@"
fi