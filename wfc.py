import numpy
import random
import os

# Base config options
base_config_file_name = "config.cfg"
cfg_keys = [
    "file_name",
    "block_size",
    "lr_connection",
    "tb_connection"
]

cfg_types = [
    str,
    int,
    bool,
    bool
]


# Class
class LoadingConfigError(Exception):
    __not_line = "Error loading config: not {} in {} line"

    def __init__(self, error_code: int,
                 config_name: str,
                 line_in_config: int):
        message = self.__not_line.format(config_name, line_in_config)
        super(LoadingConfigError, self).__init__(message)


# Deco function
def file_exist(func):
    """

    :param func:
    :return:
    """
    def call_func(*args, **kwargs):
        if not os.path.exists(args[0]):
            raise FileExistsError
        func(*args, **kwargs)
    return call_func


# function
def load_config(file_name: str) -> tuple:
    """
    This's function return Json config.
    :param file_name:
    :return:
    """
    conf = []

    with open(file_name, "r") as file:
        line_cfg = 0
        line = 1
        while True:
            line_in_file = file.readline().strip()
            if line_cfg == len(cfg_keys):
                break

            if len(line_in_file) == 0:
                raise LoadingConfigError(0, cfg_keys[line_cfg], line)
            elif line_in_file[0] != "#":
                _, cfg_argument = (arg.strip() for arg in line_in_file.split(":"))
                conf.append(parse_to_class(cfg_types[line_cfg],
                                           cfg_argument))
                line_cfg += 1
            line += 1
        return tuple(conf)


def parse_to_class(type_arg: type,
                   arg):
    """

    :param type_arg:
    :param arg:
    :return:
    """
    if type_arg == bool:
        return
    print(type_arg.__name__, arg)
    return False


def create_config(file_name: str) -> None:
    """

    :param file_name:
    :return:
    """
    description = [
        "Name image file",
        "Size search grid",
        "Connect left and right image side",
        "Connect top and bottom image side"
    ]
    base_argument = [
        "test.png",
        "3",
        "True",
        "True"
    ]
    cfg_block = "# {}\n# Type: {}\n    {}: {}\n"
    with open(file_name, "w") as file:
        for index in range(len(cfg_keys)):
            file.write(cfg_block.format(description[index],
                                        cfg_types[index].__name__,
                                        cfg_keys[index],
                                        base_argument[index]))


if __name__ == "__main__":
    if not os.path.exists(base_config_file_name):
        create_config(base_config_file_name)

    try:
        config = load_config(base_config_file_name)
    except LoadingConfigError as error:
        print(error)
