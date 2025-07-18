#!/usr/bin/env python3
"""
Academic Calendar直接访问工具
针对 https://uwaterloo.ca/academic-calendar/graduate-studies/catalog#/programs?isPrint=true
"""

import requests
import time
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

class AcademicCalendarScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.base_url = "https://uwaterloo.ca/academic-calendar/graduate-studies/catalog"
        self.print_url = "https://uwaterloo.ca/academic-calendar/graduate-studies/catalog#/programs?isPrint=true"
    
    def access_academic_calendar(self):
        """访问Academic Calendar页面"""
        print("🌐 访问Academic Calendar页面...")
        print(f"URL: {self.print_url}")
        
        try:
            response = self.session.get(self.print_url, timeout=30)
            response.raise_for_status()
            
            print(f"✅ 访问成功！状态码: {response.status_code}")
            print(f"📄 响应长度: {len(response.text):,} 字符")
            
            return response.text
            
        except Exception as e:
            print(f"❌ 访问失败: {e}")
            return None
    
    def analyze_page_structure(self, html_content):
        """分析页面结构"""
        print("\n🔍 分析页面结构...")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        analysis = {
            'title': soup.title.text if soup.title else 'No title',
            'has_javascript_loading': 'JavaScript must be enabled' in html_content,
            'has_angular_app': 'ng-app' in html_content or 'angular' in html_content.lower(),
            'scripts': len(soup.find_all('script')),
            'meta_tags': len(soup.find_all('meta')),
            'divs_with_ng': len(soup.find_all('div', attrs={'ng-app': True})),
            'potential_api_calls': []
        }
        
        # 查找可能的API调用
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                # 查找API URL模式
                api_patterns = [
                    r'api/[^"\']+',
                    r'/catalog/[^"\']+',
                    r'\.json[^"\']*',
                    r'programs[^"\']*'
                ]
                
                for pattern in api_patterns:
                    matches = re.findall(pattern, script.string)
                    analysis['potential_api_calls'].extend(matches)
        
        # 查找数据容器
        data_containers = soup.find_all(['div', 'section', 'main'], 
                                       attrs={'class': re.compile(r'(content|programs|catalog|data)')})
        analysis['data_containers'] = len(data_containers)
        
        return analysis
    
    def try_alternative_urls(self):
        """尝试访问可能的替代URL"""
        print("\n🔗 尝试访问替代URL...")
        
        alternative_urls = [
            "https://uwaterloo.ca/academic-calendar/graduate-studies/catalog",
            "https://uwaterloo.ca/academic-calendar/graduate-studies/programs",
            "https://uwaterloo.ca/academic-calendar/graduate-studies/",
            "https://uwaterloo.ca/graduate-studies-academic-calendar/",
            "https://uwaterloo.ca/academic-calendar/graduate-studies/catalog/programs",
            f"{self.print_url}&format=json",
            f"{self.print_url}&print=1"
        ]
        
        results = {}
        
        for url in alternative_urls:
            print(f"  尝试: {url}")
            try:
                response = self.session.get(url, timeout=15)
                results[url] = {
                    'status_code': response.status_code,
                    'content_length': len(response.text),
                    'content_type': response.headers.get('Content-Type', 'Unknown'),
                    'has_programs': 'program' in response.text.lower(),
                    'has_json': response.headers.get('Content-Type', '').startswith('application/json')
                }
                print(f"    ✅ {response.status_code} - {len(response.text):,} chars")
                
                # 如果找到JSON或程序内容，保存样本
                if results[url]['has_json'] or results[url]['has_programs']:
                    sample_file = f"sample_content_{url.split('/')[-1].replace('?', '_').replace('=', '_').replace('#', '_')}.txt"
                    with open(sample_file, 'w', encoding='utf-8') as f:
                        f.write(response.text[:5000])  # 保存前5000字符
                    print(f"    💾 样本保存到: {sample_file}")
                
            except Exception as e:
                results[url] = {'error': str(e)}
                print(f"    ❌ 失败: {e}")
        
        return results
    
    def extract_javascript_data(self, html_content):
        """尝试从JavaScript中提取数据"""
        print("\n💻 分析JavaScript内容...")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        js_data = {
            'script_sources': [],
            'inline_scripts': [],
            'potential_data': []
        }
        
        # 提取所有script标签
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.get('src'):
                js_data['script_sources'].append(script.get('src'))
            elif script.string:
                js_data['inline_scripts'].append(script.string[:500])  # 前500字符
                
                # 查找可能的数据结构
                if 'programs' in script.string.lower():
                    js_data['potential_data'].append({
                        'type': 'programs_related',
                        'content': script.string[:1000]
                    })
        
        return js_data
    
    def search_for_api_endpoints(self, html_content):
        """搜索可能的API端点"""
        print("\n🔍 搜索API端点...")
        
        # API端点模式
        api_patterns = [
            r'https?://[^"\'\s]+/api/[^"\'\s]+',
            r'/api/[^"\'\s]+',
            r'https?://[^"\'\s]+\.json[^"\'\s]*',
            r'/catalog/[^"\'\s]+\.json',
            r'/programs[^"\'\s]*\.json',
            r'uwaterloo\.ca/[^"\'\s]+/programs[^"\'\s]*'
        ]
        
        found_endpoints = []
        
        for pattern in api_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            found_endpoints.extend(matches)
        
        # 去重并过滤
        unique_endpoints = list(set(found_endpoints))
        
        print(f"发现 {len(unique_endpoints)} 个潜在API端点:")
        for endpoint in unique_endpoints:
            print(f"  • {endpoint}")
        
        return unique_endpoints
    
    def test_discovered_endpoints(self, endpoints):
        """测试发现的端点"""
        print("\n🧪 测试发现的端点...")
        
        results = {}
        
        for endpoint in endpoints:
            # 构造完整URL
            if endpoint.startswith('/'):
                full_url = f"https://uwaterloo.ca{endpoint}"
            elif not endpoint.startswith('http'):
                full_url = f"https://uwaterloo.ca/academic-calendar/graduate-studies/{endpoint}"
            else:
                full_url = endpoint
            
            print(f"  测试: {full_url}")
            
            try:
                response = self.session.get(full_url, timeout=15)
                results[full_url] = {
                    'status_code': response.status_code,
                    'content_length': len(response.text),
                    'content_type': response.headers.get('Content-Type', 'Unknown'),
                    'is_json': response.headers.get('Content-Type', '').startswith('application/json')
                }
                
                if response.status_code == 200:
                    print(f"    ✅ 成功! {len(response.text):,} chars")
                    
                    # 如果是JSON，尝试解析
                    if results[full_url]['is_json']:
                        try:
                            data = response.json()
                            results[full_url]['json_keys'] = list(data.keys()) if isinstance(data, dict) else 'array'
                            print(f"    📄 JSON数据包含: {results[full_url]['json_keys']}")
                        except:
                            print(f"    ⚠️ JSON解析失败")
                
            except Exception as e:
                results[full_url] = {'error': str(e)}
                print(f"    ❌ 失败: {e}")
        
        return results
    
    def save_analysis_results(self, page_analysis, js_data, endpoints, endpoint_results):
        """保存分析结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"academic_calendar_analysis_{timestamp}.json"
        
        full_analysis = {
            'analysis_timestamp': datetime.now().isoformat(),
            'target_url': self.print_url,
            'page_analysis': page_analysis,
            'javascript_data': js_data,
            'discovered_endpoints': endpoints,
            'endpoint_test_results': endpoint_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(full_analysis, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 完整分析结果保存到: {filename}")
        return filename

def main():
    """主函数"""
    print("🎯 Academic Calendar 直接访问分析工具")
    print("="*70)
    print("目标URL: https://uwaterloo.ca/academic-calendar/graduate-studies/catalog#/programs?isPrint=true")
    
    scraper = AcademicCalendarScraper()
    
    # 1. 访问主页面
    html_content = scraper.access_academic_calendar()
    if not html_content:
        print("❌ 无法访问主页面，退出分析")
        return
    
    # 2. 分析页面结构
    page_analysis = scraper.analyze_page_structure(html_content)
    
    print(f"\n📋 页面分析结果:")
    print(f"  标题: {page_analysis['title']}")
    print(f"  需要JavaScript: {page_analysis['has_javascript_loading']}")
    print(f"  Angular应用: {page_analysis['has_angular_app']}")
    print(f"  脚本数量: {page_analysis['scripts']}")
    
    # 3. 提取JavaScript数据
    js_data = scraper.extract_javascript_data(html_content)
    print(f"\n💻 JavaScript分析:")
    print(f"  外部脚本: {len(js_data['script_sources'])}")
    print(f"  内联脚本: {len(js_data['inline_scripts'])}")
    print(f"  程序相关数据: {len(js_data['potential_data'])}")
    
    # 4. 搜索API端点
    endpoints = scraper.search_for_api_endpoints(html_content)
    
    # 5. 尝试替代URL
    alternative_results = scraper.try_alternative_urls()
    
    # 6. 测试发现的端点
    if endpoints:
        endpoint_results = scraper.test_discovered_endpoints(endpoints)
    else:
        endpoint_results = {}
    
    # 7. 保存结果
    analysis_file = scraper.save_analysis_results(page_analysis, js_data, endpoints, endpoint_results)
    
    print(f"\n✨ 分析完成!")
    print(f"🔍 发现的关键信息:")
    print(f"  • 页面使用JavaScript动态加载内容")
    print(f"  • 发现 {len(endpoints)} 个潜在API端点")
    print(f"  • 测试了 {len(alternative_results)} 个替代URL")
    
    return analysis_file

if __name__ == "__main__":
    main() 