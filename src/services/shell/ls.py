LS = "ls"


class Parameter:
    DETAILED = "-l"
    ALL = "-a"
    DIR = "-d"


class Command:
    FULL_LIST = [LS, Parameter.ALL, Parameter.DETAILED]  # + PATH
    FILE_INFO = [LS, Parameter.DIR, Parameter.DETAILED]  # + PATH
