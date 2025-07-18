#!/usr/bin/python3
# coding=utf-8
# author troy

import sqlite3
import json
import os

# --- 设置 ---
input_directory = "../final_verified_course_data"
db_filename = "course_database.db"  # 使用新文件名以避免与旧版混淆


def create_connection(db_file):
    """ 创建一个到SQLite数据库的连接 """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"成功连接到SQLite数据库: {db_file}")
    except sqlite3.Error as e:
        print(e)
    return conn


def create_tables_v2(conn):
    """ 在数据库中创建我们【升级版】的表 """
    try:
        c = conn.cursor()

        # Courses 表 (不变)
        c.execute("""
                  CREATE TABLE IF NOT EXISTS Courses
                  (
                      courseId
                      TEXT
                      PRIMARY
                      KEY,
                      subjectCode
                      TEXT
                      NOT
                      NULL,
                      catalogNumber
                      TEXT
                      NOT
                      NULL,
                      title
                      TEXT,
                      description
                      TEXT,
                      requirementsDescription
                      TEXT
                  );
                  """)

        # Terms 表 (不变)
        c.execute("""
                  CREATE TABLE IF NOT EXISTS Terms
                  (
                      termCode
                      TEXT
                      PRIMARY
                      KEY,
                      termName
                      TEXT
                      NOT
                      NULL
                  );
                  """)

        # 【升级版】Offerings 表
        c.execute("""
                  CREATE TABLE IF NOT EXISTS Offerings
                  (
                      offeringId
                      INTEGER
                      PRIMARY
                      KEY
                      AUTOINCREMENT,
                      courseId
                      TEXT
                      NOT
                      NULL,
                      termCode
                      TEXT
                      NOT
                      NULL,
                      courseOfferNumber
                      INTEGER,
                      courseComponentCode
                      TEXT,
                      enrollConsentCode
                      TEXT,
                      FOREIGN
                      KEY
                  (
                      courseId
                  ) REFERENCES Courses
                  (
                      courseId
                  ),
                      FOREIGN KEY
                  (
                      termCode
                  ) REFERENCES Terms
                  (
                      termCode
                  )
                      );
                  """)

        # 【新增】Prerequisites 表
        c.execute("""
                  CREATE TABLE IF NOT EXISTS Prerequisites
                  (
                      prerequisiteId
                      INTEGER
                      PRIMARY
                      KEY
                      AUTOINCREMENT,
                      courseId
                      TEXT
                      NOT
                      NULL,
                      prerequisiteCourseId
                      TEXT
                      NOT
                      NULL,
                      isAntirequisite
                      INTEGER
                      NOT
                      NULL
                      DEFAULT
                      0,
                      FOREIGN
                      KEY
                  (
                      courseId
                  ) REFERENCES Courses
                  (
                      courseId
                  )
                      );
                  """)

        # 【新增】ProgramPrerequisites 表
        c.execute("""
                  CREATE TABLE IF NOT EXISTS ProgramPrerequisites
                  (
                      programReqId
                      INTEGER
                      PRIMARY
                      KEY
                      AUTOINCREMENT,
                      courseId
                      TEXT
                      NOT
                      NULL,
                      requiredProgram
                      TEXT
                      NOT
                      NULL,
                      description
                      TEXT,
                      FOREIGN
                      KEY
                  (
                      courseId
                  ) REFERENCES Courses
                  (
                      courseId
                  )
                      );
                  """)

        print("所有升级版表已成功创建或确认存在。")
        conn.commit()
    except sqlite3.Error as e:
        print(f"创建表时发生错误: {e}")


def populate_database_v2(conn, source_dir):
    """ 遍历文件并用数据填充数据库 (包括Offerings的新字段) """
    cursor = conn.cursor()
    print("\n开始填充数据库，请稍候...")

    courses_added = set()
    terms_added = set()
    offerings_added = 0

    for subject_code in os.listdir(source_dir):
        subject_path = os.path.join(source_dir, subject_code)
        if not os.path.isdir(subject_path): continue

        for term_filename in os.listdir(subject_path):
            term_code = term_filename.replace('.json', '')
            filepath = os.path.join(subject_path, term_filename)

            with open(filepath, 'r', encoding='utf-8') as f:
                courses_in_file = json.load(f)

            for course in courses_in_file:
                # 插入 Term
                if term_code not in terms_added:
                    cursor.execute("INSERT OR IGNORE INTO Terms (termCode, termName) VALUES (?, ?)",
                                   (term_code, course.get('termName')))
                    terms_added.add(term_code)

                # 插入 Course
                course_id = course.get('courseId')
                if course_id not in courses_added:
                    cursor.execute("""
                                   INSERT
                                   OR IGNORE INTO Courses (courseId, subjectCode, catalogNumber, title, description, requirementsDescription) 
                        VALUES (?, ?, ?, ?, ?, ?)
                                   """, (
                                       course_id, course.get('subjectCode'), course.get('catalogNumber'),
                                       course.get('title'), course.get('description'),
                                       course.get('requirementsDescription')
                                   ))
                    courses_added.add(course_id)

                # 插入【升级版】Offering
                cursor.execute("""
                               INSERT INTO Offerings (courseId, termCode, courseOfferNumber, courseComponentCode,
                                                      enrollConsentCode)
                               VALUES (?, ?, ?, ?, ?)
                               """, (
                                   course_id, term_code, course.get('courseOfferNumber'),
                                   course.get('courseComponentCode'), course.get('enrollConsentCode')
                               ))
                offerings_added += 1

    conn.commit()
    print("\n数据库填充完毕！")
    print(f"总计处理了 {len(courses_added)} 门独立课程。")
    print(f"总计处理了 {len(terms_added)} 个学期。")
    print(f"总计创建了 {offerings_added} 条课程开设记录。")


# --- 主执行流程 ---
if os.path.exists(db_filename):
    os.remove(db_filename)
    print(f"已删除旧的数据库文件: {db_filename}")

connection = create_connection(db_filename)
if connection:
    create_tables_v2(connection)
    populate_database_v2(connection, input_directory)
    connection.close()
    print(f"\n数据库基础框架构建完成！下一步是解析先修课程关系。")