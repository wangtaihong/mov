#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-01 11:20:41
# @Author  : taihong (wangtaihong1@gmail.com)
# @Link    : citybrain.top
# @Version : $Id$

# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import requests

# 容错最大的有色判断
MAX_RGB_VALUE = 20
# 噪点大小
MAX_NOISY_COUNT = 25

# RGBA白色定义
WHITE_COLOR = (255, 255, 255, 255)
# RGBA黑色定义
BLACK_COLOR = (0, 0, 0, 255)


def print_char_pic(width, height, s_data):
    """
    画出字符图, 空格为白色, 点为黑色
    """
    _pic_str = ''
    for y in range(0, height):
        for x in range(0, width):
            _point = s_data[y * width + x]
            if _point == WHITE_COLOR:
                _pic_str += ' '
            else:
                _pic_str += '*'
        _pic_str += '\n'

    print _pic_str


def gen_white_black_points(image):
    """
    根据点阵颜色强制转换黑白点
    """
    data = image.getdata()
    new_data = []
    for item in data:
        if item[0] > MAX_RGB_VALUE and item[1] > MAX_RGB_VALUE and item[2] > MAX_RGB_VALUE:
            new_data.append(WHITE_COLOR)
        else:
            new_data.append(BLACK_COLOR)
    return new_data


def reduce_noisy(width, height, points):
    """
    横向扫描, 获取最大边界大小. 除去小于最大噪点大小的面积.
    """
    # 标记位置, 初始化都是0, 未遍历过
    flag_list = []
    for i in xrange(width * height):
        flag_list.append(0)

    # 遍历
    for index, value in enumerate(points):
        _y = index // width
        _x = index - _y * width
        # print _x, _y
        if flag_list[index] == 0 and value == BLACK_COLOR:
            flag_list[index] = 1
            _tmp_list = [index]
            recursion_scan_black_point(
                _x, _y, width, height, _tmp_list, flag_list, points)
            if len(_tmp_list) <= MAX_NOISY_COUNT:
                for x in _tmp_list:
                    points[x] = WHITE_COLOR

        else:
            flag_list[index] = 1


def recursion_scan_black_point(x, y, width, height, tmp_list, flag_list, points):
        # 左上
    if 0 <= (x - 1) < width and 0 <= (y - 1) < height:
        _x = x - 1
        _y = y - 1
        _inner_recursion(_x, _y, width, height, tmp_list, flag_list, points)

    # 上
    if 0 <= (y - 1) < height:
        _x = x
        _y = y - 1
        _inner_recursion(_x, _y, width, height, tmp_list, flag_list, points)

    # 右上
    if 0 <= (x + 1) < width and 0 <= (y - 1) < height:
        _x = x + 1
        _y = y - 1
        _inner_recursion(_x, _y, width, height, tmp_list, flag_list, points)

    # 左
    if 0 <= (x - 1) < width:
        _x = x - 1
        _y = y
        _inner_recursion(_x, _y, width, height, tmp_list, flag_list, points)

    # 右
    if 0 <= (x + 1) < width:
        _x = x + 1
        _y = y
        _inner_recursion(_x, _y, width, height, tmp_list, flag_list, points)

    # 左下
    if 0 <= (x - 1) < width and 0 <= (y + 1) < height:
        _x = x - 1
        _y = y + 1
        _inner_recursion(_x, _y, width, height, tmp_list, flag_list, points)

    # 下
    if 0 <= (y + 1) < height:
        _x = x
        _y = y + 1
        _inner_recursion(_x, _y, width, height, tmp_list, flag_list, points)

    # 右下
    if 0 <= (x + 1) < width and 0 <= (y + 1) < height:
        _x = x + 1
        _y = y + 1
        _inner_recursion(_x, _y, width, height, tmp_list, flag_list, points)


def _inner_recursion(new_x, new_y, width, height, tmp_list, flag_list, points):
    _index = new_x + width * new_y
    if flag_list[_index] == 0 and points[_index] == BLACK_COLOR:
        tmp_list.append(_index)
        flag_list[_index] = 1
        recursion_scan_black_point(
            new_x, new_y, width, height, tmp_list, flag_list, points)
    else:
        flag_list[_index] = 1


def download(imgurl, path='./tmp/', timeout=3.5):
    filename = path + imgurl.split('=')[-1]
    r = requests.get(imgurl, stream=True, timeout=timeout)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):  # 分片write图片
            if chunk:
                f.write(chunk)
                f.flush()
        f.close()
    return filename


def recognize_url(url):
	filename = download(imgurl=url)
	img = Image.open(filename)
	img = img.convert('RGBA')
	w, h = img.size[0], img.size[1]
	point_list = gen_white_black_points(img)
	reduce_noisy(w, h, point_list)
	img.putdata(point_list)
	os.remove(filename)
	return pytesseract.image_to_string(img)

def recognize(filename):
    img = Image.open(filename)
    img = img.convert('RGBA')
    w, h = img.size[0], img.size[1]
    point_list = gen_white_black_points(img)
    reduce_noisy(w, h, point_list)

    img.putdata(point_list)
    os.remove(filename)
    return pytesseract.image_to_string(img)
