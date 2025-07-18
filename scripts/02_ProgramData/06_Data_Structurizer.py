#!/usr/bin/python3
# coding=utf-8
# author troy

import json
import re
from datetime import datetime
from collections import defaultdict
import logging
import sys

class ProgramDataStructurizer:
    """
    专业要求数据结构化处理器
    清理、标准化和结构化从学术日历爬取的原始数据
    """
    
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 标准化映射
        self.degree_type_mapping = {
            'masc': 'MASc',
            'meng': 'MEng', 
            'msc': 'MSc',
            'phd': 'PhD',
            'march': 'MArch',
            'mmath': 'MMath'
        }
        
        self.faculty_mapping = {
            'engineering': 'Faculty of Engineering',
            'mathematics': 'Faculty of Mathematics',
            'science': 'Faculty of Science',
            'arts': 'Faculty of Arts',
            'environment': 'Faculty of Environment'
        }
        
    def clean_text(self, text):
        """清理文本内容"""
        if not text or not isinstance(text, str):
            return ""
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 移除HTML实体
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        
        # 移除JavaScript片段
        text = re.sub(r'\{["\']path["\'].*?\}', '', text)
        
        return text
    
    def extract_course_codes(self, text):
        """从文本中提取课程代码"""
        if not text:
            return []
        
        course_pattern = r'\b[A-Z]{2,6}\s*\d{3}[A-Z]?\b'
        courses = re.findall(course_pattern, text.upper())
        
        # 标准化格式
        standardized = []
        for course in courses:
            # 移除空格并重新格式化
            course = re.sub(r'\s+', ' ', course.strip())
            standardized.append(course)
        
        return list(set(standardized))  # 去重
    
    def categorize_requirements(self, requirements_list):
        """分类专业要求"""
        categorized = {
            'core_courses': [],
            'elective_courses': [],
            'credit_requirements': [],
            'prerequisite_courses': [],
            'general_requirements': []
        }
        
        for req in requirements_list:
            if not isinstance(req, dict):
                continue
                
            req_type = req.get('type', '').lower()
            content = req.get('description', '') or req.get('content', '')
            courses = self.extract_course_codes(content)
            
            # 分类逻辑
            content_lower = content.lower()
            
            if any(word in content_lower for word in ['core', 'required', 'mandatory', 'must take']):
                categorized['core_courses'].append({
                    'description': self.clean_text(content),
                    'courses': courses,
                    'type': 'core'
                })
            elif any(word in content_lower for word in ['elective', 'optional', 'choose', 'select']):
                categorized['elective_courses'].append({
                    'description': self.clean_text(content),
                    'courses': courses,
                    'type': 'elective'
                })
            elif any(word in content_lower for word in ['credit', 'unit', 'hour']):
                categorized['credit_requirements'].append({
                    'description': self.clean_text(content),
                    'courses': courses,
                    'type': 'credit'
                })
            elif any(word in content_lower for word in ['prerequisite', 'background', 'prior']):
                categorized['prerequisite_courses'].append({
                    'description': self.clean_text(content),
                    'courses': courses,
                    'type': 'prerequisite'
                })
            else:
                categorized['general_requirements'].append({
                    'description': self.clean_text(content),
                    'courses': courses,
                    'type': 'general'
                })
        
        return categorized
    
    def extract_numeric_requirements(self, text):
        """提取数值要求（学分、GPA等）"""
        requirements = {}
        
        if not text:
            return requirements
        
        # 学分要求
        credit_patterns = [
            r'(\d+(?:\.\d+)?)\s*credits?',
            r'(\d+(?:\.\d+)?)\s*units?',
            r'(\d+)\s*courses?'
        ]
        
        for pattern in credit_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                requirements['credits'] = {
                    'value': float(match.group(1)),
                    'unit': 'credits' if 'credit' in pattern else 'courses',
                    'description': match.group(0)
                }
                break
        
        # GPA要求
        gpa_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:gpa|average)',
            r'(?:gpa|average).*?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)%'
        ]
        
        for pattern in gpa_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                gpa_value = float(match.group(1))
                # 转换百分制到4.0制
                if gpa_value > 4.0:
                    gpa_value = gpa_value / 100 * 4.0
                
                requirements['gpa'] = {
                    'value': gpa_value,
                    'description': match.group(0)
                }
                break
        
        # 时长要求
        duration_patterns = [
            r'(\d+)\s*years?',
            r'(\d+)\s*terms?',
            r'(\d+)\s*months?',
            r'(\d+)\s*semesters?'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                requirements['duration'] = {
                    'value': int(match.group(1)),
                    'unit': match.group(0).split()[-1].lower(),
                    'description': match.group(0)
                }
                break
        
        return requirements
    
    def standardize_program_data(self, raw_program):
        """标准化单个专业的数据"""
        try:
            standardized = {
                'program_id': self._generate_program_id(raw_program),
                'basic_info': self._extract_basic_info(raw_program),
                'requirements': self._extract_requirements(raw_program),
                'specializations': self._extract_specializations(raw_program),
                'application_info': self._extract_application_info(raw_program),
                'metadata': self._extract_metadata(raw_program)
            }
            
            return standardized
            
        except Exception as e:
            self.logger.error(f"标准化专业数据失败: {e}")
            return None
    
    def _generate_program_id(self, program):
        """生成唯一的专业ID"""
        name = program.get('program_name', '')
        degree = program.get('degree_type', '')
        
        # 清理名称
        clean_name = re.sub(r'[^\w\s]', '', name).replace(' ', '_').lower()
        clean_degree = degree.lower()
        
        return f"{clean_name}_{clean_degree}"
    
    def _extract_basic_info(self, program):
        """提取基本信息"""
        return {
            'program_name': self.clean_text(program.get('program_name', '')),
            'degree_type': self._standardize_degree_type(program.get('degree_type', '')),
            'academic_level': program.get('academic_level', ''),
            'faculty': self._standardize_faculty(program.get('faculty_info', {})),
            'duration': program.get('duration'),
            'program_url': program.get('program_url', ''),
            'description': self._extract_program_description(program)
        }
    
    def _extract_requirements(self, program):
        """提取并分类要求信息"""
        # 合并所有要求相关信息
        all_requirements = []
        
        # 添加入学要求
        admission_reqs = program.get('admission_requirements', [])
        if isinstance(admission_reqs, list):
            all_requirements.extend(admission_reqs)
        
        # 添加课程要求
        course_reqs = program.get('course_requirements', [])
        if isinstance(course_reqs, list):
            all_requirements.extend(course_reqs)
        
        # 添加学位要求
        degree_reqs = program.get('degree_requirements', {})
        if isinstance(degree_reqs, dict):
            for key, value in degree_reqs.items():
                all_requirements.append({
                    'type': key,
                    'description': str(value),
                    'content': str(value)
                })
        
        # 分类要求
        categorized = self.categorize_requirements(all_requirements)
        
        # 提取数值要求
        all_text = ' '.join([str(req) for req in all_requirements])
        numeric_reqs = self.extract_numeric_requirements(all_text)
        
        return {
            'categorized_requirements': categorized,
            'numeric_requirements': numeric_reqs,
            'all_courses': self._extract_all_courses(all_requirements)
        }
    
    def _extract_specializations(self, program):
        """提取专业方向信息"""
        specs = program.get('specializations', [])
        if not isinstance(specs, list):
            return []
        
        cleaned_specs = []
        for spec in specs:
            if isinstance(spec, dict):
                cleaned_spec = {
                    'name': self.clean_text(spec.get('name', '')),
                    'description': self.clean_text(spec.get('description', '')),
                    'type': spec.get('type', ''),
                    'courses': self.extract_course_codes(spec.get('description', ''))
                }
                
                # 过滤掉过短或无意义的专业方向
                if len(cleaned_spec['name']) > 10 and 'javascript' not in cleaned_spec['name'].lower():
                    cleaned_specs.append(cleaned_spec)
        
        return cleaned_specs
    
    def _extract_application_info(self, program):
        """提取申请信息"""
        app_info = program.get('application_info', {})
        funding_info = program.get('funding_info', [])
        
        return {
            'application_deadlines': app_info.get('deadline', ''),
            'funding_opportunities': [
                {
                    'type': fund.get('type', ''),
                    'description': self.clean_text(fund.get('description', ''))
                }
                for fund in funding_info if isinstance(fund, dict)
            ]
        }
    
    def _extract_metadata(self, program):
        """提取元数据"""
        return {
            'source': program.get('source', 'academic_calendar'),
            'scraped_timestamp': program.get('scraped_timestamp', ''),
            'last_updated': datetime.now().isoformat(),
            'data_quality_score': self._calculate_quality_score(program)
        }
    
    def _standardize_degree_type(self, degree):
        """标准化学位类型"""
        if not degree:
            return 'Unknown'
        
        degree_lower = degree.lower().strip()
        return self.degree_type_mapping.get(degree_lower, degree)
    
    def _standardize_faculty(self, faculty_info):
        """标准化学院信息"""
        if isinstance(faculty_info, dict):
            faculty = faculty_info.get('faculty', '')
        else:
            faculty = str(faculty_info)
        
        faculty_lower = faculty.lower()
        for key, value in self.faculty_mapping.items():
            if key in faculty_lower:
                return value
        
        return faculty
    
    def _extract_program_description(self, program):
        """提取专业描述"""
        # 尝试从多个字段中提取描述
        possible_descriptions = [
            program.get('description', ''),
            program.get('program_overview', ''),
            ' '.join([spec.get('description', '') for spec in program.get('specializations', []) if isinstance(spec, dict)])
        ]
        
        for desc in possible_descriptions:
            clean_desc = self.clean_text(desc)
            if len(clean_desc) > 50 and 'javascript' not in clean_desc.lower():
                return clean_desc[:500]  # 限制长度
        
        return ''
    
    def _extract_all_courses(self, requirements):
        """提取所有课程代码"""
        all_courses = set()
        
        for req in requirements:
            if isinstance(req, dict):
                content = req.get('description', '') or req.get('content', '')
                courses = self.extract_course_codes(content)
                all_courses.update(courses)
        
        return sorted(list(all_courses))
    
    def _calculate_quality_score(self, program):
        """计算数据质量分数"""
        score = 0
        
        # 基本信息完整性
        if program.get('program_name'):
            score += 20
        if program.get('degree_type'):
            score += 15
        if program.get('program_url'):
            score += 10
        
        # 要求信息完整性
        if program.get('course_requirements'):
            score += 20
        if program.get('admission_requirements'):
            score += 15
        if program.get('degree_requirements'):
            score += 10
        
        # 额外信息
        if program.get('specializations'):
            score += 5
        if program.get('duration'):
            score += 3
        if program.get('research_areas'):
            score += 2
        
        return min(score, 100)
    
    def process_batch(self, raw_data_file, output_file):
        """批量处理专业数据"""
        try:
            self.logger.info(f"🔄 开始处理数据文件: {raw_data_file}")
            
            # 读取原始数据
            with open(raw_data_file, 'r', encoding='utf-8') as f:
                raw_programs = json.load(f)
            
            if not isinstance(raw_programs, list):
                self.logger.error("输入数据格式错误，期望列表格式")
                return False
            
            # 处理数据
            structured_programs = []
            processed_count = 0
            
            for program in raw_programs:
                structured = self.standardize_program_data(program)
                if structured:
                    structured_programs.append(structured)
                    processed_count += 1
                    
                    if processed_count % 10 == 0:
                        self.logger.info(f"已处理: {processed_count}/{len(raw_programs)}")
            
            # 生成统计报告
            stats = self._generate_statistics(structured_programs)
            
            # 保存结果
            output_data = {
                'programs': structured_programs,
                'statistics': stats,
                'metadata': {
                    'total_programs': len(structured_programs),
                    'processed_timestamp': datetime.now().isoformat(),
                    'source_file': raw_data_file
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ 处理完成！")
            self.logger.info(f"📊 总计处理: {len(structured_programs)} 个专业")
            self.logger.info(f"💾 结果保存到: {output_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 批量处理失败: {e}")
            return False
    
    def _generate_statistics(self, programs):
        """生成统计信息"""
        stats = {
            'degree_distribution': defaultdict(int),
            'faculty_distribution': defaultdict(int),
            'avg_quality_score': 0,
            'total_courses_found': 0,
            'specializations_count': 0
        }
        
        total_quality = 0
        all_courses = set()
        
        for program in programs:
            # 学位分布
            degree = program['basic_info']['degree_type']
            stats['degree_distribution'][degree] += 1
            
            # 学院分布
            faculty = program['basic_info']['faculty']
            stats['faculty_distribution'][faculty] += 1
            
            # 质量分数
            quality = program['metadata']['data_quality_score']
            total_quality += quality
            
            # 课程统计
            courses = program['requirements']['all_courses']
            all_courses.update(courses)
            
            # 专业方向统计
            specs = program['specializations']
            stats['specializations_count'] += len(specs)
        
        # 计算平均值
        if programs:
            stats['avg_quality_score'] = total_quality / len(programs)
        
        stats['total_courses_found'] = len(all_courses)
        
        # 转换为普通字典
        stats['degree_distribution'] = dict(stats['degree_distribution'])
        stats['faculty_distribution'] = dict(stats['faculty_distribution'])
        
        return stats

def main():
    """主函数"""
    print("📊 专业要求数据结构化处理器")
    print("=" * 50)
    
    structurizer = ProgramDataStructurizer()
    
    # 检查命令行参数
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        # 自动寻找最新的增强版程序文件
        import glob
        
        enhanced_files = glob.glob("enhanced_programs_*.json")
        if enhanced_files:
            # 选择最新的文件
            input_file = max(enhanced_files)
            output_file = "structured_program_requirements_final.json"
            print(f"🔍 自动发现文件: {input_file}")
        else:
            print("❌ 未找到输入文件，请提供文件名参数")
            print("用法: python 06_Data_Structurizer.py <input_file> <output_file>")
            return
    
    print(f"📄 输入文件: {input_file}")
    print(f"📄 输出文件: {output_file}")
    
    success = structurizer.process_batch(input_file, output_file)
    
    if success:
        print("✅ 数据结构化完成！")
    else:
        print("❌ 数据结构化失败")

if __name__ == "__main__":
    main() 