#!/usr/bin/python3
# coding=utf-8
# author troy

import requests
import json
import os
import time
from datetime import datetime

# --- 您的API密钥 ---
api_key = "82EE1A91C80C48168A2B7156862DE865"
headers = {'x-api-key': api_key}

# --- 配置设置 ---
class Config:
    # =================================================================
    # 数据获取范围配置 (三种模式)
    # =================================================================
    
    # 模式1: 推荐配置 (基于实际课程表验证的最优范围)
    MODE_RECOMMENDED = {
        'enabled': True,
        'start_year': 2021,  # 基于智能探索：100%数据有效性
        'end_year': 2025,    # 最新有效学期
        'description': '推荐配置：基于实际课程表验证的最佳数据范围'
    }
    
    # 模式2: 自定义年份范围 (可随时调整)
    MODE_CUSTOM = {
        'enabled': False,
        'start_year': 2020,  # 🔧 可调整：最早有效年份
        'end_year': 2025,    # 🔧 可调整：最新有效年份
        'description': '完整有效范围：包含所有验证有效的学期'
    }
    
    # 模式3: 完整历史数据 (1956-2029，数据量巨大)
    MODE_ALL_HISTORICAL = {
        'enabled': False,
        'description': '完整历史：获取所有74年数据（需要很长时间）'
    }
    
    # 模式4: 仅最新数据 (快速测试用)
    MODE_RECENT_ONLY = {
        'enabled': False,
        'start_year': 2025,
        'end_year': 2025,
        'description': '仅最新：只获取2025年数据进行快速测试'
    }
    
    # 模式5: 验证有效的完整范围 (2020-2025，基于智能探索结果)
    MODE_VERIFIED_COMPLETE = {
        'enabled': False,
        'start_year': 2020,  # 最早有部分有效数据的年份
        'end_year': 2025,    # 最新有效年份
        'description': '完整验证：包含所有经过课程表验证的有效学期 (17个学期)'
    }
    
    # =================================================================
    # 课程类型过滤
    # =================================================================
    # 推荐设置：包含所有课程类型，提供最大灵活性
    # 优势：
    # 1. 支持研究生选择高级本科课程
    # 2. 未来可扩展到本科生推荐系统
    # 3. 完整的先修课程依赖关系网络
    # 4. 跨层次的学习路径规划
    INCLUDE_GRADUATE_ONLY = False  # True: 只获取研究生课程, False: 获取所有课程
    INCLUDE_UNDERGRADUATE = True   # 是否包含本科生课程
    
    # 输出目录
    OUTPUT_BASE_DIR = "API_course_data_comprehensive"
    FILTERED_OUTPUT_BASE_DIR = "API_course_data_filtered"
    GRADUATE_DIR = "graduate_courses"
    ALL_COURSES_DIR = "all_courses"
    SCHEDULE_DIR = "API_schedule_data_comprehensive"
    
    # 推荐：为了更好的数据组织，建议使用新的目录结构
    # OUTPUT_BASE_DIR = "../course_data_complete"  # 新的完整数据集目录
    
    # 性能设置
    REQUEST_DELAY = 0.3  # 请求间隔（秒）
    MAX_RETRIES = 3      # 最大重试次数
    BATCH_SIZE = 10      # 批处理大小

def setup_directories():
    """创建输出目录（原始、过滤后、课表）"""
    # 原始课程数据子目录（按照是否仅研究生）
    subdir = Config.GRADUATE_DIR if Config.INCLUDE_GRADUATE_ONLY else Config.ALL_COURSES_DIR

    course_raw_dir = os.path.join(Config.OUTPUT_BASE_DIR, subdir)
    course_filtered_dir = os.path.join(Config.FILTERED_OUTPUT_BASE_DIR, subdir)
    schedule_data_dir = Config.SCHEDULE_DIR

    for directory in [course_raw_dir, course_filtered_dir, schedule_data_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}")

    return course_raw_dir, course_filtered_dir, schedule_data_dir

def get_all_subjects():
    """获取所有专业列表"""
    subjects_url = "https://openapi.data.uwaterloo.ca/v3/Subjects"
    print("\n🔍 正在获取所有专业代码列表...")
    
    try:
        subjects_response = requests.get(subjects_url, headers=headers)
        subjects_response.raise_for_status()
        all_subjects = subjects_response.json()
        print(f"✅ 成功获取到 {len(all_subjects)} 个专业")
        return all_subjects
    except Exception as e:
        print(f"❌ 获取专业列表失败: {e}")
        return None

def get_all_terms():
    """获取所有可用学期"""
    terms_url = "https://openapi.data.uwaterloo.ca/v3/Terms"
    print("\n🔍 正在获取所有学期列表...")
    
    try:
        terms_response = requests.get(terms_url, headers=headers)
        terms_response.raise_for_status()
        all_terms = terms_response.json()
        print(f"✅ 成功获取学期列表，总共 {len(all_terms)} 个学期")
        return all_terms
    except Exception as e:
        print(f"❌ 获取学期列表失败: {e}")
        return None

def filter_terms(all_terms):
    """根据配置过滤学期"""
    # 确定启用的模式
    active_mode = None
    mode_name = ""
    
    if Config.MODE_RECOMMENDED['enabled']:
        active_mode = Config.MODE_RECOMMENDED
        mode_name = "推荐模式"
    elif Config.MODE_CUSTOM['enabled']:
        active_mode = Config.MODE_CUSTOM
        mode_name = "自定义模式"
    elif Config.MODE_ALL_HISTORICAL['enabled']:
        print(f"📅 {Config.MODE_ALL_HISTORICAL['description']} ({len(all_terms)} 个学期)")
        return all_terms
    elif Config.MODE_RECENT_ONLY['enabled']:
        active_mode = Config.MODE_RECENT_ONLY
        mode_name = "最新数据模式"
    elif Config.MODE_VERIFIED_COMPLETE['enabled']:
        active_mode = Config.MODE_VERIFIED_COMPLETE
        mode_name = "完整验证模式"
    else:
        # 默认使用推荐模式
        active_mode = Config.MODE_RECOMMENDED
        mode_name = "默认推荐模式"
        print("⚠️  没有启用任何模式，使用默认推荐模式")
    
    # 按年份范围过滤
    filtered_terms = []
    start_year = active_mode['start_year']
    end_year = active_mode['end_year']
    
    for term in all_terms:
        term_name = term.get("name", "")
        try:
            year = int(term_name.split()[-1]) if term_name else 0
            if start_year <= year <= end_year:
                filtered_terms.append(term)
        except:
            continue
    
    print(f"📅 {mode_name}: {active_mode['description']}")
    print(f"   年份范围: {start_year}-{end_year} ({len(filtered_terms)} 个学期)")
    return filtered_terms

def download_course_details(all_subjects, target_terms, course_raw_dir, course_filtered_dir):
    """下载所有课程详细信息，同时生成按课表过滤的数据"""
    print(f"\n📚 开始下载课程详细信息...")
    print(f"   专业数量: {len(all_subjects)}")
    print(f"   学期数量: {len(target_terms)}")
    print(f"   预计请求数: {len(all_subjects) * len(target_terms)}")
    
    total_courses_found = 0
    successful_requests = 0
    failed_requests = 0
    
    # 显示学期信息
    print(f"\n📋 目标学期:")
    for term in target_terms:
        print(f"   • {term.get('name', 'N/A')} (代码: {term.get('termCode', 'N/A')})")
    
    print(f"\n🚀 开始下载...")
    
    for i, subject_info in enumerate(all_subjects):
        subject_code = subject_info.get("code")
        print(f"\n📖 处理专业: {subject_code} ({i + 1}/{len(all_subjects)})")

        subject_total_courses = 0
        
        for j, term in enumerate(target_terms):
            term_code = term.get("termCode")
            term_name = term.get("name")
            
            courses_url = f"https://openapi.data.uwaterloo.ca/v3/Courses/{term_code}/{subject_code}"
            
            # 重试机制
            for retry in range(Config.MAX_RETRIES):
                try:
                    courses_response = requests.get(courses_url, headers=headers)
                    if courses_response.status_code == 200:
                        raw_course_data = courses_response.json()
                        
                        if raw_course_data:
                            # 根据配置过滤课程
                            if Config.INCLUDE_GRADUATE_ONLY:
                                # 只获取研究生课程
                                filtered_courses = [course for course in raw_course_data 
                                                  if course.get("associatedAcademicCareer") == "GRD"]
                            elif Config.INCLUDE_UNDERGRADUATE:
                                # 获取所有课程（本科 + 研究生）
                                filtered_courses = raw_course_data
                            else:
                                # 只包含研究生课程（fallback）
                                filtered_courses = [course for course in raw_course_data 
                                                  if course.get("associatedAcademicCareer") == "GRD"]
                            
                            if filtered_courses:
                                # 原始数据保存
                                raw_subject_dir = os.path.join(course_raw_dir, subject_code)
                                if not os.path.exists(raw_subject_dir):
                                    os.makedirs(raw_subject_dir)

                                raw_file_path = os.path.join(raw_subject_dir, f"{term_code}.json")
                                with open(raw_file_path, 'w', encoding='utf-8') as f:
                                    json.dump(filtered_courses, f, ensure_ascii=False, indent=2)

                                # 读取课表，按实际开课再过滤
                                schedule_ids = set()
                                schedule_path = os.path.join(Config.SCHEDULE_DIR, f"{term_code}.json")
                                if os.path.exists(schedule_path):
                                    try:
                                        with open(schedule_path, 'r', encoding='utf-8') as sf:
                                            schedule_ids = set(json.load(sf))
                                    except Exception:
                                        pass

                                filtered_by_schedule = [c for c in filtered_courses if c.get('courseId') in schedule_ids]

                                # 保存过滤后的数据
                                filt_subject_dir = os.path.join(course_filtered_dir, subject_code)
                                if not os.path.exists(filt_subject_dir):
                                    os.makedirs(filt_subject_dir)

                                filt_file_path = os.path.join(filt_subject_dir, f"{term_code}.json")
                                with open(filt_file_path, 'w', encoding='utf-8') as f:
                                    json.dump(filtered_by_schedule, f, ensure_ascii=False, indent=2)

                                subject_total_courses += len(filtered_courses)
                                total_courses_found += len(filtered_courses)

                                # 统计输出
                                course_type = "研究生" if Config.INCLUDE_GRADUATE_ONLY else "全部"
                                print(f"     ✅ {term_name}: 原始 {len(filtered_courses)} 条, 过滤后 {len(filtered_by_schedule)} 条 ({course_type}课程)")
                        
                        successful_requests += 1
                        break  # 成功，跳出重试循环
                        
                    elif courses_response.status_code == 404:
                        # 404通常表示该学期该专业没有课程，这是正常的
                        break
                    else:
                        if retry == Config.MAX_RETRIES - 1:
                            print(f"     ❌ {term_name}: HTTP {courses_response.status_code}")
                            failed_requests += 1
                        else:
                            time.sleep(1)  # 重试前等待
                        
                except Exception as e:
                    if retry == Config.MAX_RETRIES - 1:
                        print(f"     ❌ {term_name}: 错误 - {e}")
                        failed_requests += 1
                    else:
                        time.sleep(1)  # 重试前等待
            
            # 请求间隔
            time.sleep(Config.REQUEST_DELAY)
        
        if subject_total_courses > 0:
            print(f"   📊 {subject_code} 总计: {subject_total_courses} 门课程")
    
    print(f"\n📈 课程详情下载统计:")
    print(f"   ✅ 成功请求: {successful_requests}")
    print(f"   ❌ 失败请求: {failed_requests}")
    print(f"   📚 总课程数: {total_courses_found}")

def download_schedules(target_terms, schedule_data_dir):
    """下载课程表信息"""
    print(f"\n📅 开始下载课程表信息...")
    
    successful_schedules = 0
    total_schedule_records = 0
    
    for term in target_terms:
        term_code = term.get("termCode")
        term_name = term.get("name")

        print(f"\n📋 获取 {term_name} ({term_code}) 的课程表...")
        schedule_url = f"https://openapi.data.uwaterloo.ca/v3/ClassSchedules/{term_code}"

        # 重试机制
        for retry in range(Config.MAX_RETRIES):
            try:
                schedule_response = requests.get(schedule_url, headers=headers)
                if schedule_response.status_code == 200:
                    schedule_data = schedule_response.json()

                    if schedule_data:
                        file_path = os.path.join(schedule_data_dir, f"{term_code}.json")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(schedule_data, f, ensure_ascii=False, indent=2)
                        
                        record_count = len(schedule_data)
                        total_schedule_records += record_count
                        successful_schedules += 1
                        print(f"   ✅ 保存了 {record_count:,} 条开课记录")
                    else:
                        print(f"   ⚠️  该学期课程表为空")
                    break
                    
                elif schedule_response.status_code == 404:
                    print(f"   ⚠️  该学期暂无课程表数据")
                    break
                else:
                    if retry == Config.MAX_RETRIES - 1:
                        print(f"   ❌ HTTP {schedule_response.status_code}")
                    else:
                        time.sleep(1)
                        
            except Exception as e:
                if retry == Config.MAX_RETRIES - 1:
                    print(f"   ❌ 错误: {e}")
                else:
                    time.sleep(1)

        time.sleep(Config.REQUEST_DELAY)
    
    print(f"\n📈 课程表下载统计:")
    print(f"   ✅ 成功学期: {successful_schedules}/{len(target_terms)}")
    print(f"   📋 总记录数: {total_schedule_records:,}")

def save_metadata(all_terms, target_terms, all_subjects, course_raw_dir):
    """保存元数据信息"""
    metadata = {
        "download_timestamp": datetime.now().isoformat(),
        "config": {
            "mode_recommended": Config.MODE_RECOMMENDED,
            "mode_custom": Config.MODE_CUSTOM,
            "mode_all_historical": Config.MODE_ALL_HISTORICAL,
            "mode_recent_only": Config.MODE_RECENT_ONLY,
            "mode_verified_complete": Config.MODE_VERIFIED_COMPLETE,
            "graduate_only": Config.INCLUDE_GRADUATE_ONLY,
            "include_undergraduate": Config.INCLUDE_UNDERGRADUATE,
            "data_validation": "Based on schedule data verification"
        },
        "statistics": {
            "total_available_terms": len(all_terms),
            "downloaded_terms": len(target_terms),
            "total_subjects": len(all_subjects)
        },
        "terms_downloaded": [
            {
                "term_code": term.get("termCode"),
                "term_name": term.get("name")
            }
            for term in target_terms
        ],
        "subjects": [
            {
                "code": subject.get("code"),
                "name": subject.get("name", "")
            }
            for subject in all_subjects
        ]
    }
    
    metadata_file = os.path.join(course_raw_dir, "download_metadata.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"💾 元数据已保存到: {metadata_file}")

def main():
    """主函数"""
    print("🎓 滑铁卢大学课程数据批量获取工具 (全学期版)")
    print("=" * 80)
    
    # 显示配置
    print("⚙️  当前配置:")
    
    # 显示启用的模式
    active_modes = []
    if Config.MODE_RECOMMENDED['enabled']:
        active_modes.append(f"推荐模式 ({Config.MODE_RECOMMENDED['start_year']}-{Config.MODE_RECOMMENDED['end_year']})")
    if Config.MODE_CUSTOM['enabled']:
        active_modes.append(f"自定义模式 ({Config.MODE_CUSTOM['start_year']}-{Config.MODE_CUSTOM['end_year']})")
    if Config.MODE_ALL_HISTORICAL['enabled']:
        active_modes.append("完整历史模式 (1956-2029)")
    if Config.MODE_RECENT_ONLY['enabled']:
        active_modes.append(f"最新数据模式 ({Config.MODE_RECENT_ONLY['start_year']}-{Config.MODE_RECENT_ONLY['end_year']})")
    if Config.MODE_VERIFIED_COMPLETE['enabled']:
        active_modes.append(f"完整验证模式 ({Config.MODE_VERIFIED_COMPLETE['start_year']}-{Config.MODE_VERIFIED_COMPLETE['end_year']})")
    
    if not active_modes:
        active_modes.append("默认推荐模式 (2021-2025)")
    
    print(f"   📅 获取模式: {', '.join(active_modes)}")
    # 确定课程类型描述
    if Config.INCLUDE_GRADUATE_ONLY:
        course_type_desc = "仅研究生课程"
    elif Config.INCLUDE_UNDERGRADUATE:
        course_type_desc = "所有课程（本科 + 研究生）"
    else:
        course_type_desc = "仅研究生课程（默认）"
    
    print(f"   🎓 课程类型: {course_type_desc}")
    print(f"   📁 输出目录: {Config.OUTPUT_BASE_DIR}")
    print(f"   ⏱️  请求间隔: {Config.REQUEST_DELAY}秒")
    
    # 设置输出目录
    course_raw_dir, course_filtered_dir, schedule_data_dir = setup_directories()
    
    # 获取基础数据
    all_subjects = get_all_subjects()
    if not all_subjects:
        print("❌ 无法获取专业列表，程序终止")
        return
    
    all_terms = get_all_terms()
    if not all_terms:
        print("❌ 无法获取学期列表，程序终止")
        return
    
    # 过滤学期
    target_terms = filter_terms(all_terms)
    if not target_terms:
        print("❌ 没有符合条件的学期，程序终止")
        return
    
    print(f"\n🎯 准备下载:")
    print(f"   📚 专业: {len(all_subjects)} 个")
    print(f"   📅 学期: {len(target_terms)} 个")
    print(f"   🔢 总请求: ~{len(all_subjects) * len(target_terms)} 个")
    
    # 询问用户确认
    response = input(f"\n是否继续下载？[y/N]: ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ 用户取消操作")
        return
    
    start_time = datetime.now()
    print(f"\n🚀 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 先下载课程表（用于后续过滤）
    download_schedules(target_terms, schedule_data_dir)

    # 再下载课程详情（会根据课表生成过滤数据）
    download_course_details(all_subjects, target_terms, course_raw_dir, course_filtered_dir)
    
    # 保存元数据（放在原始数据目录下）
    save_metadata(all_terms, target_terms, all_subjects, course_raw_dir)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print("✅ 所有数据下载完毕！")
    print(f"⏱️  总耗时: {duration}")
    print(f"📁 课程数据保存在: {course_raw_dir}")
    print(f"📅 课程表保存在: {schedule_data_dir}")

if __name__ == "__main__":
    main() 