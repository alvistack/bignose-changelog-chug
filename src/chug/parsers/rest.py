# src/chug/parsers/rest.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Parser features for reStructuredText documents. """

import docutils.core


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
