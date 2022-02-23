import subprocess

from gevent import thread


def test_process(arguments: list):
    popen = subprocess.Popen(executable="adb", args=arguments, stderr=subprocess.PIPE)

    exp_size = 8704660
    while True:
        thread.sleep(0.25)
        run = subprocess.run(executable="adb", stdout=subprocess.PIPE, args="adb shell ls -l /sdcard/file".split(' '))
        if run.stdout and run.stdout.decode().split()[3].isdigit():
            size = int(run.stdout.decode().split()[3])
            print(f"{int(size / exp_size * 100)}%")
            if size == exp_size:
                break

    print(popen.communicate())

# test_process("adb push /sdcard/file ~/file".split(' '))
