#!/usr/bin/python3
# coding=utf-8
# author troy

import json
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import logging

class AcademicCalendarScraper:
    """
    高级学术日历爬取器
    专门处理滑铁卢大学JavaScript渲染的学术日历网站
    """
    
    def __init__(self, headless=True):
        self.base_url = "https://uwaterloo.ca/academic-calendar/graduate-studies/catalog#/programs"
        self.headless = headless
        self.driver = None
        self.wait = None
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 数据存储
        self.programs_data = []
        
    def setup_driver(self):
        """设置Chrome WebDriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            
            self.logger.info("✅ Chrome WebDriver 设置成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ WebDriver 设置失败: {e}")
            return False
    
    def wait_for_page_load(self, timeout=20):
        """等待页面完全加载"""
        try:
            # 等待页面基本元素加载
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 等待JavaScript渲染完成
            time.sleep(3)
            
            # 检查是否还在loading状态
            loading_indicators = ["Loading", "loading", "spinner"]
            max_attempts = 10
            
            for attempt in range(max_attempts):
                page_text = self.driver.page_source.lower()
                if not any(indicator.lower() in page_text for indicator in loading_indicators):
                    break
                time.sleep(2)
                
            self.logger.info("✅ 页面加载完成")
            return True
            
        except TimeoutException:
            self.logger.warning("⚠️ 页面加载超时，但继续执行")
            return False
    
    def extract_programs_list(self):
        """提取所有专业项目的基本信息"""
        try:
            self.logger.info("🔍 开始提取专业项目列表...")
            
            # 等待页面元素加载
            time.sleep(5)
            
            # 获取页面源代码并解析
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 查找专业项目链接的多种可能选择器
            program_selectors = [
                'a[href*="/programs/"]',
                'a[href*="graduate"]',
                '.program-link',
                '.program-item a',
                '[data-program]',
                'a[href*="masc"]',
                'a[href*="meng"]', 
                'a[href*="phd"]'
            ]
            
            programs_found = set()
            
            for selector in program_selectors:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href', '')
                    text = element.get_text(strip=True)
                    
                    if href and text and len(text) > 5:
                        # 构建完整URL
                        if href.startswith('/'):
                            full_url = f"https://uwaterloo.ca{href}"
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                            
                        # 过滤相关的研究生项目
                        if any(keyword in text.lower() for keyword in ['master', 'phd', 'doctorate', 'graduate', 'msc', 'masc', 'meng']):
                            programs_found.add((text, full_url))
            
            # 转换为列表并添加基本信息
            for program_name, program_url in programs_found:
                program_info = {
                    'program_name': program_name,
                    'program_url': program_url,
                    'discovery_timestamp': datetime.now().isoformat(),
                    'source': 'academic_calendar'
                }
                self.programs_data.append(program_info)
            
            self.logger.info(f"✅ 发现 {len(programs_found)} 个专业项目")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 提取专业列表失败: {e}")
            return False
    
    def scrape_program_details(self, program_info):
        """爬取单个专业的详细信息"""
        try:
            program_name = program_info['program_name']
            program_url = program_info['program_url']
            
            self.logger.info(f"📚 爬取专业详情: {program_name}")
            
            # 访问专业详情页面
            self.driver.get(program_url)
            self.wait_for_page_load()
            
            # 解析页面内容
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 提取详细信息
            details = {
                'program_name': program_name,
                'program_url': program_url,
                'degree_type': self._extract_degree_type(soup, program_name),
                'academic_level': self._extract_academic_level(soup, program_name),
                'duration': self._extract_duration(soup),
                'admission_requirements': self._extract_admission_requirements(soup),
                'course_requirements': self._extract_course_requirements(soup),
                'specializations': self._extract_specializations(soup),
                'certificates': self._extract_certificates(soup),
                'degree_requirements': self._extract_degree_requirements(soup),
                'research_areas': self._extract_research_areas(soup),
                'faculty_info': self._extract_faculty_info(soup),
                'application_info': self._extract_application_info(soup),
                'funding_info': self._extract_funding_info(soup),
                'scraped_timestamp': datetime.now().isoformat()
            }
            
            return details
            
        except Exception as e:
            self.logger.error(f"❌ 爬取 {program_name} 详情失败: {e}")
            return None
    
    def _extract_degree_type(self, soup, program_name):
        """提取学位类型"""
        degree_patterns = {
            'MASc': r'master.*applied.*science|masc',
            'MEng': r'master.*engineering|meng',
            'MSc': r'master.*science|msc',
            'PhD': r'phd|doctorate|doctor',
            'MArch': r'master.*architecture',
            'MMath': r'master.*mathematics'
        }
        
        text = soup.get_text().lower()
        program_name_lower = program_name.lower()
        
        for degree, pattern in degree_patterns.items():
            if re.search(pattern, text) or re.search(pattern, program_name_lower):
                return degree
        
        return 'Unknown'
    
    def _extract_academic_level(self, soup, program_name):
        """提取学术层次"""
        text = soup.get_text().lower()
        if 'phd' in text or 'doctorate' in text:
            return 'Doctoral'
        elif 'master' in text or any(deg in text for deg in ['masc', 'meng', 'msc']):
            return 'Master'
        return 'Unknown'
    
    def _extract_duration(self, soup):
        """提取项目时长"""
        text = soup.get_text()
        
        # 查找时长模式
        duration_patterns = [
            r'(\d+)\s*years?',
            r'(\d+)\s*terms?',
            r'(\d+)\s*months?',
            r'(\d+)\s*semesters?'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return {
                    'value': int(match.group(1)),
                    'unit': match.group(0).split()[-1].lower(),
                    'raw_text': match.group(0)
                }
        
        return None
    
    def _extract_admission_requirements(self, soup):
        """提取入学要求"""
        requirements = []
        
        # 查找包含入学要求的章节
        admission_keywords = ['admission', 'requirement', 'prerequisite', 'eligibility']
        
        for keyword in admission_keywords:
            sections = soup.find_all(text=re.compile(keyword, re.I))
            for section in sections[:3]:  # 限制结果数量
                parent = section.parent if hasattr(section, 'parent') else None
                if parent:
                    # 获取父级元素的更大范围文本
                    for ancestor in [parent, parent.parent, parent.parent.parent if parent.parent else None]:
                        if ancestor and ancestor.name:
                            text = ancestor.get_text(strip=True)
                            if len(text) > 50 and len(text) < 1000:
                                requirements.append({
                                    'type': keyword,
                                    'content': text[:500],  # 限制长度
                                    'source_tag': ancestor.name
                                })
                                break
        
        return requirements[:5]  # 最多返回5个要求
    
    def _extract_course_requirements(self, soup):
        """提取课程要求"""
        requirements = []
        course_pattern = r'\b[A-Z]{2,6}\s*\d{3}[A-Z]?\b'
        
        # 查找包含课程代码的文本
        text_elements = soup.find_all(['p', 'div', 'li', 'td'])
        
        for element in text_elements:
            text = element.get_text()
            courses = re.findall(course_pattern, text)
            
            if courses and len(text) > 20:
                # 判断要求类型
                req_type = 'general'
                lower_text = text.lower()
                
                if any(word in lower_text for word in ['core', 'required', 'mandatory', 'must']):
                    req_type = 'core'
                elif any(word in lower_text for word in ['elective', 'optional', 'choose', 'select']):
                    req_type = 'elective'
                elif any(word in lower_text for word in ['credit', 'unit']):
                    req_type = 'credit'
                
                requirements.append({
                    'type': req_type,
                    'courses': list(set(courses)),  # 去重
                    'description': text[:300],  # 限制描述长度
                    'course_count': len(set(courses))
                })
        
        return requirements[:10]  # 最多返回10个要求
    
    def _extract_specializations(self, soup):
        """提取专业方向信息"""
        specializations = []
        spec_keywords = ['specialization', 'concentration', 'track', 'area', 'option', 'stream']
        
        for keyword in spec_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.I))
            for element in elements[:5]:
                parent = element.parent if hasattr(element, 'parent') else None
                if parent:
                    text = parent.get_text(strip=True)
                    if 20 < len(text) < 500:
                        specializations.append({
                            'name': text[:100],
                            'type': keyword,
                            'description': text,
                            'keyword_matched': keyword
                        })
        
        return specializations
    
    def _extract_certificates(self, soup):
        """提取证书信息"""
        certificates = []
        cert_keywords = ['certificate', 'diploma', 'certification']
        
        for keyword in cert_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.I))
            for element in elements[:3]:
                parent = element.parent if hasattr(element, 'parent') else None
                if parent:
                    text = parent.get_text(strip=True)
                    if 20 < len(text) < 300:
                        certificates.append({
                            'name': text[:100],
                            'description': text,
                            'type': keyword
                        })
        
        return certificates
    
    def _extract_degree_requirements(self, soup):
        """提取学位要求"""
        text = soup.get_text()
        requirements = {}
        
        # 学分要求
        credit_patterns = [
            r'(\d+)\s*credit',
            r'(\d+)\s*units?',
            r'(\d+)\s*course'
        ]
        
        for pattern in credit_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                requirements['credits'] = {
                    'value': int(match.group(1)),
                    'description': match.group(0)
                }
                break
        
        # GPA要求
        gpa_match = re.search(r'(\d+\.?\d*)\s*(gpa|average|grade)', text, re.I)
        if gpa_match:
            requirements['gpa'] = {
                'value': float(gpa_match.group(1)),
                'description': gpa_match.group(0)
            }
        
        # 论文要求
        if re.search(r'thesis|dissertation|research', text, re.I):
            requirements['thesis_required'] = True
        
        return requirements
    
    def _extract_research_areas(self, soup):
        """提取研究领域"""
        research_areas = []
        research_keywords = ['research', 'area', 'field', 'topic']
        
        for keyword in research_keywords:
            sections = soup.find_all(text=re.compile(keyword, re.I))
            for section in sections[:3]:
                parent = section.parent if hasattr(section, 'parent') else None
                if parent:
                    text = parent.get_text(strip=True)
                    if 30 < len(text) < 400:
                        research_areas.append({
                            'area': text[:200],
                            'description': text,
                            'keyword': keyword
                        })
        
        return research_areas
    
    def _extract_faculty_info(self, soup):
        """提取学院信息"""
        faculty_info = {}
        
        # 查找学院名称
        faculty_patterns = [
            r'faculty of (\w+)',
            r'school of (\w+)',
            r'department of ([\w\s]+)'
        ]
        
        text = soup.get_text()
        for pattern in faculty_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                faculty_info['faculty'] = match.group(1).title()
                break
        
        return faculty_info
    
    def _extract_application_info(self, soup):
        """提取申请信息"""
        app_info = {}
        
        # 查找申请截止日期
        date_patterns = [
            r'deadline.*?(\w+\s+\d{1,2})',
            r'application.*?due.*?(\w+\s+\d{1,2})',
            r'submit.*?by.*?(\w+\s+\d{1,2})'
        ]
        
        text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                app_info['deadline'] = match.group(1)
                break
        
        return app_info
    
    def _extract_funding_info(self, soup):
        """提取资助信息"""
        funding_info = []
        funding_keywords = ['funding', 'scholarship', 'fellowship', 'assistantship', 'stipend']
        
        for keyword in funding_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.I))
            for element in elements[:2]:
                parent = element.parent if hasattr(element, 'parent') else None
                if parent:
                    text = parent.get_text(strip=True)
                    if 20 < len(text) < 300:
                        funding_info.append({
                            'type': keyword,
                            'description': text[:200]
                        })
        
        return funding_info
    
    def save_data(self, filename):
        """保存爬取的数据"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.programs_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ 数据已保存到: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 保存数据失败: {e}")
            return False
    
    def run_full_scrape(self, max_programs=None):
        """运行完整的爬取流程"""
        try:
            self.logger.info("🚀 开始学术日历爬取流程")
            
            # 设置WebDriver
            if not self.setup_driver():
                return False
            
            # 访问主页面
            self.logger.info(f"📡 访问主页面: {self.base_url}")
            self.driver.get(self.base_url)
            
            # 等待页面加载
            self.wait_for_page_load()
            
            # 提取专业列表
            if not self.extract_programs_list():
                return False
            
            # 爬取详细信息
            detailed_programs = []
            total_programs = len(self.programs_data)
            max_programs = max_programs or total_programs
            
            self.logger.info(f"📚 开始爬取 {min(max_programs, total_programs)} 个专业的详细信息")
            
            for i, program_info in enumerate(self.programs_data[:max_programs]):
                try:
                    details = self.scrape_program_details(program_info)
                    if details:
                        detailed_programs.append(details)
                    
                    # 进度显示
                    self.logger.info(f"进度: {i+1}/{min(max_programs, total_programs)}")
                    
                    # 礼貌性延迟
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"爬取第 {i+1} 个专业失败: {e}")
            
            # 更新数据
            self.programs_data = detailed_programs
            
            # 保存数据
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"academic_calendar_programs_{timestamp}.json"
            self.save_data(filename)
            
            self.logger.info(f"🎉 爬取完成！成功爬取 {len(detailed_programs)} 个专业")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 爬取流程失败: {e}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("🔚 WebDriver 已关闭")

def main():
    """主函数"""
    print("🎓 滑铁卢大学学术日历高级爬取器")
    print("=" * 60)
    
    # 创建爬取器
    scraper = AcademicCalendarScraper(headless=True)
    
    # 运行爬取
    success = scraper.run_full_scrape(max_programs=10)  # 先测试10个专业
    
    if success:
        print("✅ 爬取成功完成！")
    else:
        print("❌ 爬取失败，请检查日志信息")

if __name__ == "__main__":
    main() 