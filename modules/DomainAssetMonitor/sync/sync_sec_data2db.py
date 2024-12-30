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
from comm.mysql import *
from modules.DomainAssetMonitor.config.logger_config import *  # 引入日志配置

# 配置日志记录器
logger = setup_logger()

# 从sec平台获取所有的主域名，生成列表
def get_domain_from_sec():
    """
    从sec获取所有的主域名，生成列表【弃用，改为从表中获取域名】
    :param:
    :return:['xxx','xxx']
    """
    allMainDomainsList = []
    try:
        sec = secApiClient()  # 实例化secClient
        res = sec.get_domaininfo_lucene()  # 不带 query 参数是查询所有域名信息 数量 30087
        # allMainDomainsList = []
        if res is None:
            # print('sec接口返回数据为空')
            logger.warning('sec接口返回数据为空')
            return allMainDomainsList
        else:
            for domain in res:
                if domain.get('DomainName') not in allMainDomainsList:
                    # 去重获取 才14699 共30087 有重复的？ 对，sec有重复域名，域名解析多个IP的算多个
                    allMainDomainsList.append(domain.get('DomainName'))
        logger.info(f"Retrieved {len(allMainDomainsList)} unique domains from SEC")
        return allMainDomainsList
    except Exception as e:
        logger.error(f"Failed to get domains from SEC: {e}")
        return allMainDomainsList


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
        logger.error(f"Failed to insert record for domain {domain}, owner {owner}: {e}")


# 同步SEC接口数据和原始域名表数据
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
            logger.warning('sec接口返回数据为空')
            return allMainDomainsList
        else:
            for item in res:
                if item.get('DomainName') not in allMainDomainsList:  # 去重获取 才14699 共30087
                    # insert_record_origin(item.get('DomainName'), item.get('PrincipalName', ''))   # owner 对应 PrincipalName
                    # logger.info(f"Inserted domain {item.get('DomainName')} into asset_dns_origin")
                    allMainDomainsList.append(
                        {'domain': item.get('DomainName'), 'owner': item.get('PrincipalName', '')})
                    # 域名直接插入数据库
        logger.info(f"Retrieved {len(allMainDomainsList)} unique domains from SEC")
        # print("allMainDomainsList:", allMainDomainsList)

        # 先获取所有域名，然后再插入数据库
        for item in allMainDomainsList:
            insert_record_origin(item.get('domain'), item.get('owner', ''))
            logger.info(f"Mysql Inserted domain {item.get('domain')} into asset_dns_origin")
        logger.info(f"Mysql Inserted {len(allMainDomainsList)} unique domains into asset_dns_origin success")

        return allMainDomainsList
    except Exception as e:
        logger.error(f"Failed to get domains from SEC: {e}")
        return []


if __name__ == '__main__':
    sync_domain_from_sec2db()
