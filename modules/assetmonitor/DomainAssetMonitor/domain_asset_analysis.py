#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version: v2.0
    function: 获取SEC域名并解析入库
    date: 2024.12.25
    note:
        - 该模块主要负责以下操作：
            1. 同步原始域名数据
            2. 进行域名解析并入库
            3. 记录操作完成时间
            4. 后续将各个模块的任务抽象出来到目录外
        - 执行频率
            1. 每天执行一次
            2. 执行方式，计划任务：0  5  *  *  *  nohup python3 AssetMonitor/modules/DomainAssetMonitor/domain_asset_analysis.py
"""

# 引用SEC接口
import dns.resolver
from comm.mysql import *
from modules.assetmonitor.DomainAssetMonitor.sync.sync_sec_data2db import sync_domain_from_sec2db
from modules.assetmonitor.DomainAssetMonitor.config.logger_config import setup_logger
import fnmatch  # 用于支持通配符匹配域名

# current_abs_path = os.path.abspath(__file__)  # 当前文件位置
# current_abs_path_dir = os.path.dirname(current_abs_path)  # 当前目录
# log_dir_path = os.path.abspath(current_abs_path_dir) + '../../../log/'  # 从当前目录找到日志目录的位置

# 配置日志记录器
logger = setup_logger()


# 从文件中读取域名
def read_domains_from_file(file_path):
    """Read domains from a file and return them as a list."""
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file if line.strip()]
    return domains


# 封装数据插入数据库 -- asset_dns_records
def insert_record(domain, record_type, record_info):
    """
    封装插入sql语句
    :param domain:
    :param record_type:
    :param record_info:
    :return:
    """
    # record_info = {'record_value': '192.168.1.1', 'priority': 10, 'weight': 5, 'port': 80, 'target': 'example.com'}
    try:
        sql = (
                "INSERT INTO asset_dns_records (domain, recordType, recordValue, priority, weight, port, target) "
                "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s') "
                "ON DUPLICATE KEY UPDATE "
                "recordValue='%s', priority='%s', weight='%s', port='%s', target='%s', updateTime=CURRENT_TIMESTAMP(6);" % (
                    domain, record_type, record_info.get('record_value', ''),
                    record_info.get('priority', ''),
                    # 字段类型是int，所以默认为0，不然mysql汇报错 【1366, "Incorrect integer value: '' for column 'priority' at row 1"】 -- 改成 vachar
                    record_info.get('weight', ''),
                    record_info.get('port', ''),
                    record_info.get('target', ''),
                    # 重复一遍用于 ON DUPLICATE KEY UPDATE 部分
                    record_info.get('record_value', ''),
                    record_info.get('priority', ''),
                    record_info.get('weight', ''),
                    record_info.get('port', ''),
                    record_info.get('target', ''),
                )
        )

        # 调用mysql插入函数
        MySQL(sql=sql).exec()
        return sql
    except Exception as e:
        logger.error(f"Failed to insert record for domain {domain}, record_type {record_type}: {e}")


# 从数据表 asset_dns_origin 获取所有域名，生成列表
def get_all_domains_from_db():
    """
    从 asset_dns_origin 表中获取需要解析的域名列表
    :return:
    """
    allDomainsList = []
    try:
        sql = (
            "SELECT domain FROM asset_dns_origin"  # 获取原始表中所有域名数据
        )
        resOrigindomains = MySQL(sql=sql).exec()
        # allDomainsList = []
        if resOrigindomains.get('state') == 1:
            for item in resOrigindomains.get('data'):
                allDomainsList.append(item.get('domain'))
            logger.info(f"modules.DomainAssetMonitor.domain_asset_check.get_domain_from_db() Retrieved {len(allDomainsList)} domains from asset_dns_origin")
            return allDomainsList
        else:
            logger.warning(f"modules.DomainAssetMonitor.domain_asset_check.get_domain_from_db() Failed to retrieve domains from asset_dns_origin: {resOrigindomains.get('msg')}")
    except Exception as e:
        logger.error(f"modules.DomainAssetMonitor.domain_asset_check.get_domain_from_db() Failed to get domains from asset_dns_origin: {e}")
        return allDomainsList


def get_records(domain, record_type):
    """
    Query the specified DNS records for a domain and return them as a list
    :param domain:
    :param record_type:
    :return:records:[{},{}]
    """
    # records = []
    try:
        answers = dns.resolver.resolve(domain, record_type)

        if record_type in ['A', 'AAAA']:
            records = [{'record_value': answer.address} for answer in answers]
        elif record_type == 'CNAME':
            records = [{'record_value': answer.to_text(), 'target': str(answer.target)} for answer in answers]
        elif record_type == 'MX':
            records = [{'record_value': str(answer.exchange), 'priority': answer.preference} for answer in answers]
        elif record_type == 'NS':
            records = [{'record_value': str(answer.target)} for answer in answers]
        elif record_type == 'TXT':
            records = [{'record_value': answer.strings[0].decode('utf-8')} for answer in answers]
        elif record_type == 'SRV':
            records = [{'record_value': f"{answer.priority} {answer.weight} {answer.port} {answer.target}",
                        'priority': answer.priority, 'weight': answer.weight, 'port': answer.port,
                        'target': str(answer.target)} for answer in answers]
        else:
            records = [{'record_value': answer.to_text()[:2048]} for answer in answers]  # 截断过长的记录值

        logger.info(f"Retrieved {len(records)} {record_type} records for domain {domain}")
        return records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        logger.warning(f"No {record_type} record found for domain {domain}")
        return None
    except dns.resolver.Timeout:
        logger.warning(f"Timeout while resolving {record_type} record for domain {domain}")
        return "Timeout"
    except dns.exception.DNSException as e:
        logger.error(f"DNS exception while resolving {record_type} record for domain {domain}: {e}")
        return str(e)


# 域名过滤白名单函数
def filter_domains(domains):
    """
    过滤域名白名单，支持通配符类型的域名
    减少查询次数，查一次表把白名单都都取出来
    返回域名列表 = 所有域名 - 白名单域名
    :param domains: 需要过白名单的域名列表
    :return:['','']
    """
    # whitelist = ['example.com', 'example.net']
    sql_whitelist = "SELECT domain FROM asset_dns_white where isWhite = '1'"  # 数据库中获取白名单
    res = MySQL(sql=sql_whitelist).exec()
    if res.get('state') == 1:  # 数据库sql执行成功
        if res.get('data') is not None:  # 数据库存在数据
            whitelist = [item['domain'] for item in res.get('data')]
            logger.info(f"Retrieved {len(whitelist)} domains from database godv.asset_dns_white ")
        else:  # 数据库不存在数据
            logger.warning('Database contains no whitelist data')
    else:  # 数据库sql执行失败
        logger.error(f"Failed to get whitelist from database: {res.get('msg')}")
    # print("whitelist:", whitelist)

    # 使用 fnmatch.filter 进行通配符匹配
    filtered_domains = []
    for domain in domains:
        if not any(fnmatch.fnmatch(domain, pattern) for pattern in whitelist):
            filtered_domains.append(domain)

    # 返回不在白名单里面的域名
    # return [domain for domain in domains if domain not in whitelist]
    return filtered_domains


# 获取sec域名的域名解析并入库
def get_sec_domain_records_insert_db():
    """
    获取sec域名的域名解析
    :param:
    :return:
    """
    # 解析类型定义
    record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SRV']

    # 获取SEC所有域名
    # originAlldomains = get_domain_from_sec()
    # 从域名表 asset_dns_origin 中获取域名信息
    originAlldomains = get_all_domains_from_db()
    # 从文件中读取域名 测试使用
    # originAlldomains = read_domains_from_file('domains2.txt')

    # 增加域名过滤白名单的逻辑 返回 不在白名单中的域名列表 继续循环解析
    alldomains = filter_domains(originAlldomains)
    # print(alldomains)

    # 循环域名
    for domain in alldomains:
        # print(f"\nChecking records for domain: {domain}")
        # 循环解析类型
        for record_type in record_types:
            records = get_records(domain, record_type)
            if records is None:  # 记录为空
                logger.info(f"{record_type}: No record found")
                # print(f"{record_type}: No record found")
            elif isinstance(records, str):  # 返回为字符串,说明报错了
                logger.warning(f"An error for resolving {record_type} record: {records}")
                # print(f"{record_type}: {records}")
            else:  # 说明有记录，进入循环插入
                # print(f"{record_type}: {records}")
                for record_info in records:  #
                    insert_record(domain, record_type, record_info)
                    logger.info(f"{record_type}: Mysql Inserted {record_info['record_value']}")
                    # print(f"{record_type}: Inserted {record_info['record_value']}")
    return None


# run运行函数
def run_domain_asset_analysis():
    """
    函数串联，执行总函数。
    该函数按顺序执行以下操作：
    1. 同步原始域名数据
    2. 进行域名解析并入库 -- 去除 白名单域名
    3. 记录操作完成时间
    """
    try:
        logger.info("Starting domain_asset_analysis.py script")
        # 先运行原始域名数据同步操作
        sync_domain_from_sec2db()

        # 再运行域名解析入库操作
        get_sec_domain_records_insert_db()
        logger.info("Domain_asset_monitor.py monitoring script completed")
        # 运行周期1小时
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == '__main__':
    run_domain_asset_analysis()
    # domains = ['example.com', 'example.net', 'whw3ylsyzrrzbdne111111.o.xhaoma.net']  # 加白表添加： *.xhaoma.net
    # res = filter_domains(domains)
    # print("res:", res)   # res: ['example.net']  成功过滤
    # sync_domain_from_sec2db()
    # res = get_all_domains_from_db()
    # print("get_all_domains_from_db:", res)
