import datetime

size_types = (
    ('BYTE', 'B'),
    ('KILOBYTE', 'KB'),
    ('MEGABYTE', 'MB'),
    ('GIGABYTE', 'GB'),
    ('TERABYTE', 'TB')
)

file_types = (
    ('-', 'File'),
    ('d', 'Directory'),
    ('l', 'Link'),
    ('c', 'Character'),
    ('b', 'Block'),
    ('s', 'Socket'),
    ('p', 'FIFO')
)

months = (
    ('NONE', 'None', 'None'),
    ('JANUARY', 'Jan.', 'January'),
    ('FEBRUARY', 'Feb.', 'February'),
    ('MARCH', 'Mar.', 'March'),
    ('APRIL', 'Apr.', 'April'),
    ('MAY', 'May', 'May'),
    ('JUNE', 'Jun.', 'June'),
    ('JULY', 'Jul.', 'Jule'),
    ('AUGUST', 'Aug.', 'August'),
    ('SEPTEMBER', 'Sep.', 'September'),
    ('OCTOBER', 'Oct.', 'October'),
    ('NOVEMBER', 'Nov.', 'November'),
    ('DECEMBER', 'Dec.', 'December'),
)

days = (
    ('MONDAY', 'Monday'),
    ('TUESDAY', 'Tuesday'),
    ('WEDNESDAY', 'Wednesday'),
    ('THURSDAY', 'Thursday'),
    ('FRIDAY', 'Friday'),
    ('SATURDAY', 'Saturday'),
    ('SUNDAY', 'Sunday'),
)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class File:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name")
        self._path: str = kwargs.get("path")
        self.permissions: str = kwargs.get("permissions")
        self.owner: str = kwargs.get("owner")
        self.group: str = kwargs.get("group")
        self.other: str = kwargs.get("other")

        self._date: datetime.datetime = kwargs.get("date_time")

        self._link: str = kwargs.get("link")
        self._link_type: str = kwargs.get("link_type")

        self._size: int = kwargs.get("size")

    def __str__(self):
        return f"{self.name} at {self._path}"

    @property
    def size(self):
        if self.type == FileTypes.DIRECTORY or self._link:
            return ''
        count = 0
        result = self._size
        while result >= 1024 and count < len(size_types):
            result /= 1024
            count += 1

        return f"{round(result, 2)} {size_types[count][1]}"

    @property
    def date(self):
        created = self._date
        now = datetime.datetime.now()
        if created.year < now.year:
            return f"{created.day} {months[created.month][1]} {created.year}"
        elif created.month < now.month:
            return f"{created.day} {months[created.month][1]}"
        elif created.day + 7 < now.day:
            return f"{created.day} {months[created.month][2]}"
        elif created.day + 1 < now.day:
            return f"{days[created.weekday()][1]} at {created.hour}:{created.minute}"
        elif created.day < now.day:
            return f"Yesterday at {str(created.time())[:-3]}"
        else:
            return f"{str(created.time())[:-3]}"

    @property
    def link(self):
        return self._link

    @property
    def link_type(self):
        return self._link_type

    @property
    def type(self):
        for ft in file_types:
            if self.permissions[0] == ft[0]:
                return ft[1]
        return 'Unknown'

    @property
    def date_raw(self):
        return str(self._date)


class FileTypes:
    FILE = 'File'
    DIRECTORY = 'Directory'
    LINK = 'Link'
    CHARACTER = 'Character'
    BLOCK = 'Block'
    SOCKET = 'Socket'
    UNKNOWN = 'Unknown'


class Device:
    def __init__(self, **kwargs):
        self.id: str = kwargs.get("id")
        self.name: str = kwargs.get("name")
        self.type: str = kwargs.get("type")
