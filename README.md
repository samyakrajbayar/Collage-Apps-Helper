# 🎓 College Application Assistant

A comprehensive Python-based tool to help students manage their college applications, track deadlines, organize essays, compare schools, and prepare for the entire college admission process.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Technical Details](#-technical-details)
- [File Structure](#-file-structure)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

### Core Modules

1. **📋 Application Tracker**
   - Store college applications with deadlines and requirements
   - Track application status (Not Started, In Progress, Submitted)
   - View applications sorted by deadline with days remaining
   - Update status and add notes for each application

2. **✍️ Personal Statement Helper**
   - Save and organize multiple essay drafts
   - Automatic word count and character analysis
   - Keyword frequency analysis
   - Detect filler words and suggest improvements
   - Store essays linked to specific colleges

3. **💰 Scholarship Finder**
   - Filter scholarships by GPA, major, and deadlines
   - CSV-based scholarship database
   - Eligibility checking based on user profile
   - Display matching scholarships with award amounts

4. **🏫 College Comparison Tool**
   - Compare colleges using custom "fit score" algorithm
   - Factors in SAT scores, budget, acceptance rates, and location
   - Rank schools based on personal preferences
   - Display comprehensive comparison table

5. **⏰ Deadline Notifier**
   - Automatic detection of urgent deadlines (within 7 days)
   - Email notification system with SMTP integration
   - Configurable reminder settings
   - Status-based filtering (excludes submitted applications)

6. **💵 Financial Aid Estimator**
   - Income-based financial aid calculation
   - Merit-based aid estimation using GPA
   - Net cost calculation with loan estimates
   - Detailed breakdown of aid packages

7. **📝 Essay Analyzer**
   - Advanced readability analysis using TextStat
   - Flesch Reading Ease and Grade Level scores
   - Sentence variety and length analysis
   - Vocabulary diversity metrics
   - Passive voice detection

8. **📄 Resume Formatter**
   - Interactive resume builder
   - PDF generation using ReportLab
   - Professional formatting with education and experience sections
   - Customizable templates

9. **🎤 Interview Prep Bot**
   - Practice with 10+ common college interview questions
   - Randomized question selection
   - Response length feedback
   - Save practice sessions for review

10. **🎯 Major Suggestion Quiz**
    - Personality and interest-based questionnaire
    - Weighted scoring system for 20+ majors
    - Top 3 major recommendations with detailed descriptions
    - Career pathway information for each major

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Internet connection (for initial setup and some features)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/college-application-assistant.git
cd college-application-assistant
```

### Step 2: Install Dependencies

**Option A: Automatic Installation (Recommended)**
```bash
python college_assistant.py
# Uncomment install_requirements() on first run
```

**Option B: Manual Installation**
```bash
pip install pandas requests beautifulsoup4 textstat nltk reportlab
```

### Required Packages

```
pandas>=1.3.0          # Data manipulation and CSV handling
requests>=2.25.0       # HTTP requests for web scraping
beautifulsoup4>=4.9.0  # HTML parsing for scholarship data
textstat>=0.7.0        # Text readability analysis
nltk>=3.6.0           # Natural language processing
reportlab>=3.5.0      # PDF generation for resumes
```

## 🚀 Quick Start

### First Run Setup

1. **Run the application:**
   ```bash
   python college_assistant.py
   ```

2. **Create sample data (optional):**
   ```python
   # Uncomment this line in the main section
   create_sample_data()
   ```

3. **Configure your profile:**
   - Choose option 11 (Setup & Configuration)
   - Select "Update user profile"
   - Enter your GPA, test scores, and preferences

4. **Set up email notifications:**
   - Choose option 11 (Setup & Configuration)
   - Select "Setup email notifications"
   - Enter your email and app password

## 📖 Usage Guide

### Main Menu Navigation

```
🎓 COLLEGE APPLICATION ASSISTANT 🎓
==================================================
1.  📋 Application Tracker
2.  ✍️  Personal Statement Helper
3.  💰 Scholarship Finder
4.  🏫 College Comparison Tool
5.  ⏰ Deadline Notifier
6.  💵 Financial Aid Estimator
7.  📝 Essay Analyzer
8.  📄 Resume Formatter
9.  🎤 Interview Prep Bot
10. 🎯 Major Suggestion Quiz
11. ⚙️  Setup & Configuration
12. ❌ Exit
```

### Common Workflows

#### Adding Your First Application
1. Select "Application Tracker" (Option 1)
2. Choose "Add new application"
3. Enter college details, deadline, and requirements
4. Set initial status and add notes

#### Writing and Analyzing Essays
1. Select "Personal Statement Helper" (Option 2)
2. Save your essay draft with title and content
3. Use "Essay Analyzer" (Option 7) for detailed feedback
4. Revise based on readability and vocabulary suggestions

#### Finding Scholarships
1. Update your user profile with GPA and major
2. Select "Scholarship Finder" (Option 3)
3. Review eligible scholarships and deadlines
4. Add scholarship deadlines to your application tracker

#### Comparing Colleges
1. Ensure your profile has SAT/ACT scores and budget
2. Select "College Comparison Tool" (Option 4)
3. Enter preferences and view ranked results
4. Use fit scores to guide your application list

## 🔧 Technical Details

### Database Schema

The application uses SQLite with three main tables:

**Applications Table:**
- College name, deadline, status
- Essay and recommendation requirements
- Application fees and notes

**Essays Table:**
- Title, content, word count
- Creation date and associated college
- Automatic analysis metrics

**User Profile Table:**
- Academic stats (GPA, SAT, ACT)
- Contact information for notifications
- Preferences (major, location, budget)

### File Structure

```
college-application-assistant/
├── college_assistant.py          # Main application file
├── college_assistant.db          # SQLite database (created on first run)
├── scholarships.csv              # Scholarship database
├── colleges.csv                  # College comparison data
├── .email_config                 # Email configuration (created during setup)
├── interview_practice.json       # Saved interview responses
├── *_resume.pdf                  # Generated resume files
└── README.md                     # This file
```

### Data Files Format

**scholarships.csv:**
```csv
name,amount,gpa_min,major,deadline
Merit Excellence Scholarship,5000,3.5,Any,2024-03-15
STEM Leadership Award,10000,3.7,STEM,2024-02-28
```

**colleges.csv:**
```csv
name,tuition,sat_avg,acceptance_rate,location,size
State University,25000,1250,0.65,CA,Large
Tech Institute,45000,1450,0.25,MA,Medium
```

## ⚙️ Configuration

### Email Setup

For Gmail users:
1. Enable 2-factor authentication
2. Generate an app password: [Google App Passwords](https://support.google.com/accounts/answer/185833)
3. Use app password instead of regular password

### Customization Options

**Adding New Scholarships:**
- Edit `scholarships.csv` directly
- Add columns: name, amount, gpa_min, major, deadline

**Adding New Colleges:**
- Edit `colleges.csv` directly
- Add columns: name, tuition, sat_avg, acceptance_rate, location, size

**Modifying Major Quiz:**
- Edit the `questions` list in `MajorSuggestionQuiz` class
- Adjust `major_descriptions` dictionary for new majors

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found" errors:**
```bash
# Install missing packages
pip install [package_name]

# Or reinstall all requirements
pip install -r requirements.txt
```

**2. Database errors:**
```bash
# Reset database if corrupted
# Use option 11 -> "Reset database" in the application
```

**3. Email notifications not working:**
- Check email/password configuration
- Verify app password for Gmail
- Ensure SMTP settings are correct

**4. PDF generation fails:**
```bash
# Reinstall ReportLab
pip uninstall reportlab
pip install reportlab
```

**5. NLTK data missing:**
```python
import nltk
nltk.download('punkt')
```

### Performance Tips

- **Large essay analysis:** Break very long essays into sections
- **Database performance:** Regularly clean old data using reset option
- **Memory usage:** Close and restart application periodically for large datasets

## 📊 Sample Data

The application includes sample data for testing:

- **3 sample college applications** with different deadlines
- **5 sample scholarships** with varying requirements
- **5 sample colleges** for comparison testing

To load sample data, uncomment `create_sample_data()` in the main section.

## 🔒 Privacy & Security

- **Local Storage:** All data stored locally in SQLite database
- **No Cloud Sync:** Data never leaves your computer
- **Email Security:** Passwords stored locally (use app passwords)
- **Data Export:** Easy to backup database file

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Made with ❤️ for students navigating the college application process**
