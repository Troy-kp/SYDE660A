#!/usr/bin/python3
# coding=utf-8
# author troy

# 获取program的代码和名称的对照表

import requests
import json

# --- 您的API密钥 ---
api_key = "82EE1A91C80C48168A2B7156862DE865"
headers = {'x-api-key': api_key}

# --- API端点和输出文件名 ---
subjects_url = "https://openapi.data.uwaterloo.ca/v3/Subjects"
output_filename = "subjects_dictionary.json"

print("正在获取所有专业的全称列表...")

try:
    # 1. 发送API请求
    response = requests.get(subjects_url, headers=headers)
    response.raise_for_status()  # 确保请求成功

    # 2. 获取原始数据（一个对象列表）
    # e.g., [{"code": "ACC", "name": "Accounting"}, {"code": "ACINTY", "name": "Academic Integrity"}, ...]
    all_subjects_list = response.json()

    # 3. 将列表转换为更易于查找的字典格式
    # e.g., {"ACC": "Accounting", "ACINTY": "Academic Integrity", ...}
    subjects_dictionary = {
        subject.get("code"): subject.get("name")
        for subject in all_subjects_list
    }

    # 4. 将这个方便的字典保存到JSON文件中
    with open(output_filename, 'w', encoding='utf-8') as f:
        # 使用 indent=4 参数让JSON文件格式化，易于人类阅读
        json.dump(subjects_dictionary, f, ensure_ascii=False, indent=4)

    print(f"\n成功获取到 {len(subjects_dictionary)} 个专业的全称。")
    print(f"数据已成功保存到文件: {output_filename}")
    print("\n您现在可以打开这个文件，查看所有专业缩写的含义了。")

except requests.exceptions.RequestException as e:
    print(f"获取专业列表时发生错误: {e}")
except Exception as e:
    print(f"处理数据时发生未知错误: {e}")