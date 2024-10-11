# test/test_parsers_rest.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Test cases for ‘chug.parsers.rest’ module. """

import textwrap
import unittest.mock

import docutils.core
import docutils.utils
import testscenarios
import testtools

import chug.parsers.rest


def patch_docutils_publish_doctree(testcase, *, fake_document=None):
    """ Patch function ‘docutils.core.publish_doctree’ during `testcase`.

        :param testcase: The `TestCase` instance for binding to the patch.
        :param fake_document: The document to return from the mocked callable.
        :return: ``None``.
        """
    func_patcher = unittest.mock.patch.object(
        docutils.core, "publish_doctree", autospec=True)
    func_patcher.start()
    testcase.addCleanup(func_patcher.stop)

    docutils.core.publish_doctree.return_value = fake_document


class parse_rest_document_from_text_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘parse_person_field’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.parse_rest_document_from_text)

    scenarios = [
        ('simple', {
            'test_document_text': textwrap.dedent("""\
                Lorem ipsum, dolor sit amet.
                """),
        }),
        ('empty', {
            'test_document_text': "",
        }),
        ('type-none', {
            'test_document_text': None,
            'expected_error': TypeError,
        }),
        ('type-bytes', {
            'test_document_text': b"b0gUs",
            'expected_error': TypeError,
        }),
    ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        if not hasattr(self, 'test_file_path'):
            self.test_file_path = self.getUniqueString()
        self.fake_document_node = docutils.utils.new_document(
            source_path=self.test_file_path,
        )
        patch_docutils_publish_doctree(
            self,
            fake_document=self.fake_document_node)

        self.test_args = [self.test_document_text]

    def test_calls_publish_doctree_with_specified_text(self):
        """
        Should call ‘docutils.core.publish_doctree’ with the document text.
        """
        if hasattr(self, 'expected_error'):
            self.skipTest("will not use Docutils when input is wrong type")
        __ = self.function_to_test(*self.test_args)
        docutils.core.publish_doctree.assert_called_with(
            self.test_document_text)

    def test_returns_expected_result(self):
        """ Should return expected result. """
        if hasattr(self, 'expected_error'):
            self.assertRaises(
                self.expected_error,
                self.function_to_test, *self.test_args)
        else:
            expected_result = self.fake_document_node
            result = self.function_to_test(*self.test_args)
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
