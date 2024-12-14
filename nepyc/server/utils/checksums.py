"""
Author: Taylor B. tayjaybabee@gmail.com
Date: 2024-12-13 19:56:40
LastEditors: Taylor B. tayjaybabee@gmail.com
LastEditTime: 2024-12-13 19:57:23
FilePath: nepyc/server/utils/checksums.py
Description: 这是默认设置,可以在设置》工具》File Description中进行配置
"""
import hashlib


def calculate_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
