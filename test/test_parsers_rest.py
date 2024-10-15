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
import docutils.nodes
import docutils.utils
import testscenarios
import testtools

import chug.parsers.rest

from . import make_expected_error_context


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


class get_node_text_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_node_text’ function. """

    function_to_test = staticmethod(chug.parsers.rest.get_node_text)

    test_document = docutils.core.publish_doctree(textwrap.dedent("""\
        Felis gravida lacinia
        #####################

        Maecenas feugiat nibh sed enim fringilla faucibus.
        """))

    scenarios = [
        ('document-title-node', {
            'test_args': [next(
                node for node in test_document.children
                if isinstance(node, docutils.nodes.title))],
            'expected_result': "Felis gravida lacinia",
        }),
        ('paragraph-node', {
            'test_args': [next(
                node for node in test_document.children
                if isinstance(node, docutils.nodes.paragraph))],
            'expected_result': (
                "Maecenas feugiat nibh sed enim fringilla faucibus."),
        }),
        ('not-a-node', {
            'test_args': [object()],
            'expected_error': TypeError,
        }),
    ]

    def test_returns_expected_result(self):
        """ Should return expected result or raise expected error. """
        with make_expected_error_context(self):
            result = self.function_to_test(*self.test_args)
        if hasattr(self, 'expected_result'):
            self.assertEqual(self.expected_result, result)


class get_node_title_text_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_node_title_text’ function. """

    function_to_test = staticmethod(chug.parsers.rest.get_node_title_text)

    test_document = docutils.core.publish_doctree(textwrap.dedent("""\
        #####################
        Felis gravida lacinia
        #####################

        Sed commodo ipsum ac felis gravida lacinia.

        Tempus lorem aliquet
        ====================

        Maecenas feugiat nibh sed enim fringilla faucibus.
        """))

    scenarios = [
        ('document-node', {
            'test_args': [test_document],
            'expected_result': "Felis gravida lacinia",
        }),
        ('section-node', {
            'test_args': [next(
                node for node in test_document.children
                if isinstance(node, docutils.nodes.section))],
            'expected_result': "Tempus lorem aliquet",
        }),
        ('paragraph-node', {
            'test_args': [next(
                node for node in test_document.children
                if isinstance(node, docutils.nodes.paragraph))],
            'expected_result': None,
        }),
        ('not-a-node', {
            'test_args': [object()],
            'expected_error': TypeError,
        }),
    ]

    def test_returns_expected_result(self):
        """ Should return expected result or raise expected error. """
        with make_expected_error_context(self):
            result = self.function_to_test(*self.test_args)
        if hasattr(self, 'expected_result'):
            self.assertEqual(self.expected_result, result)


class get_node_title_text_ErrorTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Error test cases for ‘get_node_title_text’ function. """

    function_to_test = staticmethod(chug.parsers.rest.get_node_title_text)

    scenarios = [
        ('not-a-node', {
            'test_args': [object()],
            'expected_error': TypeError,
        }),
    ]

    def test_raises_expected_error(self):
        """ Should raise the `expected_error` type. """
        with make_expected_error_context(self):
            __ = self.function_to_test(*self.test_args)


def make_rest_document_test_scenarios():
    """ Make a sequence of scenarios for testing different reST documents.

        :return: Sequence of tuples `(name, parameters)`. Each is a scenario
            as specified for `testscenarios`.
        """
    scenarios = [
        ('entries-one', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.
                """),
            # Docutils treats a lone top-level section title specially: it is
            # “lifted up to be the document's title”.
            # <URL:https://docutils.sourceforge.io/docs/user/rst/quickref.html>
            # Therefore there are no top-level `section` nodes.
            'expected_document_title_text': "Version 1.0",
            'expected_document_subtitle_text': None,
            'expected_sections_title_text': [],
            'expected_versions_text': [
                "1.0",
            ],
        }),
        ('entries-three', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Pellentesque elementum mollis finibus.
                """),
            # There are three sibling top-level sections. Therefore they are
            # not treated specially.
            'expected_document_title_text': None,
            'expected_document_subtitle_text': None,
            'expected_sections_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
        }),
        ('preamble-paragraph entries-one', {
            'test_document_text': textwrap.dedent("""\
                Maecenas feugiat nibh sed enim fringilla faucibus.

                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.
                """),
            # The section is not alone at the top level (the preamble paragraph
            # is its sibling). Therefore the section is not treated specially.
            'expected_document_title_text': None,
            'expected_document_subtitle_text': None,
            'expected_sections_title_text': [
                "Version 1.0",
            ],
            'expected_versions_text': [
                "1.0",
            ],
        }),
        ('preamble-paragraph entries-three', {
            'test_document_text': textwrap.dedent("""\
                Maecenas feugiat nibh sed enim fringilla faucibus.

                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Pellentesque elementum mollis finibus.
                """),
            # The sections are not alone at the top level (the preamble
            # paragraph is a sibling). Therefore the sections are not treated
            # specially.
            'expected_document_title_text': None,
            'expected_document_subtitle_text': None,
            'expected_sections_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
        }),
        ('document-title entries-one', {
            'test_document_text': textwrap.dedent("""\
                #####################
                Felis gravida lacinia
                #####################


                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.
                """),
            # Docutils treats a lone top-level section with lone subsection
            # specially: their titles are “lifted up to be the document's
            # (sub)title”.
            # <URL:https://docutils.sourceforge.io/docs/user/rst/quickref.html>
            # Therefore there are no top-level `section`s.
            'expected_document_title_text': "Felis gravida lacinia",
            'expected_document_subtitle_text': "Version 1.0",
            'expected_sections_title_text': [],
            'expected_versions_text': [
                "1.0",
            ],
        }),
        ('document-title entries-three', {
            'test_document_text': textwrap.dedent("""\
                #####################
                Felis gravida lacinia
                #####################


                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Pellentesque elementum mollis finibus.
                """),
            # Docutils treats a lone top-level section title specially: it is
            # “lifted up to be the document's title”.
            # <URL:https://docutils.sourceforge.io/docs/user/rst/quickref.html>
            # Therefore the subsequent sections are the top-level `section`s.
            'expected_document_title_text': "Felis gravida lacinia",
            'expected_document_subtitle_text': None,
            'expected_sections_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
        }),
        ('document-title preamble-paragraph entries-one', {
            'test_document_text': textwrap.dedent("""\
                #####################
                Felis gravida lacinia
                #####################

                Maecenas feugiat nibh sed enim fringilla faucibus.


                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.
                """),
            # Docutils treats a lone top-level section title specially: it is
            # “lifted up to be the document's title”.
            # <URL:https://docutils.sourceforge.io/docs/user/rst/quickref.html>
            # Therefore the subsequent section is the top-level `section`.
            'expected_document_title_text': "Felis gravida lacinia",
            'expected_document_subtitle_text': None,
            'expected_sections_title_text': [
                "Version 1.0",
            ],
            'expected_versions_text': [
                "1.0",
            ],
        }),
        ('document-title preamble-paragraph entries-three', {
            'test_document_text': textwrap.dedent("""\
                #####################
                Felis gravida lacinia
                #####################

                Maecenas feugiat nibh sed enim fringilla faucibus.


                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Pellentesque elementum mollis finibus.
                """),
            # Docutils treats a lone top-level section title specially: it is
            # “lifted up to be the document's title”.
            # <URL:https://docutils.sourceforge.io/docs/user/rst/quickref.html>
            # Therefore the subsequent sections are the top-level `section`s.
            'expected_document_title_text': "Felis gravida lacinia",
            'expected_document_subtitle_text': None,
            'expected_sections_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
        }),
        ('document-title top-sections-one changelog-format-invalid', {
            'test_document_text': textwrap.dedent("""\
                #####################
                Felis gravida lacinia
                #####################

                Sed commodo ipsum ac felis gravida lacinia.

                Tempus lorem aliquet
                ####################

                Maecenas feugiat nibh sed enim fringilla faucibus.


                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.
                """),
            # The document title has multiple children: a stand-alone paragraph
            # and another section. The section is a single top-level `section`.
            # The resulting document has no changelog entries at the top level.
            'expected_document_title_text': "Felis gravida lacinia",
            'expected_document_subtitle_text': None,
            'expected_sections_title_text': [
                "Tempus lorem aliquet",
            ],
            'expected_versions_text': [],
        }),
        ('document-title top-sections-three changelog-format-invalid', {
            'test_document_text': textwrap.dedent("""\
                #####################
                Felis gravida lacinia
                #####################

                Sed commodo ipsum ac felis gravida lacinia.

                Tempus lorem aliquet
                ####################

                Maecenas feugiat nibh sed enim fringilla faucibus.


                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Pellentesque elementum mollis finibus.
                """),
            # The document title has multiple children: a stand-alone paragraph
            # and another section. The section is a single top-level `section`.
            # The resulting document has no changelog entries at the top level.
            'expected_document_title_text': "Felis gravida lacinia",
            'expected_document_subtitle_text': None,
            'expected_sections_title_text': [
                "Tempus lorem aliquet",
            ],
            'expected_versions_text': [],
        }),
        ('document-title-and-subtitle entries-one', {
            'test_document_text': textwrap.dedent("""\
                #####################
                Felis gravida lacinia
                #####################

                Tempus lorem aliquet
                ####################


                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.
                """),
            # Docutils treats a lone top-level section with lone subsection
            # specially: their titles are “lifted up to be the document's
            # (sub)title”.
            # <URL:https://docutils.sourceforge.io/docs/user/rst/quickref.html>
            # Therefore the subsequent section is the top-level `section`.
            'expected_document_title_text': "Felis gravida lacinia",
            'expected_document_subtitle_text': "Tempus lorem aliquet",
            'expected_sections_title_text': [
                "Version 1.0",
            ],
            'expected_versions_text': [
                "1.0",
            ],
        }),
        ('document-title-and-subtitle entries-three', {
            'test_document_text': textwrap.dedent("""\
                #####################
                Felis gravida lacinia
                #####################

                Tempus lorem aliquet
                ####################


                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Pellentesque elementum mollis finibus.
                """),
            # Docutils treats a lone top-level section with lone subsection
            # specially: their titles are “lifted up to be the document's
            # (sub)title”.
            # <URL:https://docutils.sourceforge.io/docs/user/rst/quickref.html>
            # Therefore the subsequent sections are the top-level `section`s.
            'expected_document_title_text': "Felis gravida lacinia",
            'expected_document_subtitle_text': "Tempus lorem aliquet",
            'expected_sections_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
        }),
        ('document-title-and-subtitle preamble-paragraph entries-one', {
            'test_document_text': textwrap.dedent("""\
                #####################
                Felis gravida lacinia
                #####################

                Tempus lorem aliquet
                ####################

                Maecenas feugiat nibh sed enim fringilla faucibus.


                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.
                """),
            # Docutils treats a lone top-level section with lone subsection
            # specially: their titles are “lifted up to be the document's
            # (sub)title”.
            # <URL:https://docutils.sourceforge.io/docs/user/rst/quickref.html>
            # Therefore the subsequent section is the top-level `section`.
            'expected_document_title_text': "Felis gravida lacinia",
            'expected_document_subtitle_text': "Tempus lorem aliquet",
            'expected_sections_title_text': [
                "Version 1.0",
            ],
            'expected_versions_text': [
                "1.0",
            ],
        }),
        ('document-title-and-subtitle preamble-paragraph entries-three', {
            'test_document_text': textwrap.dedent("""\
                #####################
                Felis gravida lacinia
                #####################

                Tempus lorem aliquet
                ####################

                Maecenas feugiat nibh sed enim fringilla faucibus.


                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>

                * Pellentesque elementum mollis finibus.
                """),
            # Docutils treats a lone top-level section with lone subsection
            # specially: their titles are “lifted up to be the document's
            # (sub)title”.
            # <URL:https://docutils.sourceforge.io/docs/user/rst/quickref.html>
            # Therefore the subsequent sections are the top-level `section`s.
            'expected_document_title_text': "Felis gravida lacinia",
            'expected_document_subtitle_text': "Tempus lorem aliquet",
            'expected_sections_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
        }),
    ]
    return scenarios


def make_error_rest_document_test_scenarios():
    """ Make a sequence of scenarios for testing errors for reST documents.

        :return: Sequence of tuples `(name, parameters)`. Each is a scenario
            as specified for `testscenarios`.
        """
    scenarios = [
        ('not-a-node', {
            'test_args': [object()],
            'expected_error': TypeError,
        }),
        ('not-a-document-root', {
            'test_args': [docutils.nodes.container(
                "imperdiet malesuada finibus",
                docutils.nodes.title("sagittis tincidunt"),
                docutils.nodes.subtitle("euismod erat viverra"),
                docutils.nodes.section("euismod eu nunc"),
                docutils.nodes.section("viverra consectetur ante"),
            )],
            'expected_error': TypeError,
        }),
    ]
    return scenarios


class get_document_title_text_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_document_title_text’ function. """

    function_to_test = staticmethod(chug.parsers.rest.get_document_title_text)

    scenarios = make_rest_document_test_scenarios()

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)

        self.test_args = [self.test_document]

    def test_result_is_expected_title_text(self):
        """ Should return the expected text of document's `title`. """
        result = self.function_to_test(*self.test_args)
        self.assertEqual(self.expected_document_title_text, result)


class get_document_title_text_ErrorTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Error test cases for ‘get_document_title_text’ function. """

    function_to_test = staticmethod(chug.parsers.rest.get_document_title_text)

    scenarios = make_error_rest_document_test_scenarios()

    def test_raises_expected_error(self):
        """ Should raise the `expected_error` type. """
        with testtools.ExpectedException(self.expected_error):
            __ = self.function_to_test(*self.test_args)


class get_document_subtitle_text_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_document_subtitle_text’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_document_subtitle_text)

    scenarios = make_rest_document_test_scenarios()

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)

        self.test_args = [self.test_document]

    def test_result_is_expected_document_subtitle_text(self):
        """ Should return the expected text of document's `subtitle`. """
        result = self.function_to_test(*self.test_args)
        self.assertEqual(self.expected_document_subtitle_text, result)


class get_document_subtitle_text_ErrorTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Error test cases for ‘get_document_subtitle_text’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_document_subtitle_text)

    scenarios = make_error_rest_document_test_scenarios()

    def test_raises_expected_error(self):
        """ Should raise the `expected_error` type. """
        with testtools.ExpectedException(self.expected_error):
            __ = self.function_to_test(*self.test_args)


class get_top_level_sections_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_top_level_sections’ function. """

    function_to_test = staticmethod(chug.parsers.rest.get_top_level_sections)

    scenarios = make_rest_document_test_scenarios()

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)

        self.test_args = [self.test_document]

    def test_returns_section_nodes(self):
        """ Should return a sequence of `section` iff we expect any. """
        result = self.function_to_test(*self.test_args)
        expected_type = docutils.nodes.section
        self.assertTrue(
            all(isinstance(item, expected_type) for item in result))

    def test_result_sections_have_expected_title_child_text(self):
        """
        Should return a sequence of `section`s with expected `title` node text.
        """
        result = self.function_to_test(*self.test_args)
        result_list = list(result)
        result_sequence_title = (
            next(
                node for node in section.children
                if isinstance(node, docutils.nodes.title)
            )
            for section in result_list)
        result_sequence_title_child_text = (
            (next(iter(title.children)))
            for title in result_sequence_title)
        self.assertEqual(
            list(self.expected_sections_title_text),
            list(result_sequence_title_child_text))


class get_top_level_sections_ErrorTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Error test cases for ‘get_top_level_sections’ function. """

    function_to_test = staticmethod(chug.parsers.rest.get_top_level_sections)

    scenarios = make_error_rest_document_test_scenarios()

    def test_raises_expected_error(self):
        """ Should raise the `expected_error` type. """
        with testtools.ExpectedException(self.expected_error):
            __ = self.function_to_test(*self.test_args)


class get_version_text_from_changelog_entry_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_version_text_from_changelog_entry’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_version_text_from_changelog_entry)

    scenarios = make_rest_document_test_scenarios()

    def test_returns_expected_result(self):
        """ Should return expected result. """
        test_document = docutils.core.publish_doctree(
            self.test_document_text)
        changelog_entry_nodes = chug.parsers.rest.get_top_level_sections(
            test_document)
        for (entry_node, expected_version_text) in (zip(
                changelog_entry_nodes,
                self.expected_versions_text)):
            with self.subTest(expected_version_text=expected_version_text):
                test_args = [entry_node]
                result = self.function_to_test(*test_args)
            self.assertEqual(expected_version_text, result)


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
