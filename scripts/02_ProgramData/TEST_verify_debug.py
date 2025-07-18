#!/usr/bin/python3
# coding=utf-8
# author troy

# debug_the_verifier.py

import json
import re

# 确保这两个列表与您最终使用的 parse_details.py 中的完全一致
SECTION_HEADERS = [
    "Faculty", "Academic unit", "Admit term(s)", "Delivery mode",
    "Delivery mode information", "Registration option(s)", "Program type(s)",
    "Study option(s)", "Length of program", "Graduate research fields",
    "Admission requirements: Minimum requirements",
    "Admission requirements: Application materials",
    "Admission requirements: References", "Degree requirements",
    "Course requirements", "Milestone requirements", "Other requirements",
    "Relevant links", "Graduate Diploma: Course requirements"
]

try:
    with open('programs_final_structured.json', 'r', encoding='utf-8') as f:
        programs = json.load(f)
except FileNotFoundError:
    print("错误: programs_final_structured.json 文件未找到。")
    exit()

print("--- 开始对第一个专业进行深度调试 ---")

# 只取第一个专业作为样本
program = programs[0]

# --- 1. 获取原始文本和解析后的字典 ---
original_text = program.get('details', '')
parsed_details = program.get('parsed_details', {})

if original_text.endswith('\nfile_upload'):
    original_text = original_text[:-len('\nfile_upload')].strip()

# --- 2. 重建文本（使用我之前提供的、有问题的逻辑）---
reconstructed_parts = []
if 'Program Title' in parsed_details:
    reconstructed_parts.append(parsed_details['Program Title'])

for header in SECTION_HEADERS:
    if header in parsed_details:
        reconstructed_parts.append(header)
        reconstructed_parts.append(parsed_details[header])

reconstructed_text = '\n'.join(reconstructed_parts)

# --- 3. 标准化两个文本 ---
original_normalized = "".join(original_text.split())
reconstructed_normalized = "".join(reconstructed_text.split())

# --- 4. 打印所有用于调试的信息 ---
print("\n======================= 原始文本 (标准化后) =======================")
print(original_normalized)
print(f"\n原始文本长度: {len(original_normalized)}")

print("\n======================= 重建文本 (标准化后) =======================")
print(reconstructed_normalized)
print(f"\n重建文本长度: {len(reconstructed_normalized)}")

print("\n=========================== 对比结果 ===========================")
if original_normalized == reconstructed_normalized:
    print("✅ 两个字符串完全匹配！")
else:
    print("❌ 两个字符串不匹配。请将以上所有输出内容复制给我进行分析。")