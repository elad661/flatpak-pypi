# flatpak_manifest.py - functions to manipulate a flatpak manifest
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

from typing import List, Dict
import collections
import json
import os
import os.path
import shutil


def _find_backup_name(manifest: str) -> str:
    """ Find a name for the backup file """
    name = manifest + '.orig'
    if not os.path.exists(name):
        return name

    for i in range(0, 99999):
        name_i = name + str(i)
        if not os.path.exists(name_i):
            return name_i

    raise Exception("Can't find a name for the backup file for your manifest")


def backup_manifest(manifest: str) -> str:
    """Create a backup of the manifest file, returns the backup name"""
    backup = _find_backup_name(manifest)
    shutil.copy2(manifest, backup)
    if not os.path.exists(backup):
        raise Exception("Backup failed, not going to edit your manifest")
    return backup


def package_to_flatpak_module(package: Dict[str, str]) -> Dict[str, str]:
    """ Turn a dict containing name,sha256 and url to a flatpak manifest compatible module definition """
    return {"name": package["name"],
            "buildsystem": "simple",
            "ensure-writable": ["easy-install.pth"],
            "build-commands": ["python3 setup.py install --prefix=/app"],
            "sources": [{"type": "archive",
                         "url": package["url"],
                        "sha256": package["sha256"]}]}


def edit_manifest(manifest: str, packages: List[Dict[str, str]]) -> None:
    """Add python packages to a flatpak manifest"""
    backup = backup_manifest(manifest)
    with open(manifest, "r") as f:
        manifest_obj = json.load(f, object_pairs_hook=collections.OrderedDict)

    # Prevent duplicates
    current_module_names = set()
    for module in manifest_obj['modules']:
        current_module_names.add(module['name'])

    modified = False

    for package in packages:
        if package['name'] in current_module_names:
            print(f"Skipping '{package['name']}' as it is already listed in the manifest")
            continue
        modified = True
        manifest_obj['modules'].append(package_to_flatpak_module(package))

    if modified:
        with open(manifest, "w") as f:
            json.dump(manifest_obj, f, indent=4)
        print("Manifest saved")
    else:
        print("Manifest not modified")
        os.unlink(backup)
