#! /usr/bin/env bash
# Start the local Orchidarium stack.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
UDEV_RULES_DIR="/etc/udev/rules.d"
ENV_FILE="scripts/.env.sh"
DEBUG_ENABLED=false
DOCKER_COMPOSE_ARGS=()

cd "${REPO_ROOT}"

for argument in "$@"; do
    if [ "${argument}" = '--debug' ]; then
        DEBUG_ENABLED=true
        continue
    fi

    DOCKER_COMPOSE_ARGS+=("${argument}")
done

##
# Install local Orchidarium udev rules when udev is available.
#   -> return::void
_install_udev_rules()
{
    if [ ! -d "${UDEV_RULES_DIR}" ] || ! command -v udevadm >/dev/null 2>&1; then
        printf "INFO: udev is not available; skipping Orchidarium udev rule installation.\\n"
        return
    fi

    for rule in config/rules/*.rules; do
        if [ ! -f "${rule}" ]; then
            printf "ERROR: No udev rule files found under config/rules.\\n" >&2
            exit 1
        fi

        sudo install -m 0644 "${rule}" "${UDEV_RULES_DIR}/99-orchidarium-$(basename "${rule}")"
    done

    sudo udevadm control --reload-rules
    sudo udevadm trigger
}

##
# Source the local Docker Compose environment file and apply CLI overrides.
#   -> return::void
_load_environment()
{
    if [ ! -f "${ENV_FILE}" ]; then
        printf "ERROR: Expected %s to exist.\\n" "${ENV_FILE}" >&2
        exit 1
    fi

    # shellcheck source=scripts/.env.sh
    source "${ENV_FILE}"

    if [ "${DEBUG_ENABLED}" = true ]; then
        export DEBUG='true'
    fi
}

##
# Print exported environment variable names declared by the environment file.
#   -> return::stdout
_environment_exports()
{
    awk '
        /^[[:space:]]*export[[:space:]]+/ {
            for (i = 2; i <= NF; i++) {
                variable = $i
                sub(/=.*/, "", variable)
                sub(/[^A-Za-z0-9_].*/, "", variable)

                if (variable ~ /^[A-Za-z_][A-Za-z0-9_]*$/) {
                    print variable
                }
            }
        }
    ' "${ENV_FILE}" | sort -u
}

##
# Check whether an exported environment variable is allowed to be empty.
#   variable::string -> return::bool
_allows_empty_environment_value()
{
    case "$1" in
        DEBUG|DISPLAY|QT_QUICK_BACKEND)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

##
# Validate required environment variables parsed from the environment file.
#   -> return::void
_require_environment()
{
    local variables
    local missing=false
    local variable

    mapfile -t variables < <(_environment_exports)

    for variable in "${variables[@]}"; do
        if [ -z "${!variable+x}" ]; then
            printf "ERROR: Expected %s to be exported by %s.\\n" "${variable}" "${ENV_FILE}" >&2
            missing=true
            continue
        fi

        if [ -z "${!variable}" ] && ! _allows_empty_environment_value "${variable}"; then
            printf "ERROR: Expected %s from %s to be non-empty.\\n" "${variable}" "${ENV_FILE}" >&2
            missing=true
        fi
    done

    if [ "${missing}" = true ]; then
        exit 1
    fi
}

##
# Validate the configured UI display backend before Docker Compose starts.
#   -> return::void
_validate_ui_display_environment()
{
    case "${QT_QPA_PLATFORM}" in
        wayland)
            ;;
        xcb)
            if [ -z "${DISPLAY}" ]; then
                printf "ERROR: Expected DISPLAY to be set when QT_QPA_PLATFORM=xcb.\\n" >&2
                exit 1
            fi

            return
            ;;
        offscreen)
            return
            ;;
        *)
            printf "ERROR: Unsupported QT_QPA_PLATFORM %s.\\n" "${QT_QPA_PLATFORM}" >&2
            exit 1
            ;;
    esac

    if [ ! -d "${WAYLAND_RUNTIME_DIR}" ]; then
        printf "ERROR: Expected Wayland runtime directory %s to exist.\\n" "${WAYLAND_RUNTIME_DIR}" >&2
        exit 1
    fi

    if [ ! -S "${WAYLAND_RUNTIME_DIR}/${WAYLAND_DISPLAY}" ]; then
        printf "ERROR: Expected Wayland socket %s/%s to exist.\\n" "${WAYLAND_RUNTIME_DIR}" "${WAYLAND_DISPLAY}" >&2
        exit 1
    fi
}

##
# Allow Docker clients to connect to XQuartz when using the xcb UI backend.
#   -> return::void
_authorize_xquartz_clients()
{
    local display_number
    local xquartz_display

    if [ "$(uname -s)" != 'Darwin' ] || [ "${QT_QPA_PLATFORM}" != 'xcb' ]; then
        return
    fi

    if [ ! -x /opt/X11/bin/xhost ]; then
        printf "ERROR: Expected /opt/X11/bin/xhost to exist when QT_QPA_PLATFORM=xcb on macOS.\\n" >&2
        printf "Install and start XQuartz before using the xcb UI backend.\\n" >&2
        exit 1
    fi

    display_number="${DISPLAY##*:}"
    display_number="${display_number%%.*}"
    xquartz_display="${ORCHIDARIUM_XQUARTZ_DISPLAY:-:${display_number:-0}}"

    if ! DISPLAY="${xquartz_display}" /opt/X11/bin/xhost +localhost >/dev/null 2>&1; then
        printf "ERROR: Could not authorize XQuartz clients with DISPLAY=%s /opt/X11/bin/xhost +localhost.\\n" "${xquartz_display}" >&2
        printf "Open XQuartz, enable Settings > Security > Allow connections from network clients, fully restart XQuartz, then retry.\\n" >&2
        exit 1
    fi
}

_install_udev_rules
_load_environment
_require_environment
_validate_ui_display_environment
_authorize_xquartz_clients

./scripts/generate-test-self-signed-certs.sh

docker compose up -d --build "${DOCKER_COMPOSE_ARGS[@]}"
