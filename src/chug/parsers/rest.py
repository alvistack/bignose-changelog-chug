# src/chug/parsers/rest.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Parser features for reStructuredText documents. """

import docutils.core
import docutils.nodes


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


def get_node_text(node):
    """ Get the child text of the `node`.

        :param node: The `docutils.nodes.Node` instance to query.
        :return: The child text of `node`, or ``None`` if absent.
        :raises TypeError: If the `node` is not a `docutils.nodes.Node`.
        """
    if not isinstance(node, docutils.nodes.Node):
        raise TypeError("not a Docutils node: {!r}".format(node))
    node_text_children = (
        [
            child_node for child_node in node.children
            if isinstance(child_node, docutils.nodes.Text)]
        if node is not None
        else None)
    result = (
        next(iter(node_text_children)) if node_text_children
        else None)
    return result


def get_node_title_text(node):
    """ Get the `node`'s `title` node child text.

        :param rest_document: Document root, as a `docutils.nodes.document`
            instance.
        :return: The text of the `title` node, if any, of the `node`; or
            ``None`` if absent.
        :raises TypeError: If the `node` is not a `docutils.nodes.Node`.
        """
    if not isinstance(node, docutils.nodes.Node):
        raise TypeError("not a Docutils node: {!r}".format(node))
    title_nodes = [
        child_node for child_node in node.children
        if isinstance(child_node, docutils.nodes.title)]
    title = (next(iter(title_nodes)) if title_nodes else None)
    result = (
        get_node_text(title) if title is not None
        else None)
    return result


def get_document_title_text(rest_document):
    """ Get the document's `title` node child text.

        :param rest_document: Document root, as a `docutils.nodes.document`
            instance.
        :return: The text of the document's `title` node, or ``None`` if
            absent.
        :raises TypeError: If the `rest_document` is not a
            `docutils.nodes.document`.
        """
    if not isinstance(rest_document, docutils.nodes.document):
        raise TypeError(
            "not a Docutils document root: {!r}".format(rest_document))
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
    if not isinstance(rest_document, docutils.nodes.document):
        raise TypeError(
            "not a Docutils document root: {!r}".format(rest_document))
    subtitle_nodes = [
        child_node for child_node in rest_document.children
        if isinstance(child_node, docutils.nodes.subtitle)]
    subtitle = (next(iter(subtitle_nodes)) if subtitle_nodes else None)
    result = (
        get_node_text(subtitle) if subtitle is not None
        else None)
    return result


def get_top_level_sections(rest_document):
    """ Get the top-level section objects from `rest_document`.

        :param rest_document: Document root, as a `docutils.nodes.document`
            instance.
        :return: Sequence of `docutils.nodes.section` instances.
        :raises TypeError: If the `rest_document` is not a
            `docutils.nodes.document`.
        """
    if not isinstance(rest_document, docutils.nodes.document):
        raise TypeError(
            "not a Docutils document root: {!r}".format(rest_document))
    sections = (
        node for node in rest_document.children
        if isinstance(node, docutils.nodes.section))
    return sections


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
