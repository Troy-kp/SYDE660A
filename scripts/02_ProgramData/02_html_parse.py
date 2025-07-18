#!/usr/bin/python3
# coding=utf-8
# author troy

from bs4 import BeautifulSoup
import json
import re

# --- 输入和输出文件名 ---
input_html_file = "raw_page_content.html"
output_json_file = "official_graduate_programs.json"

print(f"正在读取并解析您的本地文件: {input_html_file}")

try:
    # 1. 打开并读取您提供的HTML文件
    with open(input_html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 2. 使用BeautifulSoup进行解析
    soup = BeautifulSoup(html_content, 'html.parser')

    # 3. 准备一个列表来存放所有处理好的项目
    all_programs = []

    # 初始化当前处理的学位级别
    current_academic_level = None

    # 4. 找到包含所有内容的核心区域
    content_area = soup.find('div', role='article')

    # 5. 查找内容区域中所有的标题(h2)和列表(ul)，并按它们在文档中出现的顺序处理
    for element in content_area.find_all(['h2', 'ul']):

        # 如果是标题，就更新我们当前所处的“区域”
        if element.name == 'h2':
            title_text = element.get_text(strip=True)
            if "Master's programs" in title_text:
                current_academic_level = "Master's"
                print(f"\n进入 '{current_academic_level}' 项目区...")
            elif "Doctor of Philosophy (PhD) programs" in title_text:
                current_academic_level = "Doctoral"
                print(f"进入 '{current_academic_level}' 项目区...")
            elif "Graduate Diploma (GDip) programs" in title_text:
                current_academic_level = "Diploma"
                print(f"进入 '{current_academic_level}' 项目区...")

        # 如果是列表，并且我们已经确定了当前所处的区域
        elif element.name == 'ul' and current_academic_level:
            # 6. 遍历列表中的每一个项目 (li)
            for item in element.find_all('li'):
                link = item.find('a')
                if not link:
                    continue

                full_text = link.get_text(strip=True).replace('‑', '-')  # 统一连字符
                program_url = link.get('href')

                # 确保URL是完整的
                if program_url and not program_url.startswith('http'):
                    program_url = 'https://uwaterloo.ca' + program_url

                # 7. 解析项目名称和学位
                # 从右边分割一次，以处理 "Program - Name - (Degree)" 的情况
                parts = full_text.rsplit(' - ', 1)
                if len(parts) == 2:
                    program_name = parts[0].strip()
                    degree_info = parts[1].strip()

                    # 从学位信息中提取括号里的缩写
                    degree_match = re.search(r'\((.*?)\)', degree_info)
                    degree = degree_match.group(1) if degree_match else degree_info  # 如果没括号，就用整个部分
                else:
                    program_name = full_text  # 如果无法分割，整个都是项目名
                    degree = "Unknown"

                # 8. 为每个学位创建一个记录
                all_programs.append({
                    "program_name": program_name,
                    "degree": degree,
                    "academic_level": current_academic_level,
                    "program_url": program_url
                })

    # 9. 保存到最终的JSON文件
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(all_programs, f, ensure_ascii=False, indent=4)

    print(f"\n任务完成！成功从您的HTML文件中提取并结构化了 {len(all_programs)} 个学位项目。")
    print(f"您的官方项目列表已保存到: {output_json_file}")

except FileNotFoundError:
    print(f"错误: 找不到输入文件 '{input_html_file}'。请确保它和本脚本在同一目录下。")
except Exception as e:
    print(f"处理数据或解析HTML时发生错误: {e}")