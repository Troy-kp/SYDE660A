#!/usr/bin/python3
# coding=utf-8
# author troy

# create_final_engineering_dataset.py

import json
import re

# ==============================================================================
# 1. 定义一个我们所知的所有可能的章节标题的权威列表
#    这是成功的关键，它基于对您提供的所有样本的观察。
# ==============================================================================
ALL_POSSIBLE_HEADERS = [
    "Faculty", "Academic unit", "Admit term(s)", "Delivery mode",
    "Delivery mode information", "Registration option(s)", "Registration options information",
    "Program type(s)", "Study option(s)", "Length of program", "Graduate research fields",
    "Admission requirements: Minimum requirements",
    "Admission requirements: Application materials",
    "Admission requirements: References", "Degree requirements",
    "Course requirements", "Milestone requirements", "Other requirements", "Relevant links",
    "Accelerated program details", "Additional program information", "Graduate specializations",
    # 为了处理不同学习选项下的子标题，我们把它们也视为可能的顶级切分点
    "Thesis option: Course requirements", "Thesis option: Milestone requirements",
    "Master's Research Paper option: Course requirements", "Master’s Research Paper option: Milestone requirements",
    "Coursework option: Course requirements", "Coursework option: Milestone requirements",
    "Graduate Diploma: Course requirements", "Graduate Diploma: Milestone requirements"
]

# --- 核心修复：按长度对标题进行降序排序 ---
# 这可以保证正则表达式引擎优先匹配最长、最精确的标题。
ALL_POSSIBLE_HEADERS.sort(key=len, reverse=True)

# --- 2. 加载已爬取的完整数据 ---
try:
    with open('programs_with_details.json', 'r', encoding='utf-8') as f:
        all_programs_raw = json.load(f)
    print(f"成功加载 {len(all_programs_raw)} 个专业的原始数据。")
except FileNotFoundError:
    print("错误: programs_with_details.json 文件未找到。请先运行 get_details.py。")
    exit()

# --- 3. 遍历所有项目，筛选工程学院并进行精细解析 ---
engineering_programs_final = []
print("\n开始筛选工程学院的项目并进行最终的结构化解析...")

for program in all_programs_raw:
    details_text = program.get('details', '')

    # 使用一种更可靠的方式来检查项目是否属于工程学院
    # 我们直接在解析后的数据中检查 'Faculty' 字段

    # --- 解析所有章节，无论学院为何 ---
    temp_parsed_details = {}
    headers_pattern = '|'.join(re.escape(h) for h in ALL_POSSIBLE_HEADERS)
    matches = list(re.finditer(headers_pattern, details_text))

    last_end = 0
    # 处理第一个标题之前的内容
    if matches:
        first_match_start = matches[0].start()
        program_title_text = details_text[last_end:first_match_start].strip()
        if program_title_text:
            temp_parsed_details['Program Title'] = program_title_text

    # 遍历所有找到的标题，按顺序提取内容
    for i, match in enumerate(matches):
        header = match.group(0)
        start_index = match.end()
        end_index = matches[i + 1].start() if i + 1 < len(matches) else len(details_text)
        content = details_text[start_index:end_index].strip()
        temp_parsed_details[header] = content

    # --- 现在，根据解析出的 'Faculty' 字段来判断是否为工程学院 ---
    if temp_parsed_details.get('Faculty') == 'Faculty of Engineering':
        eng_program_data = {
            "faculty": program.get("faculty"),
            "name": program.get("name"),
            "url": program.get("url"),
            "structured_details": temp_parsed_details  # 存储所有解析出的章节
        }
        engineering_programs_final.append(eng_program_data)

# --- 4. 保存最终的、全面的、结构化的工程学院数据 ---
output_filename = 'engineering_programs_fully_structured.json'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(engineering_programs_final, f, ensure_ascii=False, indent=4)

print(f"\n解析完成！")
print(f"共找到并处理了 {len(engineering_programs_final)} 个工程学院的项目。")
print(f"最终的、完整的结构化数据已保存到: {output_filename}")