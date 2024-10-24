# test/module.mk
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

# Makefile rules for test suite.

MAKE_TEST_MODULE_DIR := $(CURDIR)/test

export LANG ?= C.UTF-8
export LC_ALL ?= C.UTF-8

export COVERAGE_FILE = $(CURDIR)/.coverage
coverage_html_report_dir = $(CURDIR)/htmlcov

TEST_MODULES += $(shell find ${MAKE_TEST_MODULE_DIR}/ -name 'test_*.py')
CODE_PACKAGE_DIRS += ${MAKE_TEST_MODULE_DIR}

TEST_UNITTEST_OPTS ?=

TEST_COVERAGE_MINIMUM_PERCENT ?= 95
TEST_COVERAGE_RUN_OPTS ?= --data-file ${COVERAGE_FILE} \
	--branch
TEST_COVERAGE_REPORT_OPTS ?= --data-file ${COVERAGE_FILE}\
	--fail-under ${TEST_COVERAGE_MINIMUM_PERCENT}
TEST_COVERAGE_HTML_OPTS ?= --data-file ${COVERAGE_FILE}\
	--directory ${coverage_html_report_dir}/


test: test-unittest

.PHONY: test-unittest
test-unittest: pip-confirm-build-dependencies-installed
test-unittest:
	$(PYTHON) -m unittest ${TEST_UNITTEST_OPTS}


.PHONY: test-coverage
test-coverage: test-coverage-run test-coverage-html test-coverage-report

.PHONY: test-coverage-run
test-coverage-run: pip-confirm-build-dependencies-installed
test-coverage-run: ${COVERAGE_FILE}

${COVERAGE_FILE}: ${CODE_MODULES}
	$(PYTHON) -m coverage run ${TEST_COVERAGE_RUN_OPTS} \
		-m unittest ${TEST_UNITTEST_OPTS}

GENERATED_FILES += ${COVERAGE_FILE}

.PHONY: test-coverage-html
test-coverage-html: ${COVERAGE_FILE}
	$(PYTHON) -m coverage html ${TEST_COVERAGE_HTML_OPTS}

GENERATED_FILES += ${coverage_html_report_dir}

.PHONY: test-coverage-report
test-coverage-report: ${COVERAGE_FILE}
	$(PYTHON) -m coverage report ${TEST_COVERAGE_REPORT_OPTS}


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
