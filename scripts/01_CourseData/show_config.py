#!/usr/bin/python3
# coding=utf-8
"""
配置显示脚本 - 显示当前数据收集配置
"""

def show_current_config():
    """显示当前的数据收集配置"""
    print("🎓 滑铁卢大学课程数据收集 - 当前配置")
    print("=" * 60)
    print()
    
    print("📋 配置更改总结:")
    print("   ✅ INCLUDE_GRADUATE_ONLY = False  (已修改)")
    print("   ✅ INCLUDE_UNDERGRADUATE = True   (已修改)")
    print()
    
    print("🎯 新配置的优势:")
    print("   📚 包含所有课程类型（本科 + 研究生）")
    print("   🔄 支持未来扩展到本科生推荐")
    print("   🔗 完整的先修课程依赖网络")
    print("   📈 更全面的学习路径分析")
    print("   🎓 研究生可选择合适的本科课程")
    print()
    
    print("📊 预期数据量（2021-2025年）:")
    print("   • 学期数量: 15 个学期")
    print("   • 专业数量: 258 个专业")
    print("   • 课程类型: 本科课程 + 研究生课程")
    print("   • 数据验证: 基于实际课程表")
    print()
    
    print("🚀 运行数据收集:")
    print("   python 01_GetData_AllTerms.py")
    print()
    print("📁 输出目录:")
    print("   course_data_comprehensive/all_courses/  (所有课程)")
    print("   schedule_data_comprehensive/            (课程表数据)")
    print()

if __name__ == "__main__":
    show_current_config() 