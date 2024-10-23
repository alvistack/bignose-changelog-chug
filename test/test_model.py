# test/test_model.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit test for ‘chug.model’ module. """

import collections
import contextlib
import functools
import textwrap

import testscenarios
import testtools

import chug.model


class ChangeLogEntry_BaseTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Base class for ‘ChangeLogEntry’ test case classes. """

    def expected_error_context(self):
        """ Make a context manager to expect the nominated error. """
        context = contextlib.nullcontext()
        if hasattr(self, 'expected_error'):
            context = testtools.ExpectedException(self.expected_error)
        return context


class ChangeLogEntry_TestCase(ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry’ class. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_instance = chug.model.ChangeLogEntry()

    def test_instantiate(self):
        """ New instance of ‘ChangeLogEntry’ should be created. """
        self.assertIsInstance(
                self.test_instance, chug.model.ChangeLogEntry)

    def test_minimum_zero_arguments(self):
        """ Initialiser should not require any arguments. """
        instance = chug.model.ChangeLogEntry()
        self.assertIsNot(instance, None)


class ChangeLogEntry_release_date_TestCase(ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.release_date’ attribute. """

    scenarios = [
        ('default', {
            'test_args': {},
            'expected_release_date':
            chug.model.ChangeLogEntry.default_release_date,
        }),
        ('unknown token', {
            'test_args': {'release_date': "UNKNOWN"},
            'expected_release_date': "UNKNOWN",
        }),
        ('future token', {
            'test_args': {'release_date': "FUTURE"},
            'expected_release_date': "FUTURE",
        }),
        ('2001-01-01', {
            'test_args': {'release_date': "2001-01-01"},
            'expected_release_date': "2001-01-01",
        }),
        ('bogus', {
            'test_args': {'release_date': "b0gUs"},
            'expected_error': chug.model.DateInvalidError,
        }),
    ]

    def test_has_expected_release_date(self):
        """ Should have default `release_date` attribute. """
        with self.expected_error_context():
            instance = chug.model.ChangeLogEntry(**self.test_args)
        if hasattr(self, 'expected_release_date'):
            self.assertEqual(self.expected_release_date, instance.release_date)


class ChangeLogEntry_version_TestCase(ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.version’ attribute. """

    scenarios = [
        ('default', {
            'test_args': {},
            'expected_version':
            chug.model.ChangeLogEntry.default_version,
        }),
        ('unknown token', {
            'test_args': {'version': "UNKNOWN"},
            'expected_version': "UNKNOWN",
        }),
        ('next token', {
            'test_args': {'version': "NEXT"},
            'expected_version': "NEXT",
        }),
        ('0.0', {
            'test_args': {'version': "0.0"},
            'expected_version': "0.0",
        }),
        ('1.2.3', {
            'test_args': {'version': "1.2.3"},
            'expected_version': "1.2.3",
        }),
        ('1.23.456', {
            'test_args': {'version': "1.23.456"},
            'expected_version': "1.23.456",
        }),
        ('1.23.456a5', {
            'test_args': {'version': "1.23.456a5"},
            'expected_error': chug.model.VersionInvalidError,
        }),
        ('1.23.456-alpha5', {
            'test_args': {'version': "1.23.456-alpha5"},
            'expected_version': "1.23.456-alpha5",
        }),
        ('123.456.789', {
            'test_args': {'version': "123.456.789"},
            'expected_version': "123.456.789",
        }),
        ('non-number', {
            'test_args': {'version': "b0gUs"},
            'expected_error': chug.model.VersionInvalidError,
        }),
        ('negative', {
            'test_args': {'version': "-1.0"},
            'expected_error': chug.model.VersionInvalidError,
        }),
        ('non-number parts', {
            'test_args': {'version': "1.b0gUs.0"},
            'expected_error': chug.model.VersionInvalidError,
        }),
    ]

    def test_has_expected_version(self):
        """ Should have default `version` attribute. """
        with self.expected_error_context():
            instance = chug.model.ChangeLogEntry(**self.test_args)
        if hasattr(self, 'expected_version'):
            self.assertEqual(self.expected_version, instance.version)


class ChangeLogEntry_maintainer_TestCase(ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.maintainer’ attribute. """

    scenarios = [
        ('default', {
            'test_args': {},
            'expected_maintainer': None,
        }),
        ('person', {
            'test_args': {'maintainer': "Foo Bar <foo.bar@example.org>"},
            'expected_maintainer': "Foo Bar <foo.bar@example.org>",
        }),
        ('bogus', {
            'test_args': {'maintainer': "b0gUs"},
            'expected_error': chug.model.PersonDetailsInvalidError,
        }),
    ]

    def test_has_expected_maintainer(self):
        """ Should have default `maintainer` attribute. """
        with self.expected_error_context():
            instance = chug.model.ChangeLogEntry(**self.test_args)
        if hasattr(self, 'expected_maintainer'):
            self.assertEqual(self.expected_maintainer, instance.maintainer)


class ChangeLogEntry_body_TestCase(ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.body’ attribute. """

    scenarios = [
        ('default', {
            'test_args': {},
            'expected_body': None,
        }),
        ('simple', {
            'test_args': {'body': "Foo bar baz."},
            'expected_body': "Foo bar baz.",
        }),
    ]

    def test_has_expected_body(self):
        """ Should have default `body` attribute. """
        instance = chug.model.ChangeLogEntry(**self.test_args)
        self.assertEqual(self.expected_body, instance.body)


class ChangeLogEntry_repr_TestCase(
        ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.__repr__’ method. """

    scenarios = [
        ('default', {
            'test_args': {},
            'expected_repr': (
                "<ChangeLogEntry"
                " release_date: 'UNKNOWN'"
                " version: 'UNKNOWN'"
                " maintainer: None"
                " body: None"
                ">"),
        }),
        ('simple', {
            'test_args': {'body': "Foo bar baz."},
            'expected_repr': (
                "<ChangeLogEntry"
                " release_date: 'UNKNOWN'"
                " version: 'UNKNOWN'"
                " maintainer: None"
                " body: 'Foo bar baz.'"
                ">"),
        }),
        ('body-too-long', {
            'test_args': {
                'body': textwrap.dedent("""\
                    Aenean non elementum arcu. Sed mattis, quam eu interdum
                    convallis, augue velit dignissim arcu, sed luctus mi velit
                    in nisi.
                    """),
            },
            'expected_repr': (
                "<ChangeLogEntry"
                " release_date: 'UNKNOWN'"
                " version: 'UNKNOWN'"
                " maintainer: None"
                " body: 'Aenean non elementum [...]'"
                ">"),
        }),
    ]

    def test_has_expected_repr(self):
        """ Should have expected programmer representation. """
        instance = chug.model.ChangeLogEntry(**self.test_args)
        result = repr(instance)
        self.assertEqual(self.expected_repr, result)


class ChangeLogEntry_eq_TestCase(
        ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.__eq__’ method. """

    scenarios = [
        ('identical', {
            'test_instance': chug.model.ChangeLogEntry(
                release_date="2004-01-01",
                version="0.8",
                maintainer="Foo Bar <foo.bar@example.org>",
                body="* Donec venenatis nisl aliquam ipsum.\n",
            ),
            'test_other': chug.model.ChangeLogEntry(
                release_date="2004-01-01",
                version="0.8",
                maintainer="Foo Bar <foo.bar@example.org>",
                body="* Donec venenatis nisl aliquam ipsum.\n",
            ),
            'expected_result': True,
        }),
        ('all fields different', {
            'test_instance': chug.model.ChangeLogEntry(
                release_date="2004-01-01",
                version="0.8",
                maintainer="Foo Bar <foo.bar@example.org>",
                body="* Donec venenatis nisl aliquam ipsum.\n",
            ),
            'test_other': chug.model.ChangeLogEntry(
                release_date="2001-01-01",
                version="0.7.2",
                maintainer="Foo Bar <foo.bar@example.org>",
                body="* Pellentesque elementum mollis finibus.\n",
            ),
            'expected_result': False,
        }),
        ('different types', {
            'test_instance': chug.model.ChangeLogEntry(
                release_date="2004-01-01",
                version="0.8",
                maintainer="Foo Bar <foo.bar@example.org>",
                body="* Donec venenatis nisl aliquam ipsum.\n",
            ),
            'test_other': {
                'release_date': "2004-01-01",
                'version': "0.8",
                'maintainer': "Foo Bar <foo.bar@example.org>",
                'body': "* Donec venenatis nisl aliquam ipsum.\n",
            },
            'expected_result': False,
        }),
    ]

    def test_compares_equality_as_expected(self):
        """ Should compare for equality as expected. """
        result = (self.test_instance == self.test_other)
        self.assertEqual(self.expected_result, result)


class ChangeLogEntry_as_version_info_entry_TestCase(
        ChangeLogEntry_BaseTestCase):
    """ Test cases for ‘ChangeLogEntry.as_version_info_entry’ attribute. """

    scenarios = [
        ('default', {
            'test_args': {},
            'expected_result': collections.OrderedDict([
                (
                    'release_date',
                    chug.model.ChangeLogEntry.default_release_date),
                ('version', chug.model.ChangeLogEntry.default_version),
                ('maintainer', None),
                ('body', None),
            ]),
        }),
    ]

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()

        self.test_instance = chug.model.ChangeLogEntry(**self.test_args)

    def test_returns_result(self):
        """ Should return expected result. """
        result = self.test_instance.as_version_info_entry()
        self.assertEqual(self.expected_result, result)


DefaultNoneDict = functools.partial(collections.defaultdict, lambda: None)


class get_latest_version_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_latest_version’ function. """

    scenarios = [
        ('simple', {
            'test_versions': [
                DefaultNoneDict({'release_date': "LATEST"}),
            ],
            'expected_result': chug.model.ChangeLogEntry.make_ordered_dict(
                DefaultNoneDict({'release_date': "LATEST"})),
        }),
        ('no versions', {
            'test_versions': [],
            'expected_result': collections.OrderedDict(),
        }),
        ('ordered versions', {
            'test_versions': [
                DefaultNoneDict({'release_date': "1"}),
                DefaultNoneDict({'release_date': "2"}),
                DefaultNoneDict({'release_date': "LATEST"}),
            ],
            'expected_result': chug.model.ChangeLogEntry.make_ordered_dict(
                DefaultNoneDict({'release_date': "LATEST"})),
        }),
        ('un-ordered versions', {
            'test_versions': [
                DefaultNoneDict({'release_date': "2"}),
                DefaultNoneDict({'release_date': "LATEST"}),
                DefaultNoneDict({'release_date': "1"}),
            ],
            'expected_result': chug.model.ChangeLogEntry.make_ordered_dict(
                DefaultNoneDict({'release_date': "LATEST"})),
        }),
    ]

    def test_returns_expected_result(self):
        """ Should return expected result. """
        result = chug.model.get_latest_version(self.test_versions)
        self.assertDictEqual(self.expected_result, result)


# Copyright © 2008–2024 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-3’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
