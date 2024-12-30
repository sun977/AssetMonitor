#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version: v2.0
    function: 检查域名情况并邮件
    date: 2024.12.25
    note:
        1. 新增域名告警  --- sec域名和 asset_dns_origin 中域名差值
        2. 域名有效性告警 --- 失效域名 落表 asset_dns
            - 域名检查加白 --- asset_dns_white 表 数据在 asset_dns 中字段置1 isWhite=1
            - 域名失效 --- asset_dns_origin 存在 但是 没有解析
            - 域名IP为CDN --- 判断IP是 cdn IP
        3. 原始域名表删除 7 天前的数据
        4. 域名解析表删除 7 天之前没有解析的域名
"""


from comm.mysql import *
from modules.DomainAssetMonitor.config.logger_config import *  # 引入日志配置
from modules.DomainAssetMonitor.sync.sync_sec_data2db import get_domain_from_sec


# 配置日志记录器
logger = setup_logger()


# 分析新增域名

