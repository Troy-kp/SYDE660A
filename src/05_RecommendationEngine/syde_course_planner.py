#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYDE Course Planner
===================
A comprehensive course planning system for Systems Design Engineering graduate students.

Usage:
    python syde_course_planner.py

Author: AI Assistant
Date: 2025
"""

import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
from pathlib import Path
import itertools

@dataclass
class Course:
    """Course data structure"""
    course_id: str
    subject_code: str
    catalog_number: str
    title: str
    description: str
    credit_weight: float
    requirements_description: Optional[str]
    term_code: str
    term_name: str
    academic_career: str
    
    @property
    def course_code(self) -> str:
        return f"{self.subject_code} {self.catalog_number}"

@dataclass
class CourseRequirement:
    """Course requirement structure"""
    type: str  # 'compulsory', 'compulsory_choice', 'elective', 'specified'
    courses: List[str]
    n_to_choose: int = 1
    description: str = ""

@dataclass
class SemesterPlan:
    """Semester planning structure"""
    semester: int
    term_type: str  # 'Fall', 'Winter', 'Spring'
    courses: List[str]
    total_credits: float
    notes: List[str]

class PrerequisiteParser:
    """Parse course prerequisites from text descriptions"""
    
    def __init__(self):
        self.prereq_patterns = [
            r'[Pp]re[-]?req(?:uisite)?s?[:]\s*',
            r'[Pp]rerequisite?s?[:]\s*'
        ]
        self.antireq_patterns = [
            r'[Aa]nti[-]?req(?:uisite)?s?[:]\s*',
            r'[Aa]ntirequisite?s?[:]\s*'
        ]
        self.coreq_patterns = [
            r'[Cc]o[-]?req(?:uisite)?s?[:]\s*',
            r'[Cc]orequisite?s?[:]\s*'
        ]
    
    def parse_requirements(self, requirements_text: str) -> Dict[str, List[str]]:
        """Parse course requirements text into structured data"""
        if not requirements_text:
            return {'prereq': [], 'antireq': [], 'coreq': []}
        
        result = {
            'prereq': self._extract_courses(requirements_text, self.prereq_patterns),
            'antireq': self._extract_courses(requirements_text, self.antireq_patterns),
            'coreq': self._extract_courses(requirements_text, self.coreq_patterns)
        }
        
        # Handle mixed formats like "Prereq/coreq:"
        if 'prereq/coreq' in requirements_text.lower():
            courses = self._extract_mixed_requirements(requirements_text)
            result['prereq'].extend(courses)
            result['coreq'].extend(courses)
        
        return result
    
    def _extract_courses(self, text: str, patterns: List[str]) -> List[str]:
        """Extract course codes for specific requirement types"""
        courses = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = match.end()
                end = self._find_next_boundary(text, start)
                segment = text[start:end]
                
                # Extract course codes (e.g., SYDE 600, CS 240)
                course_codes = re.findall(r'\b([A-Z]{2,6})\s*(\d{3}[A-Z]?)\b', segment)
                courses.extend([f"{subj} {num}" for subj, num in course_codes])
        
        return list(set(courses))
    
    def _find_next_boundary(self, text: str, start: int) -> int:
        """Find the end of current requirement section"""
        # Look for next requirement keyword or sentence end
        boundaries = []
        for pattern_group in [self.prereq_patterns, self.antireq_patterns, self.coreq_patterns]:
            for pattern in pattern_group:
                match = re.search(pattern, text[start:], re.IGNORECASE)
                if match:
                    boundaries.append(start + match.start())
        
        # Also look for period or semicolon
        punctuation = re.search(r'[.;]', text[start:])
        if punctuation:
            boundaries.append(start + punctuation.start())
        
        return min(boundaries) if boundaries else len(text)
    
    def _extract_mixed_requirements(self, text: str) -> List[str]:
        """Extract courses from mixed requirement formats"""
        # Simple implementation for "Prereq/coreq: COURSE XXX"
        match = re.search(r'prereq/coreq[:]\s*([^.;]+)', text, re.IGNORECASE)
        if match:
            segment = match.group(1)
            course_codes = re.findall(r'\b([A-Z]{2,6})\s*(\d{3}[A-Z]?)\b', segment)
            return [f"{subj} {num}" for subj, num in course_codes]
        return []

class SYDECourseLoader:
    """Load and manage SYDE course data"""
    
    def __init__(self, course_data_dir: str = "../API_course_data_filtered/SYDE"):
        self.course_data_dir = Path(course_data_dir)
        self.courses: Dict[str, Course] = {}
        self.course_availability: Dict[str, List[str]] = {}
        self.prerequisite_parser = PrerequisiteParser()
        
    def load_courses(self) -> None:
        """Load all SYDE courses from JSON files"""
        print(f"Loading SYDE courses from {self.course_data_dir}...")
        
        if not self.course_data_dir.exists():
            raise FileNotFoundError(f"Course data directory not found: {self.course_data_dir}")
        
        for json_file in self.course_data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    term_courses = json.load(f)
                
                for course_data in term_courses:
                    course = Course(
                        course_id=course_data.get('courseId', ''),
                        subject_code=course_data.get('subjectCode', ''),
                        catalog_number=course_data.get('catalogNumber', ''),
                        title=course_data.get('title', ''),
                        description=course_data.get('description', ''),
                        credit_weight=float(course_data.get('creditWeight', 0.5)),
                        requirements_description=course_data.get('requirementsDescription'),
                        term_code=course_data.get('termCode', ''),
                        term_name=course_data.get('termName', ''),
                        academic_career=course_data.get('associatedAcademicCareer', '')
                    )
                    
                    course_code = course.course_code
                    
                    # Store course (use latest version if duplicates)
                    if course_code not in self.courses or course.term_code > self.courses[course_code].term_code:
                        self.courses[course_code] = course
                    
                    # Track availability
                    if course_code not in self.course_availability:
                        self.course_availability[course_code] = []
                    if course.term_name not in self.course_availability[course_code]:
                        self.course_availability[course_code].append(course.term_name)
                        
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        print(f"Loaded {len(self.courses)} unique SYDE courses")
    
    def get_course(self, course_code: str) -> Optional[Course]:
        """Get course by course code"""
        return self.courses.get(course_code)
    
    def get_courses_by_level(self, level_range: Tuple[int, int]) -> List[Course]:
        """Get courses within a specific level range"""
        courses = []
        for course in self.courses.values():
            try:
                level = int(course.catalog_number[:1])
                if level_range[0] <= level <= level_range[1]:
                    courses.append(course)
            except (ValueError, IndexError):
                continue
        return courses
    
    def get_course_availability(self, course_code: str) -> List[str]:
        """Get terms when course is typically offered"""
        return self.course_availability.get(course_code, [])

class SYDEProgramLoader:
    """Load and manage SYDE program requirements"""
    
    def __init__(self, programs_file: str = "./syde_programs.json"):
        self.programs_file = Path(programs_file)
        self.programs: List[Dict] = []
        
    def load_programs(self) -> None:
        """Load SYDE program data"""
        if not self.programs_file.exists():
            raise FileNotFoundError(f"Programs file not found: {self.programs_file}")
        
        with open(self.programs_file, 'r', encoding='utf-8') as f:
            self.programs = json.load(f)
        
        print(f"Loaded {len(self.programs)} SYDE programs")
    
    def get_program(self, degree: str, specialization: str = None) -> Optional[Dict]:
        """Get program requirements by degree and specialization"""
        for program in self.programs:
            program_name = program.get('program_name', '').lower()
            
            # Match degree type
            if degree.lower() not in program_name:
                continue
            
            # If no specialization specified, return base program
            if not specialization:
                if 'specializations' not in program:
                    return program
                continue
            
            # Match specialization
            if 'specializations' in program:
                for spec in program['specializations']:
                    if specialization.lower() in spec.get('name', '').lower():
                        # Merge base program with specialization
                        merged_program = program.copy()
                        merged_program['active_specialization'] = spec
                        return merged_program
        
        return None

class SYDECoursePlanner:
    """Main course planning engine for SYDE students"""
    
    def __init__(self):
        self.course_loader = SYDECourseLoader()
        self.program_loader = SYDEProgramLoader()
        self.term_sequence = ['Fall', 'Winter', 'Spring']
        
    def initialize(self) -> None:
        """Initialize the planner by loading data"""
        print("Initializing SYDE Course Planner...")
        self.course_loader.load_courses()
        self.program_loader.load_programs()
        print("Initialization complete!\n")
    
    def plan_courses(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main course planning function
        
        Args:
            user_input: {
                'degree': 'MEng',  # MASc, MEng, PhD
                'semesters': 3,    # planned graduation semesters
                'specialization': 'Artificial Intelligence and Machine Learning',  # optional
                'background': 'direct_from_undergrad',  # optional for PhD
                'preferences': {
                    'course_load': 'normal',  # light, normal, heavy
                    'focus_areas': ['machine_learning', 'control_systems']
                }
            }
        
        Returns:
            Complete course plan with requirements, course pool, and semester suggestions
        """
        
        # 1. Get program requirements
        program = self.program_loader.get_program(
            user_input['degree'], 
            user_input.get('specialization')
        )
        
        if not program:
            available_programs = [p['program_name'] for p in self.program_loader.programs]
            return {
                'error': f"Program not found for degree: {user_input['degree']}, specialization: {user_input.get('specialization')}",
                'available_programs': available_programs
            }
        
        # 2. Parse requirements
        requirements = self._parse_program_requirements(program, user_input)
        
        # 3. Build course pool
        course_pool = self._build_course_pool(requirements)
        
        # 4. Suggest semester allocation
        semester_plan = self._suggest_semester_allocation(
            course_pool, 
            requirements,
            user_input['semesters']
        )
        
        # 5. Generate comprehensive plan
        plan = {
            'program_info': {
                'program_name': program['program_name'],
                'specialization': user_input.get('specialization'),
                'total_semesters': user_input['semesters']
            },
            'requirements_summary': requirements,
            'course_pool': course_pool,
            'semester_plan': semester_plan,
            'recommendations': self._generate_recommendations(course_pool, requirements)
        }
        
        return plan
    
    def _parse_program_requirements(self, program: Dict, user_input: Dict) -> Dict[str, Any]:
        """Parse program requirements into structured format"""
        degree_rules = program.get('degree_rules', {})
        
        requirements = {
            'total_courses': degree_rules.get('total_courses', 0),
            'compulsory_courses': [],
            'compulsory_choices': [],
            'elective_requirements': [],
            'constraints': {
                'level_constraints': degree_rules.get('level_constraints', {}),
                'departmental_constraints': degree_rules.get('departmental_constraints', {})
            }
        }
        
        # Add compulsory courses
        if 'compulsory_courses' in degree_rules:
            requirements['compulsory_courses'] = degree_rules['compulsory_courses']
        
        # Add compulsory choices
        if 'compulsory_choices' in degree_rules:
            requirements['compulsory_choices'] = degree_rules['compulsory_choices']
        
        # Handle specialization requirements
        if 'active_specialization' in program:
            spec = program['active_specialization']
            spec_req = spec.get('requirements', {})
            
            # Override total courses if specialization specifies
            if 'total_courses' in spec_req:
                requirements['total_courses'] = spec_req['total_courses']
            
            # Add specialization compulsory courses
            if 'compulsory_courses' in spec_req:
                requirements['compulsory_courses'].extend(spec_req['compulsory_courses'])
            
            # Add specialization choices
            if 'compulsory_choices' in spec_req:
                requirements['compulsory_choices'].extend(spec_req['compulsory_choices'])
            
            # Add elective rules
            if 'elective_rules' in spec_req:
                requirements['elective_requirements'] = spec_req['elective_rules']
        
        return requirements
    
    def _build_course_pool(self, requirements: Dict) -> List[Dict]:
        """Build pool of available courses based on requirements"""
        course_pool = []
        
        # Add compulsory courses
        for course_code in requirements.get('compulsory_courses', []):
            course = self.course_loader.get_course(course_code)
            if course:
                course_dict = asdict(course)
                course_dict['course_code'] = course.course_code
                course_pool.append({
                    'course': course_dict,
                    'category': 'compulsory',
                    'priority': 10,
                    'availability': self.course_loader.get_course_availability(course_code)
                })
        
        # Add compulsory choice courses
        for choice in requirements.get('compulsory_choices', []):
            for course_code in choice.get('courses', []):
                course = self.course_loader.get_course(course_code)
                if course:
                    course_dict = asdict(course)
                    course_dict['course_code'] = course.course_code
                    course_pool.append({
                        'course': course_dict,
                        'category': 'compulsory_choice',
                        'choice_group': choice,
                        'priority': 9,
                        'availability': self.course_loader.get_course_availability(course_code)
                    })
        
        # Add elective courses based on requirements
        self._add_elective_courses(course_pool, requirements)
        
        # Add general SYDE graduate courses as additional options
        self._add_general_syde_courses(course_pool, requirements)
        
        return course_pool
    
    def _add_elective_courses(self, course_pool: List[Dict], requirements: Dict) -> None:
        """Add elective courses based on specialization requirements"""
        for elective_rule in requirements.get('elective_requirements', []):
            if elective_rule.get('type') == 'choose_n_from_list':
                for course_code in elective_rule.get('courses', []):
                    course = self.course_loader.get_course(course_code)
                    if course:
                        course_dict = asdict(course)
                        course_dict['course_code'] = course.course_code
                        course_pool.append({
                            'course': course_dict,
                            'category': 'specified_elective',
                            'elective_rule': elective_rule,
                            'priority': 7,
                            'availability': self.course_loader.get_course_availability(course_code)
                        })
            
            elif elective_rule.get('type') == 'complex':
                # Handle complex elective rules (specified + elective lists)
                for list_name in ['specified_list', 'elective_list']:
                    if list_name in elective_rule:
                        priority = 8 if list_name == 'specified_list' else 6
                        for course_code in elective_rule[list_name]:
                            course = self.course_loader.get_course(course_code)
                            if course:
                                course_dict = asdict(course)
                                course_dict['course_code'] = course.course_code
                                course_pool.append({
                                    'course': course_dict,
                                    'category': f'complex_{list_name}',
                                    'elective_rule': elective_rule,
                                    'priority': priority,
                                    'availability': self.course_loader.get_course_availability(course_code)
                                })
    
    def _add_general_syde_courses(self, course_pool: List[Dict], requirements: Dict) -> None:
        """Add general SYDE graduate courses as additional options"""
        existing_courses = {f"{item['course']['subject_code']} {item['course']['catalog_number']}" for item in course_pool}
        
        # Get 600+ level SYDE courses
        graduate_courses = self.course_loader.get_courses_by_level((6, 9))
        
        for course in graduate_courses:
            if course.course_code not in existing_courses:
                course_dict = asdict(course)
                course_dict['course_code'] = course.course_code  # Add the computed property
                course_pool.append({
                    'course': course_dict,
                    'category': 'general_elective',
                    'priority': 5,
                    'availability': self.course_loader.get_course_availability(course.course_code)
                })
    
    def _suggest_semester_allocation(self, course_pool: List[Dict], requirements: Dict, total_semesters: int) -> List[SemesterPlan]:
        """Suggest how to allocate courses across semesters"""
        semester_plans = []
        
        # Calculate courses per semester
        total_courses = requirements.get('total_courses', 8)
        courses_per_semester = max(1, total_courses // total_semesters)
        extra_courses = total_courses % total_semesters
        
        # Sort courses by priority
        sorted_courses = sorted(course_pool, key=lambda x: x['priority'], reverse=True)
        
        # Allocate courses to semesters
        allocated_courses = []
        for semester in range(1, total_semesters + 1):
            semester_course_count = courses_per_semester + (1 if semester <= extra_courses else 0)
            
            # Select courses for this semester
            semester_courses = []
            semester_credits = 0.0
            
            # First, add highest priority courses that haven't been allocated
            for course_item in sorted_courses:
                if len(semester_courses) >= semester_course_count:
                    break
                
                course_code = course_item['course']['course_code']
                if course_code not in allocated_courses:
                    semester_courses.append(course_code)
                    allocated_courses.append(course_code)
                    semester_credits += course_item['course']['credit_weight']
            
            # Determine likely term type (simplified)
            term_type = self.term_sequence[(semester - 1) % len(self.term_sequence)]
            
            semester_plan = SemesterPlan(
                semester=semester,
                term_type=term_type,
                courses=semester_courses,
                total_credits=semester_credits,
                notes=self._generate_semester_notes(semester_courses, course_pool)
            )
            
            semester_plans.append(asdict(semester_plan))
        
        return semester_plans
    
    def _generate_semester_notes(self, semester_courses: List[str], course_pool: List[Dict]) -> List[str]:
        """Generate notes for semester planning"""
        notes = []
        
        # Find course categories in this semester
        categories = set()
        for course_code in semester_courses:
            for course_item in course_pool:
                if course_item['course']['course_code'] == course_code:
                    categories.add(course_item['category'])
                    break
        
        if 'compulsory' in categories:
            notes.append("Includes required compulsory course(s)")
        
        if 'compulsory_choice' in categories:
            notes.append("Includes courses from required choice group")
        
        if len(semester_courses) > 3:
            notes.append("Heavy course load - consider prerequisites and workload")
        
        return notes
    
    def _generate_recommendations(self, course_pool: List[Dict], requirements: Dict) -> List[str]:
        """Generate planning recommendations"""
        recommendations = []
        
        # Check for compulsory courses
        compulsory_count = sum(1 for item in course_pool if item['category'] == 'compulsory')
        if compulsory_count > 0:
            recommendations.append(f"Complete {compulsory_count} compulsory course(s) first")
        
        # Check for choice requirements
        choice_groups = set()
        for item in course_pool:
            if item['category'] == 'compulsory_choice':
                choice_groups.add(str(item.get('choice_group', {})))
        
        if choice_groups:
            recommendations.append(f"Select from {len(choice_groups)} required choice group(s)")
        
        # Level constraints
        level_constraints = requirements.get('constraints', {}).get('level_constraints', {})
        if 'max_500_level' in level_constraints:
            max_500 = level_constraints['max_500_level']
            recommendations.append(f"Maximum {max_500} course(s) at 500-level allowed")
        
        # Departmental constraints
        dept_constraints = requirements.get('constraints', {}).get('departmental_constraints', {})
        if 'min_syde_courses' in dept_constraints:
            min_syde = dept_constraints['min_syde_courses']
            recommendations.append(f"Minimum {min_syde} SYDE course(s) required")
        
        return recommendations

def main():
    """Main function for testing the course planner"""
    print("=== SYDE Course Planner ===\n")
    
    # Initialize planner
    planner = SYDECoursePlanner()
    
    try:
        planner.initialize()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure data files are in the correct locations:")
        print("- syde_programs.json in current directory")
        print("- SYDE course data in ../API_course_data_filtered/SYDE/")
        return
    
    # Example usage scenarios
    test_scenarios = [
        {
            'name': 'MEng Student - AI & ML Specialization',
            'input': {
                'degree': 'MEng',
                'semesters': 3,
                'specialization': 'Artificial Intelligence and Machine Learning',
                'preferences': {
                    'course_load': 'normal',
                    'focus_areas': ['machine_learning', 'pattern_recognition']
                }
            }
        },
        {
            'name': 'MASc Student - General',
            'input': {
                'degree': 'MASc',
                'semesters': 2,
                'preferences': {
                    'course_load': 'normal'
                }
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'='*60}")
        print(f"Testing: {scenario['name']}")
        print(f"{'='*60}")
        
        try:
            result = planner.plan_courses(scenario['input'])
            
            if 'error' in result:
                print(f"Error: {result['error']}")
                if 'available_programs' in result:
                    print("Available programs:")
                    for prog in result['available_programs']:
                        print(f"  - {prog}")
                continue
            
            # Display results
            print(f"\nProgram: {result['program_info']['program_name']}")
            if result['program_info']['specialization']:
                print(f"Specialization: {result['program_info']['specialization']}")
            print(f"Total Semesters: {result['program_info']['total_semesters']}")
            
            print(f"\nRequirements Summary:")
            req = result['requirements_summary']
            print(f"  Total Courses: {req['total_courses']}")
            print(f"  Compulsory Courses: {len(req['compulsory_courses'])}")
            print(f"  Compulsory Choices: {len(req['compulsory_choices'])}")
            
            print(f"\nCourse Pool: {len(result['course_pool'])} courses available")
            
            # Show course categories
            categories = {}
            for course_item in result['course_pool']:
                cat = course_item['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            for cat, count in categories.items():
                print(f"  - {cat}: {count} courses")
            
            print(f"\nSemester Plan:")
            for semester in result['semester_plan']:
                print(f"  Semester {semester['semester']} ({semester['term_type']}):")
                for course_code in semester['courses']:
                    print(f"    - {course_code}")
                print(f"    Total Credits: {semester['total_credits']}")
                if semester['notes']:
                    for note in semester['notes']:
                        print(f"    Note: {note}")
            
            print(f"\nRecommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
                
        except Exception as e:
            print(f"Error processing scenario: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main() 