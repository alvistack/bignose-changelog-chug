# test/test_util_metadata.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit test for ‘util.metadata’ packaging module. """

import textwrap

import testscenarios
import testtools

import util.metadata


class FakeObject:
    """ A fake object for testing. """


class docstring_from_object_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘docstring_from_object’ function. """

    scenarios = [
        ('single-line', {
            'test_docstring': textwrap.dedent("""\
                Lorem ipsum, dolor sit amet.
                """),
            'expected_result': "Lorem ipsum, dolor sit amet.",
            }),
        ('synopsis one-paragraph', {
            'test_docstring': textwrap.dedent("""\
                Lorem ipsum, dolor sit amet.

                Donec et semper sapien, et faucibus felis. Nunc suscipit
                quam id lectus imperdiet varius. Praesent mattis arcu in
                sem laoreet, at tincidunt velit venenatis.
                """),
            'expected_result': textwrap.dedent("""\
                Lorem ipsum, dolor sit amet.

                Donec et semper sapien, et faucibus felis. Nunc suscipit
                quam id lectus imperdiet varius. Praesent mattis arcu in
                sem laoreet, at tincidunt velit venenatis."""),
            }),
        ('synopsis three-paragraphs', {
            'test_docstring': textwrap.dedent("""\
                Lorem ipsum, dolor sit amet.

                Ut ac ultrices turpis. Nam tellus ex, scelerisque ac
                tellus ac, placerat convallis erat. Nunc id mi libero.

                Donec et semper sapien, et faucibus felis. Nunc suscipit
                quam id lectus imperdiet varius. Praesent mattis arcu in
                sem laoreet, at tincidunt velit venenatis.

                Suspendisse potenti. Fusce egestas id quam non posuere.
                Maecenas egestas faucibus elit. Aliquam erat volutpat.
                """),
            'expected_result': textwrap.dedent("""\
                Lorem ipsum, dolor sit amet.

                Ut ac ultrices turpis. Nam tellus ex, scelerisque ac
                tellus ac, placerat convallis erat. Nunc id mi libero.

                Donec et semper sapien, et faucibus felis. Nunc suscipit
                quam id lectus imperdiet varius. Praesent mattis arcu in
                sem laoreet, at tincidunt velit venenatis.

                Suspendisse potenti. Fusce egestas id quam non posuere.
                Maecenas egestas faucibus elit. Aliquam erat volutpat."""),
            }),
        ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()
        self.test_object = FakeObject()
        self.test_object.__doc__ = self.test_docstring

    def test_returns_expected_result(self):
        """ Should return expected result. """
        result = util.metadata.docstring_from_object(self.test_object)
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
