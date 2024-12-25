#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version: v1.0
    function:
    date: 2024.12.24
    note:
"""

# 引用SEC接口
from modules.SecAPI.sec.getSecApiClient import *
import dns.resolver
from comm.mysql import *
import logging
from logging.handlers import RotatingFileHandler

# 配置日志记录器
logging.basicConfig(
    # level=logging.DEBUG,  # 设置日志级别 详细信息
    level=logging.INFO,  # 设置日志级别 确认程序按预期工作
    format='%(asctime)s[%(levelname)s] %(message)s',  # 设置日志格式
    datefmt='%Y-%m-%d %H:%M:%S',  # 设置日期格式
    handlers=[
        RotatingFileHandler(
            "../../log/asset_monitor.log",  # 将日志写入文件
            maxBytes=20 * 1024 * 1024,  # 最大文件大小为 20MB
            backupCount=5  # 最多保留 5 个备份文件
        ),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)


# 从文件中读取域名
def read_domains_from_file(file_path):
    """Read domains from a file and return them as a list."""
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file if line.strip()]
    return domains


# 封装数据插入数据库
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
        logging.error(f"Failed to insert record for domain {domain}, record_type {record_type}: {e}")


# 获取全量的域名信息【从中只挑主域名】
def get_domain_from_sec():
    """
    从sec获取所有的主域名，生成列表
    :param:
    :return:['xxx','xxx']
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
            for domain in res:
                if domain.get(
                        'DomainName') not in allMainDomainsList:  # 去重获取 才14699 共30087 有重复的？ 对，sec有重复域名，域名解析多个IP的算多个
                    allMainDomainsList.append(domain.get('DomainName'))
        logging.info(f"Retrieved {len(allMainDomainsList)} unique domains from SEC")
        return allMainDomainsList
    except Exception as e:
        logging.error(f"Failed to get domains from SEC: {e}")
        return []


# 获取域名解析函数
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

        logging.info(f"Retrieved {len(records)} {record_type} records for domain {domain}")
        return records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        logging.warning(f"No {record_type} record found for domain {domain}")
        return None
    except dns.resolver.Timeout:
        logging.warning(f"Timeout while resolving {record_type} record for domain {domain}")
        return "Timeout"
    except dns.exception.DNSException as e:
        logging.error(f"DNS exception while resolving {record_type} record for domain {domain}: {e}")
        return str(e)


# 域名过滤白名单函数
def filter_domains(domains):
    """
    过滤域名白名单，不支持通配符类型的域名
    减少查询次数，查一次表把白名单都都取出来
    返回域名列表 = 所有域名 - 白名单域名
    :param domains: 需要过白名单的域名列表
    :return:['','']
    """
    # whitelist = ['example.com', 'example.net']
    sql_whitelist = "SELECT domain FROM asset_dns_white"  # 数据库中获取白名单
    res = MySQL(sql=sql_whitelist).exec()
    if res.get('state') == 1:  # 数据库sql执行成功
        if res.get('data') is not None:  # 数据库存在数据
            whitelist = [item['domain'] for item in res.get('data')]
            logging.info(f"Retrieved {len(whitelist)} domains from database godv.asset_dns_white ")
        else:  # 数据库不存在数据
            logging.warning('Database contains no whitelist data')
    else:  # 数据库sql执行失败
        logging.error(f"Failed to get whitelist from database: {res.get('msg')}")
    print("whitelist:", whitelist)

    # 返回不在白名单里面的域名
    return [domain for domain in domains if domain not in whitelist]


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
    # 从文件中读取域名 测试使用
    originAlldomains = read_domains_from_file('domains2.txt')

    # 增加域名过滤白名单的逻辑 返回 不在白名单中的域名列表 继续循环解析
    alldomains = filter_domains(originAlldomains)
    print(alldomains)

    # 循环域名
    for domain in alldomains:
        # print(f"\nChecking records for domain: {domain}")
        # 循环解析类型
        for record_type in record_types:
            records = get_records(domain, record_type)
            if records is None:  # 记录为空
                logging.info(f"{record_type}: No record found")
                # print(f"{record_type}: No record found")
            elif isinstance(records, str):  # 返回为字符串,说明报错了
                logging.warning(f"A error for resolving {record_type} record: {records}")
                # print(f"{record_type}: {records}")
            else:  # 说明有记录，进入循环插入
                # print(f"{record_type}: {records}")
                for record_info in records:  #
                    insert_record(domain, record_type, record_info)
                    logging.info(f"{record_type}: Mysql Inserted {record_info['record_value']}")
                    # print(f"{record_type}: Inserted {record_info['record_value']}")


# run函数
def run():
    """
    函数串联，执行总函数
    :return:
    """
    logging.info("Starting asset monitoring script")
    # print(len(get_domain_from_sec()))
    get_sec_domain_records_insert_db()
    logging.info("Asset monitoring script completed")
    # 运行了1小时


if __name__ == '__main__':
    run()
    # domains = ['example.com', 'example.net']
    # res = filter_domains(domains)
    # print("res:", res)
