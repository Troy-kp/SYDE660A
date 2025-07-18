import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional

# --- Configuration ---
COURSE_DATA_FOLDER = Path("../API_course_data_filtered/SYDE")
PROGRAM_RULES_FILE = Path("syde_programs_structured.json")
INPUT_FILE = Path("input.json")
OUTPUT_FILE = Path("output.json")
SEM_CAPACITY = [3, 3, 2]
TERM_MAP = {1: "Winter", 5: "Spring", 9: "Fall"}


# --- Helper Functions ---
def next_term_code(code: str) -> str:
    """Calculates the next term code (e.g., '1249' -> '1251')."""
    year_code = int(code[:-1])
    term_digit = int(code[-1])
    if term_digit == 9: return str(year_code + 1) + '1'
    return str(year_code) + str(term_digit + 4)


def term_sequence(start: str, n: int) -> List[str]:
    """Generates a sequence of n term codes."""
    seq, current_code = [start], start
    for _ in range(n - 1):
        current_code = next_term_code(current_code)
        seq.append(current_code)
    return seq


def human_term(tc: str) -> str:
    """Converts a term code to a readable string (e.g., '1249' -> 'Fall 2024')."""
    year, term_digit = int(tc[:-1]), int(tc[-1])
    return f"{TERM_MAP[term_digit]} {1900 + year}"


def calculate_min_terms(total_courses: int, capacity: List[int]) -> int:
    """Calculates the minimum number of terms to complete a number of courses."""
    if total_courses <= 0: return 0
    courses_done, terms_needed = 0, 0
    while courses_done < total_courses:
        courses_done += capacity[terms_needed % len(capacity)]
        terms_needed += 1
    return terms_needed


def load_offerings(term_codes: List[str], folder: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Loads course offerings, predicting future terms based on the previous year."""
    offers = {}
    for tc in term_codes:
        file_path = folder / f"{tc}.json"
        status = "Confirmed"
        if not file_path.exists():
            try:
                past_tc = str(int(tc[:-1]) - 1) + tc[-1]
                file_path = folder / f"{past_tc}.json"
                if file_path.exists():
                    status = f"Predicted (from {human_term(past_tc)})"
                else:
                    continue
            except (ValueError, IndexError):
                continue

        data = json.loads(file_path.read_text(encoding="utf-8"))
        for c in data:
            is_grad = c.get('associatedAcademicCareer') == 'GRD'
            catalog = c.get('catalogNumber', '')
            is_500 = isinstance(catalog, str) and catalog.startswith('5')
            if not (is_grad or is_500): continue

            code = f"{c['subjectCode']} {catalog}"
            if code not in offers: offers[code] = []
            offers[code].append({"term": tc, "status": status, "title": c.get('title', 'No Title')})
    return offers


def generate_plan(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """Main logic to generate the structured course plan."""
    program_name = user_input.get("program_name")
    specialization_name = user_input.get("specialization_name")
    start_term = user_input.get("start_term")
    num_terms = user_input.get("num_terms")

    # --- Load Rules ---
    all_rules = json.loads(PROGRAM_RULES_FILE.read_text(encoding="utf-8"))
    program_rules = next((p for p in all_rules if p['program_name'] == program_name), None)
    if not program_rules: return {"error": f"Program '{program_name}' not found."}

    # --- Minimum Term Validation ---
    total_courses_required = program_rules.get('degree_rules', {}).get('total_courses', 8)
    min_terms = calculate_min_terms(total_courses_required, SEM_CAPACITY)
    if num_terms < min_terms:
        return {
            "error": f"To complete {total_courses_required} courses, you need at least {min_terms} terms. You planned for only {num_terms}."}

    # --- Find Specialization Rules (if any) ---
    spec_rules = {}
    if specialization_name and program_rules.get('specializations'):
        spec_rules = next((s for s in program_rules['specializations'] if s['name'] == specialization_name), None)
        if not spec_rules: return {"error": f"Specialization '{specialization_name}' not found."}

    # --- Generate Course Pool ---
    terms = term_sequence(start_term, num_terms)
    offerings = load_offerings(terms, COURSE_DATA_FOLDER)

    def build_course_info(code):
        course_offerings = offerings.get(code, [])
        title = course_offerings[0]['title'] if course_offerings else "Unknown Title"
        return {"code": code, "title": title, "offered_in": course_offerings}

    # Combine compulsory courses from both degree and specialization
    program_compulsory = program_rules.get('degree_rules', {}).get('compulsory_courses', [])
    spec_compulsory = spec_rules.get('requirements', {}).get('compulsory_courses', [])
    all_compulsory = sorted(list(set(program_compulsory + spec_compulsory)))

    pool = {
        "compulsory_fixed": [build_course_info(c) for c in all_compulsory],
        "compulsory_choices": [], "electives": []
    }

    # Populate choices and electives based on specialization
    for rule in spec_rules.get('requirements', {}).get('compulsory_choices', []):
        pool['compulsory_choices'].append({"group_name": rule['group_name'], "n_to_choose": rule['n_to_choose'],
                                           "courses": [build_course_info(c) for c in rule['courses']]})
    for rule in spec_rules.get('requirements', {}).get('elective_rules', []):
        pool['electives'].append(rule)  # This part is already well-structured for the front-end

    return {
        "success": True,
        "program": program_name, "specialization": specialization_name or "None",
        "planning_window": [human_term(t) for t in terms],
        "degree_rules": program_rules.get('degree_rules', {}),
        "course_pool": pool
    }


def main():
    """Main function to run the backend process."""
    try:
        user_input = json.loads(INPUT_FILE.read_text(encoding='utf-8'))
        print(f"Processing request for: {user_input.get('program_name')}...")
    except FileNotFoundError:
        output = {"error": f"Input file not found at '{INPUT_FILE}'."}
        print(output['error'])
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4)
        return
    except json.JSONDecodeError:
        output = {"error": f"Could not decode JSON from '{INPUT_FILE}'."}
        print(output['error'])
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4)
        return

    output_data = generate_plan(user_input)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    if "error" in output_data:
        print(f"Processing failed: {output_data['error']}")
    else:
        print(f"Successfully generated course plan. Output written to '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    main()