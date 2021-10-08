#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: utils.py
@time: 2020/9/30 下午5:53
@desc: 
'''
import os
from time import time
from functools import wraps

# def SetRange(param, low, high, value):
#     full = torch.full_like(param.data, value)
#     index = torch.logical_and(param.data < high, param.data > low)
#     param.data = torch.where(index, full, param.data)
#
#
# def ClipPrecision(modules):
#     for m in modules:
#         for param in m.parameters():
#             param.data = torch.div(torch.mul(param.data, 100).int().float(), 100)
#
#         # print param
#         # for param in m.parameters():
#         #     p = param.data.cpu().numpy()
#         #     print(p)


def Walk(path, suffix:list, depth=None):
    file_list = []
    suffix = [s.lower() for s in suffix]
    if not os.path.exists(path):
        print("not exist path {}".format(path))
        return []

    if os.path.isfile(path):
        return [path,]

    count = 0
    root_depth = len(path.strip(os.path.sep).split(os.path.sep))
    for root, dirs, files in os.walk(path):
        if depth is not None and len(root.strip(os.path.sep).split(os.path.sep))-root_depth > depth:
            continue
        for file in files:
            if os.path.splitext(file)[1].lower()[1:] in suffix:
                file_list.append(os.path.join(root, file))

        count += 1

    return file_list


def MkdirSimple(path):
    path_current = path
    suffix = os.path.splitext(os.path.split(path)[1])[1]

    if suffix != "":
        path_current = os.path.dirname(path)
        if path_current in ["", "./", ".\\"]:
            return
    if not os.path.exists(path_current):
        os.makedirs(path_current)

def WriteTxt(txt, path, encoding="w"):
    MkdirSimple(path)
    with open(path, encoding) as out:
        out.write(txt)

def Timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print('[{name} spent time: {time:.2f}s]'.format(name = function.__name__,time = t1 - t0))
        return result
    return function_timer