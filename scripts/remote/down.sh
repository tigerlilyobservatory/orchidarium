#! /usr/bin/env bash
# Stop Orchidarium on the configured Raspberry Pi with Ansible.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ANSIBLE_CONFIG_PATH="${REPO_ROOT}/ansible/ansible.cfg"
ANSIBLE_INVENTORY="${ORCHIDARIUM_REMOTE_INVENTORY:-${REPO_ROOT}/ansible/inventory/hosts.yml}"
ANSIBLE_PLAYBOOK=()

cd "${REPO_ROOT}"

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

_resolve_ansible_playbook

"${ANSIBLE_PLAYBOOK[@]}" \
    -i "${ANSIBLE_INVENTORY}" \
    ansible/playbooks/down.yml \
    "$@"
