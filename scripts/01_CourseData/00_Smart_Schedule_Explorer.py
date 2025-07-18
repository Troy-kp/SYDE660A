#!/usr/bin/python3
# coding=utf-8
# author troy

import requests
import json
from datetime import datetime
from collections import defaultdict

# --- 您的API密钥 ---
api_key = "82EE1A91C80C48168A2B7156862DE865"
headers = {'x-api-key': api_key}

def explore_schedule_data_availability():
    """
    智能探索：基于课程表数据验证学期的真实有效性
    
    课程表数据才是验证课程实际开课的标准！
    这个函数会：
    1. 获取所有学期列表
    2. 验证每个学期的课程表数据可用性
    3. 找到最远可以获取到的有效学期
    4. 生成基于实际数据的推荐配置
    """
    print("🔍 智能探索：基于课程表验证学期数据有效性")
    print("=" * 80)
    print("💡 理念：课程表数据才是验证课程实际开课的标准！")
    print()
    
    # 获取所有学期列表
    terms_url = "https://openapi.data.uwaterloo.ca/v3/Terms"
    
    try:
        print(f"📡 正在获取学期列表...")
        terms_response = requests.get(terms_url, headers=headers)
        terms_response.raise_for_status()
        all_terms = terms_response.json()
        
        print(f"✅ 成功获取 {len(all_terms)} 个学期")
        print()
        
        # 按年份分组和排序
        terms_by_year = defaultdict(list)
        for term in all_terms:
            term_name = term.get("name", "")
            try:
                year = int(term_name.split()[-1]) if term_name else 0
                if year > 1900:  # 确保是有效年份
                    terms_by_year[year].append(term)
            except:
                continue
        
        # 验证课程表数据的有效性
        print("🧪 开始验证课程表数据可用性...")
        print("   (这是判断学期是否真正有效的关键指标)")
        print()
        
        valid_terms = []
        invalid_terms = []
        year_validity = {}
        
        # 按年份从新到旧检查（优先检查最近的数据）
        for year in sorted(terms_by_year.keys(), reverse=True):
            print(f"📅 检查 {year} 年:")
            year_valid_count = 0
            year_total_count = len(terms_by_year[year])
            
            for term in terms_by_year[year]:
                term_code = term.get("termCode")
                term_name = term.get("name")
                
                # 检查课程表数据
                schedule_url = f"https://openapi.data.uwaterloo.ca/v3/ClassSchedules/{term_code}"
                
                try:
                    schedule_response = requests.get(schedule_url, headers=headers)
                    if schedule_response.status_code == 200:
                        schedule_data = schedule_response.json()
                        
                        if schedule_data and len(schedule_data) > 0:
                            # 有真实的课程表数据
                            valid_terms.append(term)
                            year_valid_count += 1
                            print(f"   ✅ {term_name:<15} - {len(schedule_data):>5,} 条开课记录")
                        else:
                            # 没有课程表数据
                            invalid_terms.append(term)
                            print(f"   ❌ {term_name:<15} - 空课程表")
                    else:
                        # API 错误
                        invalid_terms.append(term)
                        print(f"   ❌ {term_name:<15} - HTTP {schedule_response.status_code}")
                        
                except Exception as e:
                    invalid_terms.append(term)
                    print(f"   ❌ {term_name:<15} - 错误: {e}")
            
            year_validity[year] = {
                'valid_count': year_valid_count,
                'total_count': year_total_count,
                'validity_rate': year_valid_count / year_total_count if year_total_count > 0 else 0
            }
            
            print(f"   📊 {year} 年有效性: {year_valid_count}/{year_total_count} ({year_validity[year]['validity_rate']:.1%})")
            print()
        
        # 分析结果
        print("=" * 80)
        print("📊 数据有效性分析结果")
        print("=" * 80)
        
        # 找到有效的年份范围
        valid_years = [year for year, data in year_validity.items() if data['validity_rate'] > 0]
        if valid_years:
            earliest_valid_year = min(valid_years)
            latest_valid_year = max(valid_years)
            
            print(f"✅ 有效年份范围: {earliest_valid_year} - {latest_valid_year}")
            print(f"📈 有效学期总数: {len(valid_terms)}")
            print(f"📉 无效学期总数: {len(invalid_terms)}")
            print(f"🎯 整体有效率: {len(valid_terms)/(len(valid_terms)+len(invalid_terms)):.1%}")
            print()
            
            # 找到最佳的数据获取范围
            print("💡 推荐的数据获取策略:")
            print()
            
            # 策略1: 最近5年（高质量数据）
            recent_years = [y for y in valid_years if y >= max(valid_years) - 4]
            if recent_years:
                recent_start = min(recent_years)
                recent_end = max(recent_years)
                recent_terms = [t for t in valid_terms 
                              if recent_start <= int(t.get("name", "").split()[-1]) <= recent_end]
                print(f"📈 策略1 - 最近数据 ({recent_start}-{recent_end}):")
                print(f"   年份范围: {recent_start} - {recent_end}")
                print(f"   有效学期: {len(recent_terms)} 个")
                print(f"   适用场景: 推荐系统、趋势分析")
                print()
            
            # 策略2: 完整有效范围（全面数据）
            comprehensive_terms = valid_terms
            print(f"🔍 策略2 - 完整有效数据 ({earliest_valid_year}-{latest_valid_year}):")
            print(f"   年份范围: {earliest_valid_year} - {latest_valid_year}")
            print(f"   有效学期: {len(comprehensive_terms)} 个")
            print(f"   适用场景: 历史分析、完整数据集")
            print()
            
            # 策略3: 未来规划范围
            future_years = [y for y in valid_years if y >= datetime.now().year]
            if future_years:
                future_start = min(future_years)
                future_end = max(future_years)
                future_terms = [t for t in valid_terms 
                              if future_start <= int(t.get("name", "").split()[-1]) <= future_end]
                print(f"🚀 策略3 - 未来规划 ({future_start}-{future_end}):")
                print(f"   年份范围: {future_start} - {future_end}")
                print(f"   有效学期: {len(future_terms)} 个")
                print(f"   适用场景: 课程规划、学期安排")
                print()
            
            # 生成配置建议
            print("⚙️  建议的配置设置:")
            print()
            print("```python")
            print("# 在 01_GetData_AllTerms.py 中的 Config 类:")
            print()
            
            if recent_years:
                print(f"# 策略1: 最近数据（推荐）")
                print(f"MODE_RECOMMENDED = {{")
                print(f"    'enabled': True,")
                print(f"    'start_year': {recent_start},")
                print(f"    'end_year': {recent_end},")
                print(f"    'description': '基于实际课程表验证的最近有效数据'")
                print(f"}}")
                print()
            
            print(f"# 策略2: 自定义范围")
            print(f"MODE_CUSTOM = {{")
            print(f"    'enabled': False,")
            print(f"    'start_year': {earliest_valid_year},  # 最早有效年份")
            print(f"    'end_year': {latest_valid_year},    # 最新有效年份")
            print(f"    'description': '完整的有效数据范围'")
            print(f"}}")
            print("```")
            
        else:
            print("❌ 没有找到任何有效的课程表数据！")
            print("   请检查API密钥或网络连接")
        
        # 保存详细分析结果
        analysis_results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "methodology": "基于课程表数据验证学期有效性",
            "total_terms_checked": len(all_terms),
            "valid_terms": len(valid_terms),
            "invalid_terms": len(invalid_terms),
            "validity_rate": len(valid_terms)/(len(valid_terms)+len(invalid_terms)) if (len(valid_terms)+len(invalid_terms)) > 0 else 0,
            "year_validity": year_validity,
            "valid_terms_details": [
                {
                    "term_code": term.get("termCode"),
                    "term_name": term.get("name"),
                    "year": int(term.get("name", "").split()[-1]) if term.get("name") else None
                }
                for term in valid_terms
            ],
            "recommended_ranges": {
                "recent_data": {
                    "start_year": recent_start if 'recent_start' in locals() else None,
                    "end_year": recent_end if 'recent_end' in locals() else None,
                    "terms_count": len(recent_terms) if 'recent_terms' in locals() else 0
                },
                "comprehensive": {
                    "start_year": earliest_valid_year if 'earliest_valid_year' in locals() else None,
                    "end_year": latest_valid_year if 'latest_valid_year' in locals() else None,
                    "terms_count": len(valid_terms)
                }
            }
        }
        
        output_file = "schedule_data_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细分析结果已保存到: {output_file}")
        
        return valid_terms, year_validity
        
    except Exception as e:
        print(f"❌ 探索失败: {e}")
        return None, None

def recommend_optimal_configuration(valid_terms, year_validity):
    """基于分析结果推荐最优配置"""
    if not valid_terms or not year_validity:
        return
    
    print("\n" + "=" * 80)
    print("🎯 最优配置推荐")
    print("=" * 80)
    
    # 分析数据质量
    current_year = datetime.now().year
    recent_years = [year for year in year_validity.keys() 
                   if year >= current_year - 3 and year_validity[year]['validity_rate'] > 0.5]
    
    if recent_years:
        recommended_start = min(recent_years)
        recommended_end = max(year_validity.keys())
        
        print(f"✨ 推荐配置:")
        print(f"   开始年份: {recommended_start}")
        print(f"   结束年份: {recommended_end}")
        print(f"   理由: 包含最近高质量数据并覆盖未来规划")
        print()
        
        # 计算预期数据量
        expected_terms = [t for t in valid_terms 
                         if recommended_start <= int(t.get("name", "").split()[-1]) <= recommended_end]
        
        print(f"📊 预期数据量:")
        print(f"   有效学期: {len(expected_terms)} 个")
        print(f"   年份跨度: {recommended_end - recommended_start + 1} 年")
        print(f"   数据质量: 基于实际课程表验证")

if __name__ == "__main__":
    print("🎓 滑铁卢大学智能数据探索工具")
    print("🔍 基于课程表数据验证学期有效性")
    print("=" * 80)
    
    # 执行智能探索
    valid_terms, year_validity = explore_schedule_data_availability()
    
    if valid_terms:
        # 推荐最优配置
        recommend_optimal_configuration(valid_terms, year_validity)
        
        print("\n" + "=" * 80)
        print("✅ 智能探索完成！")
        print("📋 下一步:")
        print("   1. 根据推荐配置修改 01_GetData_AllTerms.py")
        print("   2. 运行数据获取脚本")
        print("   3. 获得基于实际开课数据的高质量数据集")
    else:
        print("❌ 探索失败，请检查API密钥和网络连接") 