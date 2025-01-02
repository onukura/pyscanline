#!/usr/bin/env bash

set -e
set -x

pytest --junitxml=report.xml --cov=pyscanline/ tests/ -vvv
coverage report
coverage xml
