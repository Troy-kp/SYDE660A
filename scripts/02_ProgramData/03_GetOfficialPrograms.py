#!/usr/bin/python3
# coding=utf-8
# author troy

import requests

# 确认可用的URL
url = "https://uwaterloo.ca/academic-calendar/graduate-studies/catalog#/programs"

# 把原始HTML保存到这个文件中
output_filename = "02_programs_requirements_index.html"

print(f"正在抓取网页的全部原始HTML内容。")
print(f"正在访问目标网址: {url}")

try:
    # 1. 发送HTTP请求，获取网页内容
    response = requests.get(url, timeout=10)  # 设置10秒超时以防止无限等待

    # 2. 检查请求是否成功。如果不成功，会在此处抛出异常
    response.raise_for_status()

    # 3. 将完整的、未经处理的HTML内容保存到文件
    # 使用 'utf-8' 编码以确保所有字符都能正确保存
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(response.text)

    print("\n--------------------------------------------------")
    print("任务成功完成！")
    print(f"完整的网页原始HTML内容已被保存到了'{output_filename}' 文件中。")

except requests.exceptions.RequestException as e:
    print(f"\n错误：访问网页时失败了。")
    print(f"这可能是网络问题或网址暂时无法访问。详细错误信息: {e}")

except Exception as e:
    print(f"\n在执行过程中发生了意料之外的错误: {e}")