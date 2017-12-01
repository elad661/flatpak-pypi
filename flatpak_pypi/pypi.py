# pypi.py - Get a URL for a pypi package
#
# Copyright © 2017 Elad Alfassa <elad@fedoraproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Tuple
import requests

PYPI_URL = "https://pypi.python.org/pypi/{name}/{version}/json"


def get_name_version(tarball: str) -> Tuple[str, str]:
    """Get a tuple with the name and version from a tarball name"""
    name, version = tarball.rsplit('-', 1)

    # FIXME: a more generic & safe way to do this
    version = version.replace('.tar.gz', '')
    return name, version


def get_url(tarball: str) -> str:
    """Get pypi URL for a tarball"""
    # of course it'd be better if I could get pip to give me the URL,
    # but this works too, for now.
    name, version = get_name_version(tarball)

    result = requests.get(PYPI_URL.format(name=name, version=version))
    result.raise_for_status()

    for url in result.json()['urls']:
        if url['packagetype'] == 'sdist':
            return url['url']

    raise Exception("Couldn't find source URL for this tarball??")
