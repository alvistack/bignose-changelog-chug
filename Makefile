#! /usr/bin/make -f
#
# Makefile
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

# Makefile for ‘changelog-chug’ project.

SHELL = /bin/bash

# Variables that will be extended by module include files.
GENERATED_FILES :=

# Directories with semantic meaning.
PACKAGE_SOURCE_DIR := $(CURDIR)/src
STATIC_ANALYSIS_UTIL_DIR := $(CURDIR)/util/static-analysis
TEST_SUITE_DIR := $(CURDIR)/test
PACKAGING_UTIL_DIR := $(CURDIR)/util/packaging

# List of modules (directories) that comprise our ‘make’ project.
MODULES := ${PACKAGE_SOURCE_DIR}
MODULES += ${STATIC_ANALYSIS_UTIL_DIR}
MODULES += ${TEST_SUITE_DIR}
MODULES += ${PACKAGING_UTIL_DIR}


# Establish the default goal.
.PHONY: all
all: clean build

# Include the make data for each module.
include $(patsubst %,%/module.mk,${MODULES})


.PHONY: clean
clean:
	$(RM) -r ${GENERATED_FILES}


.PHONY: check
check:


.PHONY: build
build:


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
