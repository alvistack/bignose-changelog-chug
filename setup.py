# setup.py
# Python Setuptools configuration program for this distribution.
# Documentation: <URL:https://packaging.python.org/guides/distributing-packages-using-setuptools/#setup-py>.  # noqa: E501

# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Distribution setup for ‘changelog-chug’ library. """

import os.path
import sys

from setuptools import setup

# This module is not inside a package, so we can't use relative imports. We
# instead add its directory to the import path.
sys.path.insert(0, os.path.dirname(__file__))
import util.metadata  # noqa: E402

import src.chug as main_module  # noqa: E402


main_module_docstring = util.metadata.docstring_from_object(main_module)
(synopsis, __) = util.metadata.synopsis_and_description_from_docstring(
    main_module_docstring)

setup_kwargs = dict(
    description=synopsis,
)


if __name__ == '__main__':  # pragma: nocover
    setup(**setup_kwargs)


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
