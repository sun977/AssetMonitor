#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version: v1.0
    function: SEC PLT API old
    date: 2023.11.14
    note: https://wiki.qianxin-inc.cn/pages/viewpage.action?pageId=181776916
    API：
        1.api/v1/api/IpOnly
        2.api/v1/api/AllNetwork
        3.api/v1/api/AllIp
        4.api/v1/api/SearchIp
        5.api/v1/api/SearchIpByNetworkTag
        6.api/v1/api/TerminalIpByIp
"""

import time
import hashlib
import requests
import os
from comm.getconfig import *

requests.packages.urllib3.disable_warnings()


# PROXIES = {
#     'http': "http://127.0.0.1:8080",
#     'https': "http://127.0.0.1:8080"
# }

class GetDataFromSEC:
    # 信息在 result
    def __init__(self):
        self.offset = 0  # 初始偏移量  每次请求页面偏移数量
        self.limit = 1000  # 初始数值  每次请求限制数量
        self.config = get_config()
        self.username = self.config['SEC']['api_key']
        self.password = self.config['SEC']['api_pass']
        self.baseurl = self.config['SEC']['api_online']

    # 自定义 limit 和 offset 获取 获取IP和状态 返回列表 list  可用 -- 20241205
    def get_ip_only(self, limit, offset):  # 自定义 limit 和 offset 获取
        # api_url = self.baseurl + 'api/v1/api/AllIp'
        api_url = self.baseurl + 'api/v1/api/IpOnly'

        ip_list = []

        params = {
            'limit': limit,
            'offset': offset * limit
        }
        re = requests.get(api_url, params=params, auth=(self.username, self.password), verify=False)
        # count = re.json()['count']
        re = re.json()['results']  # 列表 里面多个字段

        if re:
            for item in re:
                ip = item['ip']
                ip_list.append(ip)
        else:
            ip_list = []
        # print(count)
        return ip_list

    # 获取所有IP（7w左右）只获取IP 返回列表 list  可用 -- 20241205
    def get_all_ip_only(self):
        limit = 10000
        offset = 0
        api_url = self.baseurl + '/api/v1/api/IpOnly'

        # 获取 count 数值
        par = {'limit': 1, 'offset': 0}
        count = int(
            requests.get(api_url, params=par, auth=(self.username, self.password), verify=False).json()['count'])
        offsetMax = int(count / limit + 1)  # 8
        # print("最大页数", offsetMax)

        # while offset < offsetMax:  # 循环所有的IP  循环每一页
        ip_list = []  # 放在循环外面
        for offset in range(offsetMax):
            params = {
                'limit': limit,
                'offset': offset * limit
            }

            re = requests.get(api_url, params=params, auth=(self.username, self.password), verify=False)
            # count = re.json()['count']
            re = re.json()['results']  # 列表 里面多个字段

            offset = offset + 1

            if re:
                for item in re:  # 遍历列表 取每一个列表元素的 IP
                    ip = item['ip']
                    ip_list.append(ip)
            else:
                # ip_list = []
                print("No results found on page",offset + 1)
                break

        return ip_list

    # 仅获取所有的网段信息 返回 list 可用 -- 20241205
    def get_all_net_only(self):  # 获取所有的网段
        limit = 1000
        offset = 0
        api_url = self.baseurl + '/api/v1/api/AllNetwork'

        # 获取 count 数值
        par = {'limit': 1, 'offset': 0}
        count = int(
            requests.get(api_url, params=par, auth=(self.username, self.password), verify=False).json()['count'])
        print(count)
        offsetMax = int(count / limit + 1)  # 8
        # print("最大页数", offsetMax)

        net_list = []
        for offset in range(offsetMax):  # 循环所有的IP
            params = {
                'limit': limit,
                'offset': offset * limit
            }

            re = requests.get(api_url, params=params, auth=(self.username, self.password), verify=False)
            # count = re.json()['count']
            re = re.json()['results']  # 列表 里面多个字段

            offset = offset + 1

            if re:
                for item in re:
                    ip = item['network']
                    net_list.append(ip)
            else:
                # net_list = []
                # ipInif_list = []
                print("No results found on page",offset + 1)
                break

        return net_list

    # 获取所有IP资产信息 返回 字典 json
    def get_allip_message(self, limit, offset):  # 自定义 limit 和 offset 获取
        api_url = self.baseurl + 'api/v1/api/AllIp'
        params = {
            'limit': limit,
            'offset': offset * limit
        }
        re = requests.get(api_url, params=params, auth=(self.username, self.password), verify=False)
        # count = re.json()['count']
        # re = re.json()['results']  # 列表 里面多个字段
        re = re.json()
        return re

    # 仅获取所有的网段信息 返回 字典 json 可用 -- 20241205
    def get_allnet_message(self, limit, offset):  # 获取所有的网段
        api_url = self.baseurl + '/api/v1/api/AllNetwork'

        # 获取 count 数值
        params = {
            'limit': limit,
            'offset': offset * limit
        }
        re = requests.get(api_url, params=params, auth=(self.username, self.password), verify=False).json()
        # count = int(re['count'])
        # print(count)
        # offsetMax = int(count / limit + 1)  # 8
        # print("最大页数", offsetMax)

        return re

    # 根据IP获取资产信息 返回 字典 json
    def get_searchip_message(self, ip):  # 获取所有的网段
        api_url = self.baseurl + '/api/v1/api/SearchIp'
        # 获取 count 数值
        params = {
            'ip': ip
        }
        re = requests.get(api_url, params=params, auth=(self.username, self.password), verify=False).json()
        return re

    # 根据网段标签获取资产信息 返回 字典 json
    # get_searchip_by_networktag(limit=5, offset=1, field=["ipassets_ip", "ipassets_ip_type", "ipassets_status"], network_tag=['/R/网段用途/业务服务器'])
    def get_searchip_by_networktag(self, limit, offset, field, network_tag):  # 获取所有的网段
        api_url = self.baseurl + '/api/v1/api/SearchIpByNetworkTag'
        params = {
            'limit': limit,
            'offset': offset * limit,
            'field': json.dumps(field),  # list
            'network_tag': json.dumps(network_tag)  # list
        }
        re = requests.get(api_url, params=params, auth=(self.username, self.password), verify=False).json()
        return re

    # 根据IP查询终端用户信息
    def get_terminalip_by_ip(self, ip):
        api_url = self.baseurl + '/api/v1/api/TerminalIpByIp'
        params = {
            'ip': ip
        }
        re = requests.get(api_url, params=params, auth=(self.username, self.password), verify=False).json()
        return re

    # 发送蓝信告警 sendby 发送人[string] sendto 接收人[list] msg 消息[string]
    def send_lanxin_message(self, sendby, sendto, msg):
        api_url = self.baseurl + 'api/v1/api/SendLanxin'
        pass

    # 发送蓝信群消息 sender_id 发送人ID[string] group_id 接收群id[string] msg 消息[string]
    def send_lanxin_group(self, sender_id, group_id, msg):
        # 三个参数均为必填参数，API使用前联系SEC平台开发者申请群ID和发送者I
        api_url = self.baseurl + 'api/v1/api/SendLanxinGroup'
        pass





if __name__ == '__main__':
    secData = GetDataFromSEC()
    # res = secData.get_ip_only(limit=10, offset=2)
    # res = secData.get_allip_message(limit=10, offset=2)  # 可用
    # res = secData.get_allnet_message(limit=10, offset=2)  # 可用
    # res = secData.get_searchip_message('10.43.120.42')  # 可用
    # res = secData.get_searchip_by_networktag(limit=5, offset=1, field=["ipassets_ip", "ipassets_ip_type", "ipassets_status"], network_tag=['/R/网段用途/业务服务器'])
    # res = secData.get_terminalip_by_ip('10.43.120.166')
    # print(result)
    # res = secData.get_all_ip_only()  # 可用
    res = secData.get_all_net_only()  # 可用
    print(res)
    print(len(res))
