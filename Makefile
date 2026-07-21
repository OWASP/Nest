include backend/Makefile
include cspell/Makefile
include docs/Makefile
include e2e/Makefile
include frontend/Makefile
include infrastructure/Makefile
include make/check.mk
include make/check-test.mk
include make/help.mk
include make/maintenance.mk
include make/run.mk
include make/security.mk
include make/shell.mk
include make/terraform.mk
include make/test.mk

.DEFAULT_GOAL := help

MAKEFLAGS += --no-print-directory
