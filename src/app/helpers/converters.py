# ADB File Explorer `tool`
# Copyright (C) 2022  Azat Aldeshov azata1919@gmail.com
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import re
from typing import List

from app.data.models import Device, File, FileType


# Converter to Device list
# command: adb devices -l
# List of attached devices
# <device_id>   <device_type>
def convert_to_devices(data: str) -> List[Device]:
    lines = convert_to_lines(data)[1:]  # Removing 'List of attached devices'

    devices = []
    for line in lines:
        data = line.split()
        name = "Unknown Device"
        for i in range(2, len(data)):
            if data[i].startswith("model:"):
                name = data[i][6:]
                break

        devices.append(
            Device(
                id=data[0],
                name=name.replace('_', ' '),
                type=data[1]
            )
        )
    return devices


# Converter to File object
# command: adb -s <device_id> shell ls -l -d <path>
# <permissions> <type?> <owner> <group> <other,?> <size?> <date&time> <filename>
def convert_to_file(data: str) -> File:
    date_pattern = '%Y-%m-%d %H:%M'
    if re.fullmatch(r'[-dlcbsp][-rwxst]{9}\s+\d+\s+\S+\s+\S+\s*\d*,?\s+\d+\s+\d{4}-\d{2}-\d{2} \d{2}:\d{2} .+', data):
        fields = data.split()

        size = 0
        date = None
        link = None
        other = None
        name = '<Unknown?>'

        owner = fields[2]
        group = fields[3]
        permission = fields[0]
        file_type = int(fields[1])

        code = permission[0]
        if ['s', 'd', '-', 'l'].__contains__(code):
            size = int(fields[4])
            date = datetime.datetime.strptime(f"{fields[5]} {fields[6]}", date_pattern)
            name = " ".join(fields[7:])
            if code == 'l':
                name = " ".join(fields[7:fields.index('->')])
                link = " ".join(fields[fields.index('->') + 1:])
        elif ['c', 'b'].__contains__(code):
            other = fields[4]
            size = int(fields[5])
            date = datetime.datetime.strptime(f"{fields[6]} {fields[7]}", date_pattern)
            name = fields[8]

        if name.startswith('/'):
            name = name[name.rindex('/') + 1:]

        return File(
            name=name,
            size=size,
            link=link,
            owner=owner,
            group=group,
            other=other,
            date_time=date,
            file_type=file_type,
            permissions=permission,
        )
    elif re.fullmatch(r'[-dlcbsp][-rwxst]{9}\s+\S+\s+\S+\s*\d*,?\s*\d*\s+\d{4}-\d{2}-\d{2} \d{2}:\d{2} .*', data):
        fields = data.split()

        size = 0
        link = None
        date = None
        other = None
        name = '<Unknown?>'

        permission = fields[0]
        owner = fields[1]
        group = fields[2]

        code = permission[0]
        if code == 'd' or code == 's':
            name = " ".join(fields[5:])
            date = datetime.datetime.strptime(f"{fields[3]} {fields[4]}", date_pattern)
        elif code == '-':
            size = int(fields[3])
            name = " ".join(fields[6:])
            date = datetime.datetime.strptime(f"{fields[4]} {fields[5]}", date_pattern)
        elif code == 'l':
            name = " ".join(fields[5:fields.index('->')])
            link = " ".join(fields[fields.index('->') + 1:])
            date = datetime.datetime.strptime(f"{fields[3]} {fields[4]}", date_pattern)
        elif code == 'c' or code == 'b':
            size = int(fields[4])
            other = fields[3]
            name = " ".join(fields[7:])
            date = datetime.datetime.strptime(f"{fields[5]} {fields[6]}", date_pattern)

        if name.startswith('/'):
            name = name[name.rindex('/') + 1:]

        return File(
            name=name,
            link=link,
            size=size,
            owner=owner,
            group=group,
            other=other,
            date_time=date,
            permissions=permission,
        )


# Converter to File list (a)
# command: adb -s <device_id> shell ls -a -l <path>
# <permissions> <type?> <owner> <group> <other,?> <size?> <date&time> <filename>
def convert_to_file_list_a(data: str, **kwargs) -> List[File]:
    lines = convert_to_lines(data)
    dirs = kwargs.get('dirs')
    path = kwargs.get('path')

    if lines[0].startswith('total'):
        lines = lines[1:]  # Skip first line: total x

    files = []
    for line in lines:
        re__permission = re.search(r'[-dlcbsp][-rwxst]{9}', line)
        re__size_datetime_name = re.search(r'\d* \d{4}-\d{2}-\d{2} \d{2}:\d{2} .+', line)
        if re__permission and re__size_datetime_name:
            size_date_name = re__size_datetime_name[0].split(' ')
            if len(size_date_name) == 4 and size_date_name[3] == '.':
                continue
            elif len(size_date_name) == 4 and size_date_name[3] == '..':
                continue

            permission = re__permission[0]
            size = int(size_date_name[0] or 0)
            date_time = datetime.datetime.strptime(
                f"{size_date_name[1]} {size_date_name[2]}",
                '%Y-%m-%d %H:%M'
            )
            names = size_date_name[3:]

            link = None
            link_type = None
            name = " ".join(names)
            if permission[0] == 'l':
                name = " ".join(names[:names.index('->')])
                link = " ".join(names[names.index('->') + 1:])
                link_type = FileType.FILE
                if dirs.__contains__(f"{path}{name}/"):
                    link_type = FileType.DIRECTORY
            files.append(
                File(
                    name=name,
                    size=size,
                    link=link,
                    path=f"{path}{name}",
                    link_type=link_type,
                    date_time=date_time,
                    permissions=permission,
                )
            )
    return files


# Converter to File list
# command: adb -s <device_id> ls <path>
#  <hex>   <hex>   <hex>    <filename>
def convert_to_file_list_b(data: str) -> List[File]:
    lines = convert_to_lines(data)[2:]  # Skip first two lines

    files = []
    for line in lines:
        fields = line.split()
        octal = oct(int(fields[0], 16))[2:]

        size = int(fields[1], 16)
        name = " ".join(fields[3:])
        permission = __converter_to_permissions_default__(list(octal))
        date_time = datetime.datetime.utcfromtimestamp(int(fields[2], 16))

        files.append(
            File(
                name=name,
                size=size,
                date_time=date_time,
                permissions=permission
            )
        )
    return files


# Get lines from raw data
def convert_to_lines(data: str) -> List[str]:
    if not data:
        return list()

    lines = re.split(r'\n', data)
    for index, line in enumerate(lines):
        regex = re.compile(r'[\r\t]')
        lines[index] = regex.sub('', lines[index])
    filtered = filter(bool, lines)
    return list(filtered)


# Converting octal data to normal permissions' field
# Created for: convert_to_file_list_b()
# 100777 (.8)   --->    '- rwx rwx rwx' (str)
def __converter_to_permissions_default__(octal_data: list) -> str:
    permission = (
        ['-', '-', '-'],
        ['-', '-', 'x'],
        ['-', 'w', '-'],
        ['-', 'w', 'x'],
        ['r', '-', '-'],
        ['r', '-', 'x'],
        ['r', 'w', '-'],
        ['r', 'w', 'x']
    )

    dir_mode = {
        0: '',
        1: 'p',
        2: 'c',
        4: 'd',
        6: 'b',
    }

    file_mode = {
        0: '-',
        2: 'l',
        4: 's',
    }

    octal_data.reverse()
    for i in range(0, len(octal_data)):
        octal_data[i] = int(octal_data[i])
    octal_data.extend([0] * (8 - len(octal_data)))

    others = permission[octal_data[0]]
    group = permission[octal_data[1]]
    owner = permission[octal_data[2]]
    if octal_data[3] == 1:
        others[2] = 't'
    elif octal_data[3] == 2:
        others[1] = 's'
    elif octal_data[3] == 4:
        others[0] = 's'

    if octal_data[5] == 0:
        file_type = dir_mode.get(octal_data[4])
    else:
        file_type = file_mode.get(octal_data[4])

    permissions = [file_type] + owner + group + others
    return "".join(permissions)
