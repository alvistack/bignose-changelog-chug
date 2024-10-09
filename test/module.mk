# test/module.mk
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

# Makefile rules for test suite.

MAKE_TEST_MODULE_DIR := $(CURDIR)/test

TEST_MODULES += $(shell find ${MAKE_TEST_MODULE_DIR}/ -name 'test_*.py')
CODE_PACKAGE_DIRS += ${MAKE_TEST_MODULE_DIR}

TEST_UNITTEST_OPTS ?=


.PHONY: test
test: test-unittest

.PHONY: test-unittest
test-unittest:
	$(PYTHON) -m unittest ${TEST_UNITTEST_OPTS}


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
