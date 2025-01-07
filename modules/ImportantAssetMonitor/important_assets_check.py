# !/usr/bin/env python3
# _*_ coding: utf-8 _*_


"""
    auth: sunhaobo
    version: v1.0
    function: Check Important Assets
    date: 2024.11.21
    note: copy from Check Important Assets
        1。用于检测重保机器日志采集情况
        2. 检测逻辑
            检测椒图状态 检测日志状态(哪一种日志)  检测漏洞状态
            判断在线状态 在线 下一步判断  不在线 告警
            判断椒图状态 状态 1 下一步判断 不为1 告警
            判断漏洞状态 状态 0 下一步判断 不为0 告警
            判断日志状态 状态 是 输出 日志采集的日志类型 状态 不是 告警
        3.需要维护重保资产的 list
"""
from modules.SecAPI.sec.getSecApiClient import *
from datetime import time, datetime
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


def write_something_to(data, file_path):
    data = data
    file = file_path
    with open(file, 'w') as f:
        f.write(str(data) + '\n')


# 全局变量
cur_path = os.path.dirname(os.path.realpath(__file__))
out_file = os.path.join(cur_path, "./file/")  # 文件输出
out_print_result = []


# Manager 类
class Manager:
    def __init__(self):
        self.secClient = secApiClient()
        self.sec_data_count = 0  # 数据条数
        self.original_data = []  # 数据

    # 使用 lucene 查询获取SEC数据
    def getSecDataOriginalLucene(self, query):
        '''
        :param query: api/v1/api/ipInformation
        :return:
        '''

        self.original_data = self.secClient.get_ipInformation_lucene_fanye(query)
        # res = self.secClient.get_ipInformation_lucene(query)
        self.sec_data_count = len(self.original_data)
        # print(query, self.sec_data_count) # 输出每次查询的内容
        return {
            "data": self.original_data,
            "count": self.sec_data_count
        }

    # 判断单个IP在线状态
    def getIPStatus(self):
        '''
        :param data:
        :return:
        '''
        ip_status = self.original_data[0]['ipassets_status']  # [{}]
        if ip_status == '在线':
            return True
        else:
            return False

    # 判断单个IP的jowto状态
    def getJowtoStatus(self):
        jowto_status = self.original_data[0]['jowto_onlineStatus']
        if jowto_status == 1:
            return True
        else:
            return False

    # 判断单个IP的漏洞状态
    def getVulnStatus(self):
        vuln_status = self.original_data[0]['ipassets_has_vul']
        if vuln_status == 0:  # 没有漏洞
            return True
        else:
            return False

    # 判断单个IP日志状态
    def getLogStatus(self):
        log_status = self.original_data[0]['ipassets_log_status']
        if log_status == '是':
            return True
        else:
            return False

    # 输出单个IP所有的日志状态信息
    def getLogStatusInfo(self):
        data = self.original_data[0]  # 获取IP的所有数据
        return {
            "ip": data['ipassets_ip'],
            "ipassets_log_status": data['ipassets_log_status'],
            "ipassets_base_installation_log_status": data['ipassets_base_installation_log_status'],
            "ipassets_system_log_status": data['ipassets_system_log_status'],
            "ipassets_base_app_log_status": data['ipassets_base_app_log_status'],
            "ipassets_upper_app_log_status": data['ipassets_upper_app_log_status'],
            "ipassets_bostion_host_status": data['ipassets_bostion_host_status'],
            "ipassets_wsus_status": data['ipassets_wsus_status'],
        }


# 业务逻辑函数
# 获取IPs的所有状态
def get_ips_all_status(ip_list):
    '''
    :param: ip list
    :return: 封装IP所有查询的信息
    '''
    # 初始化类
    M = Manager()
    # 写一个变量存储查询结果
    result_list = []

    for ip in ip_list:
        query = 'ipassets_ip:"' + ip + '"'
        # print("query", query)
        result = M.getSecDataOriginalLucene(query)
        # print("COUNT:", result['count'])
        if result['count'] == 0:
            print(ip, '没有查询到资产信息！')
            return result_list

        else:
            # print(ip, '查询到资产信息如下')
            for data in result['data']:
                # print(data)
                # 判断IP是否在线
                online_status = M.getIPStatus()
                # 判断IP的jowto状态
                jowto_status = M.getJowtoStatus()
                # 判断IP的漏洞状态
                vuln_status = M.getVulnStatus()
                # 判断IP的日志状态
                log_status = M.getLogStatus()
                # 输出IP的日志状态信息
                log_status_info = M.getLogStatusInfo()
                result_list.append({
                    "ip": data['ipassets_ip'],
                    "ipassets_project_name": data['ipassets_project_name'],
                    "online_status": online_status,
                    "jowto_status": jowto_status,
                    "vuln_status": vuln_status,
                    "log_status": log_status,
                    "log_status_info": log_status_info
                })
    # print(result_list)
    return result_list


# 检测IPs的状态告警
def check_ips_alert(ip_list):
    result_list = get_ips_all_status(ip_list)  # 获取IPs的所有状态
    # print("result_list:", result_list)
    ip_unonline_list = []
    ip_nojowto_list = []
    ip_hasvuln_list = []
    ip_unlog_list = []
    for data in result_list:  # 遍历数据
        # print("数据：", data)
        if data['online_status'] == False:
            print({"ip_tmp": data['ip'], "project": data['ipassets_project_name']}, '不在线')
            # write_something_to({"ip": data['ip'], "project": data['ipassets_project_name'], "msg": data['online_status']}, os.path.join(out_file, "out_print.txt"))
            out_print_result.append({"ip": data['ip'], "project": data['ipassets_project_name'], "msg": '资产不在线'})
            tmp_dict = {
                "ip": data['ip'],
                "ipassets_project_name": data['ipassets_project_name'],
                "online_status": data['online_status'],
                "jowto_status": data['jowto_status'],
                "vuln_status": data['vuln_status'],
                "log_status": data['log_status'],
                "log_status_info": data['log_status_info']
            }
            ip_unonline_list.append(tmp_dict)
        else:
            if data['jowto_status'] == False:
                print({"ip_tmp": data['ip'], "project": data['ipassets_project_name']}, 'jowto 不在线')
                # write_something_to({"ip": data['ip'], "project": data['ipassets_project_name'], "msg": data['jowto_status']}, os.path.join(out_file, "out_print.txt"))
                out_print_result.append(
                    {"ip": data['ip'], "project": data['ipassets_project_name'], "msg": 'jowto 不在线'})
                tmp_dict = {
                    "ip": data['ip'],
                    "ipassets_project_name": data['ipassets_project_name'],
                    "online_status": data['online_status'],
                    "jowto_status": data['jowto_status'],
                    "vuln_status": data['vuln_status'],
                    "log_status": data['log_status'],
                    "log_status_info": data['log_status_info']
                }
                ip_nojowto_list.append(tmp_dict)
                if data['vuln_status'] == False:  # True 是没有漏洞 False 是有漏洞
                    print({"ip_tmp": data['ip'], "project": data['ipassets_project_name']}, '存在漏洞')
                    # write_something_to({"ip": data['ip'], "project": data['ipassets_project_name'], "msg": data['vuln_status']}, os.path.join(out_file, "out_print.txt"))
                    out_print_result.append({"ip": data['ip'], "project": data['ipassets_project_name'], "msg": '存在漏洞'})
                    tmp_dict = {
                        "ip": data['ip'],
                        "ipassets_project_name": data['ipassets_project_name'],
                        "online_status": data['online_status'],
                        "jowto_status": data['jowto_status'],
                        "vuln_status": data['vuln_status'],
                        "log_status": data['log_status'],
                        "log_status_info": data['log_status_info']
                    }
                    ip_hasvuln_list.append(tmp_dict)
                    if data['log_status'] == False:
                        print({"ip_tmp": data['ip'], "project": data['ipassets_project_name']}, '日志状态不正常')
                        # write_something_to({"ip": data['ip'], "project": data['ipassets_project_name'], "msg": data['log_status']}, os.path.join(out_file, "out_print.txt"))
                        out_print_result.append(
                            {"ip": data['ip'], "project": data['ipassets_project_name'], "msg": '日志状态不正常'})
                        tmp_dict = {
                            "ip": data['ip'],
                            "ipassets_project_name": data['ipassets_project_name'],
                            "online_status": data['online_status'],
                            "jowto_status": data['jowto_status'],
                            "vuln_status": data['vuln_status'],
                            "log_status": data['log_status'],
                            "log_status_info": data['log_status_info']
                        }
                        ip_unlog_list.append(tmp_dict)
                        # 取出日志信息数据，判断每个键值的值是 否 输出键值名
                        for key, value in data['log_status_info'].items():
                            if value == '否':
                                print({"ip_tmp": data['ip'], "project": data['ipassets_project_name']}, key, '否')
                                out_print_result.append({"ip": data['ip'], "project": data['ipassets_project_name'],
                                                         "msg": '缺失' + key + '日志'})

    # # 写入文件
    # write_to(ip_unonline_list, os.path.join(out_file, "ip_unonline_list.txt"))
    # write_to(ip_nojowto_list, os.path.join(out_file, "ip_nojowto_list.txt"))
    # write_to(ip_hasvuln_list, os.path.join(out_file, "ip_hasvuln_list.txt"))
    # write_to(ip_unlog_list, os.path.join(out_file, "ip_unlog_list.txt"))

    return {
        "ip_unonline_list": ip_unonline_list,
        "ip_nojowto_list": ip_nojowto_list,
        "ip_hasvuln_list": ip_hasvuln_list,
        "ip_unlog_list": ip_unlog_list
    }


def send_mail(data):
    TODAY = datetime.now().strftime('%Y-%m-%d')
    data = data
    mail = MAIL()
    subject = f'今日重保资产监控-{TODAY}'
    # userlist = ['sunhaobo@qianxin.com']
    userlist = ['sunhaobo@qianxin.com', 'g-sec-opr@qianxin.com']
    content = f"""
    ------ 重保数据统计数据统计 ------

    日期：{TODAY}

    监控结果如下：
    """
    for it in data:
        content += f"""
        IP地址:{it['ip']}：
        项目：{it['project']}
        消息：{it['msg']}   
    """
    mail.send_mail(subject, userlist, content)


if __name__ == "__main__":
    test_list = [
        '10.1.11.11',
        '10.44.96.180',
        '10.44.96.183',
        '10.95.58.94'
    ]

    # 定义待检测目标
    ## crm 系统
    crm_list = [
        '10.44.112.7',
        '10.44.112.17',
        '10.44.112.18',
        '10.57.82.42',
        '10.57.82.43',
        '10.57.82.44',
        '10.44.112.20',
        '10.44.112.21',
        '10.57.82.45',
        '10.57.82.46'
    ]

    ## 奇迹系统
    qiji_list = [
        '10.249.108.9',
        '10.49.176.24',
        '10.249.108.10',
        '10.49.176.25',
        '10.249.108.11',
        '10.49.176.26',
        '10.49.165.64',
        '10.249.97.165',
        '10.41.200.165',
        '10.57.96.77',
        '10.41.200.166',
        '10.57.96.78',
        '10.41.200.167',
        '10.57.96.79'
    ]

    ## ERP
    erp_list = [
        '10.44.33.18',
        '10.57.148.40',
        '10.44.33.14',
        '10.57.148.36',
        '10.44.33.20',
        '10.57.148.42',
        '10.44.33.12',
        '10.44.33.15',
        '10.57.148.34',
        '10.57.148.37',
        '10.44.33.17',
        '10.57.148.39',
        '10.44.33.13',
        '10.44.33.19',
        '10.57.148.35',
        '10.57.148.41',
        '10.44.33.16',
        '10.57.148.38',
        '10.44.113.20',
        '10.44.113.18',
        '10.57.82.39',
        '10.57.82.40'
    ]

    ## 江河平台
    jianghe_list = [
        '10.49.44.82',
        '10.49.204.35',
        '10.49.44.80',
        '10.49.204.36',
        '10.49.44.84',
        '10.49.204.37'
    ]

    ## MES 系统
    mes_list = [
        '10.73.66.7',
    ]

    ## PDM 系统
    pdm_list = [
        '10.57.94.246',
        '10.57.94.247',
        '10.57.94.248',
        '10.57.94.249'
    ]

    ## PMIS 系统
    pmis_list = [
        '10.41.200.12',
        '10.41.200.14',
        '10.41.200.17',
        '10.41.200.40',
        '10.41.200.42',
        '10.57.96.43',
        '10.57.96.44',
        '10.57.96.45',
        '10.57.96.46'
    ]

    ## 许可证 系统
    license_list = [
        '10.249.108.20',
        '10.249.108.19',
        '10.249.97.169',
        '10.249.97.170',
        '10.249.105.10',
        '10.249.105.9',
        '10.49.204.29',
        '10.49.194.58',
        '10.249.105.246',
        '10.249.105.89',
        '10.49.200.141'
    ]

    ## 倚天 系统
    yitian_list = [
        '10.249.43.200',
        '10.249.106.197',
        '10.249.106.198',
        '10.49.40.248',
        '10.49.173.227',
        '10.49.32.105',
        '10.49.165.30',
        '10.49.173.94',
        '10.49.172.34'
    ]

    ## OA 系统
    oa_list = [
        '10.249.34.82',
        '10.249.80.27',
        '10.249.80.43',
        '10.249.80.45',
        '10.249.80.32',
        '10.249.80.42',
        '10.249.80.37',
        '10.249.34.41',
        '10.249.80.49',
        '10.249.80.106',
        '10.249.80.89',
        '10.249.80.105',
        '10.249.80.107',
        '10.249.34.73',
        '10.249.46.137',
        '10.249.46.140',
        '10.249.64.15',
        '10.249.64.14',
        '10.249.162.219',
        '10.49.204.27',
        '10.249.162.220',
        '10.49.204.28',
        '10.249.162.218',
        '10.249.162.221',
        '10.49.176.23',
        '10.249.22.178',
        '10.46.40.23',
        '10.46.40.20',
        '10.46.40.17',
        '10.46.40.26',
        '10.46.40.29',
        '10.46.40.24',
        '10.41.200.111',
        '10.46.36.27'
    ]

    ## 报账 系统
    baozhang_list = [
        '10.249.108.6',
        '10.49.176.17',
        '10.249.108.7',
        '10.249.108.8',
        '10.49.176.12',
        '10.49.176.13',
        '10.249.105.29',
        '10.49.176.8',
        '10.44.121.70',
        '10.249.122.10'
    ]

    ## 财务运营 系统
    caiyun_list = [
        '10.249.108.48',
        '10.249.108.49',
        '10.49.176.5',
        '10.249.108.52',
        '10.49.176.7',
        '10.249.108.38',
        '10.49.176.6',
        '10.249.108.40',
        '10.49.176.11',
        '10.249.108.42',
        '10.49.176.20',
        '10.249.108.44',
        '10.249.108.28',
        '10.49.176.19',
        '10.249.108.46',
        '10.49.176.18',
        '10.249.108.30',
        '10.49.176.10',
        '10.249.108.36',
        '10.249.108.37',
        '10.49.176.16',
        '10.249.108.34',
        '10.49.176.9',
        '10.249.108.33',
        '10.49.176.15',
        '10.249.108.24',
        '10.49.176.21',
        '10.249.108.15',
        '10.49.176.14',
        '10.49.44.63',
        '10.49.176.22'
    ]

    ## 百望 系统
    baiwang_list = [
        '10.41.200.127',
        '10.41.200.129'
    ]

    ## U8 系统
    u8_list = [
        '10.41.200.107',
        '10.96.20.132',
        '10.41.200.108',
        '10.96.21.3',
        '10.57.96.54',
        '10.57.96.55'
    ]

    ## CBS 系统
    cbs_list = [
        '10.44.121.90',
        '10.44.121.154',
        '10.41.200.150',
        '10.41.200.149',
        '10.44.121.156',
        '10.44.121.155'
    ]

    ## BI 系统
    bi_list = [
        '10.41.200.142',
        '10.41.76.13',
        '10.57.96.51'
    ]

    ## 数据服务 系统
    data_service_list = [
        '10.41.76.17',
        '10.41.76.19',
        '10.57.96.47'
    ]

    ## 售后 系统
    after_sale_list = [
        '10.48.48.73',
        '10.48.48.68',
        '10.48.60.87',
        '10.48.60.88',
        '10.48.60.90',
        '10.48.60.91',
        '10.48.60.89',
        '10.48.60.92',
        '10.48.48.74',
        '10.48.60.93',
        '10.44.66.49',
        '10.41.200.148',
        '10.41.200.130',
        '10.41.200.143',
        '10.41.200.131',
        '10.41.200.145',
        '10.41.200.144',
        '10.41.200.147'
    ]

    ## SAP 系统
    sap_list = [
        '10.44.120.206',
        '10.44.120.204',
        '10.44.120.205',
        '10.44.120.196',
        '10.44.120.194',
        '10.44.120.195'
    ]

    ## 基础建设 系统
    jijian_list = [
        '10.249.105.108',
        '10.249.105.35',
        '10.249.105.69',
        '10.49.174.208',
        '10.249.106.119',
        '10.249.106.120',
        '10.249.106.119',
        '10.249.106.120',
        '10.249.106.189',
        '10.249.106.190',
        '10.49.174.204',
        '10.249.106.192',
        '10.249.106.191',
        '10.49.174.207',
        '10.249.106.194',
        '10.249.106.193',
        '10.49.174.206',
        '10.249.106.192',
        '10.249.106.191',
        '10.49.174.207',
        '10.49.40.217',
        '10.49.174.205',
        '10.49.40.111',
        '10.49.40.110',
        '10.49.174.210',
        '10.49.32.83',
        '10.49.32.84',
        '10.49.40.135',
        '10.49.40.134',
        '10.49.40.133',
        '10.49.174.209',
        '10.49.41.198'
    ]

    ## 蓝信 系统
    lx_list = []

    ## 列表装填所有列表
    all_list = [
        erp_list,
        jianghe_list,
        mes_list,
        pdm_list,
        pmis_list,
        license_list,
        yitian_list,
        oa_list,
        baozhang_list,
        caiyun_list,
        baiwang_list,
        u8_list,
        cbs_list,
        bi_list,
        data_service_list,
        after_sale_list,
        sap_list,
        jijian_list,
        lx_list
    ]

    # get_ips_all_status(test_list)
    # res = check_ips_alert(test_list)
    # print(res)

    # # # 遍历列表
    # for list_name in all_list:
    #     print("LIST_NAME:" ,list_name)
    #     # 遍历每个列表里面的元素
    #     for item in list_name:
    #         print(item)
    #         res = check_ips_alert(item)

    print("------------------------------------------------------------------------")
    # 输出一下时间，便于查询run.log日志
    print("DATE:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # 列表套列表可以直接遍历
    for item in all_list:
        # print("item:", item)
        res = check_ips_alert(item)
        # print("列表结果：", res)
    print("out_print_result:", out_print_result)
    send_mail(out_print_result)
    print("------------------------------------------------------------------------")
