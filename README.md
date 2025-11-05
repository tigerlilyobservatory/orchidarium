# Orchidarium

![GitHub Release](https://img.shields.io/github/v/release/tigerlilyobservatory/orchidarium)

<p align="left" width="100%">
  <img width="20%" src="./img/orchid.png" alt="orchid">
</p>

A collection of scripts and configuration files for collecting and publishing metrics from USB sensors in an orchid terrarium.

Current supported sensors by this Python package include a

- [Humidity and Temperature sensor](https://www.amazon.com/dp/B08BYLZ3ML?ref=ppx_yo2ov_dt_b_fed_asin_title): a waterproof temperature and humidity sensor.
- [Soil metrics](https://www.amazon.com/dp/B0FJFK9PPT?ref=ppx_yo2ov_dt_b_fed_asin_title): a sensor for collecting soil analytics.

## Build

<p align="left" width="100%">
  <img width="75%" src="./img/orchid.png" alt="build">
</p>

Here's a [public Amazon list](https://www.amazon.com/hz/wishlist/ls/1ARZ5WK7A2QLO?ref_=wl_share) with most of the hardware I used to get this orchidarium off the ground.

## How it works by example

See the below screenshots from the Grafana dashboard.

## Local development

### Setup

The [`compose.yaml`](./compose.yaml) contains the configuration required to get this project started.

Source [`./scripts/.env.sh`](./scripts/.env.sh) to get started with environment variables populated from a Linux pass store.