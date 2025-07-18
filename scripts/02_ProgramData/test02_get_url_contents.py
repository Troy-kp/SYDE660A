# get_details.py (Final Version with BeautifulSoup)

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup  # 导入BeautifulSoup

# --- 1. 读取之前保存的JSON文件 ---
try:
    with open('programs.json', 'r', encoding='utf-8') as f:
        programs = json.load(f)
    print(f"成功加载 {len(programs)} 个专业链接。")
except FileNotFoundError:
    print("错误: programs.json 文件未找到。请先运行 get_links.py。")
    exit()

# --- 2. 设置Selenium ---
driver = webdriver.Chrome()
driver.maximize_window()

# --- 3. 遍历每个专业，访问其URL并抓取详情 ---
all_details = []
for i, program in enumerate(programs):
    print(f"({i + 1}/{len(programs)}) 正在爬取: {program['name']}")
    try:
        driver.get(program['url'])

        # 给页面足够的时间加载所有动态内容，5-10秒通常足够
        time.sleep(7)

        # 获取加载完成后的页面HTML源代码
        html_source = driver.page_source

        # --- 使用BeautifulSoup解析HTML ---
        soup = BeautifulSoup(html_source, 'html.parser')

        # --- 根据我们从debug_page.html中发现的结构，找到最外层的详情容器 ---
        # 这个ID是独一无二的，是完美的定位器！
        details_container = soup.find('div', id='__KUALI_TLP')

        if details_container:
            # 使用.get_text()提取所有纯文本，并用换行符分隔，去除多余空格
            details_text = details_container.get_text(separator='\n', strip=True)
            program['details'] = details_text
        else:
            # 如果因为某些原因没找到容器，则标记为错误
            program['details'] = "Error: Details container with id='__KUALI_TLP' not found."
            print("  -> 爬取失败: 未找到ID为'__KUALI_TLP'的容器。")

    except Exception as e:
        print(f"  -> 爬取时发生未知错误: {e}")
        program['details'] = f"Error: {type(e).__name__}"

    all_details.append(program)

    # 每抓取5个专业就保存一次进度
    if (i + 1) % 5 == 0 or (i + 1) == len(programs):
        with open('programs_with_details.json', 'w', encoding='utf-8') as f:
            json.dump(all_details, f, ensure_ascii=False, indent=4)
        print(f"--- 进度已保存 ---")

    # 礼貌性等待
    time.sleep(1)

# --- 4. 全部完成后，最后再完整保存一次 ---
print("\n所有专业详情爬取完成！")
print(f"最终结果已保存到 programs_with_details.json 文件。")

driver.quit()