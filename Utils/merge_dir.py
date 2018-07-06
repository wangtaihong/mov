#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-07-05 16:11:18
# @Author  : taihong (taihong.wang@androidmov.com)
# @Link    : 
# @Version : $Id$

import os
import argparse
import sys, shutil, re


def getdir_files(file_path,dirs=set([])):
    if not os.path.isdir(file_path):
        dirs.add(file_path)
        return dirs
    for f in os.listdir(file_path):
        if not os.path.isdir("/".join([file_path,f])):
            dirs.add("/".join([file_path,f]))
        else:
            getdir_files("/".join([file_path,f]),dirs)
    return dirs

def process(fs,old_dir,new_dir):
    for f in fs:
        to_file = "/".join([new_dir,re.search(old_dir+u"/(.*)",f).group(1)])
        try:
            os.makedirs(re.sub(".+/(.+)$","",to_file))
        except Exception as e:
            pass
        shutil.move(f, to_file)
        print(f, to_file)
        # return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--old_dir', type=str,help='old directory',required=True)
    parser.add_argument('--new_dir', type=str,help='new directory',required=True)
    FLAGS, unparsed = parser.parse_known_args()
    old_dir = re.sub("/$","",FLAGS.old_dir)
    new_dir = re.sub("/$","",FLAGS.new_dir)
    fs = getdir_files(old_dir)
    process(fs,old_dir,new_dir)
    