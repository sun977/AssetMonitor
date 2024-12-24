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



def read_domains_from_file(file_path):
    """Read domains from a file and return them as a list."""
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file if line.strip()]
    return domains



# 获取全量的域名信息【从中只挑主域名】
def get_domain_from_sec():
    """
    从sec获取所有的主域名，生成列表
    :param:
    :return:['xxx','xxx']
    """
    sec = secApiClient()  # 实例化secClient
    res = sec.get_domaininfo_lucene()  # 不带 query 参数是查询所有域名信息 数量 30087
    allMainDomainsList = []
    if res is None:
        print('sec接口返回数据为空')
        return allMainDomainsList
    else:
        for domain in res:
            if domain.get('DomainName') not in allMainDomainsList:   # 去重获取 才14699 共30087 有重复的？ 对，sec有重复域名，域名解析多个IP的算多个
                allMainDomainsList.append(domain.get('DomainName'))

    return allMainDomainsList


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

        return records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return None
    except dns.resolver.Timeout:
        return "Timeout"
    except dns.exception.DNSException as e:
        return str(e)


# 获取sec域名的域名解析
def get_sec_domain_records():
    """
    获取sec域名的域名解析
    :param:
    :return:
    """
    # 解析类型定义
    record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SRV']

    # 获取SEC所有域名
    # alldomains = get_domain_from_sec()
    # 从文件中读取域名
    alldomains = read_domains_from_file('domains.txt')


    # 循环域名
    for domain in alldomains:
        print(f"\nChecking records for domain: {domain}")
        for record_type in record_types:
            records = get_records(domain, record_type)
            if records is None:
                print(f"{record_type}: No record found")
            elif isinstance(records, str):
                print(f"{record_type}: {records}")
            else:
                print(f"{record_type}: {records}")







if __name__ == '__main__':
    # print(len(get_domain_from_sec()))
    get_sec_domain_records()
