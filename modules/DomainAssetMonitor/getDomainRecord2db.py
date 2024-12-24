#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
用于检测域名是否有解析，并将结果存入MySQL数据库
1、从domains.txt中读取数据
2、逐个解析然后输出结果并插入数据库
"""

import dns.resolver
import mysql.connector
from datetime import datetime

# 表结构
# CREATE TABLE dns_records (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     domain VARCHAR(255) NOT NULL,
#     record_type ENUM('A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SRV') NOT NULL,
#     record_value TEXT,
#     priority INT DEFAULT NULL,  -- 仅用于MX和SRV记录
#     weight INT DEFAULT NULL,    -- 仅用于SRV记录
#     port INT DEFAULT NULL,      -- 仅用于SRV记录
#     target VARCHAR(255) DEFAULT NULL, -- 用于CNAME, MX, NS 和 SRV 记录
#     query_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     UNIQUE KEY unique_record (domain, record_type, record_value, priority, weight, port, target)
# );



# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}

def get_records(domain, record_type):
    """Query the specified DNS records for a domain and return them as a list."""
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
            records = [{'record_value': answer.to_text()[:2048]} for answer in answers] # 截断过长的记录值

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

def insert_record(cursor, domain, record_type, record_info):
    """Insert a DNS record into the database."""
    query = """
    INSERT INTO dns_records (domain, record_type, record_value, priority, weight, port, target)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    record_value=VALUES(record_value),
    priority=VALUES(priority),
    weight=VALUES(weight),
    port=VALUES(port),
    target=VALUES(target),
    query_time=CURRENT_TIMESTAMP;
    """
    # 确保 record_value 不会超过 VARCHAR(2048) 的限制
    record_value = record_info.get('record_value', '')[:2048]

    cursor.execute(query, (
        domain,
        record_type,
        record_value,
        record_info.get('priority'),
        record_info.get('weight'),
        record_info.get('port'),
        record_info.get('target')
    ))

def main():
    file_path = 'domains2.txt'
    domains = read_domains_from_file(file_path)
    record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SRV']  # 可以根据需要添加更多记录类型

    try:
        # 连接数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for domain in domains:
            print(f"\nChecking records for domain: {domain}")
            for record_type in record_types:
                records = get_records(domain, record_type)
                if records is None:
                    print(f"{record_type}: No record found")
                elif isinstance(records, str):
                    print(f"{record_type}: {records}")
                else:
                    for record_info in records:
                        insert_record(cursor, domain, record_type, record_info)
                        conn.commit()
                        print(f"{record_type}: Inserted {record_info['record_value']}")

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()