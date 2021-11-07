import datetime

from services.models import Device, FileTypes, File
from services.settings import get_download_folder
from services.shell import ls, adb, properties


# Driver of getting device list
def get_devices():
    devices = []
    data = adb.devices()
    if not data:
        return devices

    lines = data.split()
    lines = lines[4:]  # Removing 'List of attached devices'
    if not lines:
        return devices

    i = 0
    while i < len(lines):
        device_id = lines[i]
        name = adb.shell(device_id, [properties.GET_PROPERTY, properties.Parameter.PRODUCT_MODEL]).strip()
        device = Device(id=device_id, name=name or 'Unknown Device', type=lines[i + 1])
        devices.append(device)
        i += 2
    return devices


def download_files(devices_id: str, source: str):
    data = adb.pull(devices_id, source, get_download_folder())
    if not data:
        return 'Failed:  no response'
    lines = data.split('\n')
    lines.remove('')
    return lines[len(lines) - 1]


def download_files_to(devices_id: str, source: str, destination: str):
    data = adb.pull(devices_id, source, destination)
    if not data:
        return 'Failed:  no response'
    lines = data.split('\n')
    lines.remove('')
    return lines[len(lines) - 1]


def upload_files(devices_id: str, source: str, destination: str):
    data = adb.push(devices_id, source, destination)
    if not data:
        return 'Failed:  no response'
    lines = data.split('\n')
    lines.remove('')
    return lines[len(lines) - 1]


def get_file_type(device_id, path):
    args = ls.Command.FILE_INFO + [path]
    info = adb.shell(device_id, args)
    print(info)
    if info:
        info = info[0]
        if info == 'd':
            return FileTypes.DIRECTORY
        elif info == '-':
            return FileTypes.FILE
    return FileTypes.UNKNOWN


# Driver of getting file list from ls command
def get_files(device_id, path):
    return adb_ls_universal_getter(device_id, path)


# command: adb -s <device_id> shell ls -a -l <path>
# PERMISSION OWNER   GROUP OTHER   SIZE       DATE       NAME
# drwxrwxrwx root     root              2021-11-04 05:04 var
# drwxrwxrwx root     root              1970-01-01 00:00 bin
# -rwxr-x--- root     root        94168 1970-01-01 00:00 init
#                           etc...
def adb_shell_ls_getter_variant_1(device_id, path):
    files = []

    # Getting data from device
    args = ls.Command.FULL_LIST + [path]
    data = adb.shell(device_id, args)
    if not data:
        return files

    # Splitting into data lines
    lines = data.split('\n')
    lines.remove('')

    for line in lines:
        fields = line.split()

        size = 0
        link = ''
        other = None
        link_type = None

        permission = fields[0]
        owner = fields[1]
        group = fields[2]

        code = permission[0]
        if code == 'd' or code == 's':
            name = fields[5]
            date = f"{fields[3]} {fields[4]}"
        elif code == '-':
            name = fields[6]
            date = f"{fields[4]} {fields[5]}"
            size = fields[3]
        elif code == 'l':
            name = fields[5]
            date = f"{fields[3]} {fields[4]}"
            link = fields[7]
            if link[0] == '/':
                link_type = get_file_type(device_id, link)
            else:
                link_type = get_file_type(device_id, f"{path}/{link}")
        elif code == 'c' or code == 'b':
            name = fields[7]
            date = f"{fields[5]} {fields[6]}"
            size = fields[4]
            other = fields[3]
        else:
            date = "1000-01-01 00:00"
            name = f'<Unknown file type {code} ?>'
        file = File(
            name=name,
            path=path,
            permissions=permission,
            owner=owner,
            group=group,
            date=date,
            link=link,
            link_type=link_type,
            size=size,
            other=other
        )
        files.append(file)
    return files


# command: adb -s <device_id> ls <path>
#   MODE     SIZE     DATE    NAME
# 000043ff 000004ec 061ce2cd .
# 000043ff 000004ec 061ce2cd ..
# 000041ed 00001000 051c97ed file
#           etc...
def adb_ls_universal_getter(device_id, path):
    files = []

    # Getting data from device
    data = adb.file_list(device_id, path)
    if not data:
        return files

    # Splitting into data lines
    lines = data.split('\n')
    lines = lines[2:]  # Skip first two lines
    if not lines:
        return files
    lines.remove('')

    for line in lines:
        fields = line.split()

        octal = list(oct(int(fields[0], 16))[2:])
        permission = file_mode_converter(octal)
        size = int(fields[1], 16)
        date_time = datetime.datetime.utcfromtimestamp(int(fields[2], 16))
        name = fields[3]

        file = File(
            name=name,
            size=size,
            path=path,
            date_time=date_time,
            permissions=permission,
            owner=None,
            group=None,
            link=None,
            link_type=None,
            other=None
        )

        files.append(file)
    return files


# Converting octal data to normal permissions field
# 100777 (8)    --->    - rwx rwx rwx (str)
def file_mode_converter(octal_data: []):
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

    return file_type + "".join(owner) + "".join(group) + "".join(others)
