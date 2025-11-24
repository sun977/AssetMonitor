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

from modules.assetmonitor.DomainAssetMonitor.domain_asset_analysis import run_domain_asset_analysis
from modules.assetmonitor.DomainAssetMonitor.domain_asset_check import run_domain_asset_check

## 方式一
# pip install schedule
#
# import schedule
# import time
#
# def my_task():
#     print("Task is running...")
#
# # 每30分钟执行一次任务
# schedule.every(30).minutes.do(my_task)
# while True:
#     schedule.run_pending()
#     time.sleep(1)  # 避免CPU占用过高

## 方式二
# pip install apscheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
#
# def my_task():
#     print("Task is running...")
#
# sched = BlockingScheduler()
#
# # 每30分钟执行一次任务
# sched.add_job(my_task, 'interval', minutes=30)
#
# sched.start()

if __name__ == '__main__':
    # 运行域名资产分析监控
    run_domain_asset_analysis()

    # 运行域名资产检查监控 自带邮件通知
    run_domain_asset_check()

