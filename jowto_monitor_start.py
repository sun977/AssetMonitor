# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
    auth: sunhaobo
    version: v1.0
    function: start jowto check by this
    date: 2025.11.24
    note: 调用脚本（临时）
"""

from modules.assetmonitor.JowtoDataMonitor.jowto_check_crontabv2 import run_jowto_data_count

if __name__ == '__main__':
    # 每天8点JowtoDataHandle数据统计外发邮件 --- 20240816
    # 0 8 * * * nohup python3 /data/sunhaobo/JowtoDataHandle/jowto_check_crontabv2.py >> /data/sunhaobo/JowtoDataHandle/run.log 2>&1

    # 每天8点 AssetMonitor.run_jowto_data_count 数据统计外发邮件 --- 20251124
    # 0 8 * * * nohup python3 /data/sunhaobo/AssetMonitor-prod/AssetMonitor/jowto_monitor_start.py >> /data/sunhaobo/AssetMonitor-prod/AssetMonitor/run.log 2>&1
    run_jowto_data_count()