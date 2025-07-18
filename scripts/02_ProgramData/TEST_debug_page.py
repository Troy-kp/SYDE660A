#!/usr/bin/python3
# coding=utf-8
# author troy


# debug_save_page.py

import json
import time
from selenium import webdriver

# --- 1. 从JSON文件中获取第一个URL作为样本 ---
try:
    with open('programs.json', 'r', encoding='utf-8') as f:
        programs = json.load(f)
    if not programs:
        print("错误: programs.json 文件是空的。")
        exit()

    target_url = programs[0]['url']
    print(f"将要抓取以下URL的HTML进行调试：")
    print(target_url)

except FileNotFoundError:
    print("错误: programs.json 文件未找到。请先运行 get_links.py。")
    exit()

# --- 2. 设置Selenium并访问页面 ---
driver = webdriver.Chrome()
driver.maximize_window()

try:
    print("\n正在访问页面...")
    driver.get(target_url)

    # --- 3. 强制等待，确保所有动态内容都已加载 ---
    wait_seconds = 15
    print(f"强制等待 {wait_seconds} 秒，让所有JavaScript完成加载...")
    time.sleep(wait_seconds)
    print("等待结束。")

    # --- 4. 获取渲染后的完整HTML并保存 ---
    print("正在获取页面的完整HTML源代码...")
    page_html = driver.page_source

    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(page_html)

    print("\n====================================================================")
    print("成功！")
    print("页面的完整HTML已保存到文件: debug_page.html")
    print("====================================================================")

except Exception as e:
    print(f"在执行过程中发生错误: {e}")

finally:
    driver.quit()