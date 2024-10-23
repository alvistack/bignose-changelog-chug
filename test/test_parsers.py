# test/test_parsers.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Test cases for ‘chug.parsers’ package. """

import builtins
import re
import textwrap
import unittest.mock

import semver
import testscenarios
import testtools

import chug.parsers
from chug.parsers.core import (
    ChangeLogEntryTitleFormatInvalidError,
    VersionFormatInvalidError,
)
import chug.parsers.core

from . import make_expected_error_context


class FakeNode:
    """ A fake instance of a `Node` of a document. """

    def __init__(self, source=None, line=None):
        self.source = source
        self.line = line


class InvalidFormatError_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for class `InvalidFormatError`. """

    message_scenarios = [
        ('message-specified', {
            'test_message': "Lorem ipsum, dolor sit amet.",
            'expected_message': "Lorem ipsum, dolor sit amet.",
            'expected_message_text': "Lorem ipsum, dolor sit amet.",
        }),
        ('message-unspecified', {
            'test_message': NotImplemented,
            'expected_message': None,
            'expected_message_text': "(no message)",
        }),
    ]

    node_scenarios = [
        ('node-with-source-and-line', {
            'test_node': FakeNode(source="consecteur", line=17),
            'expected_node_source_text': "consecteur",
            'expected_node_text': "consecteur line 17",
        }),
        ('node-with-source-only', {
            'test_node': FakeNode(source="consecteur"),
            'expected_node_source_text': "consecteur",
            'expected_node_text': "consecteur line (unknown)",
        }),
        ('node-with-line-only', {
            'test_node': FakeNode(line=17),
            'expected_node_source_text': "(source unknown)",
            'expected_node_text': "(source unknown) line 17",
        }),
    ]

    scenarios = testscenarios.multiply_scenarios(
        message_scenarios, node_scenarios)

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_kwargs = {}
        self.test_kwargs['node'] = self.test_node
        if (self.test_message is not NotImplemented):
            self.test_kwargs['message'] = self.test_message

    def test_has_specified_node(self):
        """ Should have specified `node` value. """
        test_instance = chug.parsers.InvalidFormatError(**self.test_kwargs)
        expected_node = self.test_kwargs['node']
        self.assertEqual(expected_node, test_instance.node)

    def test_has_specified_message(self):
        """ Should have specified `message` value. """
        test_instance = chug.parsers.InvalidFormatError(**self.test_kwargs)
        self.assertEqual(self.expected_message, test_instance.message)

    def test_str_contains_expected_message_text(self):
        """ Should have `str` containing expected message text. """
        test_instance = chug.parsers.InvalidFormatError(**self.test_kwargs)
        text = str(test_instance)
        self.assertIn(self.expected_message_text, text)

    def test_str_contains_expected_node_text(self):
        """ Should have `str` containing expected node text. """
        test_instance = chug.parsers.InvalidFormatError(**self.test_kwargs)
        text = str(test_instance)
        self.assertIn(self.expected_node_text, text)


class parse_person_field_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘parse_person_field’ function. """

    scenarios = [
        ('simple', {
            'test_person': "Foo Bar <foo.bar@example.com>",
            'expected_result': ("Foo Bar", "foo.bar@example.com"),
        }),
        ('empty', {
            'test_person': "",
            'expected_result': (None, None),
        }),
        ('none', {
            'test_person': None,
            'expected_error': TypeError,
        }),
        ('no email', {
            'test_person': "Foo Bar",
            'expected_result': ("Foo Bar", None),
        }),
    ]

    def test_returns_expected_result(self):
        """ Should return expected result. """
        if hasattr(self, 'expected_error'):
            self.assertRaises(
                self.expected_error,
                chug.parsers.parse_person_field, self.test_person)
        else:
            result = chug.parsers.parse_person_field(self.test_person)
            self.assertEqual(self.expected_result, result)


def mock_builtin_open_for_fake_files(testcase, *, fake_file_content_by_path):
    """ Mock builtin `open` during `testcase`, for specific fake files.

        :param testcase: The test case during which to mock `open`.
        :param fake_file_content_by_path: Mapping of
            `{file_path: fake_file_content}`.

        Create fake files (`io.StringIO`) containing each `fake_file_content`.
        Wrap the `builtins.open` function such that, for the specified
        `file_path` only, a specific mock `open` function will be called,
        that returns the corresponding fake file; for any unspecified path,
        the original `builtins.open` will be called as normal.
        """
    testcase.mock_open_by_path = {
        file_path: unittest.mock.mock_open(read_data=fake_file_content)
        for (file_path, fake_file_content)
        in fake_file_content_by_path.items()}

    open_orig = builtins.open

    def fake_open(file, *args, **kwargs):
        """ Wrapper for builtin `open`, faking for specific paths. """
        open_func = (
            testcase.mock_open_by_path[file]
            if file in testcase.mock_open_by_path
            else open_orig)
        return open_func(file, *args, **kwargs)

    testcase.open_patcher = unittest.mock.patch.object(
        builtins, 'open', side_effect=fake_open)
    testcase.open_patcher.start()
    testcase.addCleanup(testcase.open_patcher.stop)


class get_changelog_document_text_BaseTestCase(testtools.TestCase):
    """ Base for test cases for ‘get_changelog_document_text’ function. """

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        mock_builtin_open_for_fake_files(
            self,
            fake_file_content_by_path={
                self.test_infile_path: self.test_infile_text,
            })

        self.set_test_args()

    def set_test_args(self):
        """ Set the `test_args` test case attribute. """
        self.test_args = [
            self.test_infile_path,
        ]


class get_changelog_document_text_TestCase(
        testscenarios.WithScenarios,
        get_changelog_document_text_BaseTestCase):
    """ Test cases for ‘get_changelog_document_text’ function. """

    scenarios = [
        ('simple', {
            'test_infile_path': "lorem.changelog",
            'test_infile_text': textwrap.dedent("""\
                lorem ipsum
                """),
        }),
    ]

    def test_returns_file_text_content(self):
        """ Should return text content from the input file. """
        expected_result = self.test_infile_text
        result = chug.parsers.get_changelog_document_text(*self.test_args)
        self.assertEqual(expected_result, result)


def make_change_log_entry_title_scenarios():
    """ Make a sequence of scenarios for testing Change Log entry titles.

        :return: Sequence of tuples `(name, parameters)`. Each is a scenario
            as specified for `testscenarios`.
        """
    scenarios = [
        ('title-case', {
            'test_args': ["Version 1.0"],
            'test_kwargs': {},
            'expected_result': "1.0",
        }),
        ('lower-case', {
            'test_args': ["version 1.0"],
            'test_kwargs': {},
            'expected_result': "1.0",
        }),
        ('upper-case', {
            'test_args': ["VERSION 1.0"],
            'test_kwargs': {},
            'expected_result': "1.0",
        }),
        ('title-case regex-custom', {
            'test_args': ["Release 1.0"],
            'test_kwargs': {
                'regex_pattern': re.compile(
                    r"^release (?P<version>[\w.-]+)$",
                    re.IGNORECASE),
            },
            'expected_result': "1.0",
        }),
        ('version-complex', {
            'test_args': ["Version 4.0.17-alpha12"],
            'test_kwargs': {},
            'expected_result': "4.0.17-alpha12",
        }),
        ('empty', {
            'test_args': [""],
            'test_kwargs': {},
            'expected_error': ChangeLogEntryTitleFormatInvalidError,
        }),
        ('version-invalid', {
            'test_args': ["Version b%g^s"],
            'test_kwargs': {},
            'expected_error': ChangeLogEntryTitleFormatInvalidError,
        }),
        ('title-invalid', {
            'test_args': ["Elit Aliquam Ipsum"],
            'test_kwargs': {},
            'expected_error': ChangeLogEntryTitleFormatInvalidError,
        }),
        ('version-invalid regex-custom', {
            'test_args': ["Release b%g^s"],
            'test_kwargs': {
                'regex_pattern': re.compile(
                    r"^release (?P<version>[\w.-]+)$",
                    re.IGNORECASE),
            },
            'expected_error': ChangeLogEntryTitleFormatInvalidError,
        }),
        ('title-invalid', {
            'test_args': ["Elit Aliquam Ipsum"],
            'test_kwargs': {},
            'expected_error': ChangeLogEntryTitleFormatInvalidError,
        }),
        ('not-text', {
            'test_args': [object()],
            'test_kwargs': {},
            'expected_error': TypeError,
        }),
    ]
    return scenarios


class verify_is_change_log_entry_title_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘verify_is_change_log_entry_title’ function. """

    function_to_test = staticmethod(
        chug.parsers.core.verify_is_change_log_entry_title)

    scenarios = make_change_log_entry_title_scenarios()

    def test_returns_expected_result_or_raises_error(self):
        """ Should return or raise expected result or exception. """
        with make_expected_error_context(self):
            self.function_to_test(*self.test_args, **self.test_kwargs)


class get_version_text_from_entry_title_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_version_text_from_entry_title’ function. """

    function_to_test = staticmethod(
        chug.parsers.core.get_version_text_from_entry_title)

    scenarios = make_change_log_entry_title_scenarios()

    def test_returns_expected_result_or_raises_error(self):
        """ Should return or raise expected result or exception. """
        with make_expected_error_context(self):
            result = self.function_to_test(*self.test_args, **self.test_kwargs)
        if hasattr(self, 'expected_result'):
            self.assertEqual(self.expected_result, result)


class get_version_from_version_text_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_version_from_version_text’ function. """

    function_to_test = staticmethod(
        chug.parsers.core.get_version_from_version_text)

    scenarios = [
        ('major-only', {
            'test_args': ["1"],
            'test_kwargs': {},
            'expected_result': semver.Version.parse(
                "1", optional_minor_and_patch=True),
        }),
        ('major-and-minor-only', {
            'test_args': ["1.5"],
            'test_kwargs': {},
            'expected_result': semver.Version.parse(
                "1.5", optional_minor_and_patch=True),
        }),
        ('major-minor-patch', {
            'test_args': ["1.5.3"],
            'test_kwargs': {},
            'expected_result': semver.Version.parse(
                "1.5.3", optional_minor_and_patch=True),
        }),
        ('major-minor-patch-prerelease', {
            'test_args': ["1.5.3-beta2"],
            'test_kwargs': {},
            'expected_result': semver.Version.parse(
                "1.5.3-beta2", optional_minor_and_patch=True),
        }),
        ('major-minor-patch-build', {
            'test_args': ["1.5.3+d3adb33f"],
            'test_kwargs': {},
            'expected_result': semver.Version.parse(
                "1.5.3+d3adb33f", optional_minor_and_patch=True),
        }),
        ('major-minor-build', {
            'test_args': ["1.5+d3adb33f"],
            'test_kwargs': {},
            'expected_result': semver.Version.parse(
                "1.5+d3adb33f", optional_minor_and_patch=True),
        }),
    ]

    def test_returns_expected_result(self):
        """ Should return expected result. """
        result = self.function_to_test(*self.test_args, **self.test_kwargs)
        self.assertEqual(self.expected_result, result)


class get_version_from_version_text_ErrorTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Error test cases for ‘get_version_from_version_text’ function. """

    function_to_test = staticmethod(
        chug.parsers.core.get_version_from_version_text)

    scenarios = [
        ('empty', {
            'test_args': [""],
            'test_kwargs': {},
            'expected_error': VersionFormatInvalidError,
        }),
        ('version-meaningless', {
            'test_args': ["b%g^s"],
            'test_kwargs': {},
            'expected_error': VersionFormatInvalidError,
        }),
        ('version-too-many-components', {
            'test_args': ["2.4.6.8"],
            'test_kwargs': {},
            'expected_error': VersionFormatInvalidError,
        }),
    ]

    def test_raises_expected_error(self):
        """ Should raise error of the expected exception type. """
        with testtools.ExpectedException(self.expected_error):
            __ = self.function_to_test(*self.test_args, **self.test_kwargs)


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
