from services.data.models import File, Singleton, Communicate


class FileManager:
    __metaclass__ = Singleton

    __PATH__ = []
    __DEVICE__ = None

    @classmethod
    def path(cls):
        result = '/'
        for path in cls.__PATH__:
            result += f'{path}/'
        return result

    @classmethod
    def open(cls, file: File):
        if not cls.__DEVICE__:
            return False

        if file.isdir and file.name:
            cls.__PATH__.append(file.name)
            return True

        return False

    @classmethod
    def go(cls, file: File):
        if file.isdir and file.location:
            cls.__PATH__.clear()
            for name in file.path.split('/'):
                cls.__PATH__.append(name) if name else ''
            return True
        return False

    @classmethod
    def up(cls):
        if cls.__PATH__:
            cls.__PATH__.pop()
            return True
        return False

    @classmethod
    def get_device(cls):
        return cls.__DEVICE__

    @classmethod
    def set_device(cls, device_id):
        cls.clear_device()
        cls.__DEVICE__ = device_id

    @classmethod
    def clear_device(cls):
        cls.__DEVICE__ = None
        cls.__PATH__.clear()

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
