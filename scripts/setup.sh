#!/usr/bin/env bash

set -e
set -x

pip install -U pip uv
uv sync --compile-bytecode --link-mode=copy --frozen
