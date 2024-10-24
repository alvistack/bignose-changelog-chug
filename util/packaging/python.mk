# util/packaging/python.mk
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

# Makefile rules for Python packaging.

PYTHON3 ?= python3
PYTHON ?= ${PYTHON3}

PYTHON_BUILD_MODULE := build
PYTHON_BUILD := $(PYTHON) -m ${PYTHON_BUILD_MODULE}
PYTHON_BUILD_OPTS ?=

SETUPTOOLS_CONFIG_MODULE := setup
PACKAGING_SETUP_MODULE_FILE := $(CURDIR)/${SETUPTOOLS_CONFIG_MODULE}.py

CODE_MODULES += ${PACKAGING_SETUP_MODULE_FILE}

GENERATED_FILES += $(shell find $(CURDIR)/ -type d -name '*.egg-info')
GENERATED_FILES += $(shell find $(CURDIR)/ -type d -name '.eggs')
GENERATED_FILES += $(shell find $(CURDIR)/ -type d -name '__pycache__')
GENERATED_FILES += $(shell find $(CURDIR)/ -type f -name '*.pyc')


.PHONY: python-build
python-build: pip-confirm-build-dependencies-installed
	$(PYTHON_BUILD) ${PYTHON_BUILD_OPTS}

build: python-build

GENERATED_FILES += ${DISTRIBUTION_DIR}/


# Copyright © 2006–2024 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-3’ for details.


# Local Variables:
# mode: makefile
# coding: utf-8
# End:
# vim: fileencoding=utf-8 filetype=make :
