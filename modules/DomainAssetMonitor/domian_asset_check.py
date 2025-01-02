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
        3. 原始域名表删除 14 天前的数据
        4. 域名解析表删除 14 天之前没有解析的域名
        5. 邮件告警
"""

from comm.mysql import *
from modules.DomainAssetMonitor.config.logger_config import *  # 引入日志配置
from modules.DomainAssetMonitor.sync.sync_sec_data2db import get_domain_from_sec

# 配置日志记录器
logger = setup_logger()


# 从数据库中获取域名数据
def select_data_from_db(sql, columnName):
    """
    根据sql从数据库中获取数据 ,根据字段去重
    SQL: SELECT domain, owner FROM asset_dns_origin
    :param sql: string
    :param columnName: string
    :return:[{},{}]
    """
    resDataList = []
    try:
        res = MySQL(sql=sql).exec()
        logger.info(f"modules.DomainAssetMonitor.domian_asset_check.select_data_from_db() SQL:{sql}")
        logger.info(f"modules.DomainAssetMonitor.domian_asset_check.select_data_from_db() Retrieved {len(res.get('data'))} data from db")
        if res.get('state') == 1:
            for item in res.get('data'):
                if item.get(columnName) not in resDataList:  # 根据columnName字段去重
                    resDataList.append(item)
            return resDataList
        else:
            logger.warning(f"modules.DomainAssetMonitor.domian_asset_check.select_data_from_db() Failed to retrieve data from db: {res.get('msg')}")
            return resDataList
    except Exception as e:
        logger.error(f"modules.DomainAssetMonitor.domian_asset_check.select_data_from_db() Failed to get data from db: {e}")
        return resDataList


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
            logger.info(
                f"modules.DomainAssetMonitor.domian_asset_check.get_domain_from_db() Retrieved {len(allDomainsList)} domains from asset_dns_origin")
            return allDomainsList
        else:
            logger.warning(f"modules.DomainAssetMonitor.domian_asset_check.get_domain_from_db() Failed to retrieve domains from asset_dns_origin: {resOrigindomains.get('msg')}")
    except Exception as e:
        logger.error(f"modules.DomainAssetMonitor.domian_asset_check.get_domain_from_db() Failed to get domains from asset_dns_origin: {e}")
        return allDomainsList


# 对比SEC接口和 asset_dns_origin 表 提取新增域名 每天执行一次 执行结果发送邮件告知
def new_add_domains():
    """
    对比sec接口域名数据和数据库表中的域名数据  返回在sec接口里面的域名 但是不在db表里面的数据字典
    如果有新增域名就返回新增域名
    :param:
    :return:[{},{}]   # 返回 域名 + 所属人 [{'domain': 'imsa.comisys.net', 'owner': '党羽'}]
    """
    newAddDomains = []  # 存放新增的域名
    domainsFromSecList = get_domain_from_sec()  # [{},{}] # {'domain': item.get('DomainName'), 'owner': item.get('PrincipalName', '')}
    domainsFromDbList = get_domain_from_db()  # ['','']
    try:
        if domainsFromSecList and domainsFromDbList:  # 如果两个表都有数据
            # domainsFromSecList = [item.get('domain') for item in domainsFromSecList]
            # 遍历 domainsFromSecList 列表，判断是否在 domainsFromDbList 中
            for item in domainsFromSecList:
                if item.get('domain') not in domainsFromDbList:
                    newAddDomains.append(item)
                    logger.info(
                        f"modules.DomainAssetMonitor.domian_asset_check.new_add_domains() New domain {item.get('domain')} found from SEC")
                else:
                    logger.info(
                        f"modules.DomainAssetMonitor.domian_asset_check.new_add_domains() Domain {item.get('domain')} already exists in asset_dns_origin")
        else:
            logger.warning(
                f"modules.DomainAssetMonitor.domian_asset_check.new_add_domains() No domains found in asset_dns_origin or SEC")
            newAddDomains = []
        logger.info(
            f"modules.DomainAssetMonitor.domian_asset_check.new_add_domains() Found {len(newAddDomains)} new domains from SEC")
    except Exception as e:
        logger.error(f"modules.DomainAssetMonitor.domian_asset_check.new_add_domains() Failed to compare domains: {e}")

    return newAddDomains

# 失效域名检测
def check_invalid_domains():
    """
    检查 asset_dns_origin 表中失效域名
    有原始域名但是没有解析的域名 --- 在 asset_dns_origin 表，不在 asset_dns_records 表
    落表 asset_dns 域名 + 域名无效 + 备注（所属人）
    :param:
    :return:[{},{}]  # 返回 域名 + 所属人 [{'domain': 'imsa.comisys.net', 'owner': '党羽'}]
    """
    invalidDomains = []
    try:
        # 只查询需要的列
        domainsOriginList = select_data_from_db("SELECT domain, owner FROM asset_dns_origin", "domain")
        domainsRecordsList = select_data_from_db("SELECT domain, updateTime FROM asset_dns_records", "domain")

        if not domainsOriginList:   # 如果 asset_dns_origin 表没有数据
            logger.warning("modules.DomainAssetMonitor.domian_asset_check.check_invalid_domains() No domains found in asset_dns_origin")
            return invalidDomains

        if not domainsRecordsList:  # 如果 asset_dns_records 表没有数据
            logger.warning("modules.DomainAssetMonitor.domian_asset_check.check_invalid_domains() No domains found in asset_dns_records")
            return invalidDomains

        # 将 domainsRecordsList 转换为集合，提高查找效率
        domainsRecordsSet = {item.get('domain') for item in domainsRecordsList}

        # 遍历 domainsOriginList，判断是否在 domainsRecordsSet 中
        for item in domainsOriginList:
            domain = item.get('domain')  # 只取 domain 字段判断
            if domain not in domainsRecordsSet:   # 如果 在 domainsOriginList 不在 asset_dns_records 表
                invalidDomains.append(item)
                logger.info(f"modules.DomainAssetMonitor.domian_asset_check.check_invalid_domains() Domain {domain} is invalid")
        logger.info(f"modules.DomainAssetMonitor.domian_asset_check.check_invalid_domains() Found {len(invalidDomains)} invalid domains")
    except Exception as e:
        logger.error(f"modules.DomainAssetMonitor.domian_asset_check.check_invalid_domains() Failed to compare domains: {e}")

    return invalidDomains

# 失效域名落表
def insert_invalid_domains(directory):
    """
    [{'domain': 'imsa.comisys.net', 'owner': '党羽'}]
    :param: directory : [{'domain': 'imsa.comisys.net', 'owner': '党羽'}]
    :return:
    """




    pass



# 过期域名检测
def check_expired_domains():
    """
    检查 asset_dns_records 表中过期域名
    1、在 asset_dns_records 表，updateTime 超过 3 天没有更新的
    落表 asset_dns
    :param:
    :return:[{},{}]  # 返回 域名 + 所属人 [{'domain': 'bcslivepush.b.qianxin.com'}]
    """
    expiredDomains = []
    try:
        sql = (
            "SELECT domain FROM asset_dns_records WHERE updateTime < DATE_SUB(NOW(), INTERVAL 3 DAY)"
        )
        logger.info(f"modules.DomainAssetMonitor.domian_asset_check.check_expired_domains() Executing SQL: {sql}")
        result = MySQL(sql=sql).exec()
        # print(f"Result type: {type(result)}, Result content: {result}")  # 调试语句  Result type: <class 'dict'>
        if result.get('state') == 1:
            for item in result.get('data'):
                expiredDomains.append(item)
            logger.info(f"modules.DomainAssetMonitor.domian_asset_check.check_expired_domains() Found {len(expiredDomains)} expired domains")
            return expiredDomains
        else:
            logger.error(f"modules.DomainAssetMonitor.domian_asset_check.check_expired_domains() Failed to get expired domains: {result.get('msg')}")
    except Exception as e:
        logger.error(f"modules.DomainAssetMonitor.domian_asset_check.check_expired_domains() Failed to get expired domains: {e}")
        return expiredDomains


# 过期域名落表
def insert_expired_domains(directory):
    """
    [{'domain': 'bcslivepush.b.qianxin.com'}]
    :param: directory : [{'domain': 'bcslivepush.b.qianxin.com'}]
    :return:
    """

    pass


# 判断域名是否是内网域名 【完成】
def check_domains_net_type(domain):
    """
    判断域名是否是内网还是外网
    :param: domain  string
    :return:
    """
    # 定义 内网域名后缀列表
    internal_suffixes = ['qianxin-inc.cn']
    if domain.endswith(tuple(internal_suffixes)):
        return "Intranet"   # 内网
    else:
        return "Internet"   # 外网


# 加白域名检测 同步 asset_dns_white 的状态到 asset_dns  【完成】
def check_white_domains():
    """
    检查 asset_dns_white 表中加白域名
    落表 asset_dns
    :param:     domain / owner / email
    :return:    domain / domainType / isWhite / note
    """
    whiteDomains = []
    try:
        sql = (
            "SELECT domain, owner, email, isWhite, note FROM asset_dns_white"
        )
        logger.info(f"modules.DomainAssetMonitor.domian_asset_check.check_white_domains() Executing SQL: {sql}")
        result = MySQL(sql=sql).exec()
        if result.get('state') == 1:
            for item in result.get('data'):
                # 补充剩余字段  【内外网域名需要判断下】
                item['domainType'] = check_domains_net_type(item.get('domain'))  # 新增字段 domainType
                item['isWhite'] = item.get('isWhite')  # 新增字段 isWhite 赋值 1   # 加白表增加一个字段用来表示加白是否启用  1 启用 0 不启用 20250102
                item['note'] = item.get('owner') + '-' + item.get('email') + '-' + item.get('note', '')
                del item['email']  # 删除 email 字段
                whiteDomains.append(item)
                logger.info(f"modules.DomainAssetMonitor.domian_asset_check.check_white_domains() Found white domains {item.get('domain')}")
                # 插入数据库
                sql_insert = (
                    "INSERT INTO asset_dns (domain, domainType, isWhite, note) "
                    "VALUES ('%s', '%s', '%s', '%s') "
                    "ON DUPLICATE KEY UPDATE "
                    "domain='%s',domainType='%s', isWhite='%s',note='%s',updateTime=CURRENT_TIMESTAMP(6);" % (
                        item.get('domain'), item.get('domainType'), item.get('isWhite'), item.get('note'), item.get('domain'), item.get('domainType'), item.get('isWhite'), item.get('note'),  # 所有的参数都在这里
                    )
                )
                MySQL(sql=sql_insert).exec()
                logger.info(f"modules.DomainAssetMonitor.domian_asset_check.check_white_domains() SQL:{sql_insert}")
            logger.info(f"modules.DomainAssetMonitor.domian_asset_check.check_white_domains() Inserted {len(whiteDomains)} white domains into asset_dns")
            return whiteDomains
        else:
            logger.error(f"modules.DomainAssetMonitor.domian_asset_check.check_white_domains() Failed to get white domains: {result.get('msg')}")
    except Exception as e:
        logger.error(f"modules.DomainAssetMonitor.domian_asset_check.check_white_domains() Failed to get white domains: {e}")
        return whiteDomains


# 解析ip为cdn的域名检测
def check_ip_or_domain_isCdn():
    """
    检查 asset_dns_record 表中解析A记录ip为 CDN IP
    检查 asset_dns_origin 表中域名为CDN域名
    落表 asset_dns
    :param:
    :return:
    """
    pass


# 删除过期数据 14 天前数据
def delete_old_data():
    """
    默认 14 天之前的数据没有价值
    删除 asset_dns_origin 表中 14 天前的数据
    删除 asset_dns_record 表中 14 天之前没有解析的域名
    删除 asset_dns 监控表中 14 天之前的数据
    加白表不用删除，加白表中的数据每天会同步一次到 asset_dns 所以监控表 updateTime 数据会更新
    :param:
    :return:
    """
    MySQL(sql="DELETE FROM asset_dns_origin WHERE updateTime < DATE_SUB(NOW(), INTERVAL 14 DAY)").exec()
    MySQL(sql="DELETE FROM asset_dns_record WHERE updateTime < DATE_SUB(NOW(), INTERVAL 14 DAY)").exec()
    MySQL(sql="DELETE FROM asset_dns WHERE updateTime < DATE_SUB(NOW(), INTERVAL 14 DAY)").exec()
    return


if __name__ == '__main__':
    # res = new_add_domains()
    # print(res)
    # res = select_data_from_db("SELECT * FROM asset_dns_records limit 10", "domain")
    # print(res)

    # res = check_invalid_domains()
    # print(res)

    # res = check_expired_domains()
    # print(res)

    res = check_white_domains()
    print(res)
