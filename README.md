# Orchidarium

![GitHub Release](https://img.shields.io/github/v/release/tigerlilyplants/orchidarium) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

<p align="left" width="100%">
  <img width="20%" src="./img/orchid.png" alt="orchid">
</p>

- [Orchidarium](#orchidarium)
  - [About](#about)
  - [Motivation](#motivation)
  - [Documentation](#documentation)
    - [Runtime Hierarchy](#runtime-hierarchy)
    - [Runtime Configuration](#runtime-configuration)
    - [API](#api)
    - [Metrics Queue Fanout](#metrics-queue-fanout)
  - [Development](#development)
    - [Remote Ansible](#remote-ansible)
    - [Docker Compose](#docker-compose)
      - [Raspberry Pi Wi-Fi / SSH](#raspberry-pi-wi-fi--ssh)
      - [UI Display](#ui-display)

## About

`orchidarium` is an extensible environmental control platform for maintaining closed or confined spaces, intended to run as the operating system for Tiger Lily Plants' Vesta control module (named after the planet at the center of the plot in *Scavengers Reign*).

This project integrates off-the-shelf sensors with electrical, HVAC, lighting, and fluid-handling systems to monitor, automate, and optimize controlled environments. It supports environmental target tracking, drift, custom scheduling, fluid movement, mixing and flushing, energy measurement, and a wide range of derived operational metrics.

## Motivation

As I've progressed through my hobbies, from plants -> building terrariums -> freshwater fish -> saltwater corals / reef tanks, I've noticed a trend of the following issues that the individual consumer markets address with different, oftentimes awkwardly composable, products (I surmise similar problems exist in other fields as well).

1. Maintaining and monitoring adequate environmental conditions in confined spaces, whether liquid- or gas / atmosphere-based, is hard, and often requires different controllers and sensors to achieve long-term stability.
2. Dosing solids and liquids at the right times and in the right quantities could mean life or death for the occupants of the confined space, and the same constraints apply to the environment / climate.
3. Complex timing and scheduling of jobs is often impossible or a lot of work to configure and ends up getting done manually on a schedule.
4. Reliable feedback about how the action that took place corrected a problem is nonexistent or difficult to retrieve / obtain.

The products I've yet tried have not accomplished the basic control flow and user experience that I want on every tank and shelf:

- A centralized set of configurable, extendable and clear control loops across disciplines, with associated metrics and operations.
- Dependable, complex timing for scheduled / recurring / one-off jobs.
- Feedback about performance / general metrics.

I also want it to be small.

<!-- See [BUILD.md](./BUILD.md) for terrarium build photos, sourced components, supported sensors, and notes on previous builds. -->

## Documentation

### Runtime Hierarchy

Orchidarium has one supervisor process and separate child processes for each long-running runtime domain. Metrics, API, hardware, and UI run today.

```text
tini
└── orchidarium
    ├── metrics / orchidarium-metrics
    │   ├── metrics main thread
    │   │   ├── publisher queue registry / fanout
    │   │   ├── sensor collection interval loop
    │   │   ├── sensor ThreadPoolExecutor
    │   │   │   └── sensor_* worker thread(s)
    │   │   └── publisher ThreadPoolExecutor
    │   │       └── publisher_* worker thread(s)
    ├── api / orchidarium-api
    │   └── Flask main thread
    │       ├── /health
    │       ├── /openapi.json
    │       ├── /ready
    │       └── /metrics
    │           ├── /queue/backlog
    │           └── /sensors/active
    ├── hardware / orchidarium-hardware
    │   └── hardware main thread
    └── ui / orchidarium-ui
        └── Qt/QML main thread
```

- `orchidarium command`: CLI entrypoint in `orchidarium.entrypoint`; calls `orchidarium.daemon.run()`.
- `orchidarium`: supervisor process title; starts child processes with `ProcessPoolExecutor` from `orchidarium.daemon._processes`.
- `metrics`: child process spec; process title is `orchidarium-metrics`; owns the publisher queue registry, sensor collection, and database publication.
- `api`: child process spec; process title is `orchidarium-api`; serves Flask API endpoints using runtime snapshots published by the metrics process.
- `hardware`: child process spec; process title is `orchidarium-hardware`; currently an idle scaffold for relay and device control. It publishes a heartbeat used by `/health` and `/ready`.
- `ui`: child process spec; process title is `orchidarium-ui`; runs the Qt/QML control surface from `orchidarium.ui`.
- `sensor_*`: worker threads created by the metrics process during each collection interval, with one submitted task per discovered sensor.
- `publisher_*`: worker threads created only for publisher queues with backlog, with one queue per database backend.

`/ready` fails when any publisher queue backlog reaches `MAX_POINT_BACKLOG`, so schedulers can stop sending new work to a container that is falling behind. Set `MAX_POINT_BACKLOG=0` to disable the backlog cap.

### Runtime Configuration

The UI persists user-defined runtime settings to `/opt/orchidarium/config/state.json`. Docker Compose mounts `ORCHIDARIUM_CONFIG_DIR` at `/opt/orchidarium/config`; local startup defaults that host directory to `./.orchidarium/config`.

- `INTERVAL`: sensor collection interval in seconds. The minimum value is `5`.
- `MAX_POINT_BACKLOG`: largest allowed publisher queue backlog before `/ready` fails. The minimum value is `0`, and `0` means no configured maximum.
- `ORCHIDARIUM_STATE_PATH`: optional override for the state file path. This keeps the state location configurable as runtime domains are split into separate services.

The process environment remains the fallback source for these values. State-file reads are cached for one second per process, so repeated checks inside one interval use the same snapshot instead of re-reading the file on every access.

### API

The API process serves JSON from the Flask app in `orchidarium.api`. In Docker Compose, it is exposed on `127.0.0.1:8085` by default.

<details>
<summary>See more: GET /openapi.json</summary>

Returns the generated OpenAPI 3.1 specification for the Flask API. The document is generated with `python-openapi` from the typed response schemas in `orchidarium.api.schemas`.

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Orchidarium API",
    "version": "0.0.1"
  },
  "paths": {
    "/health": {},
    "/ready": {},
    "/metrics/queue/backlog": {},
    "/metrics/sensors/active": {},
    "/openapi.json": {}
  }
}
```

</details>

<details>
<summary>See more: GET /health</summary>

Reports liveness for the running controller. The endpoint returns HTTP 200 when the metrics thread pool is running or healthy, the hardware process has a recent heartbeat, and no sensor workers have failed. It returns HTTP 503 with the same payload shape when liveness fails.

`point_backlog` is included for debugging context, but backlog readiness does not decide the `/health` status.

```json
{
  "status": "OK",
  "hardware_process": {
    "status": "healthy",
    "process_name": "hardware",
    "last_heartbeat_at": "2026-07-02T12:00:00+00:00",
    "heartbeat_timeout_seconds": 5.0,
    "heartbeat_age_seconds": 0.25,
    "last_error": null
  },
  "point_backlog": {
    "current_backlog": 0,
    "max_point_backlog": 1000,
    "ready": true
  },
  "thread_pool": {
    "status": "healthy",
    "expected_workers": 3,
    "completed_workers": 3,
    "failed_workers": 0,
    "last_run_successful": true,
    "successful_runs": 42,
    "last_error": null
  }
}
```

</details>

<details>
<summary>See more: GET /ready</summary>

Reports scheduler readiness for the running controller. The endpoint returns HTTP 200 only when the metrics thread pool is ready, the hardware process has a recent heartbeat, and the largest publisher queue backlog is below `MAX_POINT_BACKLOG`. A `MAX_POINT_BACKLOG` value of `0` disables the backlog cap. It returns HTTP 503 with the same payload shape when readiness fails.

```json
{
  "status": "OK",
  "hardware_process": {
    "status": "healthy",
    "process_name": "hardware",
    "last_heartbeat_at": "2026-07-02T12:00:00+00:00",
    "heartbeat_timeout_seconds": 5.0,
    "heartbeat_age_seconds": 0.25,
    "last_error": null
  },
  "point_backlog": {
    "current_backlog": 0,
    "max_point_backlog": 1000,
    "ready": true
  },
  "thread_pool": {
    "status": "healthy",
    "expected_workers": 3,
    "completed_workers": 3,
    "failed_workers": 0,
    "last_run_successful": true,
    "successful_runs": 42,
    "last_error": null
  }
}
```

</details>

<details>
<summary>See more: GET /metrics/queue/backlog</summary>

Returns the latest queue activity snapshot published by the metrics process. Top-level fields summarize all publisher queues. The `queues` object is keyed by publisher name, so keys such as `influxdb` are dynamic as publishers are added.

`current_backlog` is the largest single publisher backlog. `total_current_backlog` is the sum of all publisher backlogs.

```json
{
  "current_backlog": 0,
  "total_current_backlog": 0,
  "publisher_count": 1,
  "window_seconds": 3600,
  "sample_count": 12,
  "min_queue_length": 0,
  "max_queue_length": 4,
  "average_queue_length": 0.5,
  "enqueued": 6,
  "dequeued": 6,
  "last_enqueued_at": "2026-07-02T12:00:00+00:00",
  "last_dequeued_at": "2026-07-02T12:00:01+00:00",
  "queues": {
    "influxdb": {
      "current_backlog": 0,
      "window_seconds": 3600,
      "sample_count": 12,
      "min_queue_length": 0,
      "max_queue_length": 4,
      "average_queue_length": 0.5,
      "enqueued": 6,
      "dequeued": 6,
      "last_enqueued_at": "2026-07-02T12:00:00+00:00",
      "last_dequeued_at": "2026-07-02T12:00:01+00:00"
    }
  }
}
```

</details>

<details>
<summary>See more: GET /metrics/sensors/active</summary>

Returns the number of discovered sensor classes that are currently enabled.

```json
{
  "active_sensors": 3
}
```

</details>

### Metrics Queue Fanout

The metrics process treats sensors as producers and publishers as consumers. The object named `metric_queues` in `orchidarium.data.queue` is the fanout point between those two sides.

```text
sensor thread(s)
    └── Sensor.publish(metric_queues)
        └── DataQueueRegistry.append(MetricDatum)
            ├── DataQueue("influxdb").append(MetricDatum)
            ├── DataQueue("<future publisher>").append(MetricDatum)
            └── DataQueue("<future publisher>").append(MetricDatum)

publisher thread(s)
    ├── InfluxDBPublisher.publish(DataQueue("influxdb"))
    ├── <FuturePublisher>.publish(DataQueue("<future publisher>"))
    └── <FuturePublisher>.publish(DataQueue("<future publisher>"))
```

- `PUBLISHER_SPECS` in `orchidarium.daemon.metrics` declares every metrics backend. Each spec registers one queue in `metric_queues`.
- Sensor workers receive `metric_queues` as a `MetricQueueSink`. They do not choose a database backend.
- A sensor creates one `MetricDatum` and calls `append()`. Because the sink is a `DataQueueRegistry`, that single append copies the datum into every registered publisher queue.
- Each publisher drains only its own queue. This keeps a fast backend from consuming points intended for a slower or failing backend.
- Publisher threads are created only for queues with backlog. Empty queues do not spawn publisher workers for that interval.
- If a publisher pulls a datum and submission fails, the base `Publisher.publish()` method puts that datum back on the same publisher queue before raising.
- Queue activity is sampled per queue for a one-hour rolling window. The API reads the latest metrics-process snapshot via `/metrics/queue/backlog`.
- `current_backlog` is the largest single publisher backlog. `total_current_backlog` is the sum of all publisher backlogs.
- `/ready` compares `current_backlog` to `MAX_POINT_BACKLOG`; readiness fails when any single publisher queue is too far behind. A `MAX_POINT_BACKLOG` value of `0` disables this readiness cap.
- The queues are in-memory and local to the metrics process. Runtime state is snapshotted for the API process, but queued points themselves are not durable across a process restart.

## Development

### Remote Ansible

Remote Raspberry Pi deployment lives under [`ansible/`](./ansible). The default inventory target is `orchidarium-rpi` at `172.16.0.35` on the `172.16.0.35/24` network, using SSH user `tigerlily` and the default Raspberry Pi password `raspberry`.

Start Orchidarium remotely. This installs Docker and Pi helper packages, syncs the deployable source tree to `/home/tigerlily/orchidarium`, installs the Orchidarium udev rules, generates Grafana certificates, and runs Docker Compose on the Pi.

   ```text
   ./scripts/remote/up.sh
   ```

Reset the remote stack before starting it:

   ```text
   ./scripts/remote/up.sh --reset
   ```

Start the remote stack with debug logging:

   ```text
   ./scripts/remote/up.sh --debug
   ```

Stop Orchidarium remotely. This runs Docker Compose down on the Pi and removes the installed Orchidarium udev rules.

   ```text
   ./scripts/remote/down.sh
   ```

Password-based SSH defaults require `sshpass` on the machine running Ansible unless SSH keys are configured. Override the target by editing [`ansible/inventory/hosts.yml`](./ansible/inventory/hosts.yml), or pass normal `ansible-playbook` arguments through either wrapper.

Use the dashboard profile remotely the same way as local Compose:

   ```text
   COMPOSE_PROFILES=dashboard ./scripts/remote/up.sh
   ```

For a headless Pi without a Wayland session, run the remote stack offscreen:

   ```text
   QT_QPA_PLATFORM=offscreen WAYLAND_RUNTIME_DIR=/tmp ./scripts/remote/up.sh
   ```

### Docker Compose

Start the local core stack. This installs and reloads the Orchidarium udev rules when udev is available, sources [`scripts/.env.sh`](./scripts/.env.sh), generates the self-signed Grafana certificates if they do not already exist, then runs `docker compose up -d --build`. The default profile starts Orchidarium and InfluxDB.

   ```text
   ./scripts/local/up.sh
   ```

Start the local stack with debug logging:

   ```text
   ./scripts/local/up.sh --debug
   ```

Start Grafana and MySQL as well when the dashboard stack is needed:

   ```text
   COMPOSE_PROFILES=dashboard ./scripts/local/up.sh
   ```

Stop the local stack. This runs `docker compose down`, removes the Orchidarium udev rules when udev is available, then reloads udev.

   ```text
   ./scripts/local/down.sh
   ```

#### Raspberry Pi Wi-Fi / SSH

The Docker network uses `ORCHIDARIUM_DOCKER_SUBNET`, defaulting to `172.31.240.0/24`, instead of letting Docker choose a bridge subnet. If the Pi becomes unreachable over SSH after `docker compose up`, check that this subnet does not overlap the Wi-Fi LAN:

   ```text
   ip route
   docker network inspect orchidarium-control
   ```

If it overlaps, choose a private subnet that is not used by Wi-Fi, VPN, or other Docker networks:

   ```text
   ORCHIDARIUM_DOCKER_SUBNET=172.31.241.0/24 ./scripts/local/up.sh
   ```

InfluxDB and MySQL use persistent Docker volumes instead of tmpfs by default, and Grafana/MySQL are behind the `dashboard` profile to keep the Raspberry Pi responsive enough for SSH during normal controller runs.

Remote Ansible startup refuses to run Docker Compose when `ORCHIDARIUM_DOCKER_SUBNET` overlaps the declared Raspberry Pi network, Wi-Fi, LAN, VPN, or other non-Docker host routes visible on the Pi.

#### UI Display

The UI process uses Wayland by default on Linux / Raspberry Pi. [`scripts/.env.sh`](./scripts/.env.sh) sets `QT_QPA_PLATFORM=wayland`, mounts the host user's `WAYLAND_RUNTIME_DIR` at `/wayland-runtime`, and runs the Orchidarium container as the current UID / GID so the Wayland socket can be opened.

Run `./scripts/local/up.sh` from the same desktop user that owns the Wayland session. If the compositor uses a different socket name, set it before startup:

   ```text
   WAYLAND_DISPLAY=wayland-1 ./scripts/local/up.sh
   ```

On macOS, Docker Desktop does not expose a host Wayland session. Local startup defaults to `QT_QPA_PLATFORM=offscreen`, `QT_QUICK_BACKEND=software`, and the private `/tmp/orchidarium` runtime directory so the stack can run for testing without a display socket.

To display the UI on macOS, run an X server such as XQuartz and override the backend. In XQuartz, enable `Settings > Security > Allow connections from network clients`, then fully quit and reopen XQuartz. Start XQuartz before starting the stack:

   ```text
   open -a XQuartz
   ```

Then start the stack with the Docker-facing display value. The local startup wrapper runs `/opt/X11/bin/xhost +localhost` against XQuartz before Docker Compose starts.

   ```text
   QT_QPA_PLATFORM=xcb DISPLAY=host.docker.internal:0 WAYLAND_RUNTIME_DIR=/tmp ./scripts/local/up.sh
   ```
