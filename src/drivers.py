from services.shell import ls, adb
from models import File, FileTypes


# Driver of getting file list from ls command
def get_files(path):
    files = []
    data = adb.shell(ls.Commands.ALL + [path])
    if not data or data[0] == '/':
        return files
    lines = list(filter(lambda s: s != '', data.split('\r\n' or '\r' or '\n')))
    for line in lines:
        fields = list(filter(lambda s: s != '', line.split(' ')))

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
                link_type = get_file_type(link)
            else:
                link_type = get_file_type(f"{path}/{link}")
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


def get_file_type(path):
    info = adb.shell(ls.Commands.INFO + [path])[0]
    if info == 'd':
        return FileTypes.DIRECTORY
    elif info == '-':
        return FileTypes.FILE
    return FileTypes.UNKNOWN
