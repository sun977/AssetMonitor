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


# 从数据库获取域名数据
def get_domain_from_db():
    """
    从 asset_dns_origin 获取 域名
    :return:['xxx','xxx']
    """
    allDomainsList = []
    try:
        sql = (
            "SELECT domain FROM asset_dns_origin"  # 获取原始表中所有域名数据
        )
        resOrigindomains = MySQL(sql=sql).exec()
        if resOrigindomains.get('state') == 1:
            for item in resOrigindomains.get('data'):
                allDomainsList.append(item.get('domain'))
            logger.info(f"modules.DomainAssetMonitor.domian_asset_check.get_domain_from_db() Retrieved {len(allDomainsList)} domains from asset_dns_origin")
            return allDomainsList
        else:
            logger.warning(f"modules.DomainAssetMonitor.domian_asset_check.get_domain_from_db() Failed to retrieve domains from asset_dns_origin: {resOrigindomains.get('msg')}")
    except Exception as e:
        logger.error(f"modules.DomainAssetMonitor.domian_asset_check.get_domain_from_db() Failed to get domains from asset_dns_origin: {e}")
        return allDomainsList

# 对比SEC接口和 asset_dns_origin 表 提取新增域名
def new_add_domains():
    """
    对比sec接口域名数据和数据库表中的域名数据  返回在sec接口里面的域名 但是不在db表里面的数据字典
    如果有新增域名就返回新增域名
    :param:
    :return:[{},{}]   # 返回 域名 + 所属人
    """
    newAddDomains = []   # 存放新增的域名
    domainsFromSecList = get_domain_from_sec()  # [{},{}] # {'domain': item.get('DomainName'), 'owner': item.get('PrincipalName', '')}
    domainsFromDbList = get_domain_from_db()  # ['','']
    try:
        if domainsFromSecList and domainsFromDbList:  # 如果两个表都有数据
            # domainsFromSecList = [item.get('domain') for item in domainsFromSecList]
            # 遍历 domainsFromSecList 列表，判断是否在 domainsFromDbList 中
            for item in domainsFromSecList:
                if item.get('domain') not in domainsFromDbList:
                    newAddDomains.append(item)
                    logger.info(f"modules.DomainAssetMonitor.domian_asset_check.new_add_domains() New domain {item.get('domain')} found from SEC")
                else:
                    logger.info(f"modules.DomainAssetMonitor.domian_asset_check.new_add_domains() Domain {item.get('domain')} already exists in asset_dns_origin")
        else:
            logger.warning(f"modules.DomainAssetMonitor.domian_asset_check.new_add_domains() No domains found in asset_dns_origin or SEC")
            newAddDomains = []
        logger.info(f"modules.DomainAssetMonitor.domian_asset_check.new_add_domains() Found {len(newAddDomains)} new domains from SEC")
    except Exception as e:
        logger.error(f"modules.DomainAssetMonitor.domian_asset_check.new_add_domains() Failed to compare domains: {e}")

    return newAddDomains


if __name__ == '__main__':
    res = new_add_domains()
    print(res)


