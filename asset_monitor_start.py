#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
    auth: sunhaobo
    version: v2.0
    function: 所有资产监控调用从这里开始
    date: 2024.12.25
    note:
        - domain_asset_analysis.py 该模块主要负责以下操作：
            1. 同步原始域名数据
            2. 进行域名解析并入库
            3. 记录操作完成时间
            4. 后续将各个模块的任务抽象出来到目录外
            5. 每天执行一次
            6. 执行方式，计划任务：0  5  *  *  *  nohup python3 AssetMonitor/modules/DomainAssetMonitor/domain_asset_analysis.py

"""

from modules.DomainAssetMonitor.domain_asset_analysis import run_domain_asset_analysis

if __name__ == '__main__':
    # 运行域名资产分析监控
    run_domain_asset_analysis()
