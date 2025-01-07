# !/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
    auth: sunhaobo
    version: v1.0
    function: sync im_asset_ip to key_asset_ip table
    date: 2025.01.07
    note: 调用脚本（临时）
"""
from modules.ImportantAssetMonitor.important_assets_check import get_ip_from_db
from modules.ImportantAssetMonitor.sync.sync_sec_data2db_from_txt import run_sync_sec_data2db_from_txt

if __name__ == '__main__':
    run_sync_sec_data2db_from_txt()
    # print(get_ip_from_db())
