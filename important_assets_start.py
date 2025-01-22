# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
    auth: sunhaobo
    version: v1.0
    function: sync im_asset_ip to key_asset_ip table
    date: 2025.01.07
    note: 调用脚本（临时）
"""
from modules.assetmonitor.ImportantAssetMonitor.important_assets_check import run_important_asset_check

if __name__ == '__main__':
    # 从 文件 里 读取 ip , 并获取SEC IP 数据入表 【不用长期执行，只用做批量导入新的监控数据时候 文件:modules/ImportantAssetMonitor/sync/im_asset_ip.txt 】
    # run_sync_sec_data2db_from_txt()

    # 获取 important_asset_ip 监控数据【周期执行】
    # 0  10  *  *  *  nohup python3 /data/sunhaobo/AssetMonitor-prod/AssetMonitor/important_assets_start.py >> /data/sunhaobo/AssetMonitor-prod/AssetMonitor/run.log 2>&1
    run_important_asset_check()
