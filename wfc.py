import numpy
from PIL import Image
import matplotlib.pyplot as plt
import random
import os

import sys

# Base config options
base_config_file_name = "config.cfg"
cfg_keys = [
    "file_name",
    "grid_size",
    "lr_connection",
    "tb_connection",
    "normal",
    "normal_flip",
    "rotate_90",
    "rotate_90_flip",
    "rotate_180",
    "rotate_180_flip",
    "rotate_270",
    "rotate_270_flip",
    "new_image_name",
    "new_image_count",
    "new_image_weight",
    "new_image_height",

]

cfg_types = [
    str,
    int,
    *[bool for _ in range(10)],
    str,
    *[int for _ in range(3)]
]


# Class
class LoadingConfigError(Exception):
    __not_line = "Error loading config: not {} in {} line"
    __wrong_name = "Error loading config: wrong argument in {} line"
    __wrong_type = "Error loading config: wrong type argument in {} line"

    def __init__(self, error_code: int,
                 config_name: str,
                 line_in_config: int):
        message = ""
        if error_code == 0:
            message = self.__not_line.format(config_name, line_in_config)
        elif error_code == 1:
            message = self.__wrong_name.format(line_in_config)
        elif error_code == 2:
            message = self.__wrong_type.format(line_in_config)
        super(LoadingConfigError, self).__init__(message)


# function
def load_config(file_name: str) -> tuple:
    """
    This's function return config.
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
                cfg_key, cfg_argument = (arg.strip() for arg in line_in_file.split(":"))
                if cfg_key != cfg_keys[line_cfg]:
                    raise LoadingConfigError(1, "", line)
                conf.append(parse_to_class(cfg_types[line_cfg],
                                           cfg_argument,
                                           line))
                line_cfg += 1
            line += 1
        return tuple(conf)


def parse_to_class(type_arg: type,
                   arg,
                   line: int):
    """
    Convert data to type
    :param type_arg:
    :param arg:
    :param line:
    :return:
    """
    if type_arg == str:
        return arg
    elif type_arg == int:
        if arg.isdigit():
            return int(arg)
        else:
            raise LoadingConfigError(2, "", line)
    elif type_arg == bool:
        if arg == ("True" or "False"):
            return bool(arg)
        else:
            raise LoadingConfigError(2, "", line)


def create_config(file_name: str) -> None:
    """

    :param file_name:
    :return:
    """
    description = [
        "Name image file",
        "Size search grid",
        "Connect left and right image side",
        "Connect top and bottom image side",
        *["" for _ in range(10)],
        "Name new image",
        "How many image need creates",
        "New image weight",
        "New image height",
    ]
    base_argument = [
        "test.png",
        "3",
        *["True" for _ in range(10)],
        "new.png",
        "1",
        "40",
        "40",
    ]
    cfg_block = "# {}\n# Type: {}\n    {}: {}\n"
    with open(file_name, "w") as file:
        for index in range(len(cfg_keys)):
            file.write(cfg_block.format(description[index],
                                        cfg_types[index].__name__,
                                        cfg_keys[index],
                                        base_argument[index]))


def crop_image(file_name: str,
               size_grid: int,
               lr_connection: bool,
               tb_connection: bool,
               *accepted_rotate: bool) -> tuple:
    """

    :param file_name:
    :param size_grid:
    :param lr_connection:
    :param tb_connection:
    :param accepted_rotate:
    :return:
    """
    numpy_image = image_to_numpy_array(file_name)
    image_clip = numpy.array([numpy_image[0:size_grid, 0:size_grid]], dtype=int)
    image_clip_chance = numpy.array([1], dtype=int)
    for iter1 in range(numpy_image.shape[0] - (size_grid - 1) * (not tb_connection)):
        for iter2 in range(numpy_image.shape[1] - (size_grid - 1) * (not lr_connection)):
            # all
            if iter1 + size_grid > numpy_image.shape[0] and iter2 + size_grid > numpy_image.shape[1]:
                part = numpy.append(numpy.append(numpy_image[iter1:iter1 + size_grid, iter2:iter2 + size_grid],
                                                 numpy_image[0:iter1 + size_grid - numpy_image.shape[0],
                                                 iter2:iter2 + size_grid], 0),
                                    numpy.append(numpy_image[iter1:iter1 + size_grid,
                                                 0:iter2 + size_grid - numpy_image.shape[1]],
                                                 numpy_image[0:iter1 + size_grid - numpy_image.shape[0],
                                                 0:iter2 + size_grid - numpy_image.shape[1]], 0),
                                    1)
            # lr
            elif iter2 + size_grid > numpy_image.shape[1]:
                part = numpy.append(numpy_image[iter1:iter1 + size_grid, iter2:iter2 + size_grid],
                                    numpy_image[iter1:iter1 + size_grid, 0:iter2 + size_grid - numpy_image.shape[1]], 1)
            # tb
            elif iter1 + size_grid > numpy_image.shape[0]:
                part = numpy.append(numpy_image[iter1:iter1 + size_grid, iter2:iter2 + size_grid],
                                    numpy_image[0:iter1 + size_grid - numpy_image.shape[0], iter2:iter2 + size_grid], 0)
            else:
                part = numpy_image[iter1:iter1 + size_grid, iter2:iter2 + size_grid]

            # 0
            if accepted_rotate[0]:
                array_in = array_in_array(part, image_clip)
                if not any(array_in):
                    image_clip = numpy.append(image_clip, [part], 0)
                    image_clip_chance = numpy.append(image_clip_chance, [1])
                else:
                    image_clip_chance[array_in.index(True)] += 1
            if accepted_rotate[1]:
                part_flip = numpy.flip(part, 0)
                array_in = array_in_array(part_flip, image_clip)
                if not any(array_in):
                    image_clip = numpy.append(image_clip, [part_flip], 0)
                    image_clip_chance = numpy.append(image_clip_chance, [1])
                else:
                    image_clip_chance[array_in.index(True)] += 1
            # 90
            part = numpy.rot90(part)
            if accepted_rotate[2]:
                array_in = array_in_array(part, image_clip)
                if not any(array_in):
                    image_clip = numpy.append(image_clip, [part], 0)
                    image_clip_chance = numpy.append(image_clip_chance, [1])
                else:
                    image_clip_chance[array_in.index(True)] += 1
            if accepted_rotate[3]:
                part_flip = numpy.flip(part, 0)
                array_in = array_in_array(part_flip, image_clip)
                if not any(array_in):
                    image_clip = numpy.append(image_clip, [part_flip], 0)
                    image_clip_chance = numpy.append(image_clip_chance, [1])
                else:
                    image_clip_chance[array_in.index(True)] += 1
            # 180
            part = numpy.rot90(part)
            if accepted_rotate[4]:
                array_in = array_in_array(part, image_clip)
                if not any(array_in):
                    image_clip = numpy.append(image_clip, [part], 0)
                    image_clip_chance = numpy.append(image_clip_chance, [1])
                else:
                    image_clip_chance[array_in.index(True)] += 1
            if accepted_rotate[5]:
                part_flip = numpy.flip(part, 0)
                array_in = array_in_array(part_flip, image_clip)
                if not any(array_in):
                    image_clip = numpy.append(image_clip, [part_flip], 0)
                    image_clip_chance = numpy.append(image_clip_chance, [1])
                else:
                    image_clip_chance[array_in.index(True)] += 1
            # 270
            part = numpy.rot90(part)
            if accepted_rotate[6]:
                array_in = array_in_array(part, image_clip)
                if not any(array_in):
                    image_clip = numpy.append(image_clip, [part], 0)
                    image_clip_chance = numpy.append(image_clip_chance, [1])
                else:
                    image_clip_chance[array_in.index(True)] += 1
            if accepted_rotate[7]:
                part_flip = numpy.flip(part, 0)
                array_in = array_in_array(part_flip, image_clip)
                if not any(array_in):
                    image_clip = numpy.append(image_clip, [part_flip], 0)
                    image_clip_chance = numpy.append(image_clip_chance, [1])
                else:
                    image_clip_chance[array_in.index(True)] += 1

    print(image_clip.shape)
    return image_clip, image_clip_chance


def array_in_array(array1: numpy.ndarray,
                   array2: numpy.ndarray) -> tuple:
    return tuple((array1 == array2).all(-1).all(-1).all(-1))


def image_to_numpy_array(file_name: str) -> numpy.ndarray:
    """

    :param file_name:
    :return:
    """
    with Image.open(file_name) as image:
        numpy_image = numpy.array(image)
    if numpy_image.shape[-1] == 4:
        numpy_image = numpy_image[:, :, 0:3]
    return numpy_image


if __name__ == "__main__":
    if not os.path.exists(base_config_file_name):
        create_config(base_config_file_name)
        exit()

    try:
        config = load_config(base_config_file_name)
    except LoadingConfigError as error:
        print(error)
        exit()

    if not os.path.exists(config[0]):
        print("Image not found")
        exit()

    crop_image(*config[:12])
