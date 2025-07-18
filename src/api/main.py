#!/usr/bin/python3
# coding=utf-8
# author troy

import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from src.core.planner import SYDECoursePlanner

app = Flask(__name__, template_folder='../../web/templates')
CORS(app)  # Enable CORS for all routes

# --- Global Planner Instance ---
# Initialize the planner once when the application starts.
# This avoids reloading all the data on every API call.
print("Initializing Course Planner for API...")
planner = SYDECoursePlanner()
try:
    planner.initialize()
    print("Planner initialized successfully.")
except FileNotFoundError as e:
    print(f"CRITICAL ERROR: Could not initialize planner. {e}")
    # In a real app, you might want to exit or disable the endpoint
    planner = None

@app.route('/')
def index():
    """Renders the main user interface."""
    return render_template('UserInterface.html')

@app.route('/api/v1/plan', methods=['POST'])
def get_course_plan():
    """
    API endpoint to generate a course plan.
    Expects a JSON body with user input.
    e.g., {"degree": "MEng", "specialization": "...", "semesters": 3, "start_term": "1249"}
    """
    if planner is None:
        return jsonify({"error": "Planner is not initialized due to a configuration error."}), 500

    user_input = request.json
    if not user_input or 'start_term' not in user_input:
        return jsonify({"error": "Invalid input. JSON body with 'start_term' is required."}), 400
    
    print(f"Received planning request: {user_input}")
    
    plan = planner.plan_courses(user_input)
    
    if "error" in plan:
        print(f"Error generating plan: {plan['error']}")
        return jsonify(plan), 404
        
    print("Successfully generated a plan framework.")
    return jsonify(plan)

@app.route('/api/v1/validate_move', methods=['POST'])
def validate_course_move():
    """
    Validates if a course can be placed in a specific term.
    Expects: {
        "course_code": "SYDE 660", 
        "term_code": "1255",
        "current_plan": {"1241": ["SYDE 600"], "1249": ["SYDE 610"]}, // optional
        "program_context": {"program": "Systems Design Engineering", "specialization": "Artificial_Intelligence_Machine_Learning"} // optional
    }
    """
    if planner is None:
        return jsonify({"error": "Planner is not initialized."}), 500

    data = request.json
    if not data or 'course_code' not in data or 'term_code' not in data:
        return jsonify({"error": "Invalid input. 'course_code' and 'term_code' are required."}), 400

    current_plan = data.get('current_plan', {})
    program_context = data.get('program_context', None)
    result = planner.validate_move(data['course_code'], data['term_code'], current_plan, program_context)
    return jsonify(result)

@app.route('/api/v1/programs', methods=['GET'])
def get_programs():
    """
    Get list of all available engineering programs.
    """
    if planner is None:
        return jsonify({"error": "Planner is not initialized."}), 500
    
    programs = planner.engineering_program_loader.get_all_programs()
    return jsonify({"programs": programs})

@app.route('/api/v1/specializations', methods=['POST'])
def get_specializations():
    """
    Get list of specializations for a specific program.
    Expects: {"program": "Systems Design Engineering"}
    """
    if planner is None:
        return jsonify({"error": "Planner is not initialized."}), 500
    
    data = request.json
    if not data or 'program' not in data:
        return jsonify({"error": "Invalid input. 'program' is required."}), 400
    
    specializations = planner.engineering_program_loader.get_specializations(data['program'])
    return jsonify({"specializations": specializations})

@app.route('/api/v1/switch_program', methods=['POST'])
def switch_program():
    """
    Switch to a different engineering program and get updated course pool.
    Expects: {"program_name": "Chemical Engineering"}
    """
    if planner is None:
        return jsonify({"error": "Planner is not initialized."}), 500
    
    data = request.json
    if not data or 'program_name' not in data:
        return jsonify({"error": "Invalid input. 'program_name' is required."}), 400
    
    result = planner.switch_program(data['program_name'])
    
    if not result["success"]:
        return jsonify(result), 400
    
    # Return success response with program info
    return jsonify(result)

@app.route('/api/v1/course_info', methods=['POST'])
def get_course_info():
    """
    Get detailed information about a specific course including prerequisites.
    Expects: {"course_code": "SYDE 660"}
    """
    if planner is None:
        return jsonify({"error": "Planner is not initialized."}), 500
    
    data = request.json
    if not data or 'course_code' not in data:
        return jsonify({"error": "Invalid input. 'course_code' is required."}), 400
    
    course_code = data['course_code']
    course = planner.course_loader.get_course(course_code)
    
    if not course:
        return jsonify({"error": f"Course {course_code} not found."}), 404
    
    # Parse prerequisites and antirequisites
    from src.core.planner import EnhancedPrerequisiteParser
    parser = EnhancedPrerequisiteParser()
    requirements = parser.parse_requirements(course.requirements_description)
    
    # Get availability information
    availability = planner.course_loader.get_course_availability(course_code)
    
    course_info = {
        'course_code': course.course_code,
        'title': course.title,
        'description': course.description,
        'credit_weight': course.credit_weight,
        'requirements_description': course.requirements_description,
        'prerequisites': requirements.get('prerequisites', []),
        'antirequisites': requirements.get('antirequisites', []),
        'corequisites': requirements.get('corequisites', []),
        'level_requirements': requirements.get('level_requirements', []),
        'other_requirements': requirements.get('other_requirements', []),
        'availability': availability
    }
    
    return jsonify(course_info)

@app.route('/api/v1/requirements_display', methods=['POST'])
def get_formatted_requirements():
    """
    Get formatted requirements for better display.
    Expects: {"program": "Systems Design Engineering", "specialization": "Biomedical Systems"}
    """
    if planner is None:
        return jsonify({"error": "Planner is not initialized."}), 500
    
    data = request.json
    if not data or 'program' not in data:
        return jsonify({"error": "Invalid input. 'program' is required."}), 400
    
    try:
        # Generate a minimal plan to get requirements
        user_input = {
            'program': data['program'],
            'specialization': data.get('specialization'),
            'semesters': 3,  # Minimal for requirements calculation
            'start_term': '1249'  # Default term
        }
        
        plan = planner.plan_courses(user_input)
        
        if 'error' in plan:
            return jsonify({"error": plan['error']}), 400
        
        # Extract formatted requirements
        formatted_requirements = plan.get('formatted_requirements', {})
        display_text = planner.requirements_formatter.format_for_display(formatted_requirements)
        
        return jsonify({
            'formatted_requirements': formatted_requirements,
            'display_text': display_text,
            'program_info': plan.get('program_info', {})
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to format requirements: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': 'The requested URL was not found on the server.'}), 404 