import fnmatch
import os
import shutil
from distutils.dir_util import copy_tree


def makedirs(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if os.path.isdir(path):
            pass
        else:
            raise


def copy(src, dst):
    if os.path.exists(src):
        makedirs(dst)
        if os.path.isdir(src):
            copy_tree(src, dst)
        else:
            shutil.copy(src, dst)


def remove(src):
    if os.path.exists(src):
        if os.path.isdir(src):
            shutil.rmtree(src)
        else:
            os.remove(src)


def rotate_dirs(dirs):
    delimiter = '::rotation::'
    dirs.sort(reverse=True)
    for dir in dirs:
        suffix_list = dir.split(delimiter)[1:]
        suffix = 0 if not suffix_list else int(suffix_list[0])
        dst = dir.replace(delimiter + str(suffix), '') + delimiter + str(suffix + 1)
        shutil.move(dir, dst)


def search_recursive(root, pattern):
    result = []
    for root, dirnames, filenames in os.walk(root):
        if fnmatch.filter(dirnames, pattern):
            result.append(root.replace(root.rstrip('/') + '/', ''))
    return result
