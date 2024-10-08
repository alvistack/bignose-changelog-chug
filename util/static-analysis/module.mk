# util/static-analysis/module.mk
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

# Makefile rules for static analysis suite.

MAKE_STATIC_ANALYSIS_MODULE_DIR := $(CURDIR)/util/static-analysis


.PHONY: static-analysis
static-analysis: static-text-check

.PHONY: static-text-check
static-text-check:
	${MAKE_STATIC_ANALYSIS_MODULE_DIR}/check-text-files-format


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
