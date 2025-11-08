#!/bin/bash

APP_DIR="/home/exorciste/ai-news-brief"
UV_PATH="/root/.local/bin/uv"

export PYTHONPATH="${PYTHONPATH}:${APP_DIR}"

cd ${APP_DIR} && ${UV_PATH} run ${APP_DIR}/main.py
