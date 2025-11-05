# Orchidarium

![GitHub Release](https://img.shields.io/github/v/release/tigerlilyobservatory/orchidarium)

<p align="left" width="100%">
  <img width="20%" src="./img/orchid.png" alt="orchid">
</p>

A collection of scripts and configuration files for collecting and publishing metrics from USB sensors in an orchid terrarium.

## Hardware

- [Humidity and Temperature sensor](https://www.amazon.com/dp/B08BYLZ3ML?ref=ppx_yo2ov_dt_b_fed_asin_title): a waterproof temperature and humidity sensor.
- [Soil metrics](https://www.amazon.com/dp/B0FJFK9PPT?ref=ppx_yo2ov_dt_b_fed_asin_title): a sensor for collecting soil analytics.

## Setup

The [`compose.yaml`](./compose.yaml) contains the configuration required to get this project started.

Source [`./scripts/.env.sh`](./scripts/.env.sh) to get started with environment variables populated from a Linux pass store.