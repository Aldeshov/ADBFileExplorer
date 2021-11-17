import pathlib

VERSION = 'beta v0.4'
DEBUG = True

PATH = pathlib.Path(__file__).parent.resolve() if not DEBUG else '.'


class Resource:
    logo = f'{PATH}/res/logo.png'

    icon_exit = f'{PATH}/res/icons/exit.png'
    icon_connect = f'{PATH}/res/icons/connect.png'
    icon_unknown = f'{PATH}/res/icons/unknown.png'
    icon_phone = f'{PATH}/res/icons/phone.png'
    icon_plus = f'{PATH}/res/icons/plus.png'
    icon_up = f'{PATH}/res/icons/up.png'
    icon_ok = f'{PATH}/res/icons/ok.png'
    icon_go = f'{PATH}/res/icons/go.png'

    icon_file = f'{PATH}/res/icons/files/file.png'
    icon_folder = f'{PATH}/res/icons/files/folder.png'
    icon_file_unknown = f'{PATH}/res/icons/files/file_unknown.png'
    icon_link_file = f'{PATH}/res/icons/files/link_file.png'
    icon_link_folder = f'{PATH}/res/icons/files/link_folder.png'
    icon_link_file_unknown = f'{PATH}/res/icons/files/link_file_unknown.png'
    icon_link_file_universal = f'{PATH}/res/icons/files/link_file_universal.png'

    anim_loading = f'{PATH}/res/anim/loading.gif'
