#!/bin/bash

set -e

python manage.py migrate

pytest fuzz_tests
