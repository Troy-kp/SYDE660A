#!/usr/bin/python3
# coding=utf-8
# author troy

# get_links.py

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 设置 ---
url = "https://uwaterloo.ca/academic-calendar/graduate-studies/catalog#/programs"
base_url = "https://uwaterloo.ca/academic-calendar/graduate-studies/catalog"

driver = webdriver.Chrome()
driver.maximize_window()
driver.get(url)

all_programs = []  # 创建一个空列表来存储所有专业信息

try:
    print("页面加载中，请等待...")
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.XPATH, '//h2[starts-with(@class, "style__title")]')))
    print("页面加载完成。")

    print("正在展开所有专业列表...")
    faculty_titles = driver.find_elements(By.XPATH, '//h2[starts-with(@class, "style__title")]')
    for title in faculty_titles:
        try:
            driver.execute_script("arguments[0].click();", title)
            time.sleep(0.3)
        except Exception as e:
            print(f"点击标题 '{title.text}' 时出错: {e}")
    print("所有列表已展开，开始提取数据...")

    all_elements = driver.find_elements(By.XPATH,
                                        '//h2[starts-with(@class, "style__title")] | //a[starts-with(@href, "#/programs/")]')

    current_faculty = "Unknown"

    for element in all_elements:
        if element.tag_name == 'h2':
            current_faculty = element.text
        elif element.tag_name == 'a':
            program_name = element.text
            relative_url = element.get_attribute('href')
            full_url = relative_url

            # 将数据存入一个字典
            program_data = {
                "faculty": current_faculty,
                "name": program_name,
                "url": full_url
            }
            # 将字典添加到列表中
            all_programs.append(program_data)

    print(f"\n\n提取完成！总共找到 {len(all_programs)} 个专业。")

    # --- 核心修改：将列表写入JSON文件 ---
    with open('programs.json', 'w', encoding='utf-8') as f:
        json.dump(all_programs, f, ensure_ascii=False, indent=4)
    print("所有专业链接已成功保存到 programs.json 文件！")

except Exception as e:
    print(f"在执行过程中发生错误: {e}")

finally:
    time.sleep(2)
    driver.quit()