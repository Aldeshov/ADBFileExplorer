from services.data.models import File, Singleton


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

        if file.isdir and file.name:
            cls.__PATH.append(file.name)
            return True

        return False

    @classmethod
    def go(cls, file: File):
        if file.isdir and file.location:
            cls.__PATH.clear()
            for name in file.location.split('/'):
                if name:
                    cls.__PATH.append(name)
            if file.name:
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
