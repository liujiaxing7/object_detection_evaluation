#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: utils.py
@time: 2020/10/29 下午5:39
@desc: 
'''
import numpy as np

def empty(box:np.ndarray):
    return box is None or 0 in box.shape

def bboxIou(bbox_a, bbox_b):
    if bbox_a.shape[1] != 4 or bbox_b.shape[1] != 4:
        raise IndexError

    # top left
    tl = np.maximum(bbox_a[:, None, :2], bbox_b[:, :2])
    # bottom right
    br = np.minimum(bbox_a[:, None, 2:], bbox_b[:, 2:])

    area_i = np.prod(br - tl, axis=2) * (tl < br).all(axis=2)
    area_a = np.prod(bbox_a[:, 2:] - bbox_a[:, :2], axis=1)
    area_b = np.prod(bbox_b[:, 2:] - bbox_b[:, :2], axis=1)
    return area_i / (area_a[:, None] + area_b - area_i)

def Format(array):
    if isinstance(array[0], list):
        return [Format(i) for i in array]
    else:
        return [round(i, 4) for i in array]

def Softmax(x, axis=1):
    row_max = x.max(axis=axis)
    x -=row_max.reshape(-1, 1) # avoid inf when exp(x)
    x_exp = np.exp(x)
    x_sum = np.sum(x_exp, axis=axis, keepdims=True)
    result = x_exp / x_sum

    return result

def partition_arg_topK(matrix, K, axis=0):
    """
    perform topK based on np.argpartition
    :param matrix: to be sorted
    :param K: select and sort the top K items
    :param axis: 0 or 1. dimension to be sorted.
    :return:
    """
    a_part = np.argpartition(matrix, K, axis=axis)
    if axis == 0:
        row_index = np.arange(matrix.shape[1 - axis])
        a_sec_argsort_K = np.argsort(matrix[a_part[0:K, :], row_index], axis=axis)
        return a_part[0:K, :][a_sec_argsort_K, row_index]
    else:
        column_index = np.arange(matrix.shape[1 - axis])[:, None]
        a_sec_argsort_K = np.argsort(matrix[column_index, a_part[:, 0:K]], axis=axis)
        return a_part[:, 0:K][column_index, a_sec_argsort_K], 0

def TopK(matrix, K, axis=1):
    """
    created at 2021.4.7 by jiao1943@qq.com
    @description:
        In the last version of this function, when axis != 0, there would be a 'dimentional explotion' problem
        Now this bug is fixed and the last version is reserved below as *TopK_old*

    """
    if axis == 0:
        row_index = np.arange(matrix.shape[1 - axis])
        topk_index = np.argpartition(-matrix, K, axis=axis)[0:K, :]
        topk_data = matrix[topk_index, row_index]
        topk_index_sort = np.argsort(-topk_data,axis=axis)
        topk_data_sort = topk_data[topk_index_sort,row_index]
        topk_index_sort = topk_index[0:K,:][topk_index_sort,row_index]
    else:
        topk_index = np.argpartition(-matrix, K-1, axis=axis)[..., 0:K]
        topk_data = matrix[..., topk_index.squeeze()]
        topk_index_sort = np.argsort(-topk_data, axis=axis)
        topk_data_sort = topk_data[..., topk_index_sort.squeeze()]
        topk_index_sort = topk_index[...,0:K][..., topk_index_sort.squeeze()]

    return topk_data_sort, topk_index_sort

def TopK_old(matrix, K, axis=1):
    if axis == 0:
        row_index = np.arange(matrix.shape[1 - axis])
        topk_index = np.argpartition(-matrix, K, axis=axis)[0:K, :]
        topk_data = matrix[topk_index, row_index]
        topk_index_sort = np.argsort(-topk_data,axis=axis)
        topk_data_sort = topk_data[topk_index_sort,row_index]
        topk_index_sort = topk_index[0:K,:][topk_index_sort,row_index]
    else:
        column_index = np.arange(matrix.shape[1 - axis])[:, None]
        topk_index = np.argpartition(-matrix, K, axis=axis)[..., 0:K]
        topk_data = matrix[column_index, topk_index]
        topk_index_sort = np.argsort(-topk_data, axis=axis)
        topk_data_sort = topk_data[column_index, topk_index_sort]
        topk_index_sort = topk_index[:,0:K][column_index,topk_index_sort]
    return topk_data_sort, topk_index_sort

def TestSoftmax():
    A = [[1, 1, 5],
         [0.2, 0.2, 0.5],
         [0, 0, 0],
         [3, 1, 0.2]]
    print("input: ".ljust(15, " "), Format(A))
    A= np.array(A)
    axis = 1

    s = Softmax(A, axis=axis)
    print("axis: ".ljust(15, " "), axis)

    np.set_printoptions(precision=3)
    print("softmax: ".ljust(15, " "), Format(s.tolist()))
    result = [[0.01766842, 0.01766842, 0.96466316],
              [0.29852004, 0.29852004, 0.40295991],
              [0.33333333, 0.33333333, 0.33333333],
              [0.8360188, 0.11314284, 0.05083836]]
    print("ground truth: ".ljust(15, " "), Format(result))