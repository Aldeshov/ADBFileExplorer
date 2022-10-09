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
import posixpath

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
    ('JULY', 'Jul.', 'July'),
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
        self.name = str(kwargs.get("name"))
        self.owner = str(kwargs.get("owner"))
        self.group = str(kwargs.get("group"))
        self.other = str(kwargs.get("other"))
        self.path = str(kwargs.get("path"))
        self.link = str(kwargs.get("link"))
        self.link_type = str(kwargs.get("link_type"))
        self.file_type = str(kwargs.get("file_type"))
        self.permissions = str(kwargs.get("permissions"))

        self.raw_size = kwargs.get("size") or 0
        self.raw_date = kwargs.get("date_time")

    def __str__(self):
        return "%s '%s' (at '%s')" % (self.type, self.name, self.location)

    @property
    def size(self):
        if not self.raw_size:
            return ''
        count = 0
        result = self.raw_size
        while result >= 1024 and count < len(size_types):
            result /= 1024
            count += 1

        return '%s %s' % (round(result, 2), size_types[count][1])

    @property
    def date(self):
        if not self.raw_date:
            return None

        created = self.raw_date
        now = datetime.datetime.now()
        if created.year < now.year:
            return '%s %s %s' % (created.day, months[created.month][1], created.year)
        elif created.month < now.month:
            return '%s %s' % (created.day, months[created.month][1])
        elif created.day + 7 < now.day:
            return '%s %s' % (created.day, months[created.month][2])
        elif created.day + 1 < now.day:
            return '%s at %s' % (days[created.weekday()][1], str(created.time())[:-3])
        elif created.day < now.day:
            return "Yesterday at %s" % str(created.time())[:-3]
        else:
            return str(created.time())[:-3]

    @property
    def location(self):
        return posixpath.dirname(self.path or '') + '/'

    @property
    def type(self):
        for ft in file_types:
            if self.permissions and self.permissions[0] == ft[0]:
                return ft[1]
        return 'Unknown'

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
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.type = kwargs.get("type")


class DeviceType:
    DEVICE = 'device'
    UNKNOWN = 'Unknown'


class MessageData:
    def __init__(self, **kwargs):
        self.timeout = kwargs.get("timeout") or 0
        self.title = kwargs.get("title") or "Message"
        self.body = kwargs.get("body")
        self.message_type = kwargs.get("message_type") or MessageType.MESSAGE
        self.message_catcher = kwargs.get("message_catcher") or None


class MessageType:
    MESSAGE = 1
    LOADING_MESSAGE = 2
