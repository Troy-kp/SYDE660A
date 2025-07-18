#!/usr/bin/python3
# coding=utf-8
# author troy

import sqlite3
import re
import os

# --- 设置 ---
db_filename = "course_database.db"


def parse_and_store_requirements(db_file):
    """ 连接到数据库，解析需求文本，并存储结构化关系 """
    print(f"\n正在连接到数据库 '{db_file}' 以解析先修课程...")
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 1. 从Courses表中选出所有需要解析的课程
        cursor.execute(
            "SELECT courseId, subjectCode, requirementsDescription FROM Courses WHERE requirementsDescription IS NOT NULL AND requirementsDescription != ''")
        all_courses_with_reqs = cursor.fetchall()

        print(f"找到 {len(all_courses_with_reqs)} 门课程有需求描述文本，开始解析...")

        prereqs_found = 0
        antireqs_found = 0
        program_reqs_found = 0

        for course_id, subject_code, req_text in all_courses_with_reqs:
            # 2. 解析 Antirequisite (反修课程)
            # 匹配 "Antireq: COURSE 123, SUBJ 456, ..."
            antireq_match = re.search(r'Antireq: (.*?)(;|$)', req_text, re.IGNORECASE)
            if antireq_match:
                antireq_string = antireq_match.group(1).strip()
                # 找到所有像 "SYDE 552" 或 "NANO 702" 这样的课程代码
                antireq_courses = re.findall(r'([A-Z]+)\s*(\w+)', antireq_string)
                for prereq_subj, prereq_num in antireq_courses:
                    # 我们需要根据 subject 和 catalog number 找到对应的 courseId
                    cursor.execute("SELECT courseId FROM Courses WHERE subjectCode = ? AND catalogNumber = ?",
                                   (prereq_subj, prereq_num))
                    prereq_course_id_result = cursor.fetchone()
                    if prereq_course_id_result:
                        prereq_course_id = prereq_course_id_result[0]
                        cursor.execute(
                            "INSERT INTO Prerequisites (courseId, prerequisiteCourseId, isAntirequisite) VALUES (?, ?, ?)",
                            (course_id, prereq_course_id, 1))
                        antireqs_found += 1

            # 3. 解析 Prerequisite (先修课程)
            prereq_match = re.search(r'Prereq: (.*?)(;|$|Antireq:)', req_text, re.IGNORECASE)
            if prereq_match:
                prereq_string = prereq_match.group(1).strip()
                # 寻找课程代码
                prereq_courses = re.findall(r'([A-Z]+)\s*(\w+)', prereq_string)
                for prereq_subj, prereq_num in prereq_courses:
                    cursor.execute("SELECT courseId FROM Courses WHERE subjectCode = ? AND catalogNumber = ?",
                                   (prereq_subj, prereq_num))
                    prereq_course_id_result = cursor.fetchone()
                    if prereq_course_id_result:
                        prereq_course_id = prereq_course_id_result[0]
                        cursor.execute(
                            "INSERT INTO Prerequisites (courseId, prerequisiteCourseId, isAntirequisite) VALUES (?, ?, ?)",
                            (course_id, prereq_course_id, 0))
                        prereqs_found += 1

                # 寻找特殊的项目限制，例如 "SYDE MEng plans only"
                program_match = re.search(r'([A-Z]+\s*(?:MEng|MASc|PhD)\s*plans? only)', prereq_string, re.IGNORECASE)
                if program_match:
                    program_req_desc = program_match.group(1)
                    # 简化一下，直接存 program code
                    required_program = program_req_desc.split(' ')[0]
                    cursor.execute(
                        "INSERT INTO ProgramPrerequisites (courseId, requiredProgram, description) VALUES (?, ?, ?)",
                        (course_id, required_program, program_req_desc))
                    program_reqs_found += 1

        conn.commit()
        print("\n解析完成！")
        print(f"成功解析并存储了 {prereqs_found} 条先修课程关系。")
        print(f"成功解析并存储了 {antireqs_found} 条反修课程关系。")
        print(f"成功解析并存储了 {program_reqs_found} 条项目限制关系。")

    except sqlite3.Error as e:
        print(f"处理数据库时发生错误: {e}")
    finally:
        if conn:
            conn.close()


# --- 主执行流程 ---
if __name__ == '__main__':
    if not os.path.exists(db_filename):
        print(f"错误: 数据库文件 '{db_filename}' 不存在。请先运行 'build_database_v2.py'。")
    else:
        parse_and_store_requirements(db_filename)
        print(f"\n数据库关系构建完成！'{db_filename}' 已包含完整的课程依赖信息。")