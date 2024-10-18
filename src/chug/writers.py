# src/chug/writers.py
# Part of ‘changelog-chug’, a parser for project Change Log documents.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Version information writers for various output formats. """

import json


def serialise_version_info_from_mapping_to_json(version_info):
    """ Generate the version info as JSON serialised data.

        :param version_info: Mapping of version info items.
        :return: The version info serialised to JSON.
        """
    content = json.dumps(version_info, indent=4)

    return content


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
