from services.models import File, FileTypes, Singleton


class FileManager:
    __metaclass__ = Singleton

    __DEVICE = None

    __PATH = []
    __HISTORY = []

    @classmethod
    def path(cls):
        if not cls.__PATH:
            return '/'

        result = ''
        for p in cls.__PATH:
            result += f'/{p}'
        return result

    @classmethod
    def open(cls, file: File):
        if file.type == FileTypes.DIRECTORY:
            cls.__PATH.append(file.name)
            return True
        if file.link_type == FileTypes.DIRECTORY:
            if file.link[0] == '/':
                cls.__PATH = file.link.split('/')
                cls.__PATH.remove('')
                return True
            for p in file.link.split('/'):
                if p == '..':
                    cls.__PATH.pop()
                elif p != '.':
                    cls.__PATH.append(p)
                return True
        return False

    @classmethod
    def up(cls):
        if cls.__PATH:
            cls.__PATH.pop()
            return True
        return False

    @classmethod
    def get_device(cls):
        return cls.__DEVICE

    @classmethod
    def set_device(cls, device_id):
        cls.clear_device()
        cls.__DEVICE = device_id

    @classmethod
    def clear_device(cls):
        cls.__DEVICE = None
        cls.__PATH.clear()
        cls.__HISTORY.clear()
