#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
    auth: sunhaobo
    version:
    function: ip handle
    date: 2023.11.28
    note: IP 聚合成最小网段
"""
import ipaddress

from netaddr import IPNetwork, IPAddress

def merge_ip_addresses(ip_list):
    ip_objects = [ipaddress.ip_network(ip) for ip in ip_list]
    merged_ips = ipaddress.collapse_addresses(ip_objects)
    return [str(ip) for ip in merged_ips]


# 从文件读取ip信息
def read_ip_from_file(file):
    ip_list = []
    with open(file, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            ip_list.append(line)
    return ip_list

# 把IP写入文件
def write_ip_to_file(ip_list,file):
    ip_list = ip_list
    file = file
    # 打开out.txt文件
    with open(file, 'w') as f:
        # 写入list数据
        for ip in ip_list:
            f.write(str(ip) + '\n')

if __name__ == '__main__':
    # 从 ips.txt 文件读取IP
    data_ip_list = read_ip_from_file('ips.txt')
    # 把多个IP聚合成最小网段
    data_ip_list = merge_ip_addresses(data_ip_list)
    # 把合成后的网段信息写入文件
    print(data_ip_list)
    print(len(data_ip_list))
    write_ip_to_file(data_ip_list,'ips_aggregate.txt')








