# util/packaging/module.mk
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

# Makefile rules for package build and distribution.

MAKE_PACKAGING_MODULE_DIR := $(CURDIR)/util/packaging

DISTRIBUTION_DIR ?= $(CURDIR)/dist


include ${MAKE_PACKAGING_MODULE_DIR}/python.mk


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
