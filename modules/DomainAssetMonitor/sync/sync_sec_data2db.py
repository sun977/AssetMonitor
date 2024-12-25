#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version: v1.0
    function: 获取SEC域名并入库
    date: 2024.12.25
    note:
"""

from modules.SecAPI.sec.getSecApiClient import *
import dns.resolver
from comm.mysql import *
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别 详细信息
    # level=logging.INFO,  # 设置日志级别 确认程序按预期工作
    format='%(asctime)s[%(levelname)s] %(message)s',  # 设置日志格式
    datefmt='%Y-%m-%d %H:%M:%S',  # 设置日期格式
    handlers=[
        RotatingFileHandler(
            "../../../log/asset_monitor.log",  # 将日志写入文件   目录多了一级 sync 改成了 '../../../log/asset_monitor.log'
            maxBytes=20 * 1024 * 1024,  # 最大文件大小为 20MB
            backupCount=5  # 最多保留 5 个备份文件
        ),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)


# 封装数据库插入函数 -- asset_dns_origin
def insert_record_origin(domain, owner):
    """

    :param domain:
    :param owner:
    :return:
    """
    try:
        sql = (
                "INSERT INTO asset_dns_origin (domain, owner) "
                "VALUES ('%s', '%s') "
                "ON DUPLICATE KEY UPDATE "
                "domain='%s',owner='%s', updateTime=CURRENT_TIMESTAMP(6);" % (
                    domain, owner, domain, owner,  # 所有的参数都在这里
                )
        )

        # 调用mysql插入函数
        MySQL(sql=sql).exec()
        return sql
    except Exception as e:
        logging.error(f"Failed to insert record for domain {domain}, owner {owner}: {e}")


def sync_domain_from_sec2db():
    """
    从sec获取所有的主域名，生成列表
    :param:
    :return:[{xxx},{xxx}]
    """
    try:
        sec = secApiClient()  # 实例化secClient
        res = sec.get_domaininfo_lucene()  # 不带 query 参数是查询所有域名信息 数量 30087
        allMainDomainsList = []
        if res is None:
            print('sec接口返回数据为空')
            logging.warning('sec接口返回数据为空')
            return allMainDomainsList
        else:
            for item in res:
                if item.get('DomainName') not in allMainDomainsList:  # 去重获取 才14699 共30087
                    # insert_record_origin(item.get('DomainName'), item.get('PrincipalName', ''))   # owner 对应 PrincipalName
                    # logging.info(f"Inserted domain {item.get('DomainName')} into asset_dns_origin")
                    allMainDomainsList.append(
                        {'domain': item.get('DomainName'), 'owner': item.get('PrincipalName', '')})
                    # 域名直接插入数据库
        logging.info(f"Retrieved {len(allMainDomainsList)} unique domains from SEC")
        # print("allMainDomainsList:", allMainDomainsList)

        # 先获取所有域名，然后再插入数据库
        for item in allMainDomainsList:
            insert_record_origin(item.get('domain'), item.get('owner', ''))
            logging.info(f"Mysql Inserted domain {item.get('domain')} into asset_dns_origin")
        logging.info(f"Mysql Inserted {len(allMainDomainsList)} unique domains into asset_dns_origin success")

        return allMainDomainsList
    except Exception as e:
        logging.error(f"Failed to get domains from SEC: {e}")
        return []


if __name__ == '__main__':
    sync_domain_from_sec2db()
