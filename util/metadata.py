# util/metadata.py
# Part of ‘changelog-chug’, a parser for software release information.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Functionality to work with project metadata.

    This module implements ways to derive various project metadata at build
    time.
    """

import inspect


def docstring_from_object(object):
    """ Extract the `object` docstring as a simple text string.

        :param object: The Python object to inspect.
        :return: The docstring (text), “cleaned” according to :PEP:`257`.
        """
    docstring = inspect.getdoc(object)
    return docstring


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
