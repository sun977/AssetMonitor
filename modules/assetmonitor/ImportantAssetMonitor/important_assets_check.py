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
from datetime import datetime
from comm.send_mail import *
from comm.mysql import *
from modules.assetmonitor.ImportantAssetMonitor.config.logger_config import setup_logger

# 全局变量
current_abs_path = os.path.abspath(__file__)  # 当前文件位置
current_abs_path_dir = os.path.dirname(current_abs_path)  # 当前目录
out_dir_path = os.path.abspath(current_abs_path_dir) + '/../../../file/ImportantAssetOut/'  # 从当前目录找到输出文件的位置
out_print_result = []  # 用于发送邮件的数据列表

# 配置日志记录器
logger = setup_logger()


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
    """
    :param: ip list
    :return: 封装IP所有查询的信息 [{},{}]
    """
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
            logger.info(f"{ip}:没有查询到资产信息!")
            # return result_list  # 如果返回则后续IP不会再判断
            continue  # 跳过当前 IP，继续处理下一个  --- 20251202 fix
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


# 检测IP的状态告警
def check_ips_alert(ip_list):
    """
    根据ip列表，逐步检查每个IP的状态
    :param ip_list:
    :return:
    """
    result_list = get_ips_all_status(ip_list)  # 获取IPs的所有状态
    # print("result_list:", result_list)
    ip_unonline_list = []  # 离线IP资产
    ip_nojowto_list = []  # 没有jowto的IP资产
    ip_hasvuln_list = []  # 有漏洞的IP资产
    ip_unlog_list = []  # 没有日志的
    for data in result_list:  # 遍历数据
        # print("数据：", data)
        if data['online_status'] == False:
            logger.info({"ip_tmp": data['ip'], "project": data['ipassets_project_name'], "msg": data['online_status']})
            # print({"ip_tmp": data['ip'], "project": data['ipassets_project_name']}, '不在线')
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
                logger.info({"ip_tmp": data['ip'], "project": data['ipassets_project_name'], "msg": data['jowto_status']})
                # print({"ip_tmp": data['ip'], "project": data['ipassets_project_name']}, 'jowto 不在线')
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
                    logger.info({"ip_tmp": data['ip'], "project": data['ipassets_project_name'], "msg": data['vuln_status']})
                    # print({"ip_tmp": data['ip'], "project": data['ipassets_project_name']}, '存在漏洞')
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
                        logger.info({"ip_tmp": data['ip'], "project": data['ipassets_project_name'], "msg": data['log_status']})
                        # print({"ip_tmp": data['ip'], "project": data['ipassets_project_name']}, '日志状态不正常')
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
                                logger.info({"ip_tmp": data['ip'], "project": data['ipassets_project_name'], "msg": '缺失' + key + '日志'})
                                # print({"ip_tmp": data['ip'], "project": data['ipassets_project_name']}, key, '否')
                                out_print_result.append({"ip": data['ip'], "project": data['ipassets_project_name'], "msg": '缺失' + key + '日志'})

    # # 写入文件
    write_to(ip_unonline_list, os.path.join(out_dir_path, "ip_unonline_list.txt"))
    write_to(ip_nojowto_list, os.path.join(out_dir_path, "ip_nojowto_list.txt"))
    write_to(ip_hasvuln_list, os.path.join(out_dir_path, "ip_hasvuln_list.txt"))
    write_to(ip_unlog_list, os.path.join(out_dir_path, "ip_unlog_list.txt"))

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
    ------ 重保资产检测报告 ------

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
    logger.info(f"modules.ImportantAssetMonitor.important_asset_check.send_mail() send_mail Success")


# 从数据库中获取IP列表
def get_ip_from_db():
    """
    从数据库中获取IP列表
    :return:[{},{}]
    """
    ip_list_db = []
    # 获取IP资产监控表 key_asset_ip
    sql = "SELECT ip, project, owner FROM key_asset_ip where status = '1'"  # 获取监控状态为1的IP
    res_sql = MySQL(sql=sql).exec()
    if res_sql.get('state') == 1:
        logger.info(f"modules.ImportantAssetMonitor.important_asset_check.get_ip_from_db() SQL:{sql} exec Success")
        ip_list_db = res_sql.get('data')
    else:
        logger.warning(
            f"modules.ImportantAssetMonitor.important_asset_check.get_ip_from_db() SQL:{sql} exec Failed: {res_sql.get('msg')}")
        ip_list_db = res_sql.get('data')
    return ip_list_db


# 所有IP的所有状态信息入库
def insert_key_asset_ip_detail(data):
    """
    封装成字典然后插入
    :param data:
    :return:
    """
    # data_dcit = {
    #     "ipassetsIp": ip,
    #     "ipassetsProjectName": project,
    #     "ipassetsBusinessSystem":ipassetsBusinessSystem,  # 没加
    #     "ipassetsOpsOperationsName": ipassetsOpsOperationsName,   # 运维人
    #     "ipassetsStatus": ipassetsStatus,  # 在线状态
    #     "jowtoOnlineStatus": jowtoOnlineStatus,
    #     "ipassetsHasVul": vuln_status,
    #     "ipassetsLogStatus": log_status,
    #     "note":note  note_json = json.dumps(data_dit['note'], ensure_ascii=False)
    # }
    data_dit = data
    try:
        sql_insert = (
                "INSERT INTO key_asset_ip_detail (ipassetsIp, ipassetsProjectName, ipassetsOpsOperationsName, ipassetsStatus, jowtoOnlineStatus, ipassetsHasVul, ipassetsLogStatus, note) "
                "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') "
                "ON DUPLICATE KEY UPDATE "
                "ipassetsIp='%s',ipassetsProjectName='%s',ipassetsOpsOperationsName='%s',ipassetsStatus='%s',jowtoOnlineStatus='%s',ipassetsHasVul='%s',ipassetsLogStatus='%s', note='%s', updateTime=CURRENT_TIMESTAMP(6);" % (
                    data_dit.get('ipassetsIp'), data_dit.get('ipassetsProjectName'),
                    data_dit.get('ipassetsOpsOperationsName'), data_dit.get('ipassetsStatus'),
                    data_dit.get('jowtoOnlineStatus'), data_dit.get('ipassetsHasVul'),
                    data_dit.get('ipassetsLogStatus'),
                    str(json.dumps(data_dit['note'], ensure_ascii=False)),  # note 是字典类型，需要装换成json数据,由于cool-admin前端默认是toString(),所以转换成字符串更好
                    data_dit.get('ipassetsIp'), data_dit.get('ipassetsProjectName'),
                    data_dit.get('ipassetsOpsOperationsName'), data_dit.get('ipassetsStatus'),
                    data_dit.get('jowtoOnlineStatus'), data_dit.get('ipassetsHasVul'),
                    data_dit.get('ipassetsLogStatus'),
                    str(json.dumps(data_dit['note'], ensure_ascii=False))
                )
        )
        res_sql = MySQL(sql=sql_insert).exec()
        if res_sql.get('state') == 1:
            logger.info(
                f"modules.ImportantAssetMonitor.important_asset_check.insert_key_asset_ip_detail() SQL:{sql_insert} exec Success")
        else:
            logger.warning(
                f"modules.ImportantAssetMonitor.important_asset_check.insert_key_asset_ip_detail() SQL:{sql_insert} exec Failed: {res_sql.get('msg')}")
        return sql_insert
    except Exception as e:
        logger.error(
            f"modules.ImportantAssetMonitor.important_asset_check.insert_key_asset_ip_detail() Failed to insert data into db: {e}")
        return sql_insert


# 运行函数
def run_important_asset_check():
    """
    串联运行函数  运行函数，发送邮件，更新监控表状态
    :return:
    """
    # 发邮件
    # 输出一下时间，便于查询run.log日志
    # print("DATE:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info(f"modules.ImportantAssetMonitor.important_asset_check.run_important_asset_check() run_important_asset_check Start")
    # 改为从数据库中获取IP列表
    ip_list_db = get_ip_from_db()  # [{},{}]  {'ip': '10.44.112.17', 'project': '奇安信集团- CRM系统采购及规划建设项目', 'owner': '娄卫赢'}

    ip_list = []  # 纯IP列表['','']
    for ite in ip_list_db:
        ip_list.append(ite.get('ip'))

    # 1、遍历情况发邮件
    res = check_ips_alert(ip_list)  # 直接给参数 IP列表
    # print("列表结果：", res)
    # print("out_print_result:", out_print_result)
    send_mail(out_print_result)

    # 2、获取的IP的所有状态同步资产监控表 key_asset_ip_detail
    # [{},{}]  {'ip':'','ipassets_project_name':'', 'online_status':'','jowto_status':'','vuln_status':'','log_status':'','log_status_info':''}  全是 True 和 False
    res_get_ips_all_status = get_ips_all_status(ip_list)

    # 重新封装 逻辑
    # 将 ip_list_db 转换为以 IP 为键的字典
    ip_dict = {item['ip']: item for item in ip_list_db}

    for x in res_get_ips_all_status:
        ip = x.get('ip')
        if not ip:
            continue  # 跳过无效的 IP

        # 查找对应的 IP 信息
        db_info = ip_dict.get(ip)
        if db_info:
            z = {
                'ipassetsIp': x.get('ip', ''),
                'ipassetsProjectName': db_info.get('project', ''),
                'ipassetsOpsOperationsName': db_info.get('owner', ''),
                'ipassetsStatus': x.get('online_status', ''),
                'jowtoOnlineStatus': x.get('jowto_status', ''),
                'ipassetsHasVul': x.get('vuln_status', ''),
                'ipassetsLogStatus': x.get('log_status', ''),
                'note': x.get('log_status_info', '')
            }
            # print("z:", z)
            insert_key_asset_ip_detail(z)
    logger.info(f"modules.ImportantAssetMonitor.important_asset_check.run_important_asset_check() run_important_asset_check Finished")


if __name__ == "__main__":
    run_important_asset_check()
