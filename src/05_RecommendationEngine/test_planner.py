#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for SYDE Course Planner
"""

from syde_course_planner import SYDECoursePlanner
import json

def test_basic_functionality():
    """Test basic functionality of the course planner"""
    print("=== Testing SYDE Course Planner ===\n")
    
    # Initialize planner
    planner = SYDECoursePlanner()
    
    try:
        planner.initialize()
        print("✓ Initialization successful!")
    except FileNotFoundError as e:
        print(f"✗ Initialization failed: {e}")
        return False
    
    # Test MEng AI & ML specialization
    test_input = {
        'degree': 'MEng',
        'semesters': 3,
        'specialization': 'Artificial Intelligence and Machine Learning'
    }
    
    print(f"\nTesting MEng AI & ML specialization...")
    print(f"Input: {test_input}")
    
    try:
        result = planner.plan_courses(test_input)
        
        if 'error' in result:
            print(f"✗ Error: {result['error']}")
            return False
        
        print("✓ Course planning successful!")
        
        # Display key results
        print(f"\nResults Summary:")
        print(f"  Program: {result['program_info']['program_name']}")
        print(f"  Specialization: {result['program_info']['specialization']}")
        print(f"  Total Courses Required: {result['requirements_summary']['total_courses']}")
        print(f"  Compulsory Courses: {len(result['requirements_summary']['compulsory_courses'])}")
        print(f"  Available Courses in Pool: {len(result['course_pool'])}")
        
        # Show compulsory courses
        if result['requirements_summary']['compulsory_courses']:
            print(f"\n  Compulsory Courses:")
            for course in result['requirements_summary']['compulsory_courses']:
                print(f"    - {course}")
        
        # Show semester plan
        print(f"\n  Semester Plan:")
        for semester in result['semester_plan']:
            print(f"    Semester {semester['semester']} ({semester['term_type']}):")
            for course in semester['courses']:
                print(f"      - {course}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during planning: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_loading():
    """Test data loading capabilities"""
    print("\n=== Testing Data Loading ===")
    
    planner = SYDECoursePlanner()
    
    # Test course loading
    try:
        planner.course_loader.load_courses()
        course_count = len(planner.course_loader.courses)
        print(f"✓ Loaded {course_count} SYDE courses")
        
        # Show some example courses
        print("\nExample courses loaded:")
        count = 0
        for course_code, course in planner.course_loader.courses.items():
            if count >= 5:
                break
            print(f"  - {course_code}: {course.title}")
            count += 1
            
    except Exception as e:
        print(f"✗ Course loading failed: {e}")
        return False
    
    # Test program loading
    try:
        planner.program_loader.load_programs()
        program_count = len(planner.program_loader.programs)
        print(f"✓ Loaded {program_count} SYDE programs")
        
        # Show available programs
        print("\nAvailable programs:")
        for program in planner.program_loader.programs:
            print(f"  - {program['program_name']}")
            
    except Exception as e:
        print(f"✗ Program loading failed: {e}")
        return False
    
    return True

def test_specific_course_lookup():
    """Test specific course lookups"""
    print("\n=== Testing Course Lookup ===")
    
    planner = SYDECoursePlanner()
    planner.course_loader.load_courses()
    
    # Test some known SYDE courses
    test_courses = ['SYDE 600', 'SYDE 675', 'SYDE 660A', 'SYDE 522']
    
    for course_code in test_courses:
        course = planner.course_loader.get_course(course_code)
        if course:
            print(f"✓ Found {course_code}: {course.title}")
        else:
            print(f"✗ Course not found: {course_code}")

if __name__ == "__main__":
    # Run all tests
    print("Starting SYDE Course Planner Tests...\n")
    
    success = True
    
    # Test 1: Data loading
    if not test_data_loading():
        success = False
    
    # Test 2: Course lookup
    test_specific_course_lookup()
    
    # Test 3: Basic functionality
    if not test_basic_functionality():
        success = False
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    print(f"{'='*50}") 