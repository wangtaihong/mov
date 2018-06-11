#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-06-04 08:43:13
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

from PIL import Image

class ImgProcess(object):
	"""docstrinImgProcessssName"""
	def __init__(self, **arg):
		# super(ClassNameImgProcess_init__()
		# self.arg = arg
		pass

	@staticmethod
	def ImageToJpg(input_img="C:/Users/Administrator/Desktop/pos1.png",output_img="C:/Users/Administrator/Desktop/pos1.jpg"):
		im = Image.open(input_img)
		rgb_im = im.convert('RGB')
		rgb_im.save(output_img)


if __name__ == '__main__':
	ImgProcess.ImageToJpg()
		