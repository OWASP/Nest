#!/usr/bin/env bash

check_prerequisites(){
    local tool
    for tool in "$@"; do
        if ! command -v "${tool}" >/dev/null 2>&1; then
            echo "ERROR: ${tool} not found. See infrastructure/README.md prerequisites." >&2
            exit 1
        fi
    done
    return 0
}
