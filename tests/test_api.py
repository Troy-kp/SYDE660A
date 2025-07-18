#!/usr/bin/python3
# coding=utf-8
# author troy

import sys
import os
import json
sys.path.append('05_RecommendationEngine')

from course_recommender import CourseRecommendationEngine

def test_data_loading():
    """Test if data can be loaded successfully"""
    print("=== Testing Data Loading ===")
    
    recommender = CourseRecommendationEngine()
    
    course_data_dir = "final_verified_course_data"
    program_requirements_file = "02_ProgramData/detailed_program_requirements.json"
    
    # Check if directories exist
    if not os.path.exists(course_data_dir):
        print(f"❌ Course data directory not found: {course_data_dir}")
        return False
    
    print(f"✅ Course data directory found: {course_data_dir}")
    
    # Load data
    try:
        recommender.load_data(course_data_dir, program_requirements_file)
        print(f"✅ Data loaded successfully")
        
        # Print statistics
        total_courses = sum(len(courses) for courses in recommender.course_data.values())
        print(f"📊 Statistics:")
        print(f"   - Subjects: {len(recommender.course_data)}")
        print(f"   - Total courses: {total_courses}")
        print(f"   - Programs: {len(recommender.program_requirements) if recommender.program_requirements else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

def test_recommendations():
    """Test the recommendation system"""
    print("\n=== Testing Recommendations ===")
    
    recommender = CourseRecommendationEngine()
    
    try:
        recommender.load_data("final_verified_course_data", "02_ProgramData/detailed_program_requirements.json")
        
        # Test student profile
        student_profile = {
            'program': 'Systems Design Engineering',
            'degree': 'MASc', 
            'completed_courses': ['SYDE600'],
            'interests': ['machine learning', 'control systems', 'robotics'],
            'term': 'Winter 2025'
        }
        
        print(f"👤 Testing with student profile:")
        print(f"   Program: {student_profile['program']}")
        print(f"   Interests: {student_profile['interests']}")
        print(f"   Completed: {student_profile['completed_courses']}")
        
        recommendations = recommender.recommend_courses(student_profile)
        
        print(f"\n🎯 Generated {len(recommendations)} recommendations:")
        
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"\n{i}. {rec.course_code}: {rec.title}")
            print(f"   Score: {rec.relevance_score:.1f}")
            print(f"   Reason: {rec.reason}")
            print(f"   Available: {', '.join(rec.term_available) if rec.term_available else 'TBD'}")
            if rec.description and len(rec.description) > 0:
                desc = rec.description[:100] + "..." if len(rec.description) > 100 else rec.description
                print(f"   Description: {desc}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing recommendations: {e}")
        return False

def test_specializations():
    """Test specialization recommendations"""
    print("\n=== Testing Specialization Recommendations ===")
    
    recommender = CourseRecommendationEngine()
    
    try:
        recommender.load_data("final_verified_course_data", "02_ProgramData/detailed_program_requirements.json")
        
        specializations = ['machine learning', 'robotics', 'biomedical']
        completed_courses = ['SYDE600', 'MATH600']
        
        for spec in specializations:
            print(f"\n🔬 Testing specialization: {spec}")
            recommendations = recommender.get_specialization_recommendations(spec, completed_courses)
            
            print(f"   Found {len(recommendations)} recommendations")
            
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec.course_code}: {rec.title} (Score: {rec.relevance_score:.1f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing specializations: {e}")
        return False

def test_course_search():
    """Test course search functionality"""
    print("\n=== Testing Course Search ===")
    
    recommender = CourseRecommendationEngine()
    
    try:
        recommender.load_data("final_verified_course_data", "02_ProgramData/detailed_program_requirements.json")
        
        # Test finding specific courses
        test_courses = ['SYDE600', 'SYDE655', 'SYDE671']
        
        for course_code in test_courses:
            course = recommender._find_course_by_code(course_code)
            if course:
                print(f"✅ Found {course_code}: {course.get('title', 'No title')}")
            else:
                print(f"❌ Course not found: {course_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing course search: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 UW Course Recommendation System - Test Suite")
    print("=" * 60)
    
    tests = [
        test_data_loading,
        test_recommendations,
        test_specializations,
        test_course_search
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("=" * 60)
    print(f"📋 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your recommendation system is ready.")
        print("\n🚀 Next steps:")
        print("1. Run the program scraper: python 02_ProgramData/04_detailed_program_scraper.py")
        print("2. Start the API server: python 06_WebAPI/app.py")
        print("3. Test the API endpoints")
    else:
        print("⚠️  Some tests failed. Please check your data files and dependencies.")

if __name__ == "__main__":
    main() 