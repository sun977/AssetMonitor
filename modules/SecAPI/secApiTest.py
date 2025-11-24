#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version: v2.0
    function: New SEC PLT API
    date: 2023.11.29
    note:
        1. 首个请求包含 scroll_id=true，用于获取 scroll_id和确定使用的查询方式（滚动/分页），滚动使用 scroll_id，分页使用 offset，size
        2. 后续请求包含 scroll_id，用于获取后续数据，可多次发送相同请求，返回数据滚动不一样，所以要先根据数据量计算请求次数
        3. headers 中必须包含 content-type: application/json
"""

import hmac
import requests
import json
from comm.getconfig import *
from sec.getSecApiClient import *





if __name__ == "__main__":
    # 使用前需要sec申请ip权限
    secClient = secApiClient()  # 初始化实例
    # res = secClient.get_all_ipInformation()
    # lucene = "ipassets_businessSystem:*十四大*"
    # lucene = "ipassets_businessSystem:*十四大* AND jowto_onlineStatus:1"
    # res = secClient.get_ipInformation_lucene(lucene)
    # # res = secClient.get_all_ipInformation()

    # query = 'ipassets_businessSystem:*十四大* AND jowto_onlineStatus:1'
    query = 'ipassets_ip:10.44.96.183'
    res = secClient.get_ipInformation_lucene_fanye(query)
    print(res)


    # print("结果：\n",res)
    print(len(res))








