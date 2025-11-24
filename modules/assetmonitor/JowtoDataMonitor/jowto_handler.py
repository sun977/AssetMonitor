#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version:
    function: get jowto data count from sec
    date: 2024.12.03
    note:
         1.14大业务系统在线/离线/未安装数量 在 安全域分布情况
         2.翻页查询支持 lucene 语法

"""
from datetime import time, datetime
from netaddr import IPNetwork, IPAddress
# from sec.getSecApiClient import *
from modules.SecAPI.sec.getSecApiClient import *
# from tools.send_mail import *
from comm.send_mail import *

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


class jowtoDataCount:
    def __init__(self):
        self.cur_path = os.path.dirname(os.path.realpath(__file__))
        self.network_file = os.path.join(self.cur_path, "/../../../file/JowtoDataOut/IDC_network.txt")
        self.out_file = os.path.join(self.cur_path, "/../../../file/JowtoDataOut/")  # 文件输出
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
        self.businessSystem_14_count = None  # 14大业务系统

    # 获取SEC数据
    def getSecDataOriginal(self):
        # secClient = secApiClient()  # 初始化实例
        res = self.secClient.get_all_ipInformation()
        self.sec_data_count = len(res)
        print("SEC数据总量:", self.sec_data_count)
        return {
            "data": res,
            "count": self.sec_data_count
        }

    # 使用 lucene 查询获取SEC数据
    def getSecDataOriginalLucene(self, query):
        res = self.secClient.get_ipInformation_lucene_fanye(query)
        # res = self.secClient.get_ipInformation_lucene(query)
        self.sec_data_count = len(res)
        # print(query, self.sec_data_count) # 输出每次查询的内容
        return {
            "data": res,
            "count": self.sec_data_count
        }

    # 设备在线设备(筛选所有的服务器设备)
    def get_server_online(self):
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

    # 根据查询语法获取服务器信息
    def get_server_info_lucene(self, query):
        res = self.getSecDataOriginalLucene(query)['data']
        server_item_list = []
        server_ip_list = []
        for item in res:
            server_item_list.append(item)
            server_ip_list.append(item['ipassets_ip'])
        conut = len(server_item_list)
        write_to(server_ip_list, os.path.join(self.out_file, "server_ip_list.txt"))
        return {
            "data": server_item_list,  # 返回 item
            "count": conut
        }

    # 14大业务系统在线/离线/未安装数量 在 安全域分布情况
    # 14大业务系统总量: 383
    # 14大业务系统椒图在线: 344 在线率: 89.82 %
    # 14大业务系统椒图离线: 27 离线率: 7.05 %
    # 14大业务系统椒图未安装: 12 未安装率: 3.13 %
    # 14大业务系统椒图在线统计: 344 安全域分布: S1:2, S2: 0, S3: 171, S4: 171, S5: 0
    # 14大业务系统椒图离线统计: 27 安全域分布: S1: 1, S2: 0, S3: 12, S4: 14, S5: 0
    # 14大业务系统椒图未安装统计: 12 安全域分布: S1: 0, S2: 0, S3: 7, S4: 5, S5: 0
    def get_14_businessSystemCount(self):
        lucene = "ipassets_businessSystem:*十四大*"   # 查询语法
        res = self.getSecDataOriginalLucene(lucene)['data']   # 调用查询
        businessSystem_item_list = []  # 14大所有数据
        businessSystem_ip_list = []  # 14大所有IP
        jowto_online_ip_list = []  # 椒图在线
        jowto_offline_ip_list = []  # 椒图离线
        jowto_uninstall_ip_list = []  # 椒图未安装
        error_list = []
        # 0 在线 1 离线 2 未安装
        Area_jt_ip = {
            'S1': [[], [], []],
            'S2': [[], [], []],
            'S3': [[], [], []],
            'S4': [[], [], []],
            'S5': [[], [], []],
            'Serror': [[],[],[]]
        }

        # 过滤 IP 标签
        def filter_items(data, result):
            skip_tag = '/R/椒图必要性/不需要安装'
            for item in data:
                ip_assets_tags = item.get('ipassets_ip_tags', [])
                if skip_tag not in ip_assets_tags:
                    result.append(item)
                if ip_assets_tags is None:  # 如果ipassets_ip_tags为空，则添加
                    result.append(item)

        hand_res = []
        filter_items(res, hand_res)


        # for item in res:
        for item in hand_res:
            businessSystem_item_list.append(item)
            businessSystem_ip_list.append(item['ipassets_ip'])
            # 统计椒图状态
            jowto_state = item['jowto_onlineStatus']
            least_network_tags = item['ipassets_least_network_tags']
            if jowto_state == 1:   # 在线
                jowto_online_ip_list.append(item['ipassets_ip'])
                if ("01" or "(DMZ)") in least_network_tags:
                    Area_jt_ip['S1'][0].append(item['ipassets_ip'])
                elif "02" in least_network_tags:
                    Area_jt_ip['S2'][0].append(item['ipassets_ip'])
                elif "03" in least_network_tags:
                    Area_jt_ip['S3'][0].append(item['ipassets_ip'])
                elif "04" in least_network_tags:
                    Area_jt_ip['S4'][0].append(item['ipassets_ip'])
                elif "05" in least_network_tags:
                    Area_jt_ip['S5'][0].append(item['ipassets_ip'])
                else:  # 异常设备进入Serror
                    Area_jt_ip['Serror'][0].append(item['ipassets_ip'])
            elif jowto_state == 0:  # 离线
                jowto_offline_ip_list.append(item['ipassets_ip'])
                if ("01" or "(DMZ)") in least_network_tags:
                    Area_jt_ip['S1'][1].append(item['ipassets_ip'])
                elif "02" in least_network_tags:
                    Area_jt_ip['S2'][1].append(item['ipassets_ip'])
                elif "03" in least_network_tags:
                    Area_jt_ip['S3'][1].append(item['ipassets_ip'])
                elif "04" in least_network_tags:
                    Area_jt_ip['S4'][1].append(item['ipassets_ip'])
                elif "05" in least_network_tags:
                    Area_jt_ip['S5'][1].append(item['ipassets_ip'])
                else:  # 异常设备进入Serror
                    Area_jt_ip['Serror'][1].append(item['ipassets_ip'])
            elif jowto_state == 2:  # 未安装
                jowto_uninstall_ip_list.append(item['ipassets_ip'])
                if ("01" or "(DMZ)") in least_network_tags:
                    Area_jt_ip['S1'][2].append(item['ipassets_ip'])
                elif "02" in least_network_tags:
                    Area_jt_ip['S2'][2].append(item['ipassets_ip'])
                elif "03" in least_network_tags:
                    Area_jt_ip['S3'][2].append(item['ipassets_ip'])
                elif "04" in least_network_tags:
                    Area_jt_ip['S4'][2].append(item['ipassets_ip'])
                elif "05" in least_network_tags:
                    Area_jt_ip['S5'][2].append(item['ipassets_ip'])
                else:  # 异常设备进入Serror
                    Area_jt_ip['Serror'][2].append(item['ipassets_ip'])
            else:   # 异常
                error_list.append(item['ipassets_ip'])

        businessSystem_ip_list_count = len(businessSystem_ip_list)
        jowto_online_ip_list_conut = len(jowto_online_ip_list)
        jowto_offline_ip_list_count = len(jowto_offline_ip_list)
        jowto_uninstall_ip_list_count = len(jowto_uninstall_ip_list)
        s1_0 = len(Area_jt_ip['S1'][0])  # S1椒图在线
        s2_0 = len(Area_jt_ip['S2'][0])  # S2椒图在线
        s3_0 = len(Area_jt_ip['S3'][0])  # S3椒图在线
        s4_0 = len(Area_jt_ip['S4'][0])  # S4椒图在线
        s5_0 = len(Area_jt_ip['S5'][0])  # S5椒图在线
        s1_5_0 = s1_0 + s2_0 + s3_0 + s4_0 + s5_0
        s1_1 = len(Area_jt_ip['S1'][1])  # S1椒图离线
        s2_1 = len(Area_jt_ip['S2'][1])
        s3_1 = len(Area_jt_ip['S3'][1])
        s4_1 = len(Area_jt_ip['S4'][1])
        s5_1 = len(Area_jt_ip['S5'][1])
        s1_5_1 = s1_1 + s2_1 + s3_1 + s4_1 + s5_1
        s1_2 = len(Area_jt_ip['S1'][2])  # S1椒图未安装
        s2_2 = len(Area_jt_ip['S2'][2])
        s3_2 = len(Area_jt_ip['S3'][2])
        s4_2 = len(Area_jt_ip['S4'][2])
        s5_2 = len(Area_jt_ip['S5'][2])
        s1_5_2 = s1_2 + s2_2 + s3_2 + s4_2 + s5_2

        # 写入文件
        write_to(businessSystem_ip_list, os.path.join(self.out_file, "businessSystem/businessSystem14_ip.txt"))
        write_to(Area_jt_ip['S1'][0], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_online_S1.txt"))
        write_to(Area_jt_ip['S2'][0], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_online_S2.txt"))
        write_to(Area_jt_ip['S3'][0], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_online_S3.txt"))
        write_to(Area_jt_ip['S4'][0], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_online_S4.txt"))
        write_to(Area_jt_ip['S5'][0], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_online_S5.txt"))
        write_to(Area_jt_ip['S1'][1], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_offline_S1.txt"))
        write_to(Area_jt_ip['S2'][1], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_offline_S2.txt"))
        write_to(Area_jt_ip['S3'][1], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_offline_S3.txt"))
        write_to(Area_jt_ip['S4'][1], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_offline_S4.txt"))
        write_to(Area_jt_ip['S5'][1], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_offline_S5.txt"))
        write_to(Area_jt_ip['S1'][2], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_uninstall_S1.txt"))
        write_to(Area_jt_ip['S2'][2], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_uninstall_S2.txt"))
        write_to(Area_jt_ip['S3'][2], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_uninstall_S3.txt"))
        write_to(Area_jt_ip['S4'][2], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_uninstall_S4.txt"))
        write_to(Area_jt_ip['S5'][2], os.path.join(self.out_file, "businessSystem/businessSystem14_ip_jowto_uninstall_S5.txt"))

        print("14大业务系统总量:", businessSystem_ip_list_count)
        print("14大业务系统椒图在线:{} 在线率:{:.2f}".format(jowto_online_ip_list_conut,(jowto_online_ip_list_conut/businessSystem_ip_list_count)*100),"%")
        print("14大业务系统椒图离线:{} 离线率:{:.2f}".format(jowto_offline_ip_list_count,(jowto_offline_ip_list_count/businessSystem_ip_list_count)*100),"%")
        print("14大业务系统椒图未安装:{} 未安装率:{:.2f}".format(jowto_uninstall_ip_list_count,(jowto_uninstall_ip_list_count/businessSystem_ip_list_count)*100),"%")
        print("14大业务系统椒图在线统计: {} 安全域分布: S1:{}, S2:{}, S3:{}, S4:{}, S5:{} ".format( jowto_online_ip_list_conut, s1_0, s2_0, s3_0, s4_0, s5_0))
        print("14大业务系统椒图离线统计: {} 安全域分布: S1: {}, S2:{}, S3:{}, S4:{}, S5:{} ".format(jowto_offline_ip_list_count, s1_1, s2_1, s3_1, s4_1, s5_1))
        print("14大业务系统椒图未安装统计: {} 安全域分布: S1: {}, S2:{}, S3:{}, S4:{}, S5:{} ".format(jowto_uninstall_ip_list_count, s1_2, s2_2, s3_2, s4_2, s5_2))
        print("文件导出:(businessSystem14_ip.*):", self.out_file)

        return {
            "data":{
                "businessSystem_ip_list": businessSystem_ip_list,
                "jowto_online_ip_list": jowto_online_ip_list,
                "jowto_offline_ip_list": jowto_offline_ip_list,
                "jowto_uninstall_ip_list": jowto_uninstall_ip_list,
                "Area_jt_ip": Area_jt_ip
            },
            "count":{
                "businessSystem_ip_list_count": businessSystem_ip_list_count,
                "jowto_online_ip_list_conut": jowto_online_ip_list_conut,
                "jowto_offline_ip_list_count": jowto_offline_ip_list_count,
                "jowto_uninstall_ip_list_count": jowto_uninstall_ip_list_count,
            },
            "rate":{
                "online_rate": (jowto_online_ip_list_conut/businessSystem_ip_list_count)*100,
                "offline_rate": (jowto_offline_ip_list_count/businessSystem_ip_list_count)*100,
                "install_rate": ((jowto_online_ip_list_conut + jowto_offline_ip_list_count)/businessSystem_ip_list_count)*100,  # 添加安装率
                "uninstall_rate": (jowto_uninstall_ip_list_count/businessSystem_ip_list_count)*100,
            }
        }


    # 获取设备信息 去除关联IP【太慢了】
    def get_ipinfo_remove_ipassets_other_iplist(self, query):
        # (ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网"))))
        luce = query
        server_item_list = []
        server_ip_list = []
        res = self.get_server_info_lucene(luce)['data']
        for item in res:
            # server_item_list.append(item)
            # 如果有 ipassets_other_iplist 存在，择取查询 ipassets_other_iplist 的椒图状态
            if item['ipassets_other_iplist']:
                luce2 = 'ipassets_ip:{}'.format(item['ipassets_other_iplist'])
                # res_jowto_onlineStatus = self.get_server_info_lucene(luce2)['data'][0]['jowto_onlineStatus'] # 获取关联IP的椒图状态
                res_jowto = self.get_server_info_lucene(luce2)['data'][0] if 'data' in self.get_server_info_lucene(luce2) and len(self.get_server_info_lucene(luce2)['data']) > 0 else {}
                res_jowto_onlineStatus = res_jowto.get('jowto_onlineStatus', None)  # 查询为空时，返回None

                if res_jowto_onlineStatus == 2:  # 如果椒图未安装，则统计这个设备
                    # print("关联设备椒图未安装:", item['ipassets_ip'], item['ipassets_other_iplist'])
                    server_item_list.append(item)
                    server_ip_list.append(item['ipassets_ip'])
                else:
                    continue  # 如果椒图在线或离线，则不统计这个设备
            else:
                server_item_list.append(item)
                server_ip_list.append(item['ipassets_ip'])
        count = len(server_ip_list)
        write_to(server_ip_list, os.path.join(self.out_file, "businessSystem/test.txt"))
        return {
            "data": server_item_list,
            "count": count
        }


    # 获取椒图需要安装情况分布
    # 椒图需要安装设备总量: 19056
    # 椒图需要安装设备在线: 11112  在线率: 58.31 %
    # 椒图需要安装设备离线: 1832 离线率: 9.61 %
    # 椒图需要安装设备已安装: 12944 安装率: 67.93 %
    # 椒图需要安装设备未安装: 6112 未安装率: 32.07 %
    def get_luc_need_jowto(self):
        luc_need_jowto = '(ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网"'
        luc_need_jowto_online = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND jowto_onlineStatus:1'
        luc_need_jowto_offline = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND jowto_onlineStatus:0'
        luc_need_jowto_no_install = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND jowto_onlineStatus:2'

        res_luc_need_jowto = self.get_server_info_lucene(luc_need_jowto)
        res_luc_need_jowto_online = self.get_server_info_lucene(luc_need_jowto_online)
        res_luc_need_jowto_offline = self.get_server_info_lucene(luc_need_jowto_offline)
        res_luc_need_jowto_no_install = self.get_server_info_lucene(luc_need_jowto_no_install)


        # 添加判断 ipassets_ip_tag
        ## 过滤 ipassets_ip_tag 函数
        def filter_items(data, result):
            skip_tag = '/R/椒图必要性/不需要安装'
            for item in data:
                ip_assets_tags = item.get('ipassets_ip_tags', [])
                if skip_tag not in ip_assets_tags:
                    result.append(item)
                if ip_assets_tags is None:  # 如果ipassets_ip_tags为空，则添加
                    result.append(item)

        hand_res_luc_need_jowto = []
        filter_items(res_luc_need_jowto['data'], hand_res_luc_need_jowto)
        hand_res_luc_need_jowto_online = []
        filter_items(res_luc_need_jowto_online['data'], hand_res_luc_need_jowto_online)
        hand_res_luc_need_jowto_offline = []
        filter_items(res_luc_need_jowto_offline['data'], hand_res_luc_need_jowto_offline)
        hand_res_luc_need_jowto_no_install = []
        filter_items(res_luc_need_jowto_no_install['data'], hand_res_luc_need_jowto_no_install)

        ## 计算各种率
        total_need_jowto = len(hand_res_luc_need_jowto)
        online_need_jowto = len(hand_res_luc_need_jowto_online)
        offline_need_jowto = len(hand_res_luc_need_jowto_offline)
        no_install_need_jowto = len(hand_res_luc_need_jowto_no_install)

        online_per = (online_need_jowto / (online_need_jowto + offline_need_jowto) * 100)
        offline_per = (offline_need_jowto / (online_need_jowto + offline_need_jowto) * 100)
        install_per = ((online_need_jowto + offline_need_jowto) / total_need_jowto * 100)
        no_install_per = (no_install_need_jowto / total_need_jowto * 100)

        # online_per = ((int(res_luc_need_jowto_online['count'])/(int(res_luc_need_jowto_online['count']) + int(res_luc_need_jowto_offline['count'])))*100)
        # offline_per = ((int(res_luc_need_jowto_offline['count'])/(int(res_luc_need_jowto_online['count']) + int(res_luc_need_jowto_offline['count'])))*100)
        # install_per = (((int(res_luc_need_jowto_online['count']) + int(res_luc_need_jowto_offline['count']))/int(res_luc_need_jowto['count']))*100)
        # no_install_per = ((int(res_luc_need_jowto_no_install['count'])/int(res_luc_need_jowto['count']))*100)

        # 打印结果
        print(f"椒图需要安装设备总量：{total_need_jowto}")
        print(f"椒图需要安装设备在线:{online_need_jowto} 在线率:{online_per:.2f}%")
        print(f"椒图需要安装设备离线:{offline_need_jowto} 离线率:{offline_per:.2f}%")
        print(f"椒图需要安装设备已安装:{online_need_jowto + offline_need_jowto} 安装率:{install_per:.2f}%")
        print(f"椒图需要安装设备未安装:{no_install_need_jowto} 未安装率:{no_install_per:.2f}%")

        # print("椒图需要安装设备总量:{}".format(res_luc_need_jowto['count']))
        # print("椒图需要安装设备在线:{} 在线率:{:.2f}".format(res_luc_need_jowto_online['count'], online_per), "%")
        # print("椒图需要安装设备离线:{} 离线率:{:.2f}".format(res_luc_need_jowto_offline['count'], offline_per), "%")
        # print("椒图需要安装设备已安装:{} 安装率:{:.2f}".format((int(res_luc_need_jowto_online['count']) + int(res_luc_need_jowto_offline['count'])), install_per), "%")
        # print("椒图需要安装设备未安装:{} 未安装率:{:.2f}".format(res_luc_need_jowto_no_install['count'], no_install_per), "%")

        return {
            "data": {
                "jowto": hand_res_luc_need_jowto,
                "jowto_online": hand_res_luc_need_jowto_online,
                "jowto_offline": hand_res_luc_need_jowto_offline,
                "jowto_no_install": hand_res_luc_need_jowto_no_install
            },
            "count": {
                "jowto": total_need_jowto,
                "jowto_online": online_need_jowto,
                "jowto_offline": offline_need_jowto,
                "jowto_no_install": no_install_need_jowto
            },
            "rate": {
                "online_rate": online_per,
                "offline_rate": offline_per,
                "install_rate": install_per,
                "no_install_rate": no_install_per
            }
        }


    # 获取互联网侧椒图需要安装情况分布
    # 互联网侧椒图需要安装设备总量: 1202
    # 互联网侧椒图需要安装设备在线: 1023 在线率: 85.11 %
    # 互联网侧椒图需要安装设备离线: 117 离线率: 9.73 %
    # 互联网侧椒图需要安装设备已安装: 1140 安装率: 94.84 %
    # 互联网侧椒图需要安装设备未安装: 62 未安装率: 5.16 %
    def get_luc_need_jowto_expose_internet(self):
        # 问题：我这的代码没有优先级的情况，不同的标签最小网段已经有椒图不用装的标签，但是网段标签还有椒图需要安装，这部分数据也会计算在内
        # 解决办法：增加一步判断 ipassets_ip_tags 判断，如果ipassets_ip_tags有/R/椒图必要性/不需要安装，则跳过，不统计 --- 20241203
        expose_IP_list = []
        expose_IP_online_list = []
        expose_IP_offline_list = []
        expose_IP_no_install_list = []

        luc_need_jowto_expose_public = 'ipassets_ip_type:"内网" AND (ipassets_is_expose_public_ip:1 AND (ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))))'
        luc_need_jowto_expose_public_online = '(ipassets_is_expose_public_ip:1 AND (ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND jowto_onlineStatus:1 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网"))))) AND ipassets_ip_type:"内网"'
        luc_need_jowto_expose_public_offline = '(ipassets_is_expose_public_ip:1 AND (ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND jowto_onlineStatus:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网"))))) AND ipassets_ip_type:"内网"'
        luc_need_jowto_expose_public_no_install = '(ipassets_is_expose_public_ip:1 AND (ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND jowto_onlineStatus:2 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网"))))) AND ipassets_ip_type:"内网"'

        # 获取SEC数据
        res_luc_need_jowto_expose_public = self.get_server_info_lucene(luc_need_jowto_expose_public)
        res_luc_need_jowto_expose_public_online = self.get_server_info_lucene(luc_need_jowto_expose_public_online)
        res_luc_need_jowto_expose_public_offline = self.get_server_info_lucene(luc_need_jowto_expose_public_offline)
        res_luc_need_jowto_expose_public_no_install = self.get_server_info_lucene(luc_need_jowto_expose_public_no_install)


        # 添加判断 ipassets_ip_tags
        ## 过滤 ipassets_ip_tags 标签函数
        def filter_items(data, result):
            skip_tag = '/R/椒图必要性/不需要安装'
            for item in data:
                ip_assets_tags = item.get('ipassets_ip_tags', [])
                if skip_tag not in ip_assets_tags:
                    result.append(item)
                if ip_assets_tags is None:  # 如果ipassets_ip_tags为空，则添加
                    result.append(item)


        hand_res_luc_need_jowto_expose_public = []  # 总数
        filter_items(res_luc_need_jowto_expose_public['data'], hand_res_luc_need_jowto_expose_public)

        hand_res_luc_need_jowto_expose_public_online = []  # 在线
        filter_items(res_luc_need_jowto_expose_public_online['data'], hand_res_luc_need_jowto_expose_public_online)

        hand_res_luc_need_jowto_expose_public_offline = []  # 离线
        filter_items(res_luc_need_jowto_expose_public_offline['data'], hand_res_luc_need_jowto_expose_public_offline)

        hand_res_luc_need_jowto_expose_public_no_install = []  # 未安装
        filter_items(res_luc_need_jowto_expose_public_no_install['data'], hand_res_luc_need_jowto_expose_public_no_install)
        # print("过滤后的椒图未安装item：", hand_res_luc_need_jowto_expose_public_no_install)

        # xxx / 需要安装的IP总数
        ## 计算各部分的长度(个数)
        total_devices = len(hand_res_luc_need_jowto_expose_public)
        online_devices = len(hand_res_luc_need_jowto_expose_public_online)
        offline_devices = len(hand_res_luc_need_jowto_expose_public_offline)
        no_install_devices = len(hand_res_luc_need_jowto_expose_public_no_install)
        ## 计算各种率
        online_per = (online_devices / (online_devices + offline_devices) *100)
        offline_per = (offline_devices / (online_devices + offline_devices) *100)
        install_per = ((online_devices + offline_devices) / total_devices * 100)
        no_install_per = (no_install_devices / total_devices * 100)

        # online_per = ((int(res_luc_need_jowto_expose_public_online['count']) / (int(res_luc_need_jowto_expose_public_online['count']) + int(res_luc_need_jowto_expose_public_offline['count']))) * 100)
        # offline_per = ((int(res_luc_need_jowto_expose_public_offline['count']) / (int(res_luc_need_jowto_expose_public_online['count']) + int(res_luc_need_jowto_expose_public_offline['count']))) * 100)
        # install_per = (((int(res_luc_need_jowto_expose_public_online['count']) + int(res_luc_need_jowto_expose_public_offline['count'])) / int(res_luc_need_jowto_expose_public['count'])) * 100)
        # no_install_per = ((int(res_luc_need_jowto_expose_public_no_install['count']) / int(res_luc_need_jowto_expose_public['count'])) * 100)

        # 装填IP到列表
        for item in hand_res_luc_need_jowto_expose_public:
            expose_IP_list.append(item['ipassets_ip'])
        for item in hand_res_luc_need_jowto_expose_public_online:
            expose_IP_online_list.append(item['ipassets_ip'])
        for item in hand_res_luc_need_jowto_expose_public_offline:
            expose_IP_offline_list.append(item['ipassets_ip'])
        for item in hand_res_luc_need_jowto_expose_public_no_install:
            expose_IP_no_install_list.append(item['ipassets_ip'])
        # 输出结果到文件
        write_to(expose_IP_list, self.out_file + 'expose2Internet/expose_IP_list.txt')
        write_to(expose_IP_online_list, self.out_file + 'expose2Internet/expose_IP_jowto_online_list.txt')
        write_to(expose_IP_offline_list, self.out_file + 'expose2Internet/expose_IP_jowto_offline_list.txt')
        write_to(expose_IP_no_install_list, self.out_file + 'expose2Internet/expose_IP_jowto_no_install_list.txt')


        # 打印
        # 计算安装率、未安装率等
        install_devices = online_devices + offline_devices
        install_rate = (install_devices / total_devices) * 100 if total_devices > 0 else 0
        no_install_rate = (no_install_devices / total_devices) * 100 if total_devices > 0 else 0

        # 打印结果
        print(f"互联网侧椒图需要安装设备总量: {total_devices}")
        print(f"互联网侧椒图需要安装设备在线: {online_devices} 在线率: {online_per:.2f}%")
        print(f"互联网侧椒图需要安装设备离线: {offline_devices} 离线率: {offline_per:.2f}%")
        print(f"互联网侧椒图需要安装设备已安装: {install_devices} 安装率: {install_rate:.2f}%")
        print(f"互联网侧椒图需要安装设备未安装: {no_install_devices} 未安装率: {no_install_rate:.2f}%")


        # print("互联网侧椒图需要安装设备总量:{}".format(res_luc_need_jowto_expose_public['count']))
        # print("互联网侧椒图需要安装设备在线:{} 在线率:{:.2f}".format(res_luc_need_jowto_expose_public_online['count'], online_per), "%")
        # print("互联网侧椒图需要安装设备离线:{} 离线率:{:.2f}".format(res_luc_need_jowto_expose_public_offline['count'], offline_per), "%")
        # print("互联网侧椒图需要安装设备已安装:{} 安装率:{:.2f}".format((int(res_luc_need_jowto_expose_public_online['count']) + int(res_luc_need_jowto_expose_public_offline['count'])), install_per), "%")
        # print("互联网侧椒图需要安装设备未安装:{} 未安装率:{:.2f}".format(res_luc_need_jowto_expose_public_no_install['count'], no_install_per), "%")


        return {
            "data": {
                "jowto": hand_res_luc_need_jowto_expose_public,
                "jowto_online": hand_res_luc_need_jowto_expose_public_online,
                "jowto_offline": hand_res_luc_need_jowto_expose_public_offline,
                "jowto_no_install": hand_res_luc_need_jowto_expose_public_no_install
            },
            "count": {
                "jowto_count": total_devices,
                "jowto_online_count": online_devices,
                "jowto_offline_count": offline_devices,
                "jowto_no_install_count": no_install_devices
            },
            "rate": {
                "online_rate": online_per,
                "offline_rate": offline_per,
                "install_rate": install_per,
                "no_install_rate": no_install_per
            }
        }

    # 统计S1和S3的椒图安装分布情况
    # S1椒图需要安装设备总量: 1432
    # S1椒图需要安装设备在线: 1223 在线率: 85.41 %
    # S1椒图需要安装设备离线: 86 离线率: 6.01 %
    # S1椒图需要安装设备已安装: 1309 安装率: 91.41 %
    # S1椒图需要安装设备未安装: 123 未安装率: 8.59 %
    # S3椒图需要安装设备总量: 17054
    # S3椒图需要安装设备在线: 9447 在线率: 55.39 %
    # S3椒图需要安装设备离线: 1694 离线率: 9.93 %
    # S3椒图需要安装设备已安装: 11141 安装率: 65.33 %
    # S3椒图需要安装设备未安装: 5912 未安装率: 34.67 %
    def get_luc_need_jowto_S1_S3(self):
        luc_need_jowto_S1 = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND ipassets_least_network_tags:*01*'

        luc_need_jowto_S1_online = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 ADN jowto_onlineStatus:1 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND ipassets_least_network_tags:*01*'
        luc_need_jowto_S1_offline = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 ADN jowto_onlineStatus:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND ipassets_least_network_tags:*01*'
        luc_need_jowto_S1_no_install = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 ADN jowto_onlineStatus:2 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND ipassets_least_network_tags:*01*'

        luc_need_jowto_S3 = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND ipassets_least_network_tags:*03*'

        luc_need_jowto_S3_online = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 ADN jowto_onlineStatus:1 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND ipassets_least_network_tags:*03*'
        luc_need_jowto_S3_offline = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 ADN jowto_onlineStatus:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND ipassets_least_network_tags:*03*'
        luc_need_jowto_S3_no_install = '((ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 ADN jowto_onlineStatus:2 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网" OR "/R/网段用途/带外管理")))) AND ipassets_ip_type:"内网") AND ipassets_least_network_tags:*03*'


        res_luc_need_jowto_S1 = self.get_server_info_lucene(luc_need_jowto_S1)
        res_luc_need_jowto_S1_online = self.get_server_info_lucene(luc_need_jowto_S1_online)
        res_luc_need_jowto_S1_offline = self.get_server_info_lucene(luc_need_jowto_S1_offline)
        res_luc_need_jowto_S1_no_install = self.get_server_info_lucene(luc_need_jowto_S1_no_install)
        res_luc_need_jowto_S3 = self.get_server_info_lucene(luc_need_jowto_S3)
        res_luc_need_jowto_S3_online = self.get_server_info_lucene(luc_need_jowto_S3_online)
        res_luc_need_jowto_S3_offline = self.get_server_info_lucene(luc_need_jowto_S3_offline)
        res_luc_need_jowto_S3_no_install = self.get_server_info_lucene(luc_need_jowto_S3_no_install)

        # 过滤掉 IP 标签 椒图免装的设备
        def filter_items(data, result):
            skip_tag = '/R/椒图必要性/不需要安装'
            for item in data:
                ip_assets_tags = item.get('ipassets_ip_tags', [])
                if skip_tag not in ip_assets_tags:
                    result.append(item)
                if ip_assets_tags is None:  # 如果ipassets_ip_tags为空，则添加
                    result.append(item)

        hand_res_luc_need_jowto_S1 = []
        filter_items(res_luc_need_jowto_S1['data'], hand_res_luc_need_jowto_S1)
        hand_res_luc_need_jowto_S1_online = []
        filter_items(res_luc_need_jowto_S1_online['data'], hand_res_luc_need_jowto_S1_online)
        hand_res_luc_need_jowto_S1_offline = []
        filter_items(res_luc_need_jowto_S1_offline['data'], hand_res_luc_need_jowto_S1_offline)
        hand_res_luc_need_jowto_S1_no_install = []
        filter_items(res_luc_need_jowto_S1_no_install['data'], hand_res_luc_need_jowto_S1_no_install)
        hand_res_luc_need_jowto_S3 = []
        filter_items(res_luc_need_jowto_S3['data'], hand_res_luc_need_jowto_S3)
        hand_res_luc_need_jowto_S3_online = []
        filter_items(res_luc_need_jowto_S3_online['data'], hand_res_luc_need_jowto_S3_online)
        hand_res_luc_need_jowto_S3_offline = []
        filter_items(res_luc_need_jowto_S3_offline['data'], hand_res_luc_need_jowto_S3_offline)
        hand_res_luc_need_jowto_S3_no_install = []
        filter_items(res_luc_need_jowto_S3_no_install['data'], hand_res_luc_need_jowto_S3_no_install)

        # 计算长度
        len_s1_online = len(hand_res_luc_need_jowto_S1_online)
        len_s1_offline = len(hand_res_luc_need_jowto_S1_offline)
        len_s1_total = len(hand_res_luc_need_jowto_S1)
        len_s1_no_install = len(hand_res_luc_need_jowto_S1_no_install)

        len_s3_online = len(hand_res_luc_need_jowto_S3_online)
        len_s3_offline = len(hand_res_luc_need_jowto_S3_offline)
        len_s3_total = len(hand_res_luc_need_jowto_S3)
        len_s3_no_install = len(hand_res_luc_need_jowto_S3_no_install)

        def calculate_percentage(numerator, denominator):
            if denominator == 0:
                return 0
            return (numerator / denominator) * 100
        # S1相关计算
        s1_online_per = calculate_percentage(len_s1_online, len_s1_online + len_s1_offline)
        s1_offline_per = calculate_percentage(len_s1_offline, len_s1_online + len_s1_offline)
        s1_install_per = calculate_percentage(len_s1_online + len_s1_offline, len_s1_total)
        s1_no_install_per = calculate_percentage(len_s1_no_install, len_s1_total)

        # S3相关计算
        s3_online_per = calculate_percentage(len_s3_online, len_s3_online + len_s3_offline)
        s3_offline_per = calculate_percentage(len_s3_offline, len_s3_online + len_s3_offline)
        s3_install_per = calculate_percentage(len_s3_online + len_s3_offline, len_s3_total)
        s3_no_install_per = calculate_percentage(len_s3_no_install, len_s3_total)
        # s1_online_per = ((int(res_luc_need_jowto_S1_online['count']) / ( int(res_luc_need_jowto_S1_online['count']) + int(res_luc_need_jowto_S1_offline['count']))) * 100)
        # s1_offline_per = ((int(res_luc_need_jowto_S1_offline['count']) / (int(res_luc_need_jowto_S1_online['count']) + int(res_luc_need_jowto_S1_offline['count']))) * 100)
        # s1_install_per = (((int(res_luc_need_jowto_S1_online['count']) + int(res_luc_need_jowto_S1_offline['count'])) / int(res_luc_need_jowto_S1['count'])) * 100)
        # s1_no_install_per = ((int(res_luc_need_jowto_S1_no_install['count']) / int(res_luc_need_jowto_S1['count'])) * 100)
        # s3_online_per = ((int(res_luc_need_jowto_S3_online['count']) / (int(res_luc_need_jowto_S3_online['count']) + int(res_luc_need_jowto_S3_offline['count']))) * 100)
        # s3_offline_per = ((int(res_luc_need_jowto_S3_offline['count']) / (int(res_luc_need_jowto_S3_online['count']) + int(res_luc_need_jowto_S3_offline['count']))) * 100)
        # s3_install_per = (((int(res_luc_need_jowto_S3_online['count']) + int(res_luc_need_jowto_S3_offline['count'])) / int(res_luc_need_jowto_S3['count'])) * 100)
        # s3_no_install_per = ((int(res_luc_need_jowto_S3_no_install['count']) / int(res_luc_need_jowto_S3['count'])) * 100)

        print(f"互联网侧椒图需要安装设备在线: {online_devices} 在线率: {online_per:.2f}%")

        print(f"S1椒图需要安装设备总量:{len_s1_total}")
        print(f"S1椒图需要安装设备在线:{len_s1_online} 在线率:{s1_online_per:.2f%}")
        print(f"S1椒图需要安装设备离线:{len_s1_offline} 离线率:{s1_offline_per:.2f}")
        print(f"S1椒图需要安装设备已安装:{len_s1_online + len_s1_offline} 安装率:{s1_install_per:.2f}%")
        print(f"S1椒图需要安装设备未安装:{len_s1_no_install} 未安装率:{s1_no_install_per:.2f}")
        print(f"S3椒图需要安装设备总量:{len_s3_total}")
        print(f"S3椒图需要安装设备在线:{len_s3_online} 在线率:{s3_online_per:.2f}%")
        print(f"S3椒图需要安装设备离线:{len_s3_offline} 离线率:{s3_offline_per:.2f}%")
        print(f"S3椒图需要安装设备已安装:{len_s3_online + len_s3_offline} 安装率:{s3_install_per:.2f}%")
        print(f"S3椒图需要安装设备未安装:{len_s3_no_install} 未安装率:{s3_no_install_per:.2f}%")

        return {
            "data": {
                "jowto_S1": hand_res_luc_need_jowto_S1,
                "jowto_S1_online": hand_res_luc_need_jowto_S1_online,
                "jowto_S1_offline": hand_res_luc_need_jowto_S1_offline,
                "jowto_S1_no_install": hand_res_luc_need_jowto_S1_no_install,
                "jowto_S3": hand_res_luc_need_jowto_S3,
                "jowto_S3_online": hand_res_luc_need_jowto_S3_online,
                "jowto_S3_offline": hand_res_luc_need_jowto_S3_offline,
                "jowto_S3_no_install": hand_res_luc_need_jowto_S3_no_install
            },
            "count": {
                "jowto_S1_count": len_s1_total,
                "jowto_S1_online_count": len_s1_online,
                "jowto_S1_offline_count": len_s1_offline,
                "jowto_S1_no_install_count": len_s3_no_install,
                "jowto_S3_count": len_s3_total,
                "jowto_S3_online_count": len_s3_online,
                "jowto_S3_offline_count": len_s3_offline,
                "jowto_S3_no_install_count": len_s3_no_install
            },
            "rate": {
                "s1_online_rate": s1_online_per,
                "s1_offline_rate": s1_offline_per,
                "s1_install_rate": s1_install_per,
                "s1_no_install_rate": s1_no_install_per,
                "s3_online_rate": s3_online_per,
                "s3_offline_rate": s3_offline_per,
                "s3_install_rate": s3_install_per,
                "s3_no_install_rate": s3_no_install_per
            }
        }



    # 统计函数
    def jowto_info(self):
        res_business = self.get_14_businessSystemCount()
        res_jowto = self.get_luc_need_jowto()
        res_jowto_expose = self.get_luc_need_jowto_expose_internet()
        res_jowto_S1_S3 = self.get_luc_need_jowto_S1_S3()

        return {
            "data":{
                "business":res_business['data'],
                "jowto":res_jowto['data'],
                "jowto_expose_internet":res_jowto_expose['data'],
                "jowto_S1_S3":res_jowto_S1_S3['data']
            },
            "count":{
                "business":res_business['count'],
                "jowto":res_jowto['count'],
                "jowto_expose_internet":res_jowto_expose['count'],
                "jowto_S1_S3":res_jowto_S1_S3['count']
            },
            "rate":{
                "business":res_business['rate'],
                "jowto":res_jowto['rate'],
                "jowto_expose_internet":res_jowto_expose['rate'],
                "jowto_S1_S3":res_jowto_S1_S3['rate']
            }
        }

    # send mail
    def send_mail(self):
        TODAY = datetime.now().strftime('%Y-%m-%d')
        res = self.jowto_info()
        mail = MAIL()
        subject = f'今日椒图数据统计-{TODAY}'
        userlist = ['sunhaobo@qianxin.com']
        content = """
        ------ 椒图总量数据统计 ------
        椒图需要安装设备总量:{}
        椒图需要安装设备在线:{} 在线率:{:.2f}%
        椒图需要安装设备离线:{} 离线率:{:.2f}%
        椒图需要安装设备已安装:{} 安装率:{:.2f}%
        椒图需要安装设备未安装:{} 未安装率:{:.2f}%
        
        ------ 14大椒图数据统计 ------
        14大业务系统总量:{}
        14大业务系统在线:{} 在线率:{:.2f}%
        14大业务系统离线:{} 离线率:{:.2f}%
        14大业务系统未安装:{} 未安装率:{:.2f}%
        
        ------ 互联网椒图数据统计 ------
        互联网侧椒图需要安装设备总量:{}
        互联网侧椒图需要安装设备在线:{} 在线率:{:.2f}%
        互联网侧椒图需要安装设备离线:{} 离线率:{:.2f}%
        互联网侧椒图需要安装设备已安装:{} 安装率:{:.2f}%
        互联网侧椒图需要安装设备未安装:{} 未安装率:{:.2f}%
       
        ------ S1椒图数据统计 ------
        S1椒图需要安装设备总量:{}
        S1椒图需要安装设备在线:{} 在线率:{:.2f}%
        S1椒图需要安装设备离线:{} 离线率:{:.2f}%
        S1椒图需要安装设备已安装:{} 安装率:{:.2f}%
        S1椒图需要安装设备未安装:{} 未安装率:{:.2f}%
        
        ------ S3椒图数据统计 ------
        S3椒图需要安装设备总量:{}
        S3椒图需要安装设备在线:{} 在线率:{:.2f}%
        S3椒图需要安装设备离线:{} 离线率:{:.2f}%
        S3椒图需要安装设备已安装:{} 安装率:{:.2f}%
        S3椒图需要安装设备未安装:{} 未安装率:{:.2f}%
        """.format(
            # 椒图总量
            res['count']['jowto']['jowto'],
            res['count']['jowto']['jowto_online'], res['rate']['jowto']['online_rate'],
            res['count']['jowto']['jowto_offline'], res['rate']['jowto']['offline_rate'],
            int(res['count']['jowto']['jowto_online'] + res['count']['jowto']['jowto_offline']), res['rate']['jowto']['install_rate'],  # 修改
            res['count']['jowto']['jowto_no_install'], res['rate']['jowto']['no_install_rate'],
            # 14大业务系统
            res['count']['business']['businessSystem_ip_list_count'],
            res['count']['business']['jowto_online_ip_list_conut'], res['rate']['business']['online_rate'],
            res['count']['business']['jowto_offline_ip_list_count'], res['rate']['business']['offline_rate'],
            res['count']['business']['jowto_uninstall_ip_list_count'], res['rate']['business']['uninstall_rate'],
            # 互联网侧椒图
            res['count']['jowto_expose_internet']['jowto_count'],
            res['count']['jowto_expose_internet']['jowto_online_count'], res['rate']['jowto_expose_internet']['online_rate'],
            res['count']['jowto_expose_internet']['jowto_offline_count'], res['rate']['jowto_expose_internet']['offline_rate'],
            int(res['count']['jowto_expose_internet']['jowto_online_count'] + res['count']['jowto_expose_internet']['jowto_offline_count']), res['rate']['jowto_expose_internet']['install_rate'], # 修改
            res['count']['jowto_expose_internet']['jowto_no_install_count'], res['rate']['jowto_expose_internet']['no_install_rate'],
            # S1椒图
            res['count']['jowto_S1_S3']['jowto_S1_count'],
            res['count']['jowto_S1_S3']['jowto_S1_online_count'], res['rate']['jowto_S1_S3']['s1_online_rate'],
            res['count']['jowto_S1_S3']['jowto_S1_offline_count'], res['rate']['jowto_S1_S3']['s1_offline_rate'],
            int(res['count']['jowto_S1_S3']['jowto_S1_online_count'] + res['count']['jowto_S1_S3']['jowto_S1_offline_count']), res['rate']['jowto_S1_S3']['s1_install_rate'], # 修改
            res['count']['jowto_S1_S3']['jowto_S1_no_install_count'], res['rate']['jowto_S1_S3']['s1_no_install_rate'],
            # S3椒图
            res['count']['jowto_S1_S3']['jowto_S3_count'],
            res['count']['jowto_S1_S3']['jowto_S3_online_count'], res['rate']['jowto_S1_S3']['s3_online_rate'],
            res['count']['jowto_S1_S3']['jowto_S3_offline_count'], res['rate']['jowto_S1_S3']['s3_offline_rate'],
            int(res['count']['jowto_S1_S3']['jowto_S3_online_count'] + res['count']['jowto_S1_S3']['jowto_S3_offline_count']), res['rate']['jowto_S1_S3']['s3_install_rate'], # 修改
            res['count']['jowto_S1_S3']['jowto_S3_no_install_count'], res['rate']['jowto_S1_S3']['s3_no_install_rate']
        )

        mail.send_mail(subject, userlist, content)



# 获取互联网暴露IP的椒图信息情况
def expose2internethandler():
    jowto = jowtoDataCount()
    res = jowto.get_luc_need_jowto_expose_internet()
    expose_IP_list = res['data']['jowto']
    expose_IP_online_list = res['data']['jowto_online']
    expose_IP_offline_list = res['data']['jowto_offline']
    expose_IP_no_install_list = res['data']['jowto_no_install']
    # print("暴露互联网未安装jowto：", expose_IP_no_install_list['data'])
    for item in expose_IP_no_install_list:
        print("暴露互联网未安装jowto:", item['ipassets_ip'], item['ipassets_businessSystem'])




if __name__ == '__main__':
    jowto = jowtoDataCount()
    # jowto.send_mail()
    # jowto.get_14_businessSystemCount()
    # query = 'ipassets_ip:"211.95.50.188"'
    # query = '(ipassets_status:"在线" AND ((ipassets_network_tags:"/R/椒图必要性/需要安装" OR ipassets_ip_tags:"/R/椒图必要性/需要安装") AND ipassets_is_vip:0 AND NOT(ipassets_least_network_tags:("/R/网段用途/网络设备" OR "/R/网段用途/IOT设备" OR "/R/安全域/内部服务器区/IDC 隔离区" OR "/R/安全域/内部办公桌面区/OFFICE 隔离区" OR "/R/安全域/隔离网出口" OR "/R/安全域/内部办公桌面区/OFFICE Level 02" OR "/R/安全域/内部服务器区/IDC Level 02" OR "/R/网络属性/B网"))))'
    # query = 'ipassets_businessSystem:*十四大* AND jowto_onlineStatus:1'
    # res = jowto.get_server_info_lucene(query)
    # print(res['data'])
    # res2 = jowto.get_ipinfo_remove_ipassets_other_iplist(query)
    # res = jowto.jowto_info()
    # print(res['count'],res['rate'])

    # res = jowto.get_luc_need_jowto_expose_internet()
    # # print(res['data'])
    # expose_IP_list = res['data']['jowto']
    # expose_IP_online_list = res['data']['jowto_online']
    # expose_IP_offline_list = res['data']['jowto_offline']
    # expose_IP_no_install_list = res['data']['jowto_no_install']
    # # print("暴露端口未安装jowto：", expose_IP_no_install_list['data'])
    # for item in expose_IP_no_install_list['data']:
    #     print("暴露互联网未安装jowto:", item['ipassets_ip'], item['ipassets_businessSystem'])

    # 获取互联网暴露IP的椒图信息情况
    expose2internethandler()








