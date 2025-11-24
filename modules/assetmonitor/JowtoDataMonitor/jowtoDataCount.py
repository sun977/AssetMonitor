#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version:
    function: get jowto data count from sec
    date: 2023.11.29
    note:
         1.设备在线设备
         2.全量设备椒图在线/离线/未安装数量 在 安全域分布情况
         3.设备在线 AND 在上海网段(过滤所有服务器)
         4.设备在线 AND 在上海网段 AND 需要装椒图 || 不需要装椒图 || 没有椒图标签
         5.设备在线 AND 在上海网段 AND 需要装椒图 AND 椒图在线1 || 椒图离线0 || 椒图未安装2
         6.设备在线 AND 在上海网段 AND 需要装椒图 AND 椒图在线1 || 椒图离线0 || 椒图未安装2 || 不同安全域(1/2/3/4/5)
"""

from netaddr import IPNetwork, IPAddress
# from sec.getSecApiClient import *
from modules.SecAPI.sec.getSecApiClient import *


def read_from(file_path):
    file = file_path
    # 读取文件内容
    with open(file, 'r') as f:
        data_list = f.readlines()
    # 去除每行的换行符
    data_list = [data.strip() for data in data_list]
    return data_list


def write_to(data_list, file_path):
    data_list = data_list
    file = file_path
    # 打开out.txt文件
    with open(file, 'w') as f:
        # 写入list数据
        for data in data_list:
            f.write(str(data) + '\n')


# 判断IP是否在网段
def is_ip_in_network(ip, network):
    if IPAddress(ip) in IPNetwork(network):
        return True
    else:
        return False


def ip_in_network(ip_list, network_list):
    ip_list = ip_list
    network_list = network_list
    ip_in_network_list = []
    # 遍历 ip_list
    for ip in ip_list:
        # 判断 IP 是否在 网段列表的网段中
        for network in network_list:
            if is_ip_in_network(ip, network):  # 如果放回 true 说明在
                # 这里是不是可以把安全区域带着
                ip_in_network_list.append(ip)
                break
    ip_in_network_list = list(set(ip_in_network_list))  # 去重 【原理：转成集合再转会列表，集合的特性是不重复】
    return {
        "data": ip_in_network_list,
        "count": len(ip_in_network_list)
    }


class jowtoDataCount:
    def __init__(self):
        self.cur_path = os.path.dirname(os.path.realpath(__file__))
        self.network_file = os.path.join(self.cur_path, "./file/IDC_network.txt")
        self.out_file = os.path.join(self.cur_path, "./file/jowtoCount")  # 文件输出
        self.secClient = secApiClient()  # 初始化SEC API实例
        self.sec_data_count = None  # sec设备数据总量
        self.device_online_count = None  # sec在线设备总量
        self.device_jowto_status_count_in_secArea = {
            "jowto_online_count": {
                "S1": 0,
                "S2": 0,
                "S3": 0,
                "S4": 0,
                "S5": 0,
            },
            "jowto_offline_count": {
                "S1": 0,
                "S2": 0,
                "S3": 0,
                "S4": 0,
                "S5": 0,
            },
            "jowto_no_install_count": {
                "S1": 0,
                "S2": 0,
                "S3": 0,
                "S4": 0,
                "S5": 0,
            },
        }  # 全量设备椒图在线/离线/未安装数量 在 安全域分布情况 【数据采集】
        self.device_online_in_shanghai_count = None  # 上海在线设备
        self.device_online_in_shanghai_need_jowto_count = None  # 需要装椒图
        self.device_online_in_shanghai_no_need_jowto_count = None  # 不需要装椒图
        self.device_online_in_shanghai_no_jowto_tag_count = None  # 没有椒图标签
        self.device_online_in_shanghai_need_jowto_status_1_count = None  # 椒图在线
        self.device_online_in_shanghai_need_jowto_status_0_count = None  # 椒图离线
        self.device_online_in_shanghai_need_jowto_status_2_count = None  # 椒图未安装
        self.device_online_in_shanghai_jowto_status_count_in_secArea = {
            "jowto_online_count": {
                "S1": 0,
                "S2": 0,
                "S3": 0,
                "S4": 0,
                "S5": 0,
            },
            "jowto_offline_count": {
                "S1": 0,
                "S2": 0,
                "S3": 0,
                "S4": 0,
                "S5": 0,
            },
            "jowto_no_install_count": {
                "S1": 0,
                "S2": 0,
                "S3": 0,
                "S4": 0,
                "S5": 0,
            }
        }  # 上海设备椒图在线/离线/未安装数量 在 安全域分布情况 【数据采集】

    # 展示统计数据
    def get_count(self):
        data_count = {
            "sec_data_count": self.sec_data_count,
            "device_online_count": self.device_online_count,
            "device_jowto_status_count_in_secArea": self.device_jowto_status_count_in_secArea,
            "device_online_in_shanghai_count": self.device_online_in_shanghai_count,
            "device_online_in_shanghai_need_jowto_count": self.device_online_in_shanghai_need_jowto_count,
            "device_online_in_shanghai_no_need_jowto_count": self.device_online_in_shanghai_no_need_jowto_count,
            "device_online_in_shanghai_no_jowto_tag_count": self.device_online_in_shanghai_no_jowto_tag_count,
            "device_online_in_shanghai_need_jowto_status":{
                "device_online_in_shanghai_need_jowto_online_count": self.device_online_in_shanghai_need_jowto_status_1_count,
                "device_online_in_shanghai_need_jowto_offline_count": self.device_online_in_shanghai_need_jowto_status_0_count,
                "device_online_in_shanghai_need_jowto_no_install_count": self.device_online_in_shanghai_need_jowto_status_2_count,
            },
            "device_online_in_shanghai_jowto_status_count_in_secArea": self.device_online_in_shanghai_jowto_status_count_in_secArea,
        }
        return data_count

    # 获取SEC数据
    # 后一个函数勇用前一个函数【完成】
    def getSecDataOriginal(self):
        # secClient = secApiClient()  # 初始化实例
        res = self.secClient.get_all_ipInformation()
        self.sec_data_count = len(res)
        print("SEC数据总量:", self.sec_data_count)
        return {
            "data": res,
            "count": self.sec_data_count
        }

    # 1.设备在线设备(筛选所有的服务器设备) 【完成】
    def get_device_online(self):
        res = self.getSecDataOriginal()['data']
        device_online_list = []
        for item in res:
            if (item['ipassets_status'] == '在线' or '在线' in item['ipassets_ip_tags']) and (
                    "服务器" in item['ipassets_ip_tags'] or "服务器" in item['ipassets_network_tags'] or "服务器" in
                    item['ipassets_least_network_tags']):
                device_online_list.append(item)
        self.device_online_count = len(device_online_list)
        print("SEC设备在线总量:", self.device_online_count)
        return {
            "data": device_online_list,  # [{},{},{}]
            "count": self.device_online_count
        }

    # 2.全量设备椒图在线/离线/未安装数量 在 安全域分布情况 【完成】
    def get_device_jowto_status_secAreas(self):
        res = self.getSecDataOriginal()['data']
        count = len(res)
        S = {
            'S1': [[], [], []],
            'S2': [[], [], []],
            'S3': [[], [], []],
            'S4': [[], [], []],
            'S5': [[], [], []]
        }

        IP = {
            'S1': [[], [], []],
            'S2': [[], [], []],
            'S3': [[], [], []],
            'S4': [[], [], []],
            'S5': [[], [], []]
        }

        for item in res:
            online_status = item['jowto_onlineStatus']  # 过滤 椒图状态
            network_tags = item['ipassets_least_network_tags']  # 过滤 最小网段标签

            if online_status == 1:
                if "IDC Level 01" in network_tags:
                    S['S1'][0].append(item)
                    IP['S1'][0].append(item['ipassets_ip'])
                elif "IDC Level 02" in network_tags:
                    S['S2'][0].append(item)
                    IP['S2'][0].append(item['ipassets_ip'])
                elif "IDC Level 03" in network_tags:
                    S['S3'][0].append(item)
                    IP['S3'][0].append(item['ipassets_ip'])
                elif "IDC Level 04" in network_tags:
                    S['S4'][0].append(item)
                    IP['S4'][0].append(item['ipassets_ip'])
                elif "IDC Level 05" in network_tags:
                    S['S5'][0].append(item)
                    IP['S5'][0].append(item['ipassets_ip'])
            elif online_status == 0:
                if "IDC Level 01" in network_tags:
                    S['S1'][1].append(item)
                    IP['S1'][1].append(item['ipassets_ip'])
                elif "IDC Level 02" in network_tags:
                    S['S2'][1].append(item)
                    IP['S2'][1].append(item['ipassets_ip'])
                elif "IDC Level 03" in network_tags:
                    S['S3'][1].append(item)
                    IP['S3'][1].append(item['ipassets_ip'])
                elif "IDC Level 04" in network_tags:
                    S['S4'][1].append(item)
                    IP['S4'][1].append(item['ipassets_ip'])
                elif "IDC Level 05" in network_tags:
                    S['S5'][1].append(item)
                    IP['S5'][1].append(item['ipassets_ip'])
            else:
                if "IDC Level 01" in network_tags:
                    S['S1'][2].append(item)
                    IP['S1'][2].append(item['ipassets_ip'])
                elif "IDC Level 02" in network_tags:
                    S['S2'][2].append(item)
                    IP['S2'][2].append(item['ipassets_ip'])
                elif "IDC Level 03" in network_tags:
                    S['S3'][2].append(item)
                    IP['S3'][2].append(item['ipassets_ip'])
                elif "IDC Level 04" in network_tags:
                    S['S4'][2].append(item)
                    IP['S4'][2].append(item['ipassets_ip'])
                elif "IDC Level 05" in network_tags:
                    S['S5'][2].append(item)
                    IP['S5'][2].append(item['ipassets_ip'])
        # 写入文件
        write_to(IP['S1'][0], os.path.join(self.out_file, "device_jowto_online_S1.txt"))
        write_to(IP['S2'][0], os.path.join(self.out_file, "device_jowto_online_S2.txt"))
        write_to(IP['S3'][0], os.path.join(self.out_file, "device_jowto_online_S3.txt"))
        write_to(IP['S4'][0], os.path.join(self.out_file, "device_jowto_online_S4.txt"))
        write_to(IP['S5'][0], os.path.join(self.out_file, "device_jowto_online_S5.txt"))
        write_to(IP['S1'][1], os.path.join(self.out_file, "device_jowto_offline_S1.txt"))
        write_to(IP['S2'][1], os.path.join(self.out_file, "device_jowto_offline_S2.txt"))
        write_to(IP['S3'][1], os.path.join(self.out_file, "device_jowto_offline_S3.txt"))
        write_to(IP['S4'][1], os.path.join(self.out_file, "device_jowto_offline_S4.txt"))
        write_to(IP['S5'][1], os.path.join(self.out_file, "device_jowto_offline_S5.txt"))
        write_to(IP['S1'][2], os.path.join(self.out_file, "device_jowto_no_install_S1.txt"))
        write_to(IP['S2'][2], os.path.join(self.out_file, "device_jowto_no_install_S2.txt"))
        write_to(IP['S3'][2], os.path.join(self.out_file, "device_jowto_no_install_S3.txt"))
        write_to(IP['S4'][2], os.path.join(self.out_file, "device_jowto_no_install_S4.txt"))
        write_to(IP['S5'][2], os.path.join(self.out_file, "device_jowto_no_install_S5.txt"))
        # 变量赋值
        s1_0 = self.device_jowto_status_count_in_secArea['jowto_online_count']['S1'] = len(S['S1'][0])
        s2_0 = self.device_jowto_status_count_in_secArea['jowto_online_count']['S2'] = len(S['S2'][0])
        s3_0 = self.device_jowto_status_count_in_secArea['jowto_online_count']['S3'] = len(S['S3'][0])
        s4_0 = self.device_jowto_status_count_in_secArea['jowto_online_count']['S4'] = len(S['S4'][0])
        s5_0 = self.device_jowto_status_count_in_secArea['jowto_online_count']['S5'] = len(S['S5'][0])
        s1_1 = self.device_jowto_status_count_in_secArea['jowto_offline_count']['S1'] = len(S['S1'][1])
        s2_1 = self.device_jowto_status_count_in_secArea['jowto_offline_count']['S2'] = len(S['S2'][1])
        s3_1 = self.device_jowto_status_count_in_secArea['jowto_offline_count']['S3'] = len(S['S3'][1])
        s4_1 = self.device_jowto_status_count_in_secArea['jowto_offline_count']['S4'] = len(S['S4'][1])
        s5_1 = self.device_jowto_status_count_in_secArea['jowto_offline_count']['S5'] = len(S['S5'][1])
        s1_2 = self.device_jowto_status_count_in_secArea['jowto_no_install_count']['S1'] = len(S['S1'][2])
        s2_2 = self.device_jowto_status_count_in_secArea['jowto_no_install_count']['S2'] = len(S['S2'][2])
        s3_2 = self.device_jowto_status_count_in_secArea['jowto_no_install_count']['S3'] = len(S['S3'][2])
        s4_2 = self.device_jowto_status_count_in_secArea['jowto_no_install_count']['S4'] = len(S['S4'][2])
        s5_2 = self.device_jowto_status_count_in_secArea['jowto_no_install_count']['S5'] = len(S['S5'][2])

        print("全量设备椒图[在线]安全域分布情况:S1有 {}台, S2有 {}台, S3有 {}台, S4有 {}台, S5有 {}台".format(s1_0, s2_0, s3_0, s4_0, s5_0))
        print("全量设备椒图[离线]安全域分布情况:S1有 {}台, S2有 {}台, S3有 {}台, S4有 {}台, S5有 {}台".format(s1_1, s2_1, s3_1, s4_1, s5_1))
        print("全量设备椒图[未安装]安全域分布情况:S1有 {}台, S2有 {}台, S3有 {}台, S4有 {}台, S5有 {}台".format(s1_2, s2_2, s3_2, s4_2, s5_2))


        return {
            "data": {
                "jowto_online":{
                    "S1":S['S1'][0],
                    "S2":S['S2'][0],
                    "S3":S['S3'][0],
                    "S4":S['S4'][0],
                    "S5":S['S5'][0],
                },
                "jowto_offline":{
                    "S1":S['S1'][1],
                    "S2":S['S2'][1],
                    "S3":S['S3'][1],
                    "S4":S['S4'][1],
                    "S5":S['S5'][1],
                },
                "jowto_no_install":{
                    "S1":S['S1'][2],
                    "S2":S['S2'][2],
                    "S3":S['S3'][2],
                    "S4":S['S4'][2],
                    "S5":S['S5'][2],
                }
            },
            "count":{
                "all_count":count,
                "jowto_online_count":{
                    "S1_count":s1_0,
                    "S2_count":s2_0,
                    "S3_count":s3_0,
                    "S4_count":s4_0,
                    "S5_count":s5_0,
                },
                "jowto_offline_count":{
                    "S1_count":s1_1,
                    "S2_count":s2_1,
                    "S3_count":s3_1,
                    "S4_count":s4_1,
                    "S5_count":s5_1,
                },
                "jowto_no_install_count":{
                    "S1_count":s1_2,
                    "S2_count":s2_2,
                    "S3_count":s3_2,
                    "S4_count":s4_2,
                    "S5_count":s5_2,
                }
            }
        }

    # 3.设备在线 AND 在上海网段【完成】
    def get_device_online_in_shanghai(self):
        item_list = self.get_device_online()['data'] # 这里获得的是 [{},{},{}]

        network_list = read_from(self.network_file)  # 从文件读取
        network_list = [network.strip() for network in network_list]  # 去除每行的换行符
        # print("network_list:\n",network_list)
        ip_in_network_list = []
        ip_list = []
        for item in item_list:  # 获取的是每个 {} 里面的 ipassets_ip
            # 判断 IP 是否在 网段列表的网段中
            for network in network_list:
                if is_ip_in_network(item['ipassets_ip'], network):  # 如果返回 true 说明在
                    ip_list.append(item['ipassets_ip']) # 获取纯IP清单
                    ip_in_network_list.append(item)
                    break
        # ip_in_network_list = list(set(ip_in_network_list))  # 去重 【原理：转成集合再转会列表，集合的特性是不重复】
        # 写入文件
        write_to(ip_list, os.path.join(self.out_file, "ip_online_sh.txt"))
        self.device_online_in_shanghai_count = len(ip_in_network_list)
        print("上海设备在线总量:", self.device_online_in_shanghai_count)
        return {
            "data": ip_in_network_list,  # 这是一个 [{},{},{}]
            "count": self.device_online_in_shanghai_count
        }

    # 4.设备在线 AND 在上海网段 AND 需要装椒图 || 不需要装椒图 || 没有椒图标签  【完成】
    def get_device_online_in_shanghai_need_jowto(self):
        item_list = self.get_device_online_in_shanghai()['data']  # 这个过来的是列表，[{},{},{}]
        need_list = []
        no_list = []
        no_tag = []
        need_ip = []
        no_need_ip = []
        no_tag_ip = []
        for item in item_list:
            if "椒图必要性/需要安装" in item['ipassets_ip_tags'] or "椒图必要性/需要安装" in item['ipassets_network_tags'] or "椒图必要性/需要安装" in item['ipassets_least_network_tags']:
                need_list.append(item)
                need_ip.append(item['ipassets_ip'])
            elif "椒图必要性/不需要安装" in item['ipassets_ip_tags'] or "椒图必要性/不需要安装" in item['ipassets_network_tags'] or "椒图必要性/不需要安装" in item['ipassets_least_network_tags']:
                no_list.append(item)
                no_need_ip.append(item['ipassets_ip'])
            else:
                no_tag.append(item)
                no_tag_ip.append(item['ipassets_ip'])
        # 写入文件
        write_to(need_ip, os.path.join(self.out_file, "ip_online_need_jt_sh.txt"))
        write_to(no_need_ip, os.path.join(self.out_file, "ip_online_no_need_jt_sh.txt"))
        write_to(no_tag_ip, os.path.join(self.out_file, "ip_online_no_jt_tag_sh.txt"))
        self.device_online_in_shanghai_need_jowto_count = len(need_list)
        self.device_online_in_shanghai_no_need_jowto_count = len(no_list)
        self.device_online_in_shanghai_no_jowto_tag_count = len(no_tag)
        print("上海设备在线需要装椒图总量:", self.device_online_in_shanghai_need_jowto_count)
        print("上海设备在线不需要装椒图总量:", self.device_online_in_shanghai_no_need_jowto_count)
        print("上海设备在线没有椒图标签总量:", self.device_online_in_shanghai_no_jowto_tag_count)
        return {
            "data": {
                "need_list": need_list,
                "no_list": no_list,
                "no_tag": no_tag,
            },
            "conut": {
                "need_count": self.device_online_in_shanghai_need_jowto_count,
                "no_count": self.device_online_in_shanghai_no_need_jowto_count,
                "no_tag_count": self.device_online_in_shanghai_no_jowto_tag_count,
            }
        }

    # 5.设备在线 AND 在上海网段 AND 需要装椒图 AND 椒图在线1 || 椒图离线0 || 椒图未安装2 【完成】
    def get_device_online_in_shanghai_need_jowto_status(self):
        item_list = self.get_device_online_in_shanghai_need_jowto()['data']['need_list']
        jowto_status_1 = []  # 在线
        jowto_status_0 = []  # 离线
        jowto_status_2 = []  # 未安装
        ip_1 = []
        ip_0 = []
        ip_2 = []
        for item in item_list:
            if item['jowto_onlineStatus'] == 1:
                jowto_status_1.append(item)
                ip_1.append(item['ipassets_ip'])
            elif item['jowto_onlineStatus'] == 0:
                jowto_status_0.append(item)
                ip_0.append(item['ipassets_ip'])
            else:
                jowto_status_2.append(item)
                ip_2.append(item['ipassets_ip'])
        # 写入文件
        write_to(ip_1, os.path.join(self.out_file, "ip_online_need_jt_1_sh.txt"))
        write_to(ip_0, os.path.join(self.out_file, "ip_online_need_jt_0_sh.txt"))
        write_to(ip_2, os.path.join(self.out_file, "ip_online_need_jt_2_sh.txt"))
        self.device_online_in_shanghai_need_jowto_status_1_count = len(jowto_status_1)
        self.device_online_in_shanghai_need_jowto_status_0_count = len(jowto_status_0)
        self.device_online_in_shanghai_need_jowto_status_2_count = len(jowto_status_2)
        print("上海设备在线需要装椒图椒图在线总量:", self.device_online_in_shanghai_need_jowto_status_1_count)
        print("上海设备在线需要装椒图椒图离线总量:", self.device_online_in_shanghai_need_jowto_status_0_count)
        print("上海设备在线需要装椒图椒图未安装总量:", self.device_online_in_shanghai_need_jowto_status_2_count)
        return {
            "data": {
                "jowto_status_1": jowto_status_1,
                "jowto_status_0": jowto_status_0,
                "jowto_status_2": jowto_status_2,
            },
            "count": {
                "jowto_status_1_count": self.device_online_in_shanghai_need_jowto_status_1_count,
                "jowto_status_0_count": self.device_online_in_shanghai_need_jowto_status_0_count,
                "jowto_status_2_count": self.device_online_in_shanghai_need_jowto_status_2_count,
            }
        }

    # # 6.设备在线 AND 在上海网段 AND 需要装椒图 AND 椒图在线1 || 椒图离线0 || 椒图未安装2 || 不同安全域
    def get_device_online_jowto_status_in_secAreas(self):
        # res = self.getSecDataOriginal()['data']
        res = self.get_device_online_in_shanghai_need_jowto_status()
        data = res['data']
        count = res['count']['jowto_status_1_count'] + res['count']['jowto_status_0_count'] + res['count']['jowto_status_2_count']
        ip_list_jw_1 = data.get('jowto_status_1',[])  # 获取在线椒图列表
        ip_list_jw_0 = data.get('jowto_status_0',[])  # 获取离线椒图列表
        ip_list_jw_2 = data.get('jowto_status_2',[])  # 获取未安装椒图列表

        S = {    # 1   0   2
            'S1': [[], [], []],
            'S2': [[], [], []],
            'S3': [[], [], []],
            'S4': [[], [], []],
            'S5': [[], [], []]
        }

        IP = {
            'S1': [[], [], []],
            'S2': [[], [], []],
            'S3': [[], [], []],
            'S4': [[], [], []],
            'S5': [[], [], []]
        }

        # 循环椒图在线的安全域分布情况

        # 辅助函数
        def distribute_items(items, index):
            for item in items:
                # online_status = item['jowto_onlineStatus']
                network_tags = item['ipassets_least_network_tags']
                if "IDC Level 01" in network_tags:
                    S['S1'][index].append(item)
                    IP['S1'][index].append(item['ipassets_ip'])
                elif "IDC Level 02" in network_tags:
                    S['S2'][index].append(item)
                    IP['S2'][index].append(item['ipassets_ip'])
                elif "IDC Level 03" in network_tags:
                    S['S3'][index].append(item)
                    IP['S3'][index].append(item['ipassets_ip'])
                elif "IDC Level 04" in network_tags:
                    S['S4'][index].append(item)
                    IP['S4'][index].append(item['ipassets_ip'])
                elif "IDC Level 05" in network_tags:
                    S['S5'][index].append(item)
                    IP['S5'][index].append(item['ipassets_ip'])

        distribute_items(ip_list_jw_1, 0)
        distribute_items(ip_list_jw_0, 1)
        distribute_items(ip_list_jw_2, 2)

        # 写入文件
        write_to(IP['S1'][0], os.path.join(self.out_file, "ip_jt_online_S1_sh.txt"))
        write_to(IP['S2'][0], os.path.join(self.out_file, "ip_jt_online_S2_sh.txt"))
        write_to(IP['S3'][0], os.path.join(self.out_file, "ip_jt_online_S3_sh.txt"))
        write_to(IP['S4'][0], os.path.join(self.out_file, "ip_jt_online_S4_sh.txt"))
        write_to(IP['S5'][0], os.path.join(self.out_file, "ip_jt_online_S5_sh.txt"))
        write_to(IP['S1'][1], os.path.join(self.out_file, "ip_jt_offline_S1_sh.txt"))
        write_to(IP['S2'][1], os.path.join(self.out_file, "ip_jt_offline_S2_sh.txt"))
        write_to(IP['S3'][1], os.path.join(self.out_file, "ip_jt_offline_S3_sh.txt"))
        write_to(IP['S4'][1], os.path.join(self.out_file, "ip_jt_offline_S4_sh.txt"))
        write_to(IP['S5'][1], os.path.join(self.out_file, "ip_jt_offline_S5_sh.txt"))
        write_to(IP['S1'][2], os.path.join(self.out_file, "ip_jt_no_install_S1_sh.txt"))
        write_to(IP['S2'][2], os.path.join(self.out_file, "ip_jt_no_install_S2_sh.txt"))
        write_to(IP['S3'][2], os.path.join(self.out_file, "ip_jt_no_install_S3_sh.txt"))
        write_to(IP['S4'][2], os.path.join(self.out_file, "ip_jt_no_install_S4_sh.txt"))
        write_to(IP['S5'][2], os.path.join(self.out_file, "ip_jt_no_install_S5_sh.txt"))

        s1_0 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_online_count']['S1'] = len(S['S1'][0])
        s2_0 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_online_count']['S2'] = len(S['S2'][0])
        s3_0 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_online_count']['S3'] = len(S['S3'][0])
        s4_0 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_online_count']['S4'] = len(S['S4'][0])
        s5_0 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_online_count']['S5'] = len(S['S5'][0])
        s1_1 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_offline_count']['S1'] = len(S['S1'][1])
        s2_1 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_offline_count']['S2'] = len(S['S2'][1])
        s3_1 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_offline_count']['S3'] = len(S['S3'][1])
        s4_1 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_offline_count']['S4'] = len(S['S4'][1])
        s5_1 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_offline_count']['S5'] = len(S['S5'][1])
        s1_2 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_no_install_count']['S1'] = len(S['S1'][2])
        s2_2 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_no_install_count']['S2'] = len(S['S2'][2])
        s3_2 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_no_install_count']['S3'] = len(S['S3'][2])
        s4_2 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_no_install_count']['S4'] = len(S['S4'][2])
        s5_2 = self.device_online_in_shanghai_jowto_status_count_in_secArea['jowto_no_install_count']['S5'] = len(S['S5'][2])


        print("上海椒图[在线]数量:S1有 {}台, S2有 {}台, S3有 {}台, S4有 {}台, S5有 {}台".format(s1_0, s2_0, s3_0, s4_0, s5_0))
        print("上海椒图[离线]数量:S1有 {}台, S2有 {}台, S3有 {}台, S4有 {}台, S5有 {}台".format(s1_1, s2_1, s3_1, s4_1, s5_1))
        print("上海椒图[未安装]数量:S1有 {}台, S2有 {}台, S3有 {}台, S4有 {}台, S5有 {}台".format(s1_2, s2_2, s3_2, s4_2, s5_2))

        return {
            "data": {
                "jowto_online":{
                    "S1":S['S1'][0],
                    "S2":S['S2'][0],
                    "S3":S['S3'][0],
                    "S4":S['S4'][0],
                    "S5":S['S5'][0],
                },
                "jowto_offline":{
                    "S1":S['S1'][1],
                    "S2":S['S2'][1],
                    "S3":S['S3'][1],
                    "S4":S['S4'][1],
                    "S5":S['S5'][1],
                },
                "jowto_no_install":{
                    "S1":S['S1'][2],
                    "S2":S['S2'][2],
                    "S3":S['S3'][2],
                    "S4":S['S4'][2],
                    "S5":S['S5'][2],
                }
            },
            "count":{
                "all_count":count,
                "jowto_online_count":{
                    "S1_count":s1_0,
                    "S2_count":s2_0,
                    "S3_count":s3_0,
                    "S4_count":s4_0,
                    "S5_count":s5_0,
                },
                "jowto_offline_count":{
                    "S1_count":s1_1,
                    "S2_count":s2_1,
                    "S3_count":s3_1,
                    "S4_count":s4_1,
                    "S5_count":s5_1,
                },
                "jowto_no_install_count":{
                    "S1_count":s1_2,
                    "S2_count":s2_2,
                    "S3_count":s3_2,
                    "S4_count":s4_2,
                    "S5_count":s5_2,
                }
            }
        }

    def main(self):
        res1 = self.get_device_jowto_status_secAreas()
        res2 = self.get_device_online_jowto_status_in_secAreas()
        # print(res['count'])
        res3 = self.get_count()  # 放在最后执行，必须等上面的函数执行完之后才有数据
        print(res3)



if __name__ == '__main__':
    # print(read_from("./file/IDC_network.txt"))
    jowto = jowtoDataCount()
    jowto.main()
    # res = jowto.get_device_jowto_status_secArea()
    # res = jowto.get_device_online_jowto_status_in_secAreas()
    # print(jowto.getSecDataOriginal()['data'])
    # print(jowto.getSecDataOriginal()['count'])
    # print(jowto.get_device_online()['data'])
    # print(jowto.get_device_online()['count'])
    # print(jowto.get_device_online_in_shanghai()['data'])
    # res = jowto.get_device_online_in_shanghai_need_jowto_status()
    # res = jowto.get_device_online_jowto_status_in_different_secArea()
