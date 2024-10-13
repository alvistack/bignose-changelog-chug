# src/chug/parsers/__init__.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Parsers for various input formats of Change Log document. """

from .core import (
    InvalidFormatError,
    entry_title_regex,
    get_changelog_document_text,
    parse_person_field,
)

__all__ = [
    'InvalidFormatError',
    'entry_title_regex',
    'get_changelog_document_text',
    'parse_person_field',
]


# Copyright © 2008–2024 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; version 3 or, at your option, a later version.
# No warranty expressed or implied. See the file ‘LICENSE.AGPL-3’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
