import datetime
import re
from typing import List

from services.data.models import Device, File, FileTypes
from services.shell import adb


def connect(device_id: str) -> (str, str):
    response = adb.connect(device_id)
    if not response.Successfull:
        return None, response.ErrorData or response.OutputData

    return response.OutputData, None


def get_devices() -> (List[Device], str):
    response = adb.devices()
    if not response.Successfull:
        return [], response.ErrorData or response.OutputData

    lines = response.OutputData.split()
    lines = lines[4:]  # Removing 'List of attached devices'
    if not lines:
        return [], None

    devices = []
    for i in range(0, int(len(lines) / 2)):
        device_id = lines[i * 2 - 2]
        device_type = lines[i * 2 - 1]
        response_name = adb.shell(device_id, adb.ShellCommand.GETPROP_PRODUCT_MODEL)
        device_name = 'Unknown Device'
        if response_name.Successfull and response_name.OutputData is not None:
            device_name = response_name.OutputData.strip()
        device = Device(
            id=device_id,
            name=device_name,
            type=device_type
        )
        devices.append(device)
    return devices, None


def download_path(devices_id: str, source_path: str, destination_path: str) -> (str, str):
    response = adb.pull(devices_id, source_path, destination_path)
    if not response.Successfull:
        return None, response.ErrorData or response.OutputData
    lines = __lines_from_data(response.OutputData)
    return lines[len(lines) - 1], None


def upload_path(devices_id: str, source_path: str, destination_path: str) -> (str, str):
    response = adb.push(devices_id, source_path, destination_path)
    if not response.Successfull:
        return None, response.ErrorData or response.OutputData

    lines = __lines_from_data(response.OutputData)
    return lines[len(lines) - 1], None


def create_folder(device_id, new_path) -> (str, str):
    args = [adb.ShellCommand.MKDIR, new_path]
    response = adb.shell(device_id, args)
    if not response.Successfull:
        return None, response.ErrorData or response.OutputData

    return response.OutputData, response.ErrorData


# Driver of getting file from ls command
def get_file(device_id, path) -> (File, str):
    args = adb.ShellCommand.LS_FILE_INFO + [path]
    response = adb.shell(device_id, args)
    if not response.Successfull:
        return None, response.ErrorData or response.OutputData

    # TODO
    return None, None


def get_link_type(device_id, path) -> (str, str):
    args = adb.ShellCommand.LS_FILE_INFO + [path]
    response = adb.shell(device_id, args)

    if not response.Successfull:
        return None, response.ErrorData or response.OutputData

    if not response.OutputData:
        return None, None

    if response.OutputData.__contains__('No such file or directory'):
        return None, response.OutputData

    if response.OutputData.__contains__('Not a directory'):
        return FileTypes.FILE, None

    if not response.OutputData[0] == '/':
        return FileTypes.DIRECTORY, None

    return None, None


# Driver of getting file list with adb
def get_files(device_id, path) -> (List[File], str):
    return get_files__adb_shell_ls(device_id, path)


# command: adb -s <device_id> shell ls -a -l <path>
def get_files__adb_shell_ls(device_id, path) -> (List[File], str):
    args = adb.ShellCommand.LS_FULL_LIST + [path.replace(' ', r"\ ")]
    response = adb.shell(device_id, args)
    if not response.Successfull and response.ExitCode != 1:
        return [], response.ErrorData or response.OutputData

    lines = __lines_from_data(response.OutputData)
    if not lines:
        return [], response.ErrorData
    if lines[0].startswith('total'):
        lines = lines[1:]  # Skip first line: total x

    check = lines[0]
    files = []
    if re.fullmatch(r'[-dlcbsp][-rwxst]{9}\s+\d+\s+\S+\s+\S+\s*\d*,?\s+\d+\s+\d{4}-\d{2}-\d{2} \d{2}:\d{2} .+', check):
        pattern = r'[-dlcbsp][-rwxst]{9}\s+\d+\s+\S+\s+\S+\s*\d*,?\s+\d+\s+\d{4}-\d{2}-\d{2} \d{2}:\d{2} .+'
        for line in lines[2:]:
            if re.fullmatch(pattern, line):
                files.append(__converter_to_file_version2(line, path=path, device_id=device_id))

    elif re.fullmatch(r'[-dlcbsp][-rwxst]{9}\s+\S+\s+\S+\s*\d*,?\s*\d*\s+\d{4}-\d{2}-\d{2} \d{2}:\d{2} .+', check):
        pattern = r'[-dlcbsp][-rwxst]{9}\s+\S+\s+\S+\s*\d*,?\s*\d*\s+\d{4}-\d{2}-\d{2} \d{2}:\d{2} .+'
        for line in lines:
            if re.fullmatch(pattern, line):
                files.append(__converter_to_file_version1(line, path=path, device_id=device_id))

    return files, response.ErrorData


# command: adb -s <device_id> ls <path>
def get_files__adb_ls(device_id: str, path: str) -> (List[File], str):
    response = adb.file_list(device_id, path)
    if not response.Successfull:
        return [], response.ErrorData or response.OutputData

    if not response.OutputData:
        return [], None

    lines = __lines_from_data(response.OutputData)
    lines = lines[2:]  # Skip first two lines
    if not lines:
        return [], None

    files = []
    for line in lines:
        files.append(__converter_to_file_default(line, path=path))
    return files, None


# Private tool clear function for dataline filter
def __clear(dataline) -> bool:
    return bool(dataline)


# Private tool for getting lines list from data
def __lines_from_data(data: str, separator=r'\n') -> list:
    if not data:
        return list()

    lines = re.split(separator, data)
    for i, line in enumerate(lines):
        regex = re.compile(r'[\r\t]')
        lines[i] = regex.sub('', lines[i])
    filtered = filter(__clear, lines)
    return list(filtered)


# Line Converter (to File()) - version 1 (old)
# dataline must be exact to regex:
# r'[-dlcbsp][-rwxst]{9}\s+\S+\s+\S+\s*\d*,?\s*\d*\s+\d{4}-\d{2}-\d{2} \d{2}:\d{2} .+'
def __converter_to_file_version1(dataline: str, **kwargs) -> File:
    fields = dataline.split()
    date_pattern = '%Y-%m-%d %H:%M'

    size = 0
    link = ''
    other = None
    link_type = None

    permission = fields[0]
    owner = fields[1]
    group = fields[2]

    code = permission[0]
    if code == 'd' or code == 's':
        name = " ".join(fields[5:])
        date = datetime.datetime.strptime(f"{fields[3]} {fields[4]}", date_pattern)
    elif code == '-':
        size = fields[3]
        name = " ".join(fields[6:])
        date = datetime.datetime.strptime(f"{fields[4]} {fields[5]}", date_pattern)
    elif code == 'l':
        name = " ".join(fields[5:fields.index('->')])
        link = " ".join(fields[fields.index('->') + 1:])
        date = datetime.datetime.strptime(f"{fields[3]} {fields[4]}", date_pattern)
        link_type, error = get_link_type(kwargs.get('device_id'), f"{kwargs.get('path')}{name}/")
    elif code == 'c' or code == 'b':
        size = fields[4]
        other = fields[3]
        name = " ".join(fields[7:])
        date = datetime.datetime.strptime(f"{fields[5]} {fields[6]}", date_pattern)
    else:
        date = None
        name = f'<Unknown file type {code} ?>'

    return File(
        path=kwargs.get("path"),
        file_type=kwargs.get("file_type"),
        name=name,
        permissions=permission,
        owner=owner,
        group=group,
        date_time=date,
        link=link,
        link_type=link_type,
        size=size,
        other=other
    )


# Line Converter (to File()) - version 2 (newer)
# dataline must be exact to regex:
# r'[-dlcbsp][-rwxst]{9}\s+\d+\s+\S+\s+\S+\s*\d*,?\s+\d+\s+\d{4}-\d{2}-\d{2} \d{2}:\d{2} .+'
def __converter_to_file_version2(dataline: str, **kwargs) -> File:
    fields = dataline.split()
    date_pattern = '%Y-%m-%d %H:%M'

    size = 0
    name = '<Unknown Type ?>'
    date = None
    link = None
    other = None
    link_type = None
    date_time = None

    permission = fields[0]
    file_type = fields[1]
    owner = fields[2]
    group = fields[3]

    code = permission[0]
    if ['s', 'd', '-', 'l'].__contains__(code):
        size = int(fields[4])
        date = f"{fields[5]} {fields[6]}"
        name = " ".join(fields[7:])
        if code == 'l':
            name = " ".join(fields[7:fields.index('->')])
            link = " ".join(fields[fields.index('->') + 1:])
            link_type, error = get_link_type(kwargs.get('device_id'), f"{kwargs.get('path')}{name}/")

    elif ['c', 'b'].__contains__(code):
        other = fields[4]
        size = fields[5]
        date = f"{fields[6]} {fields[7]}"
        name = fields[8]

    if date:
        date_time = datetime.datetime.strptime(date, date_pattern)

    return File(
        path=kwargs.get("path"),
        name=name,
        permissions=permission,
        file_type=file_type,
        owner=owner,
        group=group,
        date_time=date_time,
        link=link,
        link_type=link_type,
        size=size,
        other=other
    )


# Line Converter (to File()) - default
# sample dataline
#  <hex>   <hex>   <hex>
# 000041ed 00001000 051c97ed <filename>
def __converter_to_file_default(dataline: str, **kwargs) -> File:
    fields = dataline.split()
    octal = oct(int(fields[0], 16))[2:]

    date_time = datetime.datetime.utcfromtimestamp(int(fields[2], 16))
    permission = __converter_to_permissions_default(list(octal))
    size = int(fields[1], 16)
    name = fields[3]

    return File(
        name=name,
        size=size,
        date_time=date_time,
        permissions=permission,
        path=kwargs.get("path"),
        owner=kwargs.get("owner"),
        group=kwargs.get("group"),
        other=kwargs.get("other"),
        link=kwargs.get("link"),
        link_type=kwargs.get("link_type"),
        file_type=kwargs.get("file_type")
    )


# Converting octal data to normal permissions field
# Created for: Line Converter - default
# 100777 (8)    --->    '- rwx rwx rwx' (str)
def __converter_to_permissions_default(octal_data: list) -> str:
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
