#!/usr/bin/env python3
"""
Requirements Formatter
======================
Format and structure program requirements for better readability and user understanding.
"""

from typing import Dict, List, Any, Optional

class RequirementsFormatter:
    """Format program requirements into structured, user-friendly display"""
    
    def __init__(self):
        pass
    
    def format_requirements_summary(self, requirements: Dict[str, Any], specialization: Optional[str] = None) -> Dict[str, Any]:
        """
        Format requirements into a structured summary for display
        
        Returns:
            {
                'program_overview': {...},
                'core_requirements': [...],
                'specialization_requirements': [...],
                'elective_requirements': [...],
                'constraints': {...}
            }
        """
        total_courses = requirements.get('total_courses', 8)
        
        # Program overview
        program_overview = {
            'total_courses': total_courses,
            'specialization': specialization,
            'degree_type': 'Master of Engineering (MEng)'
        }
        
        # Core requirements (compulsory courses)
        core_requirements = self._format_core_requirements(requirements)
        
        # Specialization requirements (compulsory choices specific to specialization)
        specialization_requirements = self._format_specialization_requirements(requirements, specialization)
        
        # Elective requirements
        elective_requirements = self._format_elective_requirements(requirements)
        
        # Constraints
        constraints = self._format_constraints(requirements)
        
        return {
            'program_overview': program_overview,
            'core_requirements': core_requirements,
            'specialization_requirements': specialization_requirements,
            'elective_requirements': elective_requirements,
            'constraints': constraints
        }
    
    def _format_core_requirements(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format core compulsory requirements"""
        core_reqs = []
        
        compulsory_courses = requirements.get('compulsory_courses', [])
        if compulsory_courses:
            core_reqs.append({
                'type': 'compulsory',
                'title': 'Required Core Courses',
                'description': 'These courses are required for all students and appear with "Required" tags in the course pool',
                'courses': compulsory_courses,
                'count': len(compulsory_courses),
                'tag_info': {
                    'tag': 'Required',
                    'color': '#dc3545',
                    'description': 'Red tags in course pool'
                }
            })
        
        return core_reqs
    
    def _format_specialization_requirements(self, requirements: Dict[str, Any], specialization: Optional[str] = None) -> List[Dict[str, Any]]:
        """Format specialization-specific requirements"""
        spec_reqs = []
        
        compulsory_choices = requirements.get('compulsory_choices', [])
        for choice in compulsory_choices:
            group_name = choice.get('group_name', '')
            # Skip basic graduate workshop choice - focus on specialization-specific choices
            if 'Graduate Workshop' in group_name and not specialization:
                continue
                
            spec_reqs.append({
                'type': 'compulsory_choice',
                'title': group_name,
                'description': f'Choose {choice.get("n_to_choose", 1)} from the available options',
                'courses': choice.get('courses', []),
                'selection_count': choice.get('n_to_choose', 1),
                'count': len(choice.get('courses', [])),
                'tag_info': {
                    'tag': 'Core',
                    'color': '#fd7e14',
                    'description': 'Orange tags in course pool'
                }
            })
        
        # Add elective requirements from specialization
        elective_requirements = requirements.get('elective_requirements', [])
        for elective_rule in elective_requirements:
            # Focus on specialization-specific electives
            group_name = elective_rule.get('group_name', 'Specialization Electives')
            if 'AI' in group_name or 'Machine Learning' in group_name or specialization and 'AI' in specialization:
                spec_reqs.append({
                    'type': 'elective_choice',
                    'title': group_name,
                    'description': f'Choose {elective_rule.get("n_to_choose", 1)} from specialization electives',
                    'courses': elective_rule.get('courses', []),
                    'selection_count': elective_rule.get('n_to_choose', 1),
                    'count': len(elective_rule.get('courses', [])),
                    'tag_info': {
                        'tag': 'Elective',
                        'color': '#28a745',
                        'description': 'Green tags in course pool'
                    }
                })
        
        return spec_reqs
    
    def _format_elective_requirements(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format elective requirements"""
        elective_reqs = []
        
        for elective_group in requirements.get('elective_requirements', []):
            group_name = elective_group.get('group_name', '')
            courses = elective_group.get('courses', [])
            n_to_choose = elective_group.get('n_to_choose', 1)
            
            if 'Engineering graduate courses' in group_name:
                # This is the general elective requirement
                elective_reqs.append({
                    'type': 'general_electives',
                    'title': 'General Graduate Electives',
                    'description': f'Choose {n_to_choose} additional engineering graduate courses from any department. These appear with "Graduate" tags in the course pool.',
                    'n_to_choose': n_to_choose,
                    'courses': [],  # No specific course list
                    'note': 'Must satisfy level and departmental constraints',
                    'tag_info': {
                        'tag': 'Graduate',
                        'color': '#6f42c1',
                        'description': 'Purple tags in course pool'
                    }
                })
            else:
                # Specialization-specific electives
                elective_reqs.append({
                    'type': 'specialization_electives',
                    'title': self._clean_group_name(group_name),
                    'description': f'Choose {n_to_choose} from the specialization elective list. These appear with "Elective" tags in the course pool.',
                    'courses': courses,
                    'n_to_choose': n_to_choose,
                    'note': elective_group.get('description', '') if 'level course' in elective_group.get('description', '') else None,
                    'tag_info': {
                        'tag': 'Elective',
                        'color': '#28a745',
                        'description': 'Green tags in course pool'
                    }
                })
        
        return elective_reqs
    
    def _format_constraints(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Format program constraints"""
        constraints = {}
        
        program_constraints = requirements.get('constraints', {})
        
        # Level constraints
        level_constraints = program_constraints.get('level_constraints', {})
        if level_constraints:
            constraints['level_limits'] = {
                'max_500_level': level_constraints.get('max_500_level', 2),
                'description': level_constraints.get('description', '')
            }
        
        # Departmental constraints
        dept_constraints = program_constraints.get('departmental_constraints', {})
        if dept_constraints:
            constraints['departmental_requirements'] = {
                'min_syde_courses': dept_constraints.get('min_syde_courses', 2),
                'description': dept_constraints.get('description', '')
            }
        
        return constraints
    
    def _clean_group_name(self, group_name: str) -> str:
        """Clean and format group names for display"""
        # Remove redundant phrases
        clean_name = group_name.replace('Choose at least', '').replace('from:', '').strip()
        
        # Extract the meaningful part
        if ':' in clean_name:
            clean_name = clean_name.split(':', 1)[0].strip()
        
        return clean_name or 'Specialized Courses'
    
    def format_for_display(self, formatted_requirements: Dict[str, Any]) -> str:
        """Convert formatted requirements to readable text for display"""
        lines = []
        
        # Program overview
        overview = formatted_requirements['program_overview']
        lines.append(f"📚 **{overview['degree_type']}**")
        if overview['specialization']:
            lines.append(f"🎯 **Specialization:** {overview['specialization']}")
        lines.append(f"📖 **Total Courses Required:** {overview['total_courses']}")
        lines.append("")
        
        # Core requirements
        core_reqs = formatted_requirements['core_requirements']
        if core_reqs:
            lines.append("## 🎯 Core Requirements")
            for req in core_reqs:
                lines.append(f"**{req['title']}:** {', '.join(req['courses'])}")
                lines.append(f"*{req['description']}*")
                lines.append("")
        
        # Specialization requirements
        spec_reqs = formatted_requirements['specialization_requirements']
        if spec_reqs:
            lines.append("## 🔬 Specialization Requirements")
            for req in spec_reqs:
                lines.append(f"**{req['title']}** (Choose {req['selection_count']})")
                if req.get('description'):
                    lines.append(f"*{req['description']}*")
                if req.get('courses'):
                    lines.append(f"Options: {', '.join(req['courses'])}")
                if req.get('note'):
                    lines.append(f"Note: {req['note']}")
                lines.append("")
        
        # Elective requirements
        elective_reqs = formatted_requirements['elective_requirements']
        if elective_reqs:
            lines.append("## 📚 Elective Requirements")
            for req in elective_reqs:
                lines.append(f"**{req['title']}** (Choose {req['n_to_choose']})")
                lines.append(f"*{req['description']}*")
                if req.get('courses'):
                    lines.append(f"Available courses: {', '.join(req['courses'])}")
                if req.get('note'):
                    lines.append(f"⚠️ {req['note']}")
                lines.append("")
        
        # Constraints
        constraints = formatted_requirements['constraints']
        if constraints:
            lines.append("## ⚠️ Important Constraints")
            if 'level_limits' in constraints:
                level_limit = constraints['level_limits']
                lines.append(f"• **500-Level Limit:** Maximum {level_limit['max_500_level']} courses at 500-level")
            if 'departmental_requirements' in constraints:
                dept_req = constraints['departmental_requirements']
                lines.append(f"• **SYDE Requirement:** Minimum {dept_req['min_syde_courses']} SYDE courses")
        
        return '\n'.join(lines) 