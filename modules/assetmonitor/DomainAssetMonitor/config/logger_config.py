# !/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version: v1.0
    function: 统一的日志输出配置文件 适用模块 DomainAssetMonitor
    date: 2025.01.22
    note:
        1、引入
        2、logger = setup_logger() 初始化
        3、logger.info() 调用
"""

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    current_abs_path = os.path.abspath(__file__)
    current_abs_path_dir = os.path.dirname(current_abs_path)
    log_dir_path = os.path.abspath(current_abs_path_dir) + '/../../../../log/'   # 20250122 目录归档，又添加了一级目录

    # 确保日志目录存在
    if not os.path.exists(log_dir_path):
        os.makedirs(log_dir_path)

    logger = logging.getLogger('asset_monitor')
    logger.setLevel(logging.DEBUG)  # 设置日志等级

    # 避免重复配置
    if not logger.hasHandlers():
        formatter = logging.Formatter('%(asctime)s[%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        file_handler = RotatingFileHandler(
            log_dir_path + "/asset_monitor.log",
            maxBytes=20 * 1024 * 1024,  # 最大文件大小为 20MB
            backupCount=5   # 最多保留 5 个备份文件
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()  # 同时输出到控制台
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


