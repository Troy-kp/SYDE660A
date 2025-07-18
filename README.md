# UW Course Recommendation System

A comprehensive course recommendation system for University of Waterloo students, designed to help with course selection, specialization planning, and certificate completion.

## 🎯 Project Overview

Based on your problem definition for the UW Flow portal, this system addresses the need for:
- **Centralized course information** from UW's official APIs
- **Intelligent course recommendations** based on program requirements, interests, and completed courses  
- **Specialization guidance** for certificates and advanced programs
- **User-friendly search and discovery** of relevant courses

## 📁 Project Structure

```
├── 01_CourseData/              # Course data collection via UW API
├── 02_ProgramData/             # Program requirements scraping
├── 03_DataBase/                # Database storage (if needed)
├── 05_RecommendationEngine/    # AI-powered recommendation system
├── 06_WebAPI/                  # Flask API for frontend integration
├── final_verified_course_data/ # Processed course data by subject
├── requirements.txt            # Python dependencies
├── test_system.py             # Test suite
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Your Current Data

```bash
python test_system.py
```

This will verify that your existing course data can be loaded and processed.

### 3. Scrape Detailed Program Requirements

```bash
cd 02_ProgramData
python 04_detailed_program_scraper.py
```

This creates `detailed_program_requirements.json` with specific program information.

### 4. Start the API Server

```bash
cd 06_WebAPI
python app.py
```

The API will be available at `http://localhost:5000`

## 🔗 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/programs` | GET | List available programs |
| `/api/subjects` | GET | List course subjects |
| `/api/courses/<subject>` | GET | Get courses by subject |
| `/api/recommend` | POST | Get course recommendations |
| `/api/specializations/<name>` | POST | Get specialization recommendations |
| `/api/course/<code>` | GET | Get course details |
| `/api/search?q=<query>` | GET | Search courses |

### Example Usage

**Get Recommendations:**
```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "program": "Systems Design Engineering",
    "degree": "MASc",
    "completed_courses": ["SYDE600"],
    "interests": ["machine learning", "robotics"],
    "term": "Winter 2025"
  }'
```

**Search Courses:**
```bash
curl "http://localhost:5000/api/search?q=machine%20learning"
```

## 🧠 Recommendation Engine Features

### 1. Multi-Factor Scoring
- **Program Requirements** (Score: 10.0) - Courses required for your program
- **Interest Matching** (Score: 7.0) - Courses matching your interests
- **Prerequisite Chain** (Score: 5.0) - Natural next steps from completed courses

### 2. Specialization Support
Pre-configured specializations:
- Machine Learning & AI
- Robotics & Control Systems  
- Biomedical Engineering
- Human Factors & Ergonomics

### 3. Intelligent Filtering
- Excludes already completed courses
- Considers term availability
- Respects prerequisites
- Weights by relevance

## 🎓 Specialization & Certificate Planning

### For SYDE Students

The system helps with:
- **Core course selection** based on MASc/MEng requirements
- **Specialization tracks** in AI, robotics, biomedical, etc.
- **Research area alignment** with faculty and labs
- **Cross-departmental courses** for interdisciplinary learning

### Certificate Programs

Future enhancements will include:
- Graduate certificates in specific domains
- Professional development tracks
- Industry-relevant skill building
- Pathway planning for PhD programs

## 📊 Data Sources

### Current Integration
- ✅ **UW Open Data API** - Official course information
- ✅ **Academic Calendar** - Program requirements  
- ✅ **Course Descriptions** - Detailed content information

### Planned Integration
- 🔄 **Faculty Research Areas** - Research-course alignment
- 🔄 **Course Evaluations** - Student feedback data
- 🔄 **Industry Skills** - Job market relevance
- 🔄 **Prerequisites Graph** - Learning pathways

## 🛠 Development Roadmap

### Phase 1: Foundation ✅
- [x] Course data collection
- [x] Basic recommendation engine
- [x] API framework
- [x] Testing infrastructure

### Phase 2: Enhancement 🔄
- [ ] Advanced program requirements parsing
- [ ] Machine learning-based recommendations
- [ ] User preference learning
- [ ] Course difficulty estimation

### Phase 3: Integration 📅
- [ ] Frontend web application
- [ ] User authentication
- [ ] Personal dashboards
- [ ] Mobile responsiveness

### Phase 4: Intelligence 📅
- [ ] Natural language course queries
- [ ] Academic planning assistant
- [ ] Graduation timeline optimization
- [ ] Career path recommendations

## 🔧 Customization

### Adding New Specializations

Edit `05_RecommendationEngine/course_recommender.py`:

```python
specialization_keywords = {
    'your_specialization': ['keyword1', 'keyword2', 'keyword3'],
    # ... existing specializations
}
```

### Modifying Scoring Weights

Adjust scoring in the `recommend_courses` method:

```python
# Program requirements (highest priority)
'score': 10.0,  # Adjust this value

# Interest-based courses  
'score': 7.0,   # Adjust this value

# Prerequisite-based courses
'score': 5.0,   # Adjust this value
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python test_system.py
```

Expected output:
- ✅ Data loading verification
- ✅ Recommendation generation
- ✅ Specialization suggestions  
- ✅ Course search functionality

## 🤝 Contributing

This system is designed to be:
- **Modular** - Easy to extend with new features
- **Scalable** - Can handle additional universities/programs
- **Maintainable** - Clean code structure and documentation

### Adding Support for New Programs

1. Update the program scraper in `02_ProgramData/`
2. Add program-specific logic in the recommendation engine
3. Test with the new program data

### Enhancing Recommendations

1. Modify scoring algorithms in `course_recommender.py`
2. Add new data sources for enriched recommendations
3. Implement machine learning models for personalization

## 📈 Next Steps for Your Project

Based on your problem definition, here are the immediate next steps:

### 1. Data Enhancement
```bash
# Scrape detailed program requirements
python 02_ProgramData/04_detailed_program_scraper.py

# Verify data quality
python test_system.py
```

### 2. API Testing
```bash
# Start the server
python 06_WebAPI/app.py

# Test endpoints
curl http://localhost:5000/api/health
curl http://localhost:5000/api/subjects
```

### 3. Frontend Integration
- Connect to the API endpoints from your web frontend
- Implement user profile management
- Add recommendation display components
- Create course search and filtering

### 4. User Experience
- Design intuitive recommendation interfaces
- Add explanation for why courses are recommended
- Implement filtering by term, difficulty, workload
- Create academic planning tools

## 📞 Support

For questions about:
- **API Usage** - Check the endpoint documentation above
- **Data Issues** - Verify course data files are properly formatted
- **Recommendations** - Adjust scoring weights and keywords
- **Integration** - Ensure CORS is properly configured

## 🎉 Success Metrics

Your system will be successful when:
- ✅ Students can find relevant courses quickly
- ✅ Specialization planning becomes intuitive  
- ✅ Course discovery improves academic outcomes
- ✅ Information access time is significantly reduced

This aligns with your original goals of improving efficiency, reducing confusion, and enhancing the UW student experience! 