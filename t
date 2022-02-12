#!/bin/bash

set -e
.venv/bin/python3 -m unittest "$@"
