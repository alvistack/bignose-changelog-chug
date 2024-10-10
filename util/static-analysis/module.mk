# util/static-analysis/module.mk
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

# Makefile rules for static analysis suite.

MAKE_STATIC_ANALYSIS_MODULE_DIR := $(CURDIR)/util/static-analysis

TEST_PIP_CHECK_OPTS ?= --no-input --require-virtualenv

# Minimum complexity (integer) threshold for emitting a report.
TEST_PYMCCABE_MIN ?= 4
TEST_PYMCCABE_OPTS ?= --min ${TEST_PYMCCABE_MIN}

TEST_PYCODESTYLE_OPTS ?=

TEST_RUFF_CHECK_OPTS ?=

TEST_ISORT_OPTS ?= --check-only --diff


.PHONY: static-analysis
static-analysis: static-text-check

.PHONY: static-text-check
static-text-check:
	${MAKE_STATIC_ANALYSIS_MODULE_DIR}/check-text-files-format

check: static-analysis


.PHONY: pip-available-updates-check
pip-available-updates-check:
	$(PYTHON) -m pip check ${TEST_PIP_CHECK_OPTS}

check: pip-available-updates-check


.PHONY: test-pymccabe
test-pymccabe:
	for f in ${CODE_MODULES} ; do \
		printf "McCabe complexity measurement ‘%s’:\n" "$$f" ; \
		$(PYTHON) -m mccabe ${TEST_PYMCCABE_OPTS} "$$f" ; \
	done ; \
	printf "McCabe complexity measurements done.\n" ; \

.PHONY: test-pycodestyle
test-pycodestyle:
	$(PYTHON) -m pycodestyle ${TEST_PYCODESTYLE_OPTS} \
		${CODE_PACKAGE_DIRS}

.PHONY: test-ruff
test-ruff:
	$(PYTHON) -m ruff check ${TEST_RUFF_CHECK_OPTS} \
		${CODE_PACKAGE_DIRS}

static-analysis: test-pymccabe test-pycodestyle test-ruff


.PHONY: test-isort
test-isort:
	$(PYTHON) -m isort ${TEST_ISORT_OPTS} \
		${CODE_PACKAGE_DIRS}


# Copyright © 2008–2024 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; version 3 or, at your option, a later version.
# No warranty expressed or implied. See the file ‘LICENSE.AGPL-3’ for details.


# Local Variables:
# coding: utf-8
# mode: makefile
# End:
# vim: fileencoding=utf-8 filetype=make :
