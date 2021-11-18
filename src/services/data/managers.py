from services.data.models import File, Singleton, Communicate


class FileManager:
    __metaclass__ = Singleton

    __DEVICE = None

    __PATH = []

    @classmethod
    def path(cls):
        result = '/'
        for p in cls.__PATH:
            result += f'{p}/'
        return result

    @classmethod
    def open(cls, file: File):
        if not cls.__DEVICE:
            return False

        if file.isdir and file.name:
            cls.__PATH.append(file.name)
            return True

        return False

    @classmethod
    def go(cls, file: File):
        if file.isdir and file.location:
            cls.__PATH.clear()
            for name in file.path.split('/'):
                cls.__PATH.append(name) if name else ''
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

    @staticmethod
    def clear_path(path: str) -> str:
        result = ''
        array = path.split('/')
        for name in array:
            result += f'/{name}' if name else ''
        if not result:
            return '/'
        return result


class Global:
    __metaclass__ = Singleton
    communicate = Communicate()
