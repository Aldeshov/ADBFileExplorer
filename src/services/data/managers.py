from services.data.models import File, FileTypes, Singleton


class FileManager:
    __metaclass__ = Singleton

    __DEVICE = None

    __PATH = []
    __HISTORY = []

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

        if file.type == FileTypes.DIRECTORY:
            cls.__PATH.append(file.name)
            return True
        elif file.link_type == FileTypes.DIRECTORY:
            cls.__PATH.append(file.name)
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
