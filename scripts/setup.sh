#! /usr/bin/env bash
# Setup script for using this project.


conda activate
conda activate orchidarium
poetry env use "$(which python)"
poetry install