#!/usr/bin/python3
# coding=utf-8
# author troy

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 设置 ---
url = "https://uwaterloo.ca/academic-calendar/graduate-studies/catalog#/programs"
base_url = "https://uwaterloo.ca/academic-calendar/graduate-studies/catalog"

driver = webdriver.Chrome()
# 建议将窗口最大化，有时可以减少元素被遮挡的概率
driver.maximize_window()
driver.get(url)

# --- 主逻辑 ---
try:
    print("页面加载中，请等待...")
    wait = WebDriverWait(driver, 30)

    wait.until(EC.presence_of_element_located((By.XPATH, '//h2[starts-with(@class, "style__title")]')))
    print("页面加载完成。")

    print("正在展开所有专业列表...")
    faculty_titles = driver.find_elements(By.XPATH, '//h2[starts-with(@class, "style__title")]')
    for title in faculty_titles:
        try:
            # --- 核心修改：使用JavaScript点击来绕过遮挡 ---
            driver.execute_script("arguments[0].click();", title)
            time.sleep(0.3)  # 保持短暂等待，让内容有时间展开
        except Exception as e:
            print(f"点击标题 '{title.text}' 时出错: {e}")
    print("所有列表已展开，开始提取数据...")

    # 后续代码保持不变
    all_elements = driver.find_elements(By.XPATH,
                                        '//h2[starts-with(@class, "style__title")] | //a[starts-with(@href, "#/programs/")]')

    current_faculty = "Unknown"
    program_count = 0

    for element in all_elements:
        if element.tag_name == 'h2':
            current_faculty = element.text
            print(f"\n--- {current_faculty} ---")
        elif element.tag_name == 'a':
            program_name = element.text
            relative_url = element.get_attribute('href')
            # 拼接URL的逻辑可以更健壮一些
            if relative_url.startswith(base_url):
                full_url = relative_url
            else:
                full_url = base_url + relative_url

            print(f"  - 专业: {program_name}")
            print(f"    URL: {full_url}")
            program_count += 1

    print(f"\n\n提取完成！总共找到 {program_count} 个专业。")

except Exception as e:
    print(f"在执行过程中发生错误: {e}")

finally:
    time.sleep(2)
    driver.quit()