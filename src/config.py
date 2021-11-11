import pathlib

VERSION = 'alpha v0.31'
# PATH = pathlib.Path(__file__).parent.resolve()  # Production mode
PATH = '.'  # Debugging mode


class Asset:
    logo = f'{PATH}/assets/logo.png'

    icon_exit = f'{PATH}/assets/icons/exit.png'
    icon_connect = f'{PATH}/assets/icons/connect.png'
    icon_unknown = f'{PATH}/assets/icons/unknown.png'
    icon_phone = f'{PATH}/assets/icons/phone.png'
    icon_plus = f'{PATH}/assets/icons/plus.png'
    icon_up = f'{PATH}/assets/icons/up.png'
    icon_ok = f'{PATH}/assets/icons/ok.png'

    icon_file = f'{PATH}/assets/icons/files/file.png'
    icon_folder = f'{PATH}/assets/icons/files/folder.png'
    icon_file_unknown = f'{PATH}/assets/icons/files/file_unknown.png'
    icon_link_file = f'{PATH}/assets/icons/files/link_file.png'
    icon_link_folder = f'{PATH}/assets/icons/files/link_folder.png'
    icon_link_file_unknown = f'{PATH}/assets/icons/files/link_file_unknown.png'
    icon_link_file_universal = f'{PATH}/assets/icons/files/link_file_universal.png'
