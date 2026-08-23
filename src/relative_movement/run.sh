#!/usr/bin/env bash

.venv/bin/watchmedo auto-restart \
  --patterns="*.py" \
  --recursive \
  -- .venv/bin/python src/balloon/balloon.py
