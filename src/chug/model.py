# src/chug/model.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Data model for internal representation. """

import collections
import datetime
import re
import textwrap

import semver


class VersionInvalidError(ValueError):
    """ Raised when a version representation is formally invalid. """


class DateInvalidError(ValueError):
    """ Raised when a date representation is formally invalid. """


class PersonDetailsInvalidError(ValueError):
    """ Raised when a person representation is formally invalid. """


rfc822_person_regex = re.compile(r"^(?P<name>[^<]+) <(?P<email>[^>]+)>$")
""" Regular Expression pattern to match a person's contact details. """


class ChangeLogEntry:
    """ An individual entry from the Change Log document. """

    field_names = [
        'release_date',
        'version',
        'maintainer',
        'body',
    ]

    date_format = "%Y-%m-%d"
    default_version = "UNKNOWN"
    default_release_date = "UNKNOWN"

    def __init__(
            self,
            release_date=default_release_date, version=default_version,
            maintainer=None, body=None):
        self.validate_release_date(release_date)
        self.release_date = release_date

        self.validate_version(version)
        self.version = version

        self.validate_maintainer(maintainer)
        self.maintainer = maintainer
        self.body = body

    def __repr__(self):
        """ Programmer representation text of this instance. """
        body_abbreviated = (
            None if self.body is None
            else textwrap.shorten(self.body, 30))
        text = (
            "<{0.__class__.__name__}"
            " release_date: {0.release_date!r}"
            " version: {0.release_date!r}"
            " maintainer: {0.maintainer!r}"
            " body: {body!r}"
            ">").format(self, body=body_abbreviated)
        return text

    @classmethod
    def validate_release_date(cls, value):
        """ Validate the `release_date` value.

            :param value: The prospective `release_date` value.
            :return: ``None`` if the value is valid.
            :raises DateInvalidError: If the value is invalid.
            """
        if value in ["UNKNOWN", "FUTURE"]:
            # A valid non-date value.
            return None

        try:
            __ = datetime.datetime.strptime(value, ChangeLogEntry.date_format)
        except ValueError as exc:
            raise DateInvalidError(value) from exc

        # No exception raised; return successfully.
        return None

    @classmethod
    def validate_version(cls, value):
        """ Validate the `version` value.

            :param value: The prospective `version` value.
            :return: ``None`` if the value is valid.
            :raises VersionInvalidError: If the value is invalid.
            """
        if value in ["UNKNOWN", "NEXT"]:
            # A valid non-version value.
            return None

        try:
            __ = semver.Version.parse(value, optional_minor_and_patch=True)
        except ValueError as exc:
            raise VersionInvalidError(value) from exc

        # No exception raised; return successfully.
        return None

    @classmethod
    def validate_maintainer(cls, value):
        """ Validate the `maintainer` value.

            :param value: The prospective `maintainer` value.
            :return: ``None`` if the value is valid.
            :raises PersonDetailsInvalidError: If the value is invalid.
            """
        valid = False

        if value is None:
            valid = True
        elif rfc822_person_regex.search(value):
            valid = True

        if not valid:
            raise PersonDetailsInvalidError(
                "not a valid person specification {value!r}".format(
                    value=value))

        # No exception raised; return successfully.
        return None

    @classmethod
    def make_ordered_dict(cls, fields):
        """ Make an ordered dict of the fields. """
        result = collections.OrderedDict(
            (name, fields[name])
            for name in cls.field_names)
        return result

    def as_version_info_entry(self):
        """ Format the changelog entry as a version info entry. """
        fields = vars(self)
        entry = self.make_ordered_dict(fields)

        return entry

    def __eq__(self, other):
        result = False
        if isinstance(other, type(self)):
            self_mapping = self.make_ordered_dict(vars(self))
            other_mapping = self.make_ordered_dict(vars(other))
            if self_mapping == other_mapping:
                result = True
        return result


def get_latest_version(versions):
    """ Get the latest version from a collection of changelog entries.

        :param versions: A collection of mappings for changelog entries.
        :return: An ordered mapping of fields for the latest version,
            if `versions` is non-empty; otherwise, an empty mapping.
        """
    version_info = collections.OrderedDict()

    versions_by_release_date = {
        item['release_date']: item
        for item in versions}
    if versions_by_release_date:
        latest_release_date = max(versions_by_release_date.keys())
        version_info = ChangeLogEntry.make_ordered_dict(
            versions_by_release_date[latest_release_date])

    return version_info


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
