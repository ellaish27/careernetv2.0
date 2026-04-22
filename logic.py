# © CKS Tech & D@in Corp.

# Updated to handle 'N/A' grades for pending results
GRADE_POINTS = {
    'A': 6, 
    'B': 5, 
    'C': 4, 
    'D': 3, 
    'E': 2, 
    'O': 1, 
    'F': 0,
    'N/A': 0  # Added to handle pending/missing grades during registration
}

O_LEVEL_WEIGHTS = {
    '1': 0.3, '2': 0.3, 'A': 0.3, 'B': 0.3, 
    '3': 0.2, '4': 0.2, '5': 0.2, '6': 0.2, 'C': 0.2, 'D': 0.2,
    '7': 0.1, '8': 0.1, 'E': 0.1,
    '9': 0.0, 'F': 0.0
}

COURSE_DATABASE = [
    {
        "name": "Bachelor of Medicine and Surgery", "code": "MAM",
        "essential": ["Biology", "Chemistry"], "relevant": ["Math", "Physics"],
        "desirable": ["General Paper", "Sub-Maths"],
        "cutoffs": {"M": 49.7, "F": 46.3}
    },
    {
        "name": "Bachelor of Dental Surgery", "code": "BDS",
        "essential": ["Biology", "Chemistry"], "relevant": ["Physics", "Math"],
        "desirable": ["General Paper"],
        "cutoffs": {"M": 47.7, "F": 45.4}
    },
    {
        "name": "Bachelor of Science in Civil Engineering", "code": "CIV",
        "essential": ["Math", "Physics"], "relevant": ["Chemistry", "Economics", "Geography", "Technical Drawing"],
        "desirable": ["General Paper"],
        "cutoffs": {"M": 49.7, "F": 45.9}
    },
    {
        "name": "Bachelor of Laws", "code": "LAW",
        "essential": ["History", "Divinity", "Literature"], 
        "relevant": ["Economics", "Geography", "General Paper"],
        "desirable": ["Sub-Maths"],
        "cutoffs": {"M": 57.0, "F": 57.0}
    },
    {
        "name": "Bachelor of Science in Electrical Engineering", "code": "ELE",
        "essential": ["Math", "Physics"], "relevant": ["Chemistry", "Economics"],
        "desirable": ["General Paper"],
        "cutoffs": {"M": 48.9, "F": 43.8}
    },
    {
        "name": "Bachelor of Commerce", "code": "COE",
        "essential": ["Math", "Economics"], "relevant": ["Geography", "Physics", "Entrepreneurship"],
        "desirable": ["General Paper"],
        "cutoffs": {"M": 37.3, "F": 37.3}
    },
    {
        "name": "Bachelor of Science in Computer Science", "code": "CSC",
        "essential": ["Math"], 
        "relevant": ["Physics", "Economics", "Chemistry"],
        "desirable": ["General Paper"],
        "cutoffs": {"M": 38.0, "F": 43.1}
    },
    {
        "name": "Bachelor of Pharmacy",
        "code": "PHA",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Math", "Physics"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 48.9, "F": 46.1}
    },
    {
        "name": "Bachelor of Nursing Science",
        "code": "NUR",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Agriculture", "Economics", "Foods & Nutrition", "Maths", "Physics"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 44.7, "F": 43.3}
    },
    {
        "name": "Bachelor of Science in Medical Radiography",
        "code": "BMR",
        "essential": ["Biology", "Physics"],
        "relevant": ["A'Level Science Subjects"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 44.3, "F": 45.4}
    },
    {
        "name": "Bachelor of Environmental Health Science",
        "code": "BEH",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Mathematics", "Physics", "Economics", "Geography", "Agriculture"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 35.8, "F": 34.2}
    },
    {
        "name": "Bachelor of Veterinary Medicine",
        "code": "VET",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Maths", "Physics", "Agriculture", "Food & Nutrition"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 43.6, "F": 40.2}
    },
    {
        "name": "Bachelor of Biomedical Laboratory Technology",
        "code": "MLT",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["All A' Level Subjects"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 41.9, "F": 40.4}
    },
    {
        "name": "Bachelor of Science in Agriculture",
        "code": "AGR",
        "essential": ["Biology", "Chemistry", "Agriculture"],
        "relevant": ["Biology", "Agriculture", "Physics", "Chemistry", "Maths", "Geography"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 34.5, "F": 36.3}
    },
    {
        "name": "Bachelor of Science in Food Science and Technology",
        "code": "FST",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Physics", "Agriculture", "Foods & Nutrition", "Maths"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 36.6, "F": 36.9}
    },
    {
        "name": "Bachelor of Science in Agricultural Engineering",
        "code": "AGE",
        "essential": ["Mathematics", "Physics"],
        "relevant": ["Chemistry", "Agriculture", "Economics", "Technical Drawing"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 43.3, "F": 36.4}
    },
    {
        "name": "Bachelor of Agribusiness Management",
        "code": "AGM",
        "essential": ["Mathematics", "Biology", "Chemistry", "Physics", "Agriculture", "Geography", "Economics"],
        "relevant": ["Biology", "Chemistry", "Agriculture", "Geography", "Mathematics", "Physics", "Economics", "Entrepreneurship"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 35.0, "F": 35.1}
    },
    {
        "name": "Bachelor of Architecture",
        "code": "ARC",
        "essential": ["Mathematics", "Fine Art", "Technical Drawing"],
        "relevant": ["Economics", "Geography", "Physics", "Fine Art", "Technical Drawing", "Entrepreneurship"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 49.1, "F": 49.5}
    },
    {
        "name": "Bachelor of Science in Land Surveying and Geomatics",
        "code": "LSG",
        "essential": ["Mathematics", "Physics"],
        "relevant": ["Economics", "Geography", "Chemistry", "Fine Art", "Entrepreneurship", "Technical Drawing"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 47.0, "F": 43.7}
    },
    {
        "name": "Bachelor of Science in Mechanical Engineering",
        "code": "MEC",
        "essential": ["Mathematics", "Physics"],
        "relevant": ["Economics", "Chemistry", "Technical Drawing", "Entrepreneurship"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 47.9, "F": 43.0}
    },
    {
        "name": "Bachelor of Science in Quantity Surveying",
        "code": "SQS",
        "essential": ["Mathematics", "Physics", "Economics", "Geography", "Fine Art", "Technical Drawing"],
        "relevant": ["Economics", "Geography", "Physics", "Chemistry", "Fine Art", "Technical Drawing", "Entrepreneurship"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 42.1, "F": 44.8}
    },
    {
        "name": "Bachelor of Statistics",
        "code": "STA",
        "essential": ["Maths"],
        "relevant": ["Economics", "Physics", "Chemistry", "Biology", "Geography", "Entrepreneurship"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 29.7, "F": 29.7}
    },
    {
        "name": "Bachelor of Science in Actuarial Science",
        "code": "SAS",
        "essential": ["Maths"],
        "relevant": ["Economics", "Physics", "Geography", "Chemistry", "Entrepreneurship"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 25.3, "F": 25.3}
    },
    {
        "name": "Bachelor of Arts in Economics",
        "code": "ECO",
        "essential": ["Economics"],
        "relevant": ["Mathematics", "Physics", "Geography", "Entrepreneurship", "History", "Agriculture"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 28.4, "F": 28.4}
    },
    {
        "name": "Bachelor of Science with Education (Biological)",
        "code": "EDB",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Physics", "Mathematics"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 41.5, "F": 38.0}
    },
    {
        "name": "Bachelor of Science with Education (Physical)",
        "code": "EDP",
        "essential": ["Mathematics", "Physics", "Chemistry"],
        "relevant": ["Physics", "Chemistry", "Biology", "Economics", "Geography"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 42.8, "F": 37.7}
    },
    {
        "name": "Bachelor of Science with Education (Economics)",
        "code": "EEC",
        "essential": ["Mathematics", "Economics"],
        "relevant": ["Chemistry", "Physics", "Biology", "Geography"],
        "desirable": ["Computer Studies", "General Paper"],
        "cutoffs": {"M": 30.9, "F": 30.2}
    },
    {
        "name": "Bachelor of Fine Art",
        "code": "BFA",
        "essential": ["Fine Art", "Technical Drawing", "Music"],
        "relevant": ["Remaining A' Level Subjects"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 29.9, "F": 29.9}
    },
    {
        "name": "Bachelor of Arts in Music",
        "code": "MUS",
        "essential": ["All A' Level subjects"],
        "relevant": ["All A' Level subjects"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 14.7, "F": 14.7}
    },
    {
        "name": "Bachelor of Arts in Drama and Film",
        "code": "BDF",
        "essential": ["All A' Level Arts Subjects"],
        "relevant": ["All A' Level subjects"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 47.3, "F": 40.2}
    },
    {
        "name": "Bachelor of Science (Biological)",
        "code": "SCB",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Math", "Physics"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 26.8, "F": 26.5}
    },
    {
        "name": "Bachelor of Science (Physical)",
        "code": "SCP",
        "essential": ["Mathematics", "Physics", "Chemistry"],
        "relevant": ["Chemistry", "Biology", "Physics", "Economics"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 17.7, "F": 17.9}
    },
    {
        "name": "Bachelor of Science (Economics)",
        "code": "SEC",
        "essential": ["Mathematics", "Economics"],
        "relevant": ["Chemistry", "Physics", "Biology"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 15.9, "F": 17.3}
    },
    {
        "name": "Bachelor of Science in Industrial Chemistry",
        "code": "BIC",
        "essential": ["Chemistry", "Maths", "Physics"],
        "relevant": ["Biology", "Physics", "Mathematics"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 39.4, "F": 34.9}
    },
    {
        "name": "Bachelor of Science in Fisheries and Aquaculture",
        "code": "BFS",
        "essential": ["Chemistry", "Biology", "Agriculture"],
        "relevant": ["Math", "Physics", "Biology", "Chemistry", "Agriculture"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 22.4, "F": 22.6}
    },
    {
        "name": "Bachelor of Sports Science",
        "code": "BSP",
        "essential": ["Biology", "Physics", "Chemistry", "Agriculture"],
        "relevant": ["Economics", "Maths", "Physics", "Chemistry", "Biology", "Agriculture"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 21.2, "F": 21.3}
    },
    {
        "name": "Bachelor of Science in Conservation Biology",
        "code": "BCB",
        "essential": ["Biology", "Chemistry", "Agriculture"],
        "relevant": ["Geography", "Biology", "Physics", "Chemistry", "Agriculture"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 19.2, "F": 20.3}
    },
    {
        "name": "Bachelor of Science in Software Engineering",
        "code": "BSW",
        "essential": ["Maths", "Physics", "Economics", "Geography", "Chemistry", "Biology"],
        "relevant": ["Physics", "Chemistry", "Economics", "Geography", "Biology"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 44.7, "F": 40.2}
    },
    {
        "name": "Bachelor of Science in Biomedical Engineering",
        "code": "BBI",
        "essential": ["Maths", "Physics", "Biology"],
        "relevant": ["Physics", "Biology", "Chemistry", "Economics", "Technical Drawing"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 45.7, "F": 42.5}
    },
    {
        "name": "Bachelor of Cytotechnology",
        "code": "BYT",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Physics", "Maths", "Economics", "Agriculture", "F/Nutrition"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 39.8, "F": 37.9}
    },
    {
        "name": "Bachelor of Agricultural and Rural Innovation",
        "code": "BAR",
        "essential": ["Biology", "Chemistry", "Geography", "Agriculture"],
        "relevant": ["Chemistry", "Biology", "Physics", "Maths", "Economics", "Geography", "Foods & Nutrition", "Entrepreneurship", "Agriculture"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 31.3, "F": 31.3}
    },
    {
        "name": "Bachelor of Science in Human Nutrition",
        "code": "HUN",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Agriculture", "Foods & Nutrition", "Physics", "Maths", "Economics"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 38.6, "F": 38.0}
    },
    {
        "name": "Bachelor of Science in Petroleum Geoscience and Production",
        "code": "BPG",
        "essential": ["Chemistry", "Physics", "Mathematics"],
        "relevant": ["Biology", "Chemistry", "Physics", "Maths", "Economics", "Geography"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 39.9, "F": 43.5}
    },
    {
        "name": "Bachelor of Business Administration",
        "code": "ADM",
        "essential": ["Economics", "Entrepreneurship"],
        "relevant": ["Remaining A'Level Subjects"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 39.8, "F": 39.8}
    },
    {
        "name": "Bachelor of Social Work",
        "code": "SOW",
        "essential": ["All A' Level Subjects"],
        "relevant": ["All A' Level Subjects"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 48.7, "F": 43.7}
    },
    {
        "name": "Bachelor of Science in Speech and Language Therapy",
        "code": "BSL",
        "essential": ["Biology", "Chemistry"],
        "relevant": ["A'Level Science Subjects"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 40.3, "F": 37.1}
    },
    {
        "name": "Bachelor of Optometry",
        "code": "BPT",
        "essential": ["Biology", "Physics", "Mathematics"],
        "relevant": ["Chemistry", "Physics", "Mathematics"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 44.4, "F": 47.4}
    },
    {
        "name": "Bachelor of Science in Forestry",
        "code": "BOF",
        "essential": ["Biology", "Chemistry", "Agriculture", "Physics", "Mathematics", "Geography"],
        "relevant": ["Biology", "Chemistry", "Agriculture", "Physics", "Mathematics", "Geography", "Economics", "Entrepreneurship", "Technical Drawing", "Wood Work", "Metal Work"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 29.1, "F": 30.2}
    },
    {
        "name": "Bachelor of Information Systems and Technology",
        "code": "IST",
        "essential": ["Chemistry", "Physics", "Mathematics", "Economics", "Geography", "Entrepreneurship"],
        "relevant": ["All A' level subjects"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 36.9, "F": 36.9}
    },
    {
        "name": "Bachelor of Science in Water and Irrigation Engineering",
        "code": "BWE",
        "essential": ["Maths", "Physics"],
        "relevant": ["Chemistry"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 42.8, "F": 37.3}
    },
    {
        "name": "Bachelor of Science in Quantitative Economics",
        "code": "BQE",
        "essential": ["Maths", "Economics"],
        "relevant": ["Physics", "Geography", "Entrepreneurship"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 29.2, "F": 29.6}
    },
    {
        "name": "Bachelor of Science in Population Studies",
        "code": "BPS",
        "essential": ["All A' Level subjects"],
        "relevant": ["Remaining A' Level subjects"],
        "desirable": ["General Paper", "Sub-Maths", "Computer Studies"],
        "cutoffs": {"M": 15.0, "F": 15.0}
    },
    {
        "name": "Bachelor of Science in Land Economics",
        "code": "SLE",
        "essential": ["Mathematics", "Economics", "Geography", "Physics", "Fine Art", "Technical Drawing"],
        "relevant": ["Economics", "Geography", "Physics", "Chemistry", "Fine Art", "Entrepreneurship", "Technical Drawing"],
        "desirable": ["General Paper", "Computer Studies"],
        "cutoffs": {"M": 36.3, "F": 31.3}
    }
]

def normalize_grade(grade):
    """Helper to convert lowercase grades to uppercase for logic."""
    if grade is None:
        return ''
    return str(grade).upper().strip()

def calculate_olevel_bonus(grades_dict):
    """Calculates O-Level bonus based on UNEB criteria."""
    weights = []
    for sub, grade in grades_dict.items():
        g = normalize_grade(grade)
        w = O_LEVEL_WEIGHTS.get(g, 0.0)
        weights.append(w)
    
    weights.sort(reverse=True)
    top_10 = weights[:10]
    return round(sum(top_10), 1)

def compute_weight_for_course(student_a_levels, course, gender, subsidiaries_count):
    """Computes admission weight for a specific course. Handles 'N/A' grades as 0 points."""
    essential_subs = course['essential']
    student_essential_grades = []
    
    # Essential Subjects
    for sub in essential_subs:
        if sub in student_a_levels:
            grade = normalize_grade(student_a_levels[sub])
            # Returns 0 if grade is 'N/A' or unknown
            points = GRADE_POINTS.get(grade, 0)
            student_essential_grades.append(points)
    
    # If missing essential subjects, usually 0 weight (cannot qualify)
    if len(student_essential_grades) < len(essential_subs):
        # Logic check: usually requires 2 essential subs. If only 1 found, might return 0.
        # Assuming len(essential_subs) is usually 2 or 3.
        # If only 1 is found, weight is usually 0, but let's allow calculation if 1 exists.
        if len(student_essential_grades) == 0:
             return 0

    student_essential_grades.sort(reverse=True)
    essential_pts = sum(student_essential_grades[:2])
    essential_weight = essential_pts * 3
    
    # Relevant Subjects
    relevant_pts = 0
    for sub, grade in student_a_levels.items():
        if sub in course['relevant'] and sub not in essential_subs:
            g = normalize_grade(grade)
            pts = GRADE_POINTS.get(g, 0)
            if pts > relevant_pts:
                relevant_pts = pts
    
    relevant_weight = relevant_pts * 2
    
    # Desirable Subjects
    desirable_pts = 0
    for sub, grade in student_a_levels.items():
        if sub in course['desirable'] and sub not in essential_subs:
            g = normalize_grade(grade)
            pts = GRADE_POINTS.get(g, 0)
            if pts > desirable_pts:
                desirable_pts = pts
    
    desirable_weight = desirable_pts * 1
    sub_bonus = subsidiaries_count * 1.0
    gender_bonus = 1.5 if gender == 'F' else 0.0

    return essential_weight + relevant_weight + desirable_weight + sub_bonus + gender_bonus

def get_student_report(student_data):
    """Generates full eligibility report."""
    o_bonus = calculate_olevel_bonus(student_data['o_levels'])
    report = []

    for course in COURSE_DATABASE:
        a_level_weight = compute_weight_for_course(
            student_data['a_levels'], 
            course, 
            student_data['gender'], 
            student_data['subs']
        )
        
        if a_level_weight == 0:
            continue 

        total_weight = a_level_weight + o_bonus
        cutoff = course.get('cutoffs', {}).get(student_data['gender'])
        if cutoff is None:
            cutoff = 40.0
        
        status = "Not Qualified"
        gap = 0
        
        if total_weight >= cutoff:
            status = "Qualified"
        else:
            gap = round(cutoff - total_weight, 1)
            if gap <= 2.0:
                status = "Borderline"

        report.append({
            "course": course['name'],
            "code": course['code'],
            "weight": total_weight,
            "cutoff": cutoff,
            "status": status,
            "gap": gap,
            "essential_subs": course['essential'] 
        })
        
    status_order = {"Qualified": 0, "Borderline": 1, "Not Qualified": 2}
    report.sort(key=lambda x: (status_order[x['status']], -x['weight']))
    
    return report, o_bonus

def predict_requirements(student_data, course_code):
    """Calculates what grades are needed to qualify for a specific course."""
    course = next((c for c in COURSE_DATABASE if c['code'] == course_code), None)
    if not course:
        return None

    o_bonus = calculate_olevel_bonus(student_data['o_levels'])
    current_a_level_weight = compute_weight_for_course(
        student_data['a_levels'], course, student_data['gender'], student_data['subs']
    )
    
    if current_a_level_weight == 0:
        missing = [s for s in course['essential'] if s not in student_data['a_levels']]
        return {
            "needed": f"Missing essential subjects: {', '.join(missing)}",
            "suggestions": ["This course requires specific subjects not currently offered."],
            "gap": 0
        }

    total_weight = current_a_level_weight + o_bonus
    cutoff = course['cutoffs'].get(student_data['gender'])
    
    if cutoff is not None and total_weight >= cutoff:
        return {"needed": "Already Qualified", "suggestions": [], "gap": 0}

    gap = round(cutoff - total_weight, 1)
    suggestions = []
    
    # Generate suggestions for improvement
    for sub in course['essential']:
        if sub in student_data['a_levels']:
            current_grade = normalize_grade(student_data['a_levels'][sub])
            current_pts = GRADE_POINTS.get(current_grade, 0)
            if current_pts < 6:
                suggestions.append(f"Improve {sub} grades (currently {current_grade}, needs +{gap} weight points).")

    return {
        "needed": f"Need {gap} more points to reach cutoff.",
        "suggestions": suggestions,
        "gap": gap
    }