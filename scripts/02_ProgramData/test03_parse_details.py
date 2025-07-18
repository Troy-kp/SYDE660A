#!/usr/bin/python3
# coding=utf-8
# author troy

# parse_details.py (The REAL Final Version)

import json
import re

# parse_focused_details.py

import json
import re

# ==============================================================================
# 核心变更：我们只定义我们关心的、与课程和学位要求相关的章节标题
# ==============================================================================
TARGET_HEADERS = [
    "Degree requirements",
    "Course requirements",
    "Milestone requirements",
    "Graduate Diploma: Course requirements"  # 针对GDip的特殊标题
]

# 排序依然是好习惯，以防万一
TARGET_HEADERS.sort(key=len, reverse=True)

# --- 1. 加载我们已经爬取好的数据 ---
try:
    with open('programs_with_details.json', 'r', encoding='utf-8') as f:
        programs = json.load(f)
    print(f"成功加载 {len(programs)} 个专业的原始数据。")
except FileNotFoundError:
    print("错误: programs_with_details.json 文件未找到。请先运行 get_details.py。")
    exit()

# --- 2. 遍历每个专业，只提取目标章节 ---
for program in programs:
    details_text = program.get('details', '')

    # 创建一个新的键，专门存放我们需要的核心信息
    program['core_requirements'] = {}

    # 使用finditer来查找我们关心的每一个标题
    headers_pattern = '|'.join(re.escape(h) for h in TARGET_HEADERS)
    matches = list(re.finditer(headers_pattern, details_text))

    # 遍历所有找到的目标标题
    for i, match in enumerate(matches):
        header = match.group(0)

        # 提取该标题下的内容
        start_index = match.end()
        end_index = matches[i + 1].start() if i + 1 < len(matches) else len(details_text)

        content = details_text[start_index:end_index].strip()

        # 存入我们的核心信息字典
        program['core_requirements'][header] = content

    # 清理掉不再需要的原始长文本，让最终文件更小、更干净
    del program['details']
    if 'parsed_details' in program:
        del program['parsed_details']

# --- 3. 将最终的、目标明确的数据保存到新文件 ---
output_filename = 'programs_focused_data.json'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(programs, f, ensure_ascii=False, indent=4)

print(f"\n解析完成！")
print(f"只包含核心要求的数据已保存到: {output_filename}")