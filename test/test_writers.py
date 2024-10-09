# test/test_writers.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Test cases for ‘chug.writers’ package. """

import json
import unittest.mock

import testscenarios
import testtools

import chug.writers


@unittest.mock.patch.object(json, "dumps", side_effect=json.dumps)
class serialise_version_info_from_mapping_to_json_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """
    Test cases for ‘serialise_version_info_from_mapping_to_json’ function.
    """

    scenarios = [
        ('simple', {
            'test_version_info': {'foo': "spam"},
        }),
    ]

    for (name, scenario) in scenarios:
        scenario['fake_json_dump'] = json.dumps(scenario['test_version_info'])
        scenario['expected_value'] = scenario['test_version_info']

    def test_passes_specified_object(self, mock_func_json_dumps):
        """ Should pass the specified object to `json.dumps`. """
        chug.writers.serialise_version_info_from_mapping_to_json(
            self.test_version_info)
        mock_func_json_dumps.assert_called_with(
            self.test_version_info, indent=unittest.mock.ANY)

    def test_returns_expected_result(self, mock_func_json_dumps):
        """ Should return expected result. """
        mock_func_json_dumps.return_value = self.fake_json_dump
        result = chug.writers.serialise_version_info_from_mapping_to_json(
            self.test_version_info)
        value = json.loads(result)
        self.assertEqual(self.expected_value, value)


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
