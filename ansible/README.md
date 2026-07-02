# Orchidarium Ansible

This directory contains the Raspberry Pi deployment playbooks used by `scripts/remote/up.sh` and `scripts/remote/down.sh`.

The default inventory target is `orchidarium-rpi` at `172.16.0.35` on the `172.16.0.35/24` network, with SSH user `tigerlily` and the default Raspberry Pi password `raspberry`.

The `up.yml` playbook installs Docker, Pi helper packages, udev rules, deploys the current local source tree to `/home/tigerlily/orchidarium`, generates local Grafana certificates, and runs Docker Compose. The `down.yml` playbook runs Docker Compose down and removes the installed Orchidarium udev rules.

Use `scripts/remote/up.sh --debug` to start the remote stack with Orchidarium debug logging enabled.

Roles:

- `raspberry_pi`: install Raspberry Pi packages, Docker, Compose, and remote user groups.
- `orchidarium_source`: sync deployable source, write the Compose environment wrapper, and generate certs.
- `orchidarium_udev`: install or remove Orchidarium udev rules.
- `orchidarium_compose`: run the requested Docker Compose lifecycle step.
