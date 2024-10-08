# test/test_parsers.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Test cases for ‘chug.parsers’ package. """

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
