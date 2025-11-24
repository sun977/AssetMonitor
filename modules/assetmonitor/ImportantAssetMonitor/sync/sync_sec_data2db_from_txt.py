# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
    auth: sunhaobo
    version: v1.0
    function: sync im_asset_ip to key_asset_ip table
    date: 2025.01.07
    note: 从 im_asset_ip.txt 文本中获取IP，根据IP同步sec平台IP数据到监控平台
"""

from modules.assetmonitor.ImportantAssetMonitor.config.logger_config import setup_logger
from comm.mysql import *
from modules.SecAPI.sec.getSecApiClient import *

current_abs_path = os.path.abspath(__file__)  # 当前文件位置
current_abs_path_dir = os.path.dirname(current_abs_path)  # 当前目录
out_dir_path = os.path.abspath(current_abs_path_dir) + '/../../../../file/ImportantAssetOut/'  # 从当前目录找到输出文件的位置


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


# 从 SEC 平台获取 IP 信息
def get_ip_from_sec(iplist):
    """
    根据IP列表，从SEC获取IP详细信息
    :param iplist: IP列表
    :return: 包含IP详细信息的列表 [{'ip': '10.44.112.17', 'project': '奇安信集团- CRM系统采购及规划建设项目', 'owner': '娄卫赢'}, {'ip': '10.44.112.7', 'project': '奇安信集团- CRM系统采购及规划建设项目', 'owner': '娄卫赢'}]
    """

    if not isinstance(iplist, (list, tuple, set)):
        raise ValueError("iplist 必须是列表、元组或集合")

    ip_set = set(iplist)
    all_ip_info_list = []
    processed_ips = set()  # 使用集合来避免重复

    try:
        sec = secApiClient()  # 实例化secClient
        for ip in ip_set:
            query = f'ipassets_ip:"{ip}"'
            data = sec.get_ipInformation_lucene(query)

            if data is None:
                logger.warning(f'sec接口返回数据为空，IP: {ip}')
                continue

            for item in data:
                ip_address = item.get('ipassets_ip')
                if ip_address not in processed_ips:
                    processed_ips.add(ip_address)
                    all_ip_info_list.append({
                        'ip': ip_address,
                        'project': item.get('ipassets_project_name', ''),
                        'owner': item.get('ipassets_ops_operations_name', '')
                    })

        logger.info(f"modules.ImportantAssetMonitor.sync_sec_data2db_from_txt.get_ip_from_SEC() Retrieved {len(all_ip_info_list)} IPs from SEC")
        return all_ip_info_list

    except secApiClient.SpecificException as e:
        logger.error(f"modules.ImportantAssetMonitor.sync_sec_data2db_from_txt.get_ip_from_SEC() Error: {e}")
        return all_ip_info_list
    except Exception as e:
        logger.error(f"modules.ImportantAssetMonitor.sync_sec_data2db_from_txt.get_ip_from_SEC() Unexpected error : {e}")
        # raise  # 重新抛出未知异常以便进一步处理
        return all_ip_info_list


# 构造插入数据库的SQL函数
def insert_key_asset_ip(ip, project, owner):
    """
    插入数据库 key_asset_ip 表
    :param ip:
    :param project:
    :param owner:
    :return:
    """

    try:
        sql = (
                "INSERT INTO key_asset_ip (ip, project, owner) "
                "VALUES ('%s', '%s', '%s') "
                "ON DUPLICATE KEY UPDATE "
                "ip='%s',project='%s',owner='%s', updateTime=CURRENT_TIMESTAMP(6);" % (
                    ip, project, owner, ip, project, owner,  # 所有的参数都在这里
                )
        )
        # 执行SQL语句
        result = MySQL(sql=sql).exec()
        if result.get('state') == 1:
            logger.info(f"modules.ImportantAssetMonitor.sync_sec_data2db_from_txt.insert_key_asset_ip() Inserted {ip} into key_asset_ip")
        else:
            logger.error(f"modules.ImportantAssetMonitor.sync_sec_data2db_from_txt.insert_key_asset_ip() Failed to insert {ip} into key_asset_ip: {result.get('msg')}")
        return sql
    except Exception as e:
        logger.error(f"modules.ImportantAssetMonitor.sync_sec_data2db_from_txt.insert_key_asset_ip() Error: {e}")


# 运行函数
def run_sync_sec_data2db_from_txt():
    """
    运行串联函数
    :return:
    """
    logger.info(f"modules.ImportantAssetMonitor.sync_sec_data2db_from_txt.run_sync_sec_data2db_from_txt Started")
    # file_path = os.path.abspath(current_abs_path_dir) + '/iptest.txt'   # 测试文件
    file_path = os.path.abspath(current_abs_path_dir) + '/im_asset_ip.txt'  # 正式文件
    data_list = read_from(file_path)
    # print("读取文件列表：", data_list)
    logger.info(f"modules.ImportantAssetMonitor.sync_sec_data2db_from_txt.main() Read {len(data_list)} IPs from file TXT: {data_list}")
    write_to(data_list, out_dir_path + '/sync_im_ip.txt')  # 写入文件 本机保留一份当日同步的ip资产
    logger.info(f"modules.ImportantAssetMonitor.sync_sec_data2db_from_txt.main() Write {len(data_list)} IPs to file/ImportantAssetOut/sync_im_ip.txt")
    data_from_sec = get_ip_from_sec(data_list)
    # 循环插入数据到数据表
    for item in data_from_sec:
        ip = item.get('ip')
        project = item.get('project', '')
        owner = item.get('owner', '')
        insert_key_asset_ip(ip, project, owner)
    logger.info(f"modules.ImportantAssetMonitor.sync_sec_data2db_from_txt.run_sync_sec_data2db_from_txt Finished")





if __name__ == '__main__':
    run_sync_sec_data2db_from_txt()
