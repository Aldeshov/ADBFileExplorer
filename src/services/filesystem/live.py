import subprocess
import sys

from services.models import Singleton


class LiveProcess:
    __metaclass__ = Singleton

    __process: subprocess.Popen = None

    @classmethod
    def run(cls, args):
        try:
            cls.__process = subprocess.Popen(args)
        except FileNotFoundError:
            print('NOT FOUND')
            return False

    @classmethod
    def get(cls):
        if cls.__process and cls.__process.stdout:
            return cls.__process.stdout.readline()
