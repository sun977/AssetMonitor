#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
用于检测域名是否有解析
1、从domains.txt中读取数据
2、逐个解析然后输出结果
"""

import dns.resolver

# 库 会自动处理cname并解析到A记录

def get_records(domain, record_type):
    """Query the specified DNS records for a domain and return them as a list."""
    try:
        answers = dns.resolver.resolve(domain, record_type)

        if record_type in ['A', 'AAAA']:
            records = [answer.address for answer in answers]
        elif record_type == 'CNAME':
            records = [answer.to_text() for answer in answers]
        elif record_type == 'MX':
            records = [f"{answer.exchange} (priority: {answer.preference})" for answer in answers]
            # 对于 MX 记录，提取邮件交换服务器及其优先级
        elif record_type == 'NS':
            records = [str(answer.target) for answer in answers]
        elif record_type == 'TXT':
            records = [answer.strings[0].decode('utf-8') for answer in answers]
        elif record_type == 'SRV':
            records = [f"{answer.priority} {answer.weight} {answer.port} {answer.target}" for answer in answers]
        else:
            records = [answer.to_text() for answer in answers]

        return records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return None
    except dns.resolver.Timeout:
        return "Timeout"
    except dns.exception.DNSException as e:
        return str(e)

def read_domains_from_file(file_path):
    """Read domains from a file and return them as a list."""
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file if line.strip()]
    return domains

def main():
    file_path = 'domains.txt'
    domains = read_domains_from_file(file_path)
    record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SRV']  # 可以根据需要添加更多记录类型

    for domain in domains:
        print(f"\nChecking records for domain: {domain}")
        for record_type in record_types:
            records = get_records(domain, record_type)
            if records is None:
                print(f"{record_type}: No record found")
            elif isinstance(records, str):
                print(f"{record_type}: {records}")
            else:
                print(f"{record_type}: {' '.join(records)}")

if __name__ == "__main__":
    main()
