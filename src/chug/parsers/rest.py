# src/chug/parsers/rest.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Parser features for reStructuredText documents. """

import docutils.core
import docutils.nodes

from . import core


def parse_rest_document_from_text(document_text):
    """ Get the document structure, parsed from `document_text`.

        :param document_text: Text of the document in reStructuredText format.
        :return: The Docutils document root node.
        :raises TypeError: If `document_text` is not a text string.
        """
    if not isinstance(document_text, str):
        raise TypeError("not a text string: {!r}".format(document_text))
    document = docutils.core.publish_doctree(document_text)
    return document


def verify_is_docutils_node(node, *, node_type=docutils.nodes.Node):
    """ Verify that `node` is a Docutils node of type `node_type`.

        :param node: The object to inspect.
        :param node_type: The Docutils node type, or a `tuple of types, for
            which to test.
        :return: ``None``.
        :raises TypeError: If `node` is not an instance of
            `docutils.nodes.Node`.
        """
    node_type_text = (
        "({})".format(", ".join(
            "‘{}’".format(item.__name__) for item in node_type))
        if isinstance(node_type, tuple)
        else "‘{}’".format(node_type.__name__))
    message = (
        # The caller did not specify anything more specific than `Node`.
        "not a Docutils node: {node!r}" if (node_type == docutils.nodes.Node)
        # Name the node type specified by the caller.
        else "not a Docutils node of type {type_text}: {node!r}"
    ).format(node=node, type_text=node_type_text)
    if not isinstance(node, node_type):
        raise TypeError(message)


def get_node_text(node):
    """ Get the child text of the `node`.

        :param node: The `docutils.nodes.Node` instance to query.
        :return: The child text of `node`.
        :raises TypeError: If the `node` is not a `docutils.nodes.Node`.
        :raises ValueError: If the `node` has no `Text` child node.
        """
    verify_is_docutils_node(node)
    node_text_children = [
        child_node for child_node in node.children
        if isinstance(child_node, docutils.nodes.Text)]
    if not node_text_children:
        raise ValueError(
            "node has no Text children: {!r}".format(node))
    result = next(iter(node_text_children))
    return result


def get_node_title_text(node):
    """ Get the `node`'s `title` node child text.

        :param rest_document: Document root, as a `docutils.nodes.document`
            instance.
        :return: The text of the `title` node.
        :raises TypeError: If the `node` is not a `docutils.nodes.Node`.
        :raises ValueError: If the `node` has no `title` child node.
        """
    verify_is_docutils_node(node)
    title_nodes = [
        child_node for child_node in node.children
        if isinstance(child_node, docutils.nodes.title)]
    if not title_nodes:
        raise ValueError(
            "node has no ‘title’ children: {!r}".format(node))
    title = next(iter(title_nodes))
    result = get_node_text(title)
    return result


def get_document_title_text(rest_document):
    """ Get the document's `title` node child text.

        :param rest_document: Document root, as a `docutils.nodes.document`
            instance.
        :return: The text of the document's `title` node.
        :raises TypeError: If the `rest_document` is not a
            `docutils.nodes.document`.
        :raises ValueError: If the `rest_document` has no `title` child node.
        """
    verify_is_docutils_node(rest_document, node_type=docutils.nodes.document)
    result = get_node_title_text(rest_document)
    return result


def get_document_subtitle_text(rest_document):
    """ Get the document's `subtitle` node child text.

        :param rest_document: Document root, as a `docutils.nodes.document`
            instance.
        :return: The text of the document's `subtitle` node, or ``None`` if
            absent.
        :raises TypeError: If the `rest_document` is not a
            `docutils.nodes.document`.
        """
    verify_is_docutils_node(rest_document, node_type=docutils.nodes.document)
    subtitle_nodes = [
        child_node for child_node in rest_document.children
        if isinstance(child_node, docutils.nodes.subtitle)]
    if not subtitle_nodes:
        raise ValueError(
            "node has no ‘subtitle’ children: {!r}".format(rest_document))
    subtitle = next(iter(subtitle_nodes))
    result = get_node_text(subtitle)
    return result


def get_top_level_sections(rest_document):
    """ Get the top-level section objects from `rest_document`.

        :param rest_document: Document root, as a `docutils.nodes.document`
            instance.
        :return: Sequence of `docutils.nodes.section` instances.
        :raises TypeError: If the `rest_document` is not a
            `docutils.nodes.document`.
        """
    verify_is_docutils_node(rest_document, node_type=docutils.nodes.document)
    sections = (
        node for node in rest_document.children
        if isinstance(node, docutils.nodes.section))
    return sections


def get_version_text_from_changelog_entry(entry_node):
    """ Get the version text from changelog entry node `entry_node`.

        :param entry_node: The `docutils.nodes.Node` representing the change
            log entry.
        :return: The version text parsed from the `entry_node` title.
        """
    title_text = get_changelog_entry_title_from_node(entry_node)
    version_text = core.get_version_text_from_entry_title(title_text)
    return version_text


def get_changelog_entry_title_from_node(entry_node):
    """ Get the title of the change log entry, from `entry_node`.

        :param entry_node: The `docutils.nodes.Node` representing the change
            log entry.
        :return: The title (text) that is the change log entry title.
        :raises ValueError: If the `node` has no `Text` child node.

        Because of how Docutils treats some document structures specially, the
        actual title of the change log entry might be in different places.

        For a regular `section`, the child `title` node contains the title.
        If the change log entry happens to be the whole document, the title
        might be in the `title` child or the `subtitle` child.
        """
    entry_title = None
    entry_title_match = False
    try:
        entry_title = get_node_title_text(entry_node)
        core.verify_is_change_log_entry_title(entry_title)
        entry_title_match = True
    except (ValueError, core.ChangeLogEntryTitleFormatInvalidError):
        # No direct ‘title’ text matches.
        if isinstance(entry_node, docutils.nodes.document):
            try:
                entry_title = get_document_subtitle_text(entry_node)
                core.verify_is_change_log_entry_title(entry_title)
                entry_title_match = True
            except (ValueError, core.ChangeLogEntryTitleFormatInvalidError):
                # The document subtitle also doesn't match.
                # Nothing more to try.
                pass
    if not entry_title_match:
        # No title found in the expected places matched the expected Change Log
        # entry title pattern.
        raise ValueError(
            "no change log entry title found: {!r}".format(entry_node))
    return entry_title


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
