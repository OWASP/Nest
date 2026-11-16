SHELL := bash

.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

include backend/makefile
include cspell/makefile
include docs/makefile
include e2e/makefile
include frontend/makefile
include infrastructure/makefile
include make/check.mk
include make/help.mk
include make/maintenance.mk
include make/run.mk
include make/security.mk
include make/shell.mk
include make/terraform.mk
include make/test.mk
include tools/makefile

.DEFAULT_GOAL := help

MAKEFLAGS += --no-print-directory
