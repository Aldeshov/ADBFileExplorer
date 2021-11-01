import subprocess


def decoded(data):
    result = ""
    for line in data:
        if line:
            result += line.decode()
    return result


def run(args):
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    data = process.communicate()
    return decoded(data)
