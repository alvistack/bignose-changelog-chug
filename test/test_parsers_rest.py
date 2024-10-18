# test/test_parsers_rest.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Test cases for ‘chug.parsers.rest’ module. """

import itertools
import textwrap
import unittest.mock

import docutils.core
import docutils.nodes
import docutils.utils
import semver
import testscenarios
import testtools

import chug.model
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
        """ Should return expected result or raise expected error. """
        expected_result = self.fake_document_node
        with make_expected_error_context(self):
            result = self.function_to_test(*self.test_args)
            self.assertEqual(expected_result, result)


class verify_is_docutils_node_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘verify_is_docutils_node’ function. """

    function_to_test = staticmethod(chug.parsers.rest.verify_is_docutils_node)

    scenarios = [
        ('arbitrary-node', {
            'test_args': [docutils.nodes.Element()],
            'test_kwargs': {},
            'expected_result': None,
        }),
        ('arbitrary-node node-type-title', {
            'test_args': [docutils.nodes.Element()],
            'test_kwargs': {
                'node_type': docutils.nodes.title,
            },
            'expected_error': TypeError,
            'expected_error_message_regex': ".+ Docutils node of type ‘title’",
        }),
        ('paragraph-node', {
            'test_args': [docutils.nodes.paragraph("")],
            'test_kwargs': {},
            'expected_result': None,
        }),
        ('paragraph-node node-type-paragraph', {
            'test_args': [docutils.nodes.paragraph("")],
            'test_kwargs': {
                'node_type': docutils.nodes.paragraph,
            },
            'expected_result': None,
        }),
        ('paragraph-node node-type-title', {
            'test_args': [docutils.nodes.paragraph("")],
            'test_kwargs': {
                'node_type': docutils.nodes.title,
            },
            'expected_error': TypeError,
            'expected_error_message_regex': ".+ Docutils node of type ‘title’",
        }),
        ('paragraph-node node-types-section-or-document', {
            'test_args': [docutils.nodes.paragraph("")],
            'test_kwargs': {
                'node_type': (docutils.nodes.section, docutils.nodes.document),
            },
            'expected_error': TypeError,
            'expected_error_message_regex': (
                r".+ Docutils node of type \(‘section’, ‘document’\)"),
        }),
        ('document-node', {
            'test_args': [
                docutils.nodes.document(settings=None, reporter=None)],
            'test_kwargs': {},
            'expected_result': None,
        }),
        ('document-node node-type-document', {
            'test_args': [
                docutils.nodes.document(settings=None, reporter=None)],
            'test_kwargs': {
                'node_type': docutils.nodes.document,
            },
            'expected_result': None,
        }),
        ('document-node node-type-title', {
            'test_args': [
                docutils.nodes.document(settings=None, reporter=None)],
            'test_kwargs': {
                'node_type': docutils.nodes.title,
            },
            'expected_error': TypeError,
            'expected_error_message_regex': ".+ Docutils node of type ‘title’",
        }),
        ('not-a-node', {
            'test_args': [object()],
            'test_kwargs': {},
            'expected_error': TypeError,
            'expected_error_message_regex': ".+ Docutils node",
        }),
        ('not-a-node node-type-title', {
            'test_args': [object()],
            'test_kwargs': {
                'node_type': docutils.nodes.title,
            },
            'expected_error': TypeError,
            'expected_error_message_regex': ".+ Docutils node of type ‘title’",
        }),
    ]

    def test_returns_expected_result_or_raises_expected_error(self):
        """ Should return expected result or raise expected error. """
        with make_expected_error_context(self):
            result = self.function_to_test(*self.test_args, **self.test_kwargs)
        if hasattr(self, 'expected_result'):
            self.assertEqual(self.expected_result, result)


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
        ('node-without-text', {
            'test_args': [docutils.nodes.decoration()],
            'expected_error': ValueError,
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
            'expected_error': ValueError,
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
            'expected_document_subtitle_text_error': ValueError,
            'expected_sections_title_text': [],
            'expected_changelog_entries_node_id': [
                "version-1-0",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <document
                        ids="version-1-0" names="version\\ 1.0"
                        source="<string>" title="Version 1.0">
                    <title>
                        Version 1.0
                    <docinfo>
                        <field classes="released">
                            <field_name>
                                Released
                            <field_body>
                                <paragraph>
                                    2009-01-01
                        <field classes="maintainer">
                            <field_name>
                                Maintainer
                            <field_body>
                                <paragraph>
                                    Foo Bar <
                                    <reference
                                    refuri="mailto:foo.bar@example.org">
                                        foo.bar@example.org
                                    >
                    <bullet_list bullet="*">
                        <list_item>
                            <paragraph>
                                Lorem ipsum dolor sit amet.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
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
            'expected_document_title_text_error': ValueError,
            'expected_document_subtitle_text_error': ValueError,
            'expected_sections_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_changelog_entries_node_id': [
                "version-1-0",
                "version-0-8",
                "version-0-7-2",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <section ids="version-1-0" names="version\\ 1.0">
                        <title>
                            Version 1.0
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-8" names="version\\ 0.8">
                        <title>
                            version 0.8
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2004-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Donec venenatis nisl aliquam ipsum.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-7-2" names="version\\ 0.7.2">
                        <title>
                            Version 0.7.2
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2001-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Pellentesque elementum mollis finibus.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2004-01-01",
                    version="0.8",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Donec venenatis nisl aliquam ipsum.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2001-01-01",
                    version="0.7.2",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Pellentesque elementum mollis finibus.",
                ),
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
            'expected_document_title_text_error': ValueError,
            'expected_document_subtitle_text_error': ValueError,
            'expected_sections_title_text': [
                "Version 1.0",
            ],
            'expected_changelog_entries_node_id': [
                "version-1-0",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <section ids="version-1-0" names="version\\ 1.0">
                        <title>
                            Version 1.0
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
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
            'expected_document_title_text_error': ValueError,
            'expected_document_subtitle_text_error': ValueError,
            'expected_sections_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_changelog_entries_node_id': [
                "version-1-0",
                "version-0-8",
                "version-0-7-2",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <section ids="version-1-0" names="version\\ 1.0">
                        <title>
                            Version 1.0
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-8" names="version\\ 0.8">
                        <title>
                            version 0.8
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2004-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Donec venenatis nisl aliquam ipsum.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-7-2" names="version\\ 0.7.2">
                        <title>
                            Version 0.7.2
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2001-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Pellentesque elementum mollis finibus.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2004-01-01",
                    version="0.8",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Donec venenatis nisl aliquam ipsum.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2001-01-01",
                    version="0.7.2",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Pellentesque elementum mollis finibus.",
                ),
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
            'expected_changelog_entries_node_id': [
                "version-1-0",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <document
                            ids="felis-gravida-lacinia"
                            names="felis\\ gravida\\ lacinia"
                            source="<string>"
                            title="Felis gravida lacinia">
                        <title>
                            Felis gravida lacinia
                        <subtitle ids="version-1-0" names="version\\ 1.0">
                            Version 1.0
                        <docinfo>
                            <field classes="released">
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field classes="maintainer">
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
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
            'expected_document_subtitle_text_error': ValueError,
            'expected_sections_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_changelog_entries_node_id': [
                "version-1-0",
                "version-0-8",
                "version-0-7-2",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <section ids="version-1-0" names="version\\ 1.0">
                        <title>
                            Version 1.0
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-8" names="version\\ 0.8">
                        <title>
                            version 0.8
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2004-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Donec venenatis nisl aliquam ipsum.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-7-2" names="version\\ 0.7.2">
                        <title>
                            Version 0.7.2
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2001-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Pellentesque elementum mollis finibus.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2004-01-01",
                    version="0.8",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Donec venenatis nisl aliquam ipsum.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2001-01-01",
                    version="0.7.2",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Pellentesque elementum mollis finibus.",
                ),
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
            'expected_document_subtitle_text_error': ValueError,
            'expected_sections_title_text': [
                "Version 1.0",
            ],
            'expected_changelog_entries_node_id': [
                "version-1-0",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <section ids="version-1-0" names="version\\ 1.0">
                        <title>
                            Version 1.0
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
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
            'expected_document_subtitle_text_error': ValueError,
            'expected_sections_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_changelog_entries_node_id': [
                "version-1-0",
                "version-0-8",
                "version-0-7-2",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <section ids="version-1-0" names="version\\ 1.0">
                        <title>
                            Version 1.0
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-8" names="version\\ 0.8">
                        <title>
                            version 0.8
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2004-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Donec venenatis nisl aliquam ipsum.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-7-2" names="version\\ 0.7.2">
                        <title>
                            Version 0.7.2
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2001-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Pellentesque elementum mollis finibus.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2004-01-01",
                    version="0.8",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Donec venenatis nisl aliquam ipsum.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2001-01-01",
                    version="0.7.2",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Pellentesque elementum mollis finibus.",
                ),
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
            'expected_document_subtitle_text_error': ValueError,
            'expected_sections_title_text': [
                "Tempus lorem aliquet",
            ],
            'expected_changelog_entries_node_id': [
                "felis-gravida-lacinia",
            ],
            'expected_changelog_entries_title_text': [
                "Felis gravida lacinia",
            ],
            'expected_error': ValueError,
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
            'expected_document_subtitle_text_error': ValueError,
            'expected_sections_title_text': [
                "Tempus lorem aliquet",
            ],
            'expected_changelog_entries_node_id': [
                "felis-gravida-lacinia",
            ],
            'expected_changelog_entries_title_text': [
                "Felis gravida lacinia",
            ],
            'expected_error': ValueError,
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
            'expected_changelog_entries_node_id': [
                "version-1-0",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <section ids="version-1-0" names="version\\ 1.0">
                        <title>
                            Version 1.0
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
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
            'expected_changelog_entries_node_id': [
                "version-1-0",
                "version-0-8",
                "version-0-7-2",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <section ids="version-1-0" names="version\\ 1.0">
                        <title>
                            Version 1.0
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-8" names="version\\ 0.8">
                        <title>
                            version 0.8
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2004-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Donec venenatis nisl aliquam ipsum.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-7-2" names="version\\ 0.7.2">
                        <title>
                            Version 0.7.2
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2001-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Pellentesque elementum mollis finibus.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2004-01-01",
                    version="0.8",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Donec venenatis nisl aliquam ipsum.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2001-01-01",
                    version="0.7.2",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Pellentesque elementum mollis finibus.",
                ),
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
            'expected_changelog_entries_node_id': [
                "version-1-0",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <section ids="version-1-0" names="version\\ 1.0">
                        <title>
                            Version 1.0
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
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
            'expected_changelog_entries_node_id': [
                "version-1-0",
                "version-0-8",
                "version-0-7-2",
            ],
            'expected_changelog_entries_title_text': [
                "Version 1.0",
                "version 0.8",
                "Version 0.7.2",
            ],
            'expected_changelog_entries_pformat': [
                textwrap.dedent("""\
                    <section ids="version-1-0" names="version\\ 1.0">
                        <title>
                            Version 1.0
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2009-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Lorem ipsum dolor sit amet.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-8" names="version\\ 0.8">
                        <title>
                            version 0.8
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2004-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Donec venenatis nisl aliquam ipsum.
                    """),
                textwrap.dedent("""\
                    <section ids="version-0-7-2" names="version\\ 0.7.2">
                        <title>
                            Version 0.7.2
                        <field_list>
                            <field>
                                <field_name>
                                    Released
                                <field_body>
                                    <paragraph>
                                        2001-01-01
                            <field>
                                <field_name>
                                    Maintainer
                                <field_body>
                                    <paragraph>
                                        Foo Bar <
                                        <reference
                                        refuri="mailto:foo.bar@example.org">
                                            foo.bar@example.org
                                        >
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Pellentesque elementum mollis finibus.
                    """),
            ],
            'expected_versions_text': [
                "1.0",
                "0.8",
                "0.7.2",
            ],
            'expected_change_log_entries': [
                chug.model.ChangeLogEntry(
                    release_date="2009-01-01",
                    version="1.0",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Lorem ipsum dolor sit amet.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2004-01-01",
                    version="0.8",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Donec venenatis nisl aliquam ipsum.",
                ),
                chug.model.ChangeLogEntry(
                    release_date="2001-01-01",
                    version="0.7.2",
                    maintainer="Foo Bar <foo.bar@example.org>",
                    body="Pellentesque elementum mollis finibus.",
                ),
            ],
        }),
    ]

    for (__, scenario) in scenarios:
        if 'expected_versions_text' in scenario:
            scenario['expected_versions'] = [
                semver.Version.parse(
                    version_text, optional_minor_and_patch=True)
                for version_text in scenario['expected_versions_text']
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
        """
        Should return the expected text of document's `title`, or raise error.
        """
        with make_expected_error_context(
                self,
                expected_error_attr_name='expected_document_title_text_error',
                expected_error_message_regex_attr_name=(
                    'expected_document_title_text_error_regex')
        ):
            result = self.function_to_test(*self.test_args)
        if hasattr(self, 'expected_document_title_text'):
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
        """
        Should return the expected text of document's `subtitle`, or error.
        """
        with make_expected_error_context(
                self,
                expected_error_attr_name=(
                    'expected_document_subtitle_text_error'),
                expected_error_message_regex_attr_name=(
                    'expected_document_subtitle_text_error_regex')
        ):
            result = self.function_to_test(*self.test_args)
        if hasattr(self, 'expected_document_subtitle_text'):
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

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)

    def test_returns_expected_result(self):
        """ Should return expected result. """
        if not hasattr(self, 'expected_versions_text'):
            self.skipTest("no result expected")
        self.expected_version_text_by_node_id = dict(zip(
            self.expected_changelog_entries_node_id,
            self.expected_versions_text,
            strict=True,
        ))
        self.test_entry_node_by_node_id = make_entry_node_by_node_id(
            self.test_document,
            node_ids=self.expected_version_text_by_node_id.keys())
        for (
                test_node_id,
                test_entry_node
        ) in self.test_entry_node_by_node_id.items():
            expected_version_text = self.expected_version_text_by_node_id[
                test_node_id]
            with self.subTest(
                    node_id=test_node_id,
                    expected_version_text=expected_version_text,
            ):
                test_args = [test_entry_node]
                result = self.function_to_test(*test_args)
            self.assertEqual(expected_version_text, result)


def has_matching_node_id(node, node_id):
    """ Return ``True`` iff `node` attribute 'ids' matches `node_id`.

        :param node: The `docutils.nodes.Node` to query.
        :param node_id: The node identifier (text) to match.
        :return: ``True`` iff the `node_id` is in the 'ids' node attribute,
            otherwise ``False``.
        """
    node_ids_value = node.get('ids')
    result = bool(node_ids_value and (node_id in node_ids_value))
    return result


def get_nodes_matching_node_id(nodes, node_id):
    """ Get the nodes from `nodes` with identifier matching `node_id`.

        :param nodes: The collection of `docutils.nodes.Node` to query.
        :param node_id: The node identifier (text) to match.
        :return: Sequence of nodes whose 'ids' attribute contains a match for
            `node_id`.
        :raises ValueError: If no child node matches `node_id`.
        """
    matching_nodes = [
        node for node in nodes
        if has_matching_node_id(node, node_id)]
    if not matching_nodes:
        raise ValueError(
            "no match for {node_id!r} in {nodes!r}".format(
                nodes=nodes, node_id=node_id))
    return matching_nodes


def make_entry_node_by_node_id(rest_document, *, node_ids):
    """ Make a mapping of Change Log entry nodes by identifier.

        :param rest_document: Document root, as a `docutils.nodes.document`
            instance.
        :param node_ids: Sequence of identifiers to match nodes in
            `rest_document`.
        :return: A mapping `{node_id: entry_node}` for each item in `node_ids`,
            where `entry_node` is the Change Log entry node found in
            `rest_document`.
        """
    entry_node_by_node_id = dict()
    for node_id in node_ids:
        for candidate_node in get_nodes_matching_node_id(
                nodes=itertools.chain(
                    [rest_document],
                    rest_document.children),
                node_id=node_id
        ):
            entry_node = (
                candidate_node.parent if isinstance(
                    candidate_node, docutils.nodes.subtitle)
                else candidate_node)
            entry_node_by_node_id[node_id] = entry_node
    return entry_node_by_node_id


class get_changelog_entry_title_from_node_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_version_text_from_changelog_entry’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_changelog_entry_title_from_node)

    scenarios = make_rest_document_test_scenarios()

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)
        self.expected_title_by_node_id = dict(zip(
            self.expected_changelog_entries_node_id,
            self.expected_changelog_entries_title_text,
            strict=True,
        ))
        self.test_entry_node_by_node_id = make_entry_node_by_node_id(
            self.test_document,
            node_ids=self.expected_title_by_node_id.keys())

    def test_returns_expected_result_or_raises_expected_error(self):
        """ Should return expected result or raise expected error. """
        for (
                test_node_id,
                test_entry_node
        ) in self.test_entry_node_by_node_id.items():
            with self.subTest(node_id=test_node_id):
                test_args = [test_entry_node]
                with make_expected_error_context(self):
                    result = self.function_to_test(*test_args)
                if not hasattr(self, 'expected_error'):
                    expected_result = self.expected_title_by_node_id[
                        test_node_id]
                    self.assertEqual(expected_result, result)


def normalise_whitespace_to_single_space(text):
    """ Return normalised rendition of `text` with single space.

        :param text: The text value to normalise.
        :return: The normalised text.

        The rendition replaces each sequence of characters matching '[\n\t ]+'
        with a single U+0020 SPACE.
        """
    normalised_text = " ".join((
        text.replace("\n", " ").replace("\t", " ")
    ).split())
    return normalised_text


class DoctreePformatEqual(testtools.matchers.Matcher):
    """ A matcher to compare the value of Docutils node ‘pformat’ output. """

    def __init__(self, expected):
        self.expected_value = expected
        self.expected_value_normalised = normalise_whitespace_to_single_space(
            self.expected_value)

    def match(self, value):
        """ Assert the pformat output `value` matches the `expected_value`. """
        result = None
        value_normalised = normalise_whitespace_to_single_space(value)
        if value_normalised != self.expected_value_normalised:
            result = DoctreePformatValueMismatch(self.expected_value, value)
        return result


class DoctreePformatValueMismatch(testtools.matchers.Mismatch):
    """ The specified ‘pformat’ output does not match the expected value. """

    def __init__(self, expected, actual):
        self.expected_value = expected
        self.actual_value = actual

    def describe(self):
        """ Emit a text description of this mismatch. """
        text = textwrap.dedent("""\

            reference: {expected}
            actual: {actual}
            """).format(
                expected=self.expected_value, actual=self.actual_value)
        return text


class get_changelog_entry_nodes_from_document_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_changelog_entry_nodes_from_document’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_changelog_entry_nodes_from_document)

    scenarios = make_rest_document_test_scenarios()

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)
        self.test_args = [self.test_document]

    @staticmethod
    def normalise_whitespace_to_single_space(text):
        """ Return normalised rendition of `text` with single space.

            :param text: The text value to normalise.
            :return: The normalised text.

            The rendition replaces each sequence of characters matching
            '[\n\t ]+' with a single U+0020 SPACE.
            """
        normalised_text = " ".join((
            text.replace("\n", " ").replace("\t", " ")
        ).split())
        return normalised_text

    def test_returns_nodes_with_expected_node_ids(self):
        """ Should return nodes values with expected 'ids' node attributes. """
        with make_expected_error_context(self):
            result = self.function_to_test(*self.test_args)
        if hasattr(self, 'expected_changelog_entries_pformat'):
            for (expected_pformat, node) in zip(
                    self.expected_changelog_entries_pformat,
                    result,
                    strict=True,
            ):
                self.assertThat(
                    node.pformat(), DoctreePformatEqual(expected_pformat))


def make_changelog_entry_node_scenarios():
    """ Make a sequence of scenarios for testing Change Log entry nodes.

        :return: Sequence of tuples `(name, parameters)`. Each is a scenario
            as specified for `testscenarios`.
        """
    rest_document_scenarios = make_rest_document_test_scenarios()
    scenario_extra_params_by_scenario_name = {
        'entries-one': {
            'test_change_log_entry_node_id': "version-1-0",
            'expected_field_list_pformat': textwrap.dedent("""\
                <docinfo>
                    <field classes="released">
                        <field_name>
                            Released
                        <field_body>
                            <paragraph>
                                2009-01-01
                    <field classes="maintainer">
                        <field_name>
                            Maintainer
                        <field_body>
                            <paragraph>
                                Foo Bar <
                                <reference refuri="mailto:foo.bar@example.org">
                                    foo.bar@example.org
                                >
                """),
            'expected_change_log_entry': chug.model.ChangeLogEntry(
                version="1.0",
                release_date="2009-01-01",
                maintainer="Foo Bar <foo.bar@example.org>",
                body="Lorem ipsum dolor sit amet.",
            ),
        },
        'entries-three': {
            'test_change_log_entry_node_id': "version-0-7-2",
            'expected_field_list_pformat': textwrap.dedent("""\
                <field_list>
                    <field>
                        <field_name>
                            Released
                        <field_body>
                            <paragraph>
                                2001-01-01
                    <field>
                        <field_name>
                            Maintainer
                        <field_body>
                            <paragraph>
                                Foo Bar <
                                <reference refuri="mailto:foo.bar@example.org">
                                    foo.bar@example.org
                                >
                """),
            'expected_change_log_entry': chug.model.ChangeLogEntry(
                version="0.7.2",
                release_date="2001-01-01",
                maintainer="Foo Bar <foo.bar@example.org>",
                body="Pellentesque elementum mollis finibus.",
            ),
        },
    }
    scenarios = [
        (scenario_name, dict(
            test_document_text=scenario['test_document_text'],
            **(scenario_extra_params_by_scenario_name[scenario_name])
        ))
        for (scenario_name, scenario) in rest_document_scenarios
        if scenario_name in scenario_extra_params_by_scenario_name
    ]
    return scenarios


def get_node_from_document_by_node_id(rest_document, *, node_id):
    """ Get the node matching `node_id` `rest_document`.

        :param rest_document: Document root, as a `docutils.nodes.document`
            instance.
        :param node_id: The identifier to match with the target node's 'ids'
            attribute.
        :return: The `docutils.nodes.Node` matching the query.
        :raises ValueError: If no candidate node matches `node_id`.

        Candidate nodes are: the document node itself, and all its immediate
        child nodes.
        """
    candidate_nodes = itertools.chain(
        [rest_document],
        rest_document.children)
    matching_nodes = get_nodes_matching_node_id(
        candidate_nodes, node_id=node_id)
    result = next(iter(matching_nodes))
    return result


class get_field_list_from_entry_node_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_field_list_from_entry_node’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_field_list_from_entry_node)

    scenarios = make_changelog_entry_node_scenarios()

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)
        self.test_change_log_entry_node = get_node_from_document_by_node_id(
            self.test_document, node_id=self.test_change_log_entry_node_id)
        self.test_args = [self.test_change_log_entry_node]

    def test_returns_expected_result(self):
        """ Should return expected result. """
        result = self.function_to_test(*self.test_args)
        self.assertThat(
            result.pformat(),
            DoctreePformatEqual(self.expected_field_list_pformat))


class get_field_list_from_entry_node_ErrorTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Error test cases for ‘get_field_list_from_entry_node’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_field_list_from_entry_node)

    scenarios = [
        ('not-a-node', {
            'test_document': object(),
            'expected_error': TypeError,
        }),
        ('empty', {
            'test_document': docutils.core.publish_doctree(""),
            'expected_error': ValueError,
        }),
        ('document-title section-no-field-list', {
            'test_document': docutils.core.publish_doctree(
                textwrap.dedent("""\
                    Felis gravida lacinia
                    #####################

                    Maecenas feugiat nibh sed enim fringilla faucibus.
                    """),
            ),
            'expected_error': ValueError,
        }),
        ('document-title docinfo-table section-no-field-list', {
            'test_document': docutils.core.publish_doctree(
                textwrap.dedent("""\
                    Felis gravida lacinia
                    #####################

                    :Published: 2009-01-01
                    :License: AGPL-3+

                    Maecenas feugiat nibh sed enim fringilla faucibus.

                    Version 1.0
                    ===========

                    * Lorem ipsum dolor sit amet.
                    """),
            ),
            'test_change_log_entry_node_id': "version-1-0",
            'expected_error': ValueError,
        }),
    ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_change_log_entry_node = (
            get_node_from_document_by_node_id(
                self.test_document, node_id=self.test_change_log_entry_node_id)
            if hasattr(self, 'test_change_log_entry_node_id')
            else self.test_document)
        self.test_args = [self.test_change_log_entry_node]

    def test_raises_expected_error(self):
        """ Should raise expected error. """
        with make_expected_error_context(self):
            __ = self.function_to_test(*self.test_args)


class get_field_body_for_name_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_field_body_for_name’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_field_body_for_name)

    scenarios = [
        ('entries-one fields-three first-field', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Lorem ipsum dolor sit amet.
                """),
            'test_change_log_entry_node_id': "version-1-0",
            'test_field_name': "released",
            'expected_result_pformat': textwrap.dedent("""\
                <field_body>
                    <paragraph>
                        2009-01-01
                """),
        }),
        ('entries-one fields-three second-field', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Lorem ipsum dolor sit amet.
                """),
            'test_change_log_entry_node_id': "version-1-0",
            'test_field_name': "maintainer",
            'expected_result_pformat': textwrap.dedent("""\
                <field_body>
                    <paragraph>
                        Foo Bar <
                        <reference refuri="mailto:foo.bar@example.org">
                            foo.bar@example.org
                        >
                """),
        }),
        ('entries-three fields-three first-field', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Pellentesque elementum mollis finibus.
                """),
            'test_change_log_entry_node_id': "version-0-7-2",
            'test_field_name': "released",
            'expected_result_pformat': textwrap.dedent("""\
                <field_body>
                    <paragraph>
                        2001-01-01
                """),
        }),
        ('entries-three fields-three second-field', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Meep Morp <meep.morp@example.org>
                :License: AGPL-3+

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Zang Warx <zang.warx@example.org>
                :License: AGPL-3+

                * Pellentesque elementum mollis finibus.
                """),
            'test_change_log_entry_node_id': "version-0-7-2",
            'test_field_name': "maintainer",
            'expected_result_pformat': textwrap.dedent("""\
                <field_body>
                    <paragraph>
                        Zang Warx <
                        <reference refuri="mailto:zang.warx@example.org">
                            zang.warx@example.org
                        >
                """),
        }),
    ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)
        self.test_change_log_entry_node = get_node_from_document_by_node_id(
            self.test_document, node_id=self.test_change_log_entry_node_id)
        self.test_field_list_node = next(iter(
            child_node
            for child_node in self.test_change_log_entry_node.children
            if isinstance(child_node, (
                    docutils.nodes.docinfo,
                    docutils.nodes.field_list))
        ))
        self.test_args = [self.test_field_list_node, self.test_field_name]

    def test_returns_expected_result(self):
        """ Should return expected result. """
        result = self.function_to_test(*self.test_args)
        self.assertEqual(self.expected_result_pformat, result.pformat())


class get_field_body_for_name_ErrorTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Error test cases for ‘get_field_body_for_name’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_field_body_for_name)

    scenarios = [
        ('not-a-node', {
            'test_field_list_node': object(),
            'test_field_name': "b0gUs",
            'expected_error': TypeError,
        }),
        ('not-a-field-list-node', {
            'test_field_list_node': docutils.nodes.paragraph(),
            'test_field_name': "b0gUs",
            'expected_error': TypeError,
        }),
        ('empty', {
            'test_field_list_node': docutils.nodes.field_list(),
            'test_field_name': "b0gUs",
            'expected_error': KeyError,
        }),
    ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_args = [self.test_field_list_node, self.test_field_name]

    def test_raises_expected_error(self):
        """ Should raise expected error. """
        with make_expected_error_context(self):
            __ = self.function_to_test(*self.test_args)


class get_body_text_from_entry_node_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘get_body_text_from_entry_node’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_body_text_from_entry_node)

    scenarios = [
        ('entries-one paragraphs-one', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Lorem ipsum dolor sit amet.
                """),
            'test_change_log_entry_node_id': "version-1-0",
            'expected_result': "Lorem ipsum dolor sit amet.",
        }),
        ('entries-one paragraphs-three', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                Sed rhoncus fermentum dui.

                * Quisque at est tincidunt, lobortis mi sit amet,
                  lacinia sapien.

                * Lorem ipsum dolor sit amet.
                """),
            'test_change_log_entry_node_id': "version-1-0",
            'expected_result': textwrap.dedent("""\
                Sed rhoncus fermentum dui.

                Quisque at est tincidunt, lobortis mi sit amet,
                lacinia sapien.

                Lorem ipsum dolor sit amet."""),
        }),
        ('entries-three paragraphs-one', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Pellentesque elementum mollis finibus.
                """),
            'test_change_log_entry_node_id': "version-0-7-2",
            'expected_result': "Pellentesque elementum mollis finibus.",
        }),
        ('entries-three paragraphs-three', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+

                * Lorem ipsum dolor sit amet.


                version 0.8
                ===========

                :Released: 2004-01-01
                :Maintainer: Meep Morp <meep.morp@example.org>
                :License: AGPL-3+

                * Donec venenatis nisl aliquam ipsum.


                Version 0.7.2
                =============

                :Released: 2001-01-01
                :Maintainer: Zang Warx <zang.warx@example.org>
                :License: AGPL-3+

                Maecenas sodales posuere justo, eu rhoncus leo fringilla sit
                amet.

                * Nulla purus dui, lacinia ultrices bibendum sit amet,
                  pulvinar vel velit.

                * Pellentesque elementum mollis finibus.
                """),
            'test_change_log_entry_node_id': "version-0-7-2",
            'expected_result': textwrap.dedent("""\
                Maecenas sodales posuere justo, eu rhoncus leo fringilla sit
                amet.

                Nulla purus dui, lacinia ultrices bibendum sit amet,
                pulvinar vel velit.

                Pellentesque elementum mollis finibus."""),
        }),
        ('empty', {
            'test_document_text': "",
            'expected_result': "",
        }),
        ('entries-one paragraphs-none', {
            'test_document_text': textwrap.dedent("""\
                Version 1.0
                ===========

                :Released: 2009-01-01
                :Maintainer: Foo Bar <foo.bar@example.org>
                :License: AGPL-3+
                """),
            'test_change_log_entry_node_id': "version-1-0",
            'expected_result': "",
        }),
    ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)
        self.test_change_log_entry_node = (
            get_node_from_document_by_node_id(
                self.test_document, node_id=self.test_change_log_entry_node_id)
            if hasattr(self, 'test_change_log_entry_node_id')
            else self.test_document)
        self.test_args = [self.test_change_log_entry_node]

    def test_returns_expected_result(self):
        """ Should return expected result. """
        result = self.function_to_test(*self.test_args)
        self.assertEqual(self.expected_result, result)


class get_body_text_from_entry_node_ErrorTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Error test cases for ‘get_body_text_from_entry_node’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.get_body_text_from_entry_node)

    scenarios = [
        ('not-a-node', {
            'test_document': object(),
            'expected_error': TypeError,
        }),
    ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_change_log_entry_node = (
            get_node_from_document_by_node_id(
                self.test_document, node_id=self.test_change_log_entry_node_id)
            if hasattr(self, 'test_change_log_entry_node_id')
            else self.test_document)
        self.test_args = [self.test_change_log_entry_node]

    def test_raises_expected_error(self):
        """ Should raise expected error. """
        with make_expected_error_context(self):
            __ = self.function_to_test(*self.test_args)


class make_change_log_entry_from_node_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘make_change_log_entry_from_node’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.make_change_log_entry_from_node)

    scenarios = make_changelog_entry_node_scenarios()

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)
        self.test_change_log_entry_node = get_node_from_document_by_node_id(
            self.test_document, node_id=self.test_change_log_entry_node_id)
        self.test_args = [self.test_change_log_entry_node]

    def test_returns_expected_result(self):
        """ Should return expected result. """
        result = self.function_to_test(*self.test_args)
        self.assertEqual(
            self.expected_change_log_entry.as_version_info_entry(),
            result.as_version_info_entry())


class make_change_log_entry_from_node_ErrorTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Error test cases for ‘make_change_log_entry_from_node’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.make_change_log_entry_from_node)

    scenarios = [
        ('not-a-node', {
            'test_document': object(),
            'expected_error': TypeError,
        }),
        ('empty', {
            'test_document': docutils.core.publish_doctree(""),
            'expected_error': ValueError,
        }),
        ('document-title section-no-field-list', {
            'test_document': docutils.core.publish_doctree(
                textwrap.dedent("""\
                    Felis gravida lacinia
                    #####################

                    Maecenas feugiat nibh sed enim fringilla faucibus.
                    """),
            ),
            'expected_error': ValueError,
        }),
        ('document-title docinfo-table section-no-field-list', {
            'test_document': docutils.core.publish_doctree(
                textwrap.dedent("""\
                    Felis gravida lacinia
                    #####################

                    :Published: 2009-01-01
                    :License: AGPL-3+

                    Maecenas feugiat nibh sed enim fringilla faucibus.

                    Version 1.0
                    ===========

                    * Lorem ipsum dolor sit amet.
                    """),
            ),
            'test_change_log_entry_node_id': "version-1-0",
            'expected_error': ValueError,
        }),
    ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        if hasattr(self, 'test_change_log_entry_node_id'):
            matching_entry_nodes = make_entry_node_by_node_id(
                self.test_document,
                node_ids=[self.test_change_log_entry_node_id])
            self.test_change_log_entry_node = matching_entry_nodes[
                self.test_change_log_entry_node_id]
        else:
            self.test_change_log_entry_node = self.test_document
        self.test_args = [self.test_change_log_entry_node]

    def test_raises_expected_error(self):
        """ Should raise expected error. """
        with make_expected_error_context(self):
            __ = self.function_to_test(*self.test_args)


class make_change_log_entries_from_document_TestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Test cases for ‘make_change_log_entries_from_document’ function. """

    function_to_test = staticmethod(
        chug.parsers.rest.make_change_log_entries_from_document)

    scenarios = make_rest_document_test_scenarios()

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_document = docutils.core.publish_doctree(
            self.test_document_text)
        self.test_args = [self.test_document]

    def test_returns_expected_result_or_raises_expected_error(self):
        """ Should return expected result or raise expected error. """
        with make_expected_error_context(self):
            result = self.function_to_test(*self.test_args)
        if hasattr(self, 'expected_change_log_entries'):
            for (expected_change_log_entry, result_item) in zip(
                    self.expected_change_log_entries,
                    result,
                    strict=True,
            ):
                self.assertEqual(
                    expected_change_log_entry.as_version_info_entry(),
                    result_item.as_version_info_entry())


class make_change_log_entries_from_document_ErrorTestCase(
        testscenarios.WithScenarios, testtools.TestCase):
    """ Error test cases for ‘make_change_log_entries_from_document’. """

    function_to_test = staticmethod(
        chug.parsers.rest.make_change_log_entries_from_document)

    scenarios = [
        ('not-a-node', {
            'test_document': object(),
            'expected_error': TypeError,
        }),
        ('empty', {
            'test_document': docutils.core.publish_doctree(""),
            'expected_error': ValueError,
        }),
        ('document-title section-no-field-list', {
            'test_document': docutils.core.publish_doctree(
                textwrap.dedent("""\
                    Felis gravida lacinia
                    #####################

                    Maecenas feugiat nibh sed enim fringilla faucibus.
                    """),
            ),
            'expected_error': ValueError,
        }),
        ('document-title docinfo-table section-no-field-list', {
            'test_document': docutils.core.publish_doctree(
                textwrap.dedent("""\
                    Felis gravida lacinia
                    #####################

                    :Published: 2009-01-01
                    :License: AGPL-3+

                    Maecenas feugiat nibh sed enim fringilla faucibus.

                    Version 1.0
                    ===========

                    * Lorem ipsum dolor sit amet.
                    """),
            ),
            'test_change_log_entry_node_id': "version-1-0",
            'expected_error': ValueError,
        }),
    ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_args = [self.test_document]

    def test_raises_expected_error(self):
        """ Should raise expected error. """
        with make_expected_error_context(self):
            __ = self.function_to_test(*self.test_args)


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
