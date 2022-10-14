import os
import time

from functools import wraps
from loguru import logger

ct = logger.level("CalcTime", no=38, color="<yellow>", icon="🐍")


def GetFileSize(path) -> float:
    """
    获取文件大小
    :param path: 路径
    :return: 文件的大小  单位KB
    """
    size = os.path.getsize(path)
    size = round(size / 1024.00, 2)
    return size


def CreateNewFolder(name):
    """在程序运行路径下创建新文件夹"""
    if not os.path.exists(name):
        os.mkdir(name)


def timefn(func):
    """计算运行耗时的修饰器"""

    @wraps(func)
    def calcTime(*args, **kwargs):
        time_begin = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()
        logger.log("CalcTime", f"运行耗时: func -> <{func.__name__}> 耗费{time_end - time_begin: .6f} s")
        return result

    return calcTime
