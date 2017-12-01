#!/bin/env python3
# flatpak-pypi.py - Turns a python requirements.txt into a flatpak manifest compatible dependency list
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
"""
flatpak-pypi

Usage:
  ./flatpak-pypi.py <requirements_file> <flatpak_manifest>
"""
import docopt
import os.path
import shutil
import subprocess
import tempfile
from .pip_downloader import PipDownloader
from .pypi import get_url, get_name_version
from .flatpak_manifest import edit_manifest

# How does this work:
#
# first, create a virtual environment
# then, use pip in that virtual environment to process the requirements file
# and download all requirements and their dependencies.
# (Use the timestamps on these files to figure out the dependency order,
# because pip will download them in order and that saves us a lot of work)
#
# When we have all dependencies we can calculate the checksums and, extract
# the name and version from the file names - so we can use the pypi API to
# find the URL to put in the flatpak manifest.
#
# Then all we have to do is to modifiy the flatpak manifest to add the deps.


def validate_path(file: str) -> None:
    if not os.path.exists(file):
        raise Exception(f"{file}: No such file or directory")
    if not os.path.isfile(file):
        raise Exception(f"{file}: Not a file")


def create_venv(path: str) -> str:
    """ Create a Virtual Environment in `path` and return its pip executable"""
    result = subprocess.run(['virtualenv-3', path])
    result.check_returncode()
    return os.path.join(path, 'bin', 'pip')


def main():
    arguments = docopt.docopt(__doc__)
    requirements_file = arguments['<requirements_file>']
    flatpak_manifest = arguments['<flatpak_manifest>']

    validate_path(requirements_file)
    validate_path(flatpak_manifest)

    print("Initilalizing...")
    venv = tempfile.mkdtemp()
    download_dir = tempfile.mkdtemp()
    pip_path = create_venv(venv)

    print("Downloading packages (to calculate checksums)...")
    # Ideally, this step should get us the URL too, but that's kinda
    # complicated, so it doesn't do that.
    pip = PipDownloader(pip_path)
    pip_packages = pip.download(requirements_file, download_dir)
    # pip_packages: name, hash

    print("Finding URLs for the packages...")
    packages = []
    for package in pip_packages:
        url = get_url(package[0])
        name, _ = get_name_version(package[0])
        packages.append({"url": url,
                         "sha256": package[1],
                         "name": name})

    print("Editing manifest...")
    edit_manifest(flatpak_manifest, packages)

    print("Done")

    shutil.rmtree(download_dir)
    shutil.rmtree(venv)


if __name__ == "__main__":
    main()
