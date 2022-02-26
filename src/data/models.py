# ADB File Explorer `tool`
# Copyright (C) 2022  Azat Aldeshov azata1919@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import typing

from PyQt5.QtWidgets import QWidget

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


class File:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name")
        self.owner: str = kwargs.get("owner")
        self.group: str = kwargs.get("group")
        self.other: str = kwargs.get("other")
        self.path: str = kwargs.get("path")
        self.link: str = kwargs.get("link")
        self.link_type: str = kwargs.get("link_type")
        self.file_type: int = kwargs.get("file_type")
        self.permissions: str = kwargs.get("permissions")

        self.__size: int = kwargs.get("size") or 0
        self.__date: datetime.datetime = kwargs.get("date_time")

    def __str__(self):
        return f"{self.name} at {self.location}"

    @property
    def size(self):
        if not self.__size:
            return ''
        count = 0
        result = self.__size
        while result >= 1024 and count < len(size_types):
            result /= 1024
            count += 1

        return f"{round(result, 2)} {size_types[count][1]}"

    @property
    def date(self):
        if not self.__date:
            return None

        created = self.__date
        now = datetime.datetime.now()
        if created.year < now.year:
            return f"{created.day} {months[created.month][1]} {created.year}"
        elif created.month < now.month:
            return f"{created.day} {months[created.month][1]}"
        elif created.day + 7 < now.day:
            return f"{created.day} {months[created.month][2]}"
        elif created.day + 1 < now.day:
            return f"{days[created.weekday()][1]} at {str(created.time())[:-3]}"
        elif created.day < now.day:
            return f"Yesterday at {str(created.time())[:-3]}"
        else:
            return f"{str(created.time())[:-3]}"

    @property
    def location(self):
        if self.path:
            return self.path[0:(self.path.rindex('/') + 1)]

    @property
    def type(self):
        for ft in file_types:
            if self.permissions and self.permissions[0] == ft[0]:
                return ft[1]
        return 'Unknown'

    @property
    def date__raw(self):
        if self.__date:
            return str(self.__date)[:-3]

    @property
    def isdir(self):
        return self.type == FileType.DIRECTORY or self.link_type == FileType.DIRECTORY


class FileType:
    FILE = 'File'
    DIRECTORY = 'Directory'
    LINK = 'Link'
    CHARACTER = 'Character'
    BLOCK = 'Block'
    SOCKET = 'Socket'
    FIFO = 'FIFO'
    UNKNOWN = 'Unknown'


class Device:
    def __init__(self, **kwargs):
        self.id: str = kwargs.get("id")
        self.name: str = kwargs.get("name")
        self.type: str = kwargs.get("type")


class DeviceType:
    DEVICE = 'device'
    UNKNOWN = 'Unknown'


class MessageData:
    def __init__(self, **kwargs):
        self.title: str = kwargs.get("title") or "Message"
        self.body: typing.Union[QWidget, str] = kwargs.get("body") or "Empty notification"
        self.timeout: int = kwargs.get("timeout") or 0
        self.message_type: int = kwargs.get("message_type") or MessageType.BASE_MESSAGE
        self.height: int = kwargs.get("height") or 125
        self.message_catcher: callable = kwargs.get("message_catcher") or None


class MessageType:
    BASE_MESSAGE = 0
    MESSAGE = 1
    LOADING_MESSAGE = 2
