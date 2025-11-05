#! /usr/bin/env bash
# Populate a shell with the secrets required to execute the Docker compose file.


INFLUXDB_TOKEN="$(pass show personal/orchidarium/influxdb/token)"
export INFLUXDB_TOKEN

INFLUXDB_USERNAME="$(pass show personal/orchidarium/influxdb/username)"
export INFLUXDB_USERNAME

INFLUXDB_PASSWORD="$(pass show personal/orchidarium/influxdb/password)"
export INFLUXDB_PASSWORD

GF_ADMIN_PASSWORD="$(pass show personal/orchidarium/grafana/password)"
export GF_ADMIN_PASSWORD

GF_ADMIN_USER="$(pass show personal/orchidarium/grafana/username)"
export GF_ADMIN_USER