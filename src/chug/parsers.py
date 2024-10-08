# src/chug/parsers.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Parsers for various input formats of Change Log document. """

import collections

from .model import rfc822_person_regex


class InvalidFormatError(ValueError):
    """ Raised when the document is not a valid ‘ChangeLog’ document. """

    def __init__(self, node, message=None):
        self.node = node
        self.message = message

    def __str__(self):
        text = "{message}: {source} line {line}".format(
            message=(
                self.message if self.message is not None
                else "(no message)"),
            source=(
                self.node.source if (
                    hasattr(self.node, 'source')
                    and self.node.source is not None
                ) else "(source unknown)"
            ),
            line=(
                "{:d}".format(self.node.line) if (
                    hasattr(self.node, 'line')
                    and self.node.line is not None
                ) else "(unknown)"
            ),
        )

        return text


ParsedPerson = collections.namedtuple('ParsedPerson', ['name', 'email'])
""" A person's contact details: name, email address. """


def parse_person_field(value):
    """ Parse a person field into name and email address.

        :param value: The text value specifying a person.
        :return: A `ParsedPerson` instance for the person's details.

        If the `value` does not match a standard person with email
        address, the return value has `email` item set to ``None``.
        """
    result = ParsedPerson(name=None, email=None)

    match = rfc822_person_regex.match(value)
    if len(value):
        if match is not None:
            result = ParsedPerson(
                name=match.group('name'),
                email=match.group('email'))
        else:
            result = ParsedPerson(name=value, email=None)

    return result


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
