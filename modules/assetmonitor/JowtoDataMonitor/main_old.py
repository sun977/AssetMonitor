#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
    auth: sunhaobo
    version:
    function: SEC PLT API
    date: 2023.11.14
    note: https://wiki.qianxin-inc.cn/pages/viewpage.action?pageId=181776916
"""

from sec.getSecDataApi import *


# 获取内网所有椒图在线的数据
def get_intranet_all_jowto_online_ip():
    secData = GetDataFromSEC()
    ip_list = []
    # data_tmp = {}
    offset = 0
    # limit = 1000
    limit = 50
    while True:  # 永久运行了
        ip_list_tmp = secData.get_allip_message(limit, offset)
        dataCount = ip_list_tmp['count']

        result_ip_list = ip_list_tmp['results']  # 获取数据
        print("result 数据：", result_ip_list)
        if result_ip_list:
            for item in result_ip_list:  # 每条数据 {}
                if item['jowto_onlineStatus'] == 1 and item['ipassets_ip_type'] == '内网':
                    print("jowto_onlineStatus=1:", item['ipassets_ip'])
                    data_tmp = {
                        "ipassets_ip": item['ipassets_ip'],
                        "ipassets_ip_type": item['ipassets_ip_type'],
                        "jowto_onlineStatus": item['jowto_onlineStatus'],
                        "ipassets_ip_tags": item['ipassets_ip_tags'],
                        "ipassets_network_tags": item['ipassets_network_tags'],
                        "ipassets_least_network_tags": item['ipassets_least_network_tags']
                    }
                    print("data_tmp:", data_tmp)
                    ip_list.append(data_tmp)
            # ip_list.extend(ip_list_tmp)
            offset += 1
        else:
            break

    return ip_list

# 优化后的
def get_intranet_all_jowto_online_ip2():
    secData = GetDataFromSEC()
    ip_list = []
    offset = 0
    # limit = 1000
    limit = 50
    while True:  # 永久运行
        ip_list_tmp = secData.get_allip_message(limit, offset)
        dataCount = ip_list_tmp['count']
        result_ip_list = ip_list_tmp.get('results', [])  # 获取数据
        print("result 数据：", result_ip_list)
        if result_ip_list:
            for item in result_ip_list:  # 每条数据 {}
                if item['jowto_onlineStatus'] == '1' and item['ipassets_ip_type'] == '内网':
                    print("jowto_onlineStatus=1:", item['ipassets_ip'])
                    data_tmp = {
                        "ipassets_ip": item.get('ipassets_ip'),
                        "ipassets_ip_type": item.get('ipassets_ip_type'),
                        "jowto_onlineStatus": item.get('jowto_onlineStatus'),
                        "ipassets_ip_tags": item.get('ipassets_ip_tags'),
                        "ipassets_network_tags": item.get('ipassets_network_tags'),
                        "ipassets_least_network_tags": item.get('ipassets_least_network_tags')
                    }
                    print("data_tmp:", data_tmp)
                    ip_list.append(data_tmp)
            offset += 1
        else:
            break

    return ip_list








if __name__ == '__main__':
    secData = GetDataFromSEC()
    # res = secData.get_ip_only(limit=10, offset=2)
    # res = secData.get_allip_message(limit=1, offset=1)
    # res = secData.get_allnet_message(limit=10, offset=2)
    # res = secData.get_searchip_message('10.43.120.42')
    # res = secData.get_searchip_by_networktag(limit=5, offset=1, field=["ipassets_ip", "ipassets_ip_type", "ipassets_status"], network_tag=['/R/网段用途/业务服务器'])
    # res = secData.get_terminalip_by_ip('10.43.120.166')
    # print(result)
    # res = secData.get_all_ip_only()
    # res = secData.get_all_net_only()
    res = get_intranet_all_jowto_online_ip()
    # print(res['results'])
    print(res)
