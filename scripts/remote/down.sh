#! /usr/bin/env bash
# Stop Orchidarium on the configured Raspberry Pi with Ansible.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ANSIBLE_CONFIG_PATH="${REPO_ROOT}/ansible/ansible.cfg"
ANSIBLE_INVENTORY="${ORCHIDARIUM_REMOTE_INVENTORY:-${REPO_ROOT}/ansible/inventory/hosts.yml}"

cd "${REPO_ROOT}"

if ! command -v ansible-playbook >/dev/null 2>&1; then
    printf "ERROR: ansible-playbook is required. Install Ansible before running remote deployment.\\n" >&2
    exit 1
fi

if ! command -v sshpass >/dev/null 2>&1; then
    printf "INFO: sshpass is not installed. Password-based defaults may fail unless SSH keys are configured.\\n" >&2
fi

export ANSIBLE_CONFIG="${ANSIBLE_CONFIG_PATH}"

ansible-playbook \
    -i "${ANSIBLE_INVENTORY}" \
    ansible/playbooks/down.yml \
    "$@"

