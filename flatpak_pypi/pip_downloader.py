""" pip_downloader.py - A wrapper around pip download """
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
from typing import List, Tuple
import hashlib
import os
import os.path
import subprocess


def get_hash(path: str) -> str:
    """Get a sha256 hash string for file"""
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(10**6), b''):
            sha256.update(block)
    return sha256.hexdigest()


class PipDownloader(object):
    def __init__(self, pip_path: str):
        self.pip_path = pip_path

    def download(self, requirements_file: str, destination: str) -> List[Tuple[str, str]]:
        """Execute pip download on a requirements file, get a list of file names and hashes """
        assert os.path.isdir(destination)

        # Download packages

        result = subprocess.run([self.pip_path,
                                 'download',
                                 '-r', requirements_file, '-d', destination,
                                 '--no-binary=:all:'])
        result.check_returncode()

        return self._build_list(destination)

    def _build_list(self, directory: str) -> List[Tuple[str, str]]:
        """Build a list of file names and hashes, ordered by creation timestamp"""
        tarballs = reversed(sorted(os.scandir(directory),
                                   key=lambda f: f.stat().st_mtime))

        ret = []
        for tarball in tarballs:
            ret.append((tarball.name, get_hash(tarball.path)))

        return ret
