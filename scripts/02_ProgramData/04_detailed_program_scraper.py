#!/usr/bin/python3
# coding=utf-8
# author troy

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin

class ProgramRequirementsScraper:
    def __init__(self):
        self.base_url = "https://uwaterloo.ca"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def scrape_program_details(self, program_url, program_name):
        """Scrape detailed program requirements from a specific program page"""
        try:
            print(f"Scraping details for: {program_name}")
            response = self.session.get(program_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract program details
            program_details = {
                'program_name': program_name,
                'url': program_url,
                'requirements': [],
                'courses': [],
                'specializations': [],
                'certificates': [],
                'degree_requirements': {}
            }
            
            # Look for course requirements sections
            self._extract_course_requirements(soup, program_details)
            
            # Look for specialization information
            self._extract_specializations(soup, program_details)
            
            # Look for certificate options
            self._extract_certificates(soup, program_details)
            
            # Extract general degree requirements
            self._extract_degree_requirements(soup, program_details)
            
            return program_details
            
        except Exception as e:
            print(f"Error scraping {program_name}: {e}")
            return None
    
    def _extract_course_requirements(self, soup, program_details):
        """Extract course requirements from the program page"""
        # Look for sections containing course codes
        course_pattern = r'\b[A-Z]{2,6}\s*\d{3}[A-Z]?\b'
        
        # Find sections that typically contain requirements
        requirement_sections = soup.find_all(['div', 'section', 'p'], 
                                          text=re.compile(r'(requirement|course|credit)', re.I))
        
        for section in requirement_sections:
            # Get the parent element for more context
            parent = section.parent if section.parent else section
            text = parent.get_text() if parent else section.get_text()
            
            # Find course codes in the text
            courses = re.findall(course_pattern, text)
            if courses:
                program_details['courses'].extend(courses)
                
                # Try to categorize the requirement
                section_text = text.lower()
                if any(word in section_text for word in ['core', 'required', 'mandatory']):
                    req_type = 'core'
                elif any(word in section_text for word in ['elective', 'optional', 'choose']):
                    req_type = 'elective'
                else:
                    req_type = 'general'
                
                program_details['requirements'].append({
                    'type': req_type,
                    'courses': courses,
                    'description': text.strip()[:200]  # First 200 chars
                })
    
    def _extract_specializations(self, soup, program_details):
        """Extract specialization information"""
        specialization_keywords = ['specialization', 'concentration', 'track', 'option']
        
        for keyword in specialization_keywords:
            sections = soup.find_all(text=re.compile(keyword, re.I))
            for section in sections:
                parent = section.parent if hasattr(section, 'parent') else None
                if parent:
                    text = parent.get_text().strip()
                    if len(text) > 20:  # Filter out very short matches
                        program_details['specializations'].append({
                            'name': text[:100],  # First 100 chars
                            'type': keyword,
                            'details': text
                        })
    
    def _extract_certificates(self, soup, program_details):
        """Extract certificate information"""
        cert_sections = soup.find_all(text=re.compile(r'certificate|diploma', re.I))
        
        for section in cert_sections:
            parent = section.parent if hasattr(section, 'parent') else None
            if parent:
                text = parent.get_text().strip()
                if len(text) > 20:
                    program_details['certificates'].append({
                        'name': text[:100],
                        'details': text
                    })
    
    def _extract_degree_requirements(self, soup, program_details):
        """Extract general degree requirements like credit hours, GPA, etc."""
        # Look for common degree requirement patterns
        text = soup.get_text()
        
        # Credit requirements
        credit_match = re.search(r'(\d+)\s*credit', text, re.I)
        if credit_match:
            program_details['degree_requirements']['credits'] = int(credit_match.group(1))
        
        # GPA requirements
        gpa_match = re.search(r'(\d+\.?\d*)\s*GPA|average', text, re.I)
        if gpa_match:
            program_details['degree_requirements']['gpa'] = float(gpa_match.group(1))
        
        # Duration
        duration_match = re.search(r'(\d+)\s*(year|term|month)', text, re.I)
        if duration_match:
            program_details['degree_requirements']['duration'] = {
                'value': int(duration_match.group(1)),
                'unit': duration_match.group(2)
            }

def main():
    scraper = ProgramRequirementsScraper()
    
    # Load the existing programs list
    try:
        with open('official_graduate_programs.json', 'r', encoding='utf-8') as f:
            programs = json.load(f)
    except FileNotFoundError:
        print("Error: official_graduate_programs.json not found. Please run 02_html_parse.py first.")
        return
    
    detailed_programs = []
    
    # Focus on engineering programs first, especially SYDE
    engineering_programs = [p for p in programs if 'syde' in p['program_name'].lower() or 
                          'system' in p['program_name'].lower() or 
                          'engineering' in p['program_name'].lower()]
    
    print(f"Found {len(engineering_programs)} engineering-related programs to scrape")
    
    for i, program in enumerate(engineering_programs[:10]):  # Limit to first 10 for testing
        if program.get('program_url'):
            details = scraper.scrape_program_details(
                program['program_url'], 
                program['program_name']
            )
            
            if details:
                # Merge with original program data
                details.update({
                    'degree': program.get('degree'),
                    'academic_level': program.get('academic_level')
                })
                detailed_programs.append(details)
            
            # Be respectful to the server
            time.sleep(1)
            
            print(f"Progress: {i+1}/{len(engineering_programs[:10])}")
    
    # Save the detailed program data
    output_file = 'detailed_program_requirements.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_programs, f, ensure_ascii=False, indent=4)
    
    print(f"\nCompleted! Detailed program requirements saved to: {output_file}")
    print(f"Successfully scraped {len(detailed_programs)} programs")

if __name__ == "__main__":
    main() 