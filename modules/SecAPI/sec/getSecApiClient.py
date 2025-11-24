#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version: v3.0
    function: New SEC PLT API
    date: 2024.12.05
    note:
        1. 首个请求包含 scroll_id=true，用于获取 scroll_id和确定使用的查询方式（滚动/分页），滚动使用 scroll_id，分页使用 offset，size
        2. 后续请求包含 scroll_id，用于获取后续数据，可多次发送相同请求，返回数据滚动不一样，所以要先根据数据量计算请求次数
        3. headers 中必须包含 content-type: application/json
    API：
        1.api/v1/api/ipInformation 【全量IP信息表】
        2.api/v1/api/networkinfo    【全量网段信息】
        3.api/v1/api/DomainInformation  【全量域名信息】
        4.api/v1/api/ServiceAssetsInformation 【全量服务端口应用信息】
        5.api/v1/api/InternetInformation 【全量互联网信息】
        6。api/v1/api/TestAssetsInformation 【全量提测信息】
        7.api/v1/api/CloudServerInformation 【全量云服务器资产信息】
        8.api/v1/api/netpolicy-predisable 【获取网络策略ACL信息】
        9.api/v1/api/get-vuln-all 【全量资产漏洞信息接口】
"""

import hmac
import requests
import json
from comm.getconfig import *

requests.packages.urllib3.disable_warnings()

PROXIES = {
    'http': "http://127.0.0.1:8080",
    'https': "http://127.0.0.1:8080"
}


class secApiClient(object):
    def __init__(self):
        self.config = get_config()  # 从配置文件获取配置
        self.AUTH_PASSPORT = None
        self.AUTH_KEY = self.config['SEC-API']['prod']['auth_key']
        self.AUTH_SECURITY_KEY = self.config['SEC-API']['prod']['auth_security_key']
        self.AUTH_SALT_KEY = self.config['SEC-API']['prod']['salt_key']
        self.BASE_URL = self.config['SEC-API']['prod']['api_online']
        self.session = None
        self.HEADERS = None
        self.generate_session()  # 全局设置

    def generate_session(self):
        self.AUTH_PASSPORT = self.hmac_sha256(self.AUTH_SALT_KEY, self.AUTH_SECURITY_KEY)
        # print('_AUTH_PASSPORT:',self._AUTH_PASSPORT)  # 5cfa2dff4684026a2eb296110c3c1f6cfe3606a0f75d334b03ce6008b071dee7
        self.session = requests.Session()  # session 【用于发送http请求并保存会话状态，所有的请求会共享会话状态和信息】
        self.session.auth = requests.auth.HTTPBasicAuth(self.AUTH_KEY, self.AUTH_PASSPORT)
        # 构造请求头,更新到 session 里
        self.HEADERS = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        }
        self.session.headers.update(self.HEADERS)

    @staticmethod  # 静态函数
    def hmac_sha256(key, string):
        return hmac.new(key.encode('utf-8'), string.encode('utf-8'), 'SHA256').hexdigest()

    # 获取全量的 ipInformation 信息
    def get_all_ipInformation(self):
        # 不要执行一遍 generate_session()
        uri = "api/v1/api/ipInformation"  # api 请求接口
        url = f"{self.BASE_URL}/{uri}"
        # 第一次请求
        data_first = {
            "size": 1000,
            "scroll_id": True,
        }
        response = self.session.post(url=url, data=json.dumps(data_first), verify=False).json()
        data_count = int(response['count'])  # 数据总量
        scroll_id = response['scroll_id']  # 获取 scroll_id

        max_page = int(data_count / 1000 + 1)  # 计算最大页数
        # print('max_page:', max_page)
        # 后续请求
        ipInfo_list = []
        for page in range(max_page):
            data_sec = {
                "size": 1000,
                "scroll_id": scroll_id,
            }
            results = self.session.post(url=url, data=json.dumps(data_sec), verify=False).json()['results']
            # print(results)
            # page = page + 1 # 翻页
            if results:  # 如果有数据
                for item in results:  # 遍历列表 取每一个字段元素全部数据
                    ipInfo_list.append(item)
            else:
                # ipInif_list = []
                # print("No results found on page",page + 1)
                break

        return ipInfo_list

    # 使用 lucene 查询 【0-1000】
    # lucene = "ipassets_businessSystem:*十四大*"
    def get_ipInformation_lucene(self, query):
        # 不要执行一遍 generate_session()
        uri = "api/v1/api/ipInformation"  # api 请求接口
        url = f"{self.BASE_URL}/{uri}"
        # 第一次请求
        data_first = {
            "size": 2000,
            "query": query,
            "scroll_id": True,
        }
        response = self.session.post(url=url, data=json.dumps(data_first), verify=False).json()
        data_count = int(response['count'])  # 数据总量

        ipInfo_list = []
        if response:
            for item in response['results']:
                ipInfo_list.append(item)
        else:
            print("No results found on page")

        return ipInfo_list

    # 使用 lucene 查询 【翻页:1000+】
    def get_ipInformation_lucene_fanye(self, query):
        """
        两次查询
        :param query: Lucene查询语法体
        :return:[{}]
        """
        # 不要执行一遍 generate_session()
        uri = "api/v1/api/ipInformation"  # api 请求接口
        url = f"{self.BASE_URL}/{uri}"
        # 第一次请求
        data_first = {
            "size": 1000,
            "query": query,
            "scroll_id": True,
        }
        response = self.session.post(url=url, data=json.dumps(data_first), verify=False).json()
        data_count = int(response['count'])  # 数据总量
        scroll_id = response['scroll_id']  # 获取 scroll_id
        max_page = int(data_count / 1000 + 1)

        ipInfo_list = []
        # 处理第一页数据  【不单独处理第一页数据会丢掉】
        if 'results' in response:
            first_page_results = response['results']
            for item in first_page_results:
                ipInfo_list.append(item)

        for page in range(1, max_page):  # 从第二页开始迭代
            data_sec = {
                "size": 1000,
                "scroll_id": scroll_id,
            }
            results_response = self.session.post(url=url, data=json.dumps(data_sec), verify=False).json()
            if 'results' not in results_response:
                break
            results = results_response['results']

            for item in results:  # 遍历列表取出每一个字段元素全部数据
                ipInfo_list.append(item)

            scroll_id = results_response.get('scroll_id', None)  # 刷新 scroll_id

            if scroll_id is None:  # 如果没有新的 scroll_id，则退出循环
                break

        return ipInfo_list


    # 获取 networkinfo 接口信息 【完成】
    def get_networkinfo(self, limit=10, offset=1):
        """
        params: limit offset
        :return: {
        "count": 3072,
        "next": "",
        "previous": "",
        "results": [{}]
        }
        """
        uri = "api/v1/api/networkinfo"
        url = f"{self.BASE_URL}/{uri}"

        params = {
            "limit": limit,
            "offset": offset,
        }
        response = self.session.get(url=url, params=params, verify=False).json()

        return response

    # 获取 所有网段信息列表 【完成】
    def get_all_network(self):
        """
        只获取纯网段信息列表，需要区分 内网 和 外网
        需要自己计算数量
        :return: {
        'intranet': [{}],
        'internet': [{}]
        }
        """
        uri = "api/v1/api/networkinfo"
        url = f"{self.BASE_URL}/{uri}"
        nei_network_list = []  # 内网存储网段信息结果列表
        wai_network_list = []  # 外网存储网段信息结果列表
        limit = 500  # 定义每次请求的数据量
        # offset = 0  # 初始偏移量
        par_first = {
            "limit": limit,
            "offset": 0
        }
        count = int(self.session.get(url=url, params=par_first, verify=False).json()['count'])
        offsetMax = int(count / limit + 1)  # 计算最大页数
        # print("offsetMax:", offsetMax)

        for offset in range(offsetMax):
            params = {
                "limit": limit,
                "offset": offset * limit
            }

            # 多次请求
            re = self.session.get(url=url, params=params, verify=False).json()['results']

            offset = offset + 1

            if re:
                for item in re:
                    # 判断网络类型
                    if item['network_type'] == '内网网段':
                        nei_network_list.append(item['network'])
                    elif item['network_type'] == '外网网段':
                        wai_network_list.append(item['network'])
                    else:  # 网络类型为空或者其他 情况
                        nei_network_list.append(item['network'])
            else:
                print("No results found on page", offset + 1)
                break

        result = {
            'intranet': nei_network_list,
            'internet': wai_network_list
        }

        return result

    # 获取 全量域名 接口信息 【完成】
    def get_domaininfo_lucene(self, query=None):
        """
        1.获取所有的域名详细信息 -> query 参数不填
        2.获取指定域名Lucence结果 -> query 填写 Lucene查询语法体 string
        :param query: Lucene查询语法体 query = 'DomainName:"ztna.qianxin.com"'
        :return:[{}]
        """
        uri = "api/v1/api/DomainInformation"
        url = f"{self.BASE_URL}/{uri}"

        # 第一次请求
        data_first = {
            "size": 1000,
            "query": query,
            "scroll_id": True,
        }

        response = self.session.post(url=url, data=json.dumps(data_first), verify=False).json()
        data_count = int(response['count'])  # 获取数据总量
        scroll_id = response['scroll_id']  # 获取 scroll_id
        max_page = int(data_count / 1000 + 1)

        domains_list = []  # 用于存放 请求中 results 中的数据
        if 'results' in response:  # 处理第一页数据
            first_page_results = response['results']
            for item in first_page_results:
                domains_list.append(item)

        # 循环处理后续数据
        for page in range(1, max_page):  # 从第二页开始迭代
            data_sec = {
                "size": 1000,
                "scroll_id": scroll_id,
            }
            result_response = self.session.post(url=url, data=json.dumps(data_sec), verify=False).json()
            # 如果 results 字段为空 "results": [] 退出循环
            if not result_response['results']:
                break

            tmp_results = result_response['results']
            for item in tmp_results:
                domains_list.append(item)

            scroll_id = result_response.get('scroll_id', None)  # 刷新 scroll_id
            if scroll_id is None:  # 如果没有新的 scroll_id，则退出循环
                break

        return domains_list

    # 获取 服务端口应用 接口信息 【完成】
    def get_ServiceAssetsInformation_lucene(self, query=None):
        """
        1.获取所有的域名详细信息 -> query 参数不填
        2.获取指定域名Lucence结果 -> query 填写 Lucene查询语法体 string
        :param query: Lucene查询语法体 query = 'datasource:*xiaoying*' [ip:"10.44.96.183"]
        :return:[{}]
        """
        uri = "api/v1/api/ServiceAssetsInformation"
        url = f"{self.BASE_URL}/{uri}"

        # 第一次请求
        data_first = {
            "size": 500,
            "query": query,
            "scroll_id": True,
        }

        response = self.session.post(url=url, data=json.dumps(data_first), verify=False).json()
        data_count = int(response['count'])
        print("data_count:", data_count)
        scroll_id = response['scroll_id']
        max_page = int(data_count / 500 + 1)
        print("max_page:", max_page)

        Services_list = []
        # 处理第一页数据
        if 'results' in response:  # 处理第一页数据
            first_page_results = response['results']
            for item in first_page_results:
                Services_list.append(item)

        # 循环处理后续数据
        for page in range(1, max_page):  # 从第二页开始迭代
            data_sec = {
                "size": 500,
                "scroll_id": scroll_id,
            }
            result_response = self.session.post(url=url, data=json.dumps(data_sec), verify=False).json()
            if not result_response['results']:
                break
            tmp_results = result_response['results']
            for item in tmp_results:
                Services_list.append(item)
            scroll_id = result_response.get('scroll_id', None)
            if scroll_id is None:  # 如果没有新的 scroll_id，则退出循环
                break

        return Services_list

    # 获取 互联网资产 接口信息  【完成】
    def get_InternetInformation_lucene(self, query=None):
        """
        1.获取所有的域名详细信息 -> query 参数不填
        2.获取指定域名Lucence结果 -> query 填写 Lucene查询语法体 string
        :param query: Lucene查询语法体 query = 'Vip:"211.95.50.70"'  【可以获得vip和rs的映射关系】
        :return:[{}]
        """
        uri = "api/v1/api/InternetInformation"
        url = f"{self.BASE_URL}/{uri}"

        # 第一次请求
        data_first = {
            "size": 1000,
            "query": query,
            "scroll_id": True,
        }
        response = self.session.post(url=url, data=json.dumps(data_first), verify=False).json()
        data_count = int(response['count'])
        print("data_count:", data_count)
        scroll_id = response['scroll_id']
        max_page = int(data_count / 1000 + 1)
        print("max_page:", max_page)

        Internet_IP_info_list = []
        # 处理第一页数据
        if 'results' in response:
            first_page_results = response['results']
            for item in first_page_results:
                Internet_IP_info_list.append(item)

        # 循环处理后续数据
        for page in range(1, max_page):
            data_sec = {
                "size": 1000,
                "scroll_id": scroll_id,
            }
            result_response = self.session.post(url=url, data=json.dumps(data_sec), verify=False).json()
            if not result_response['results']:
                break
            tmp_results = result_response['results']
            for item in tmp_results:
                Internet_IP_info_list.append(item)
            scroll_id = result_response.get('scroll_id', None)
            if scroll_id is None:  # 如果没有新的 scroll_id，则退出循环
                break

        return Internet_IP_info_list

    # 获取 提测信息 接口数据 【完成】
    def get_TestAssetsInformation(self, limit=10, offset=1):
        """
        params: limit offset
        :return:{
        "count": 592,
        "next": "",
        "previous": "",
        "results": [{}]
        }
        """
        uri = "api/v1/api/TestAssetsInformation"
        url = f"{self.BASE_URL}/{uri}"

        params = {
            "limit": limit,
            "offset": offset
        }

        response = self.session.get(url=url, params=params, verify=False).json()
        return response

    # 获取所有 提测信息 接口数据 【完成】
    def get_all_TestAssetsInformation(self):
        """
        :return:[{}]
        """
        uri = "api/v1/api/TestAssetsInformation"
        url = f"{self.BASE_URL}/{uri}"
        results = []

        limit = 500   # 定义每页数量
        fir_params = {
            "limit": limit,
            "offset": 0
        }
        count = int(self.session.get(url=url, params=fir_params, verify=False).json()['count'])
        max_page = int(count / limit + 1)

        for offset in range(max_page):
            params = {
                "limit": limit,
                "offset": offset * limit
            }
            res = self.session.get(url=url, params=params, verify=False).json()['results']

            offset = offset + 1

            if res:
                for item in res:
                    results.append(item)

            else:
                print(f"第{offset}页数据为空")
                break

        return results

    # 获取 接入consul域名信息 接口数据 【完成】
    def get_ConsulDomainInformation(self, limit=10, offset=1):
        """
        params: limit offset
        :return:{
        "count": 282,
        "next": "",
        "previous": "",
        "results": [{}]
        }
        """
        uri = "api/v1/api/ConsulDomainInformation"
        url = f"{self.BASE_URL}/{uri}"

        params = {
            "limit": limit,
            "offset": offset
        }

        response = self.session.get(url=url, params=params, verify=False).json()
        return response

    # 获取 所有 接入consul域名信息 接口数据  【完成】
    def get_all_ConsulDomainInformation(self):
        """
        params:
        :return:[{}]
        """
        uri = "api/v1/api/ConsulDomainInformation"
        url = f"{self.BASE_URL}/{uri}"
        results = []

        limit = 500
        fir_params = {
            "limit": 1,
            "offset": 1
        }

        count = int(self.session.get(url=url, params=fir_params, verify=False).json()['count'])
        print("count:", count)
        max_page = int(count / limit + 1)
        print("max_page:", max_page)
        for offset in range(max_page):
            params = {
                "limit": limit,
                "offset": offset * limit
            }
            res = self.session.get(url=url, params=params, verify=False).json()['results']
            offset = offset + 1
            if res:
                for item in res:
                    results.append(item)
            else:
                print(f"第{offset}页数据为空")
                break

        return results

    # 获取 云服务资产信息 接口信息  【完成】
    def get_CloudServerInformation(self, limit=10, offset=1):
        """
        params: limit offset
        :return:{
        "count": 3497,
        "next": "",
        "previous": "",
        "results": [{}]
        }
        """
        uri = "api/v1/api/CloudServerInformation"
        url = f"{self.BASE_URL}/{uri}"

        params = {
            "limit": limit,
            "offset": offset
        }

        response = self.session.get(url=url, params=params, verify=False).json()
        return response

    # 获取 网络策略 接口信息 【数据错误】
    def get_NetworkPolicyInformation(self):
        """
        测试没有获取到数据，参数可能不对
        :return:
        """
        uri = "api/v1/api/netpolicy-predisable"
        url = f"{self.BASE_URL}/{uri}"
        data = {
            "data": {
                "id": 123,
                "order_list": [
                    "12423525245245",
                    "1864864170370011136"
                ]
            }
        }
        response = self.session.post(url=url, data=json.dumps(data), verify=False).json()
        return response

    # 获取 资产漏洞信息 接口
    def get_vuln_all(self):
        """
        获取的数据是所有的，不需要携带请求body和其他
        :return:{'errCode': 0, 'errMsg': 'Success', 'results': [{}]}
        """
        uri = "api/v1/api/get-vuln-all"
        url = f"{self.BASE_URL}/{uri}"
        response = self.session.get(url=url, verify=False).json()
        return response


if __name__ == "__main__":
    secClient = secApiClient()
    # uri = "api/v1/api/ipInformation"
    # url = f"{secClient.BASE_URL}/{uri}"
    # # headers= secClient.session.headers
    # # 第一次请求
    # data_first = {
    #     "size": 2,
    #     "scroll_id": True,
    # }
    #
    # data = {
    #     "size": 1000,
    #     "query": "ipassets_businessSystem:*十四大*",
    #     "scroll_id": True
    # }
    # # response = client.session.post(url=url, data=data, proxies=PROXIES, verify=False).json()
    # # 第一次请求
    # # response = secClient.session.post(url=url, data=json.dumps(data_first), verify=False, proxies=PROXIES).json()
    # response = secClient.session.post(url=url, data=json.dumps(data), verify=False).json()
    # scroll_id = response['scroll_id']
    # # print(response)
    # print(len(response['results']))
    # print(scroll_id)

    # res = secClient.get_networkinfo(limit=1, offset=1)
    # res = secClient.get_networkinfo()
    res = secClient.get_all_network()
    # res = secClient.get_NetworkPolicyInformation()
    # print(res)
    print("intranet count:", len(res['intranet']))
    print("internet count:", len(res['internet']))
    # query = 'DomainName:"ztna.qianxin.com"'
    # res = secClient.get_domaininfo_lucene(query)
    # query2 = 'Vip:"211.95.50.70"'
    # res = secClient.get_InternetInformation_lucene(query2)
    # res = secClient.get_TestAssetsInformation()
    # res = secClient.get_all_TestAssetsInformation()
    # res = secClient.get_ConsulDomainInformation(1,1)
    # res = secClient.get_all_ConsulDomainInformation()
    # res = secClient.get_CloudServerInformation(1, 1)
    # res = secClient.get_vuln_all()
    # print(len(res['results']))
    # print(res)
