# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
    auth: sunhaobo
    version: v1.0
    function: sync sec data to db
    date: 2025.12.02
    note: 调用脚本（临时）
"""

from modules.assetmonitor.ImportantAssetMonitor.sync.sync_sec_data2db_from_txt import run_sync_sec_data2db_from_txt
# AssetMonitor/modules/assetmonitor/ImportantAssetMonitor/sync/sync_sec_data2db_from_txt.py

if __name__ == '__main__':
    # 手动触发从文件中同步IP信息到系统DB
    # 文件位置：AssetMonitor/modules/assetmonitor/ImportantAssetMonitor/sync/im_asset_ip.txt
    run_sync_sec_data2db_from_txt()