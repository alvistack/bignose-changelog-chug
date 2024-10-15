# src/chug/parsers/core.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Core functionality for document parsers. """

import collections
import re

import semver

from ..model import rfc822_person_regex


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


def get_changelog_document_text(infile_path):
    """ Get the changelog document text from file at `infile_path`.

        :param infile_path: Filesystem path of the document to read.
        :return: Text content from the file.
        """
    with open(infile_path, encoding='utf-8') as infile:
        text = infile.read()
    return text


entry_title_regex = re.compile(
    r"^version (?P<version>[\w.-]+)$",
    re.IGNORECASE)
""" Regular Expression pattern to match a change log entry title. """


class ChangeLogEntryTitleFormatInvalidError(ValueError):
    """ Raised when entry title text does not match expected pattern. """


def verify_is_change_log_entry_title(
        title,
        *,
        regex_pattern=entry_title_regex,
):
    """ Verify that `title` is a valid Change Log entry title.

        :param title: The title (text) of the change log entry to query.
        :param regex_pattern: The compiled `re.Pattern` instance to use for
            matching the `title` text.
        :return: The version text parsed from `title`.
        :raises ChangeLogEntryTitleFormatInvalidError: If `title` does
            not match the expected title format.
        """
    if regex_pattern.match(title) is None:
        raise ChangeLogEntryTitleFormatInvalidError(title)


def get_version_text_from_entry_title(
        title,
        *,
        regex_pattern=entry_title_regex,
):
    """ Get the version text from the change log entry title text `title`.

        :param title: The title (text) of the change log entry to query.
        :param regex_pattern: The compiled `re.Pattern` instance to use for
            matching the `title` text.
        :return: The version text parsed from `title`.
        :raises ChangeLogEntryTitleFormatInvalidError: If `title` does
            not match the expected title format.

        The `regex_pattern` is expected to define a 'version' match group that
        will match only the version text.
        """
    match = regex_pattern.match(title)
    if match is None:
        raise ChangeLogEntryTitleFormatInvalidError(title)
    version_text = match.group('version')
    return version_text


class VersionFormatInvalidError(ValueError):
    """ Raised when entry version text is invalid for Semantic Version. """


def get_version_from_version_text(version_text):
    """ Get the `semver.Version` representation of `version_text`

        :param version_text:
        :return: A `semver.Version` instance representing the version.
        :raises VersionFormatInvalidError: If `version_text` does not parse as
            a Semantic Version value.
        """
    try:
        version = semver.Version.parse(
            version_text, optional_minor_and_patch=True)
    except ValueError as exc:
        raise VersionFormatInvalidError(version_text) from exc
    return version


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
