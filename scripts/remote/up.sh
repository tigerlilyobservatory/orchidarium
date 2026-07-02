#! /usr/bin/env bash
# Start Orchidarium on the configured Raspberry Pi with Ansible.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ANSIBLE_CONFIG_PATH="${REPO_ROOT}/ansible/ansible.cfg"
ANSIBLE_INVENTORY="${ORCHIDARIUM_REMOTE_INVENTORY:-${REPO_ROOT}/ansible/inventory/hosts.yml}"
RESET_REMOTE_STACK=false
DEBUG_ENABLED=false
ANSIBLE_ARGS=()
ANSIBLE_PLAYBOOK=()

cd "${REPO_ROOT}"

for argument in "$@"; do
    case "${argument}" in
        --debug)
            DEBUG_ENABLED=true
            continue
            ;;
        --reset)
            RESET_REMOTE_STACK=true
            continue
            ;;
    esac

    ANSIBLE_ARGS+=("${argument}")
done

##
# Resolve the ansible-playbook command from the project dev environment or PATH.
#   -> return::void
_resolve_ansible_playbook()
{
    if command -v poetry >/dev/null 2>&1 && poetry run ansible-playbook --version >/dev/null 2>&1; then
        ANSIBLE_PLAYBOOK=(poetry run ansible-playbook)
        return
    fi

    if command -v ansible-playbook >/dev/null 2>&1 && ansible-playbook --version >/dev/null 2>&1; then
        ANSIBLE_PLAYBOOK=(ansible-playbook)
        return
    fi

    printf "ERROR: ansible-playbook is required. Run 'poetry install --with dev' before remote deployment.\\n" >&2
    exit 1
}

if ! command -v sshpass >/dev/null 2>&1; then
    printf "INFO: sshpass is not installed. Password-based defaults may fail unless SSH keys are configured.\\n" >&2
fi

export ANSIBLE_CONFIG="${ANSIBLE_CONFIG_PATH}"

if [ "${DEBUG_ENABLED}" = true ]; then
    export DEBUG='true'
fi

_resolve_ansible_playbook

if [ "${RESET_REMOTE_STACK}" = true ]; then
    "${SCRIPT_DIR}/down.sh" "${ANSIBLE_ARGS[@]}"
fi

"${ANSIBLE_PLAYBOOK[@]}" \
    -i "${ANSIBLE_INVENTORY}" \
    ansible/playbooks/up.yml \
    "${ANSIBLE_ARGS[@]}"
