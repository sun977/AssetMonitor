#!/usr/bin/env python3
# _*_ coding: utf-8 _*_


"""
auth: sunhaobo
version:
function:
usage:
note:
"""

import hashlib  # 哈希
import json
import os

current_abs_path = os.path.abspath(__file__)  # 当前文件 getconfig.py 的位置
current_abs_path_dir = os.path.dirname(current_abs_path)  # 当前目录
config_path = os.path.abspath(current_abs_path_dir) + '/../config/config.json'  # 从当前目录找到配置文件 config.json 的位置
# logfile = os.path.abspath(current_abs_path_dir) + '/../log/run.log'  # 从当前目录找到配置文件 run.log 的位置
config_md5 = os.path.abspath(current_abs_path_dir) + '/../config/config.md5'  # 从当前目录找到配置文件 config.md5 的位置


# 获取配置文件函数
def get_config(file=config_path):
    with open(file, 'r', encoding="utf-8") as config:
        contents = config.read()  # 读取文件内容
        data = json.loads(contents)  # 使用 json 库格式化文件内容
        return data  # 返回json格式的配置文件


def get_config_change_status(file=config_path):
    config_md5_file = config_md5
    with open(config_md5_file, 'r') as md5_file:
        contents = md5_file.readlines()
        config_file_md5_old = contents[0]  # md5文件中的md5值不能为空

    hash_code = hashlib.md5(open(config_path, 'rb').read()).hexdigest()
    config_file_md5_new = str(hash_code).lower()

    if config_file_md5_new == config_file_md5_old:
        return {
            'state': 0,  # 0 说明配置文件的md5没变
            'msg': 'config not changed',
            'md5': 'md5_old: %s, md5_new: %s' % (config_file_md5_old, config_file_md5_new)
        }
    else:
        with open(config_md5_file, 'r+') as f:
            f.seek(0)
            f.truncate()
            f.write(config_file_md5_new)

        return {
            'state': 1,  # 1 说明配置文件的md5改变
            'msg': 'config changed, you should reload process',
            'md5': 'md5_old: %s, md5_new: %s' % (config_file_md5_old, config_file_md5_new)
        }


if __name__ == '__main__':
    # res = get_config_change_status()
    res = get_config()
    print(res)
