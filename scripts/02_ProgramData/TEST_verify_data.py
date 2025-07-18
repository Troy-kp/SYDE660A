#!/usr/bin/python3
# coding=utf-8
# author troy

# verify_reconstruction.py (The REAL Final Version)

import json

try:
    with open('programs_final_structured.json', 'r', encoding='utf-8') as f:
        programs = json.load(f)
except FileNotFoundError:
    print("错误: programs_final_structured.json 文件未找到。")
    exit()

print("--- 开始进行最终的内容重建验证 ---")
mismatch_count = 0

for program in programs:
    original_text = program.get('details', '')
    parsed_details = program.get('parsed_details', {})

    if original_text.endswith('\nfile_upload'):
        original_text = original_text[:-len('\nfile_upload')].strip()

    # --- 核心逻辑修复：直接按字典顺序重建 ---
    reconstructed_parts = []
    for header, content in parsed_details.items():
        # “Program Title”是我们自己加的键，它的内容就是文本本身
        if header == 'Program Title':
            reconstructed_parts.append(content)
        # 其他所有键都是原始文本中存在的标题
        else:
            reconstructed_parts.append(header)
            reconstructed_parts.append(content)

    reconstructed_text = '\n'.join(reconstructed_parts)

    # --- 标准化后进行比较 ---
    original_normalized = "".join(original_text.split())
    reconstructed_normalized = "".join(reconstructed_text.split())

    if original_normalized != reconstructed_normalized:
        mismatch_count += 1
        print(f"不匹配：专业 '{program['name']}' 的内容在转换后有差异。")

if mismatch_count == 0:
    print("\n========================================================")
    print("✅ 验证成功：所有专业的数据都已完整转换，没有内容遗漏！")
    print("========================================================")
else:
    print(f"\n验证失败：发现 {mismatch_count} 个专业在转换过程中存在内容差异。")