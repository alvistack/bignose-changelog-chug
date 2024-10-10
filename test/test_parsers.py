# test/test_parsers.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Test cases for ‘chug.parsers’ package. """

import textwrap
import unittest.mock

import testscenarios
import testtools

import chug.parsers


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
        filesystem paths only, a specific mock `open` function will be called,
        that returns the corresponding fake file; for any unspecified path,
        the original `builtins.open` will be called as normal.
        """
    testcase.mock_open_by_path = {
        file_path: unittest.mock.mock_open(read_data=fake_file_content)
        for (file_path, fake_file_content)
        in fake_file_content_by_path.items()}

    def fake_open(file, *args, **kwargs):
        """ Wrapper for builtin `open`, faking for specific paths. """
        open_func = (
            testcase.mock_open_by_path[file]
            if file in testcase.mock_open_by_path
            else __builtins__.open)
        return open_func(file, *args, **kwargs)

    testcase.open_patcher = unittest.mock.patch.object(
        chug.parsers.core, 'open', side_effect=fake_open)
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
