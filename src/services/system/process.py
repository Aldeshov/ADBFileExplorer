import subprocess


def run(args):
    try:
        return subprocess.check_output(args).decode()
    except FileNotFoundError or subprocess.CalledProcessError:
        return False


def call(args):
    try:
        return subprocess.call(args) == 0
    except FileNotFoundError:
        return False
