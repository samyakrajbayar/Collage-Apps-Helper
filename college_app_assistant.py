#!/usr/bin/env python3
"""
College Application Assistant
A comprehensive tool to help students manage their college applications
"""

import sqlite3
import pandas as pd
import json
import os
import smtplib
import re
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from collections import Counter
import requests
from bs4 import BeautifulSoup
import textstat
import nltk
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import csv

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class DatabaseManager:
    def __init__(self, db_name="college_assistant.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                college_name TEXT NOT NULL,
                deadline DATE NOT NULL,
                status TEXT DEFAULT 'Not Started',
                essay_required BOOLEAN DEFAULT 1,
                recommendations_required INTEGER DEFAULT 2,
                test_scores_required TEXT DEFAULT 'SAT/ACT',
                application_fee REAL DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Essays table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS essays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                word_count INTEGER,
                created_date DATE DEFAULT CURRENT_DATE,
                college_name TEXT
            )
        ''')
        
        # User profile table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY,
                gpa REAL,
                sat_score INTEGER,
                act_score INTEGER,
                email TEXT,
                phone TEXT,
                major_interest TEXT,
                location_preference TEXT,
                budget REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=None):
        """Execute a database query"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result

class ApplicationTracker:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def add_application(self):
        """Add a new college application"""
        print("\n=== Add New Application ===")
        college_name = input("College name: ")
        deadline = input("Application deadline (YYYY-MM-DD): ")
        status = input("Status (Not Started/In Progress/Submitted): ") or "Not Started"
        essay_required = input("Essay required? (y/n): ").lower() == 'y'
        recs_required = int(input("Number of recommendations required: ") or "2")
        test_scores = input("Test scores required (SAT/ACT/Both): ") or "SAT/ACT"
        app_fee = float(input("Application fee ($): ") or "0")
        notes = input("Additional notes: ")
        
        query = '''
            INSERT INTO applications 
            (college_name, deadline, status, essay_required, recommendations_required, 
             test_scores_required, application_fee, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.db.execute_query(query, (college_name, deadline, status, essay_required, 
                                    recs_required, test_scores, app_fee, notes))
        print(f"✅ Added application for {college_name}")
    
    def view_applications(self):
        """View all applications with upcoming deadlines"""
        query = '''
            SELECT college_name, deadline, status, essay_required, 
                   recommendations_required, application_fee
            FROM applications 
            ORDER BY deadline ASC
        '''
        results = self.db.execute_query(query)
        
        if not results:
            print("No applications found.")
            return
        
        print("\n=== Your College Applications ===")
        print(f"{'College':<25} {'Deadline':<12} {'Status':<15} {'Essay':<6} {'Recs':<5} {'Fee':<8}")
        print("-" * 80)
        
        for row in results:
            college, deadline, status, essay, recs, fee = row
            deadline_obj = datetime.strptime(deadline, '%Y-%m-%d')
            days_left = (deadline_obj - datetime.now()).days
            
            essay_text = "Yes" if essay else "No"
            deadline_display = f"{deadline} ({days_left}d)"
            
            print(f"{college:<25} {deadline_display:<12} {status:<15} {essay_text:<6} {recs:<5} ${fee:<7.0f}")
    
    def update_status(self):
        """Update application status"""
        self.view_applications()
        college_name = input("\nEnter college name to update: ")
        new_status = input("New status (Not Started/In Progress/Submitted): ")
        
        query = "UPDATE applications SET status = ? WHERE college_name = ?"
        self.db.execute_query(query, (new_status, college_name))
        print(f"✅ Updated status for {college_name} to {new_status}")

class PersonalStatementHelper:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def save_essay(self):
        """Save essay draft"""
        print("\n=== Save Essay Draft ===")
        title = input("Essay title: ")
        college_name = input("College name (optional): ")
        print("Enter your essay content (type 'END' on a new line to finish):")
        
        content_lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            content_lines.append(line)
        
        content = '\n'.join(content_lines)
        word_count = len(content.split())
        
        query = '''
            INSERT INTO essays (title, content, word_count, college_name)
            VALUES (?, ?, ?, ?)
        '''
        self.db.execute_query(query, (title, content, word_count, college_name))
        print(f"✅ Saved essay '{title}' ({word_count} words)")
    
    def analyze_essay(self):
        """Analyze essay for improvements"""
        query = "SELECT id, title, content FROM essays ORDER BY created_date DESC"
        essays = self.db.execute_query(query)
        
        if not essays:
            print("No essays found. Save an essay first.")
            return
        
        print("\n=== Your Essays ===")
        for i, (essay_id, title, _) in enumerate(essays, 1):
            print(f"{i}. {title}")
        
        choice = int(input("\nSelect essay to analyze: ")) - 1
        if 0 <= choice < len(essays):
            essay_id, title, content = essays[choice]
            self._perform_analysis(title, content)
    
    def _perform_analysis(self, title, content):
        """Perform detailed essay analysis"""
        print(f"\n=== Analysis for '{title}' ===")
        
        # Basic stats
        words = content.split()
        sentences = content.split('.')
        
        print(f"Word count: {len(words)}")
        print(f"Character count: {len(content)}")
        print(f"Sentence count: {len(sentences)}")
        print(f"Average words per sentence: {len(words)/len(sentences):.1f}")
        
        # Readability
        try:
            flesch_score = textstat.flesch_reading_ease(content)
            grade_level = textstat.flesch_kincaid_grade(content)
            print(f"Readability score: {flesch_score:.1f}/100")
            print(f"Grade level: {grade_level:.1f}")
        except:
            print("Readability analysis unavailable")
        
        # Common filler words
        filler_words = ['very', 'really', 'quite', 'rather', 'pretty', 'just', 'actually']
        word_freq = Counter([word.lower().strip('.,!?') for word in words])
        
        print("\n--- Filler Word Analysis ---")
        for filler in filler_words:
            count = word_freq.get(filler, 0)
            if count > 0:
                print(f"'{filler}': {count} times")
        
        # Most frequent words
        print("\n--- Most Common Words ---")
        for word, count in word_freq.most_common(5):
            if len(word) > 3:  # Skip short words
                print(f"'{word}': {count} times")
        
        # Passive voice detection (simple)
        passive_indicators = ['was', 'were', 'been', 'being']
        passive_count = sum(word_freq.get(indicator, 0) for indicator in passive_indicators)
        print(f"\nPossible passive voice instances: {passive_count}")

class ScholarshipFinder:
    def __init__(self, db_manager):
        self.db = db_manager
        self.create_sample_scholarships()
    
    def create_sample_scholarships(self):
        """Create sample scholarship data"""
        scholarships = [
            {"name": "Merit Excellence Scholarship", "amount": 5000, "gpa_min": 3.5, "major": "Any", "deadline": "2024-03-15"},
            {"name": "STEM Leadership Award", "amount": 10000, "gpa_min": 3.7, "major": "STEM", "deadline": "2024-02-28"},
            {"name": "Community Service Grant", "amount": 2500, "gpa_min": 3.0, "major": "Any", "deadline": "2024-04-01"},
            {"name": "Engineering Innovation Prize", "amount": 7500, "gpa_min": 3.8, "major": "Engineering", "deadline": "2024-03-30"},
            {"name": "Liberal Arts Excellence", "amount": 4000, "gpa_min": 3.4, "major": "Liberal Arts", "deadline": "2024-05-15"},
        ]
        
        # Save to CSV for easy access
        df = pd.DataFrame(scholarships)
        df.to_csv('scholarships.csv', index=False)
    
    def find_scholarships(self):
        """Find eligible scholarships"""
        try:
            df = pd.read_csv('scholarships.csv')
        except FileNotFoundError:
            print("Scholarship database not found.")
            return
        
        print("\n=== Scholarship Finder ===")
        gpa = float(input("Your GPA: "))
        major = input("Your major interest (or 'Any'): ")
        
        # Filter scholarships
        eligible = df[df['gpa_min'] <= gpa]
        if major.lower() != 'any':
            eligible = eligible[(eligible['major'] == 'Any') | (eligible['major'].str.contains(major, case=False))]
        
        if eligible.empty:
            print("No eligible scholarships found.")
            return
        
        print(f"\n=== Eligible Scholarships ===")
        print(f"{'Name':<30} {'Amount':<10} {'GPA Req':<8} {'Major':<15} {'Deadline'}")
        print("-" * 80)
        
        for _, row in eligible.iterrows():
            print(f"{row['name']:<30} ${row['amount']:<9} {row['gpa_min']:<8} {row['major']:<15} {row['deadline']}")

class CollegeComparison:
    def __init__(self, db_manager):
        self.db = db_manager
        self.create_sample_colleges()
    
    def create_sample_colleges(self):
        """Create sample college data"""
        colleges = [
            {"name": "State University", "tuition": 25000, "sat_avg": 1250, "acceptance_rate": 0.65, "location": "CA", "size": "Large"},
            {"name": "Tech Institute", "tuition": 45000, "sat_avg": 1450, "acceptance_rate": 0.25, "location": "MA", "size": "Medium"},
            {"name": "Liberal Arts College", "tuition": 35000, "sat_avg": 1350, "acceptance_rate": 0.45, "location": "NY", "size": "Small"},
            {"name": "Community College", "tuition": 8000, "sat_avg": 1050, "acceptance_rate": 0.90, "location": "TX", "size": "Medium"},
            {"name": "Elite University", "tuition": 55000, "sat_avg": 1520, "acceptance_rate": 0.15, "location": "CT", "size": "Large"},
        ]
        
        df = pd.DataFrame(colleges)
        df.to_csv('colleges.csv', index=False)
    
    def compare_colleges(self):
        """Compare colleges based on user preferences"""
        try:
            df = pd.read_csv('colleges.csv')
        except FileNotFoundError:
            print("College database not found.")
            return
        
        print("\n=== College Comparison Tool ===")
        sat_score = int(input("Your SAT score: "))
        budget = float(input("Your budget (annual tuition): $"))
        location = input("Preferred location (state abbreviation, or 'Any'): ")
        
        # Calculate fit scores
        df['fit_score'] = 0
        
        # SAT score fit (closer to average = better fit)
        df['sat_diff'] = abs(df['sat_avg'] - sat_score)
        df['fit_score'] += (300 - df['sat_diff']) / 300 * 40  # 40 points max
        
        # Budget fit
        df['budget_fit'] = df['tuition'] <= budget
        df['fit_score'] += df['budget_fit'] * 30  # 30 points for affordability
        
        # Acceptance rate (higher = easier to get in)
        df['fit_score'] += df['acceptance_rate'] * 30  # 30 points max
        
        # Filter by location if specified
        if location.upper() != 'ANY':
            df = df[df['location'] == location.upper()]
        
        # Sort by fit score
        df = df.sort_values('fit_score', ascending=False)
        
        print(f"\n=== College Recommendations ===")
        print(f"{'College':<25} {'Tuition':<10} {'SAT Avg':<8} {'Accept%':<8} {'Fit Score'}")
        print("-" * 70)
        
        for _, row in df.head(5).iterrows():
            fit_score = f"{row['fit_score']:.1f}/100"
            acceptance = f"{row['acceptance_rate']*100:.0f}%"
            print(f"{row['name']:<25} ${row['tuition']:<9} {row['sat_avg']:<8} {acceptance:<8} {fit_score}")

class DeadlineNotifier:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def setup_email(self):
        """Setup email configuration"""
        print("\n=== Email Setup ===")
        email = input("Your email address: ")
        password = input("Your email password (use app password for Gmail): ")
        
        # Save to user profile
        query = '''
            INSERT OR REPLACE INTO user_profile (id, email) 
            VALUES (1, ?)
        '''
        self.db.execute_query(query, (email,))
        
        # Store password temporarily (in real app, use secure storage)
        with open('.email_config', 'w') as f:
            f.write(f"{email},{password}")
        
        print("✅ Email configuration saved")
    
    def check_deadlines(self):
        """Check for upcoming deadlines"""
        query = '''
            SELECT college_name, deadline, status 
            FROM applications 
            WHERE status != 'Submitted'
            ORDER BY deadline ASC
        '''
        results = self.db.execute_query(query)
        
        urgent_deadlines = []
        today = datetime.now().date()
        
        for college, deadline_str, status in results:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            days_left = (deadline - today).days
            
            if 0 <= days_left <= 7:  # Within a week
                urgent_deadlines.append((college, deadline, days_left, status))
        
        if urgent_deadlines:
            print(f"\n⚠️  URGENT DEADLINES ⚠️")
            for college, deadline, days_left, status in urgent_deadlines:
                print(f"• {college}: {deadline} ({days_left} days left) - Status: {status}")
            
            send_email = input("\nSend email reminder? (y/n): ").lower() == 'y'
            if send_email:
                self._send_email_reminder(urgent_deadlines)
        else:
            print("No urgent deadlines found.")
    
    def _send_email_reminder(self, deadlines):
        """Send email reminder"""
        try:
            with open('.email_config', 'r') as f:
                email, password = f.read().strip().split(',')
        except FileNotFoundError:
            print("Email not configured. Run setup_email first.")
            return
        
        # Create email content
        subject = "College Application Deadline Reminder"
        body = "Urgent college application deadlines:\n\n"
        
        for college, deadline, days_left, status in deadlines:
            body += f"• {college}: {deadline} ({days_left} days left) - Status: {status}\n"
        
        body += "\nDon't forget to submit your applications on time!"
        
        # Send email (simplified version)
        try:
            msg = MimeMultipart()
            msg['From'] = email
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain'))
            
            # This is a simplified example - replace with your SMTP settings
            print("📧 Email reminder sent! (In a real app, this would send via SMTP)")
            
        except Exception as e:
            print(f"Failed to send email: {e}")

class FinancialAidEstimator:
    def estimate_aid(self):
        """Estimate financial aid package"""
        print("\n=== Financial Aid Estimator ===")
        
        family_income = float(input("Annual family income: $"))
        gpa = float(input("Your GPA: "))
        tuition = float(input("College annual tuition: $"))
        
        # Simplified financial aid calculation
        # Based on income brackets
        if family_income < 30000:
            need_based_aid = min(tuition * 0.90, tuition - 2000)
        elif family_income < 60000:
            need_based_aid = min(tuition * 0.70, tuition - 5000)
        elif family_income < 100000:
            need_based_aid = min(tuition * 0.40, tuition - 10000)
        else:
            need_based_aid = min(tuition * 0.20, tuition - 20000)
        
        # Merit-based aid based on GPA
        if gpa >= 3.8:
            merit_aid = tuition * 0.25
        elif gpa >= 3.5:
            merit_aid = tuition * 0.15
        elif gpa >= 3.2:
            merit_aid = tuition * 0.10
        else:
            merit_aid = 0
        
        total_aid = min(need_based_aid + merit_aid, tuition * 0.95)  # Max 95% aid
        net_cost = tuition - total_aid
        estimated_loans = max(net_cost - (family_income * 0.10), 0)  # 10% of income expected
        
        print(f"\n=== Financial Aid Estimate ===")
        print(f"Annual Tuition:          ${tuition:,.2f}")
        print(f"Need-based Aid:          ${need_based_aid:,.2f}")
        print(f"Merit-based Aid:         ${merit_aid:,.2f}")
        print(f"Total Aid:               ${total_aid:,.2f}")
        print(f"Net Cost:                ${net_cost:,.2f}")
        print(f"Estimated Loans Needed:  ${estimated_loans:,.2f}")

class EssayAnalyzer:
    def analyze_readability(self, text):
        """Analyze essay readability"""
        print("\n=== Advanced Essay Analysis ===")
        
        # Readability scores
        flesch_score = textstat.flesch_reading_ease(text)
        grade_level = textstat.flesch_kincaid_grade(text)
        
        print(f"Flesch Reading Ease: {flesch_score:.1f}/100")
        if flesch_score >= 90:
            print("  → Very Easy to read")
        elif flesch_score >= 80:
            print("  → Easy to read")
        elif flesch_score >= 70:
            print("  → Fairly Easy to read")
        elif flesch_score >= 60:
            print("  → Standard")
        else:
            print("  → Difficult to read")
        
        print(f"Grade Level: {grade_level:.1f}")
        
        # Sentence variety
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        print(f"\n=== Sentence Analysis ===")
        print(f"Total sentences: {len(sentences)}")
        print(f"Average sentence length: {sum(sentence_lengths)/len(sentence_lengths):.1f} words")
        print(f"Shortest sentence: {min(sentence_lengths)} words")
        print(f"Longest sentence: {max(sentence_lengths)} words")
        
        # Vocabulary diversity
        words = [word.lower().strip('.,!?";') for word in text.split()]
        unique_words = set(words)
        diversity_ratio = len(unique_words) / len(words)
        
        print(f"\n=== Vocabulary Analysis ===")
        print(f"Total words: {len(words)}")
        print(f"Unique words: {len(unique_words)}")
        print(f"Vocabulary diversity: {diversity_ratio:.2f}")

class ResumeFormatter:
    def create_resume(self):
        """Create a formatted resume"""
        print("\n=== Resume Builder ===")
        
        # Collect information
        name = input("Full name: ")
        email = input("Email: ")
        phone = input("Phone: ")
        
        print("\nEducation (type 'done' when finished):")
        education = []
        while True:
            school = input("School name (or 'done'): ")
            if school.lower() == 'done':
                break
            degree = input("Degree/Program: ")
            year = input("Graduation year: ")
            gpa = input("GPA (optional): ")
            education.append({"school": school, "degree": degree, "year": year, "gpa": gpa})
        
        print("\nExperience/Activities (type 'done' when finished):")
        experience = []
        while True:
            title = input("Position/Activity title (or 'done'): ")
            if title.lower() == 'done':
                break
            organization = input("Organization: ")
            duration = input("Duration: ")
            description = input("Brief description: ")
            experience.append({"title": title, "org": organization, "duration": duration, "desc": description})
        
        # Generate PDF resume
        filename = f"{name.replace(' ', '_')}_resume.pdf"
        self._generate_pdf_resume(name, email, phone, education, experience, filename)
        print(f"✅ Resume saved as {filename}")
    
    def _generate_pdf_resume(self, name, email, phone, education, experience, filename):
        """Generate PDF resume using ReportLab"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        story.append(Paragraph(name, styles['Title']))
        story.append(Paragraph(f"{email} | {phone}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Education
        story.append(Paragraph("EDUCATION", styles['Heading2']))
        for edu in education:
            edu_text = f"<b>{edu['school']}</b> - {edu['degree']} ({edu['year']})"
            if edu['gpa']:
                edu_text += f" | GPA: {edu['gpa']}"
            story.append(Paragraph(edu_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Experience
        story.append(Paragraph("EXPERIENCE & ACTIVITIES", styles['Heading2']))
        for exp in experience:
            exp_text = f"<b>{exp['title']}</b> - {exp['org']} ({exp['duration']})"
            story.append(Paragraph(exp_text, styles['Normal']))
            story.append(Paragraph(exp['desc'], styles['Normal']))
            story.append(Spacer(1, 6))
        
        doc.build(story)

class InterviewPrepBot:
    def __init__(self):
        self.questions = [
            "Tell me about yourself.",
            "Why are you interested in our college?",
            "What are your greatest strengths?",
            "What challenges have you overcome?",
            "Where do you see yourself in 10 years?",
            "Why should we accept you?",
            "What questions do you have for us?",
            "Describe a time you showed leadership.",
            "What's your biggest weakness?",
            "How do you handle stress?"
        ]
    
    def practice_interview(self):
        """Conduct a practice interview"""
        print("\n=== College Interview Practice ===")
        print("I'll ask you common interview questions. Answer as if in a real interview.")
        print("Type 'skip' to move to the next question, 'quit' to end.\n")
        
        import random
        selected_questions = random.sample(self.questions, 5)
        
        responses = []
        
        for i, question in enumerate(selected_questions, 1):
            print(f"\nQuestion {i}: {question}")
            print("-" * 50)
            response = input("Your answer: ")
            
            if response.lower() == 'quit':
                break
            elif response.lower() == 'skip':
                continue
            
            responses.append({"question": question, "answer": response})
            
            # Basic feedback
            word_count = len(response.split())
            if word_count < 10:
                print("💡 Try to elaborate more in your response.")
            elif word_count > 100:
                print("💡 Consider being more concise.")
            else:
                print("✅ Good length for your response!")
        
        # Summary
        if responses:
            print(f"\n=== Practice Summary ===")
            print(f"Questions answered: {len(responses)}")
            avg_length = sum(len(r['answer'].split()) for r in responses) / len(responses)
            print(f"Average response length: {avg_length:.1f} words")
            
            # Save responses
            save = input("\nSave responses for review? (y/n): ").lower() == 'y'
            if save:
                with open('interview_practice.json', 'w') as f:
                    json.dump(responses, f, indent=2)
                print("✅ Responses saved to interview_practice.json")

class MajorSuggestionQuiz:
    def __init__(self):
        self.questions = [
            {
                "question": "What type of problems do you enjoy solving?",
                "options": {
                    "a": "Mathematical and logical puzzles",
                    "b": "Social and interpersonal issues", 
                    "c": "Creative and artistic challenges",
                    "d": "Scientific and research problems"
                },
                "weights": {
                    "a": {"Engineering": 3, "Math": 3, "Computer Science": 2},
                    "b": {"Psychology": 3, "Social Work": 3, "Business": 2},
                    "c": {"Art": 3, "English": 2, "Communications": 2},
                    "d": {"Biology": 3, "Chemistry": 3, "Physics": 2}
                }
            },
            {
                "question": "What work environment appeals to you?",
                "options": {
                    "a": "Laboratory or research facility",
                    "b": "Office with team collaboration",
                    "c": "Creative studio or outdoors",
                    "d": "Hospital or healthcare setting"
                },
                "weights": {
                    "a": {"Chemistry": 3, "Biology": 2, "Physics": 3},
                    "b": {"Business": 3, "Marketing": 2, "Management": 2},
                    "c": {"Art": 3, "Environmental Science": 2, "Architecture": 2},
                    "d": {"Nursing": 3, "Medicine": 3, "Psychology": 1}
                }
            },
            {
                "question": "Which subject did you enjoy most in school?",
                "options": {
                    "a": "Mathematics and Sciences",
                    "b": "History and Social Studies",
                    "c": "English and Literature",
                    "d": "Art and Music"
                },
                "weights": {
                    "a": {"Engineering": 2, "Math": 3, "Computer Science": 2, "Physics": 2},
                    "b": {"History": 3, "Political Science": 2, "Sociology": 2},
                    "c": {"English": 3, "Communications": 2, "Journalism": 2},
                    "d": {"Art": 3, "Music": 3, "Theater": 2}
                }
            }
        ]
    
    def take_quiz(self):
        """Take the major suggestion quiz"""
        print("\n=== Major Suggestion Quiz ===")
        print("Answer these questions to get personalized major recommendations.\n")
        
        major_scores = {}
        
        for i, q in enumerate(self.questions, 1):
            print(f"Question {i}: {q['question']}")
            for key, option in q['options'].items():
                print(f"  {key}) {option}")
            
            while True:
                answer = input("\nYour answer (a/b/c/d): ").lower()
                if answer in q['options']:
                    break
                print("Please enter a, b, c, or d")
            
            # Add weights to major scores
            if answer in q['weights']:
                for major, weight in q['weights'][answer].items():
                    major_scores[major] = major_scores.get(major, 0) + weight
        
        # Get top 3 recommendations
        top_majors = sorted(major_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        print(f"\n=== Your Top 3 Major Recommendations ===")
        
        major_descriptions = {
            "Engineering": "Design and build solutions to technical problems. High earning potential in various industries.",
            "Computer Science": "Develop software, apps, and digital solutions. Excellent job market and growth opportunities.",
            "Business": "Learn management, finance, and entrepreneurship. Versatile degree with many career paths.",
            "Psychology": "Study human behavior and mental processes. Can lead to counseling, research, or therapy careers.",
            "Biology": "Study living organisms and life processes. Foundation for medical, research, or environmental careers.",
            "Art": "Express creativity through various mediums. Can lead to design, fine arts, or creative industry careers.",
            "English": "Study literature, writing, and communication. Useful for law, journalism, or teaching careers.",
            "Math": "Study abstract concepts and problem-solving. Applicable to finance, research, and technology.",
            "Chemistry": "Study matter and chemical reactions. Essential for pharmaceuticals, research, and industry.",
            "Physics": "Study fundamental laws of nature. Important for research, engineering, and technology.",
            "History": "Study past events and their significance. Develops critical thinking for law, education, or research.",
            "Communications": "Study media, public relations, and information sharing. Useful for marketing and journalism.",
            "Nursing": "Provide healthcare and patient care. High demand field with job security.",
            "Medicine": "Diagnose and treat medical conditions. Requires extensive education but offers high rewards.",
            "Social Work": "Help individuals and communities solve problems. Meaningful work in social services.",
            "Marketing": "Promote products and services to consumers. Creative field with business applications.",
            "Environmental Science": "Study environmental problems and solutions. Growing field focused on sustainability.",
            "Political Science": "Study government, politics, and public policy. Useful for law, government, or advocacy.",
            "Sociology": "Study society and social behavior. Helps understand social issues and human interaction.",
            "Journalism": "Report news and information to the public. Important for media and communication industries.",
            "Architecture": "Design buildings and spaces. Combines creativity with technical skills.",
            "Music": "Study musical performance, composition, or theory. Can lead to performance or education careers.",
            "Theater": "Study dramatic arts and performance. Develops creativity and public speaking skills.",
            "Management": "Learn to lead teams and organizations. Essential for business leadership roles."
        }
        
        for i, (major, score) in enumerate(top_majors, 1):
            description = major_descriptions.get(major, "A field of study with various career opportunities.")
            print(f"\n{i}. {major} (Score: {score})")
            print(f"   {description}")

class CollegeApplicationAssistant:
    def __init__(self):
        self.db = DatabaseManager()
        self.app_tracker = ApplicationTracker(self.db)
        self.essay_helper = PersonalStatementHelper(self.db)
        self.scholarship_finder = ScholarshipFinder(self.db)
        self.college_comparison = CollegeComparison(self.db)
        self.deadline_notifier = DeadlineNotifier(self.db)
        self.aid_estimator = FinancialAidEstimator()
        self.essay_analyzer = EssayAnalyzer()
        self.resume_formatter = ResumeFormatter()
        self.interview_bot = InterviewPrepBot()
        self.major_quiz = MajorSuggestionQuiz()
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("🎓 COLLEGE APPLICATION ASSISTANT 🎓")
        print("="*50)
        print("1.  📋 Application Tracker")
        print("2.  ✍️  Personal Statement Helper")
        print("3.  💰 Scholarship Finder")
        print("4.  🏫 College Comparison Tool")
        print("5.  ⏰ Deadline Notifier")
        print("6.  💵 Financial Aid Estimator")
        print("7.  📝 Essay Analyzer")
        print("8.  📄 Resume Formatter")
        print("9.  🎤 Interview Prep Bot")
        print("10. 🎯 Major Suggestion Quiz")
        print("11. ⚙️  Setup & Configuration")
        print("12. ❌ Exit")
        print("="*50)
    
    def application_tracker_menu(self):
        """Application tracker submenu"""
        while True:
            print("\n=== Application Tracker ===")
            print("1. Add new application")
            print("2. View all applications")
            print("3. Update application status")
            print("4. Back to main menu")
            
            choice = input("\nChoose an option: ")
            
            if choice == '1':
                self.app_tracker.add_application()
            elif choice == '2':
                self.app_tracker.view_applications()
            elif choice == '3':
                self.app_tracker.update_status()
            elif choice == '4':
                break
            else:
                print("Invalid option. Please try again.")
    
    def essay_helper_menu(self):
        """Essay helper submenu"""
        while True:
            print("\n=== Personal Statement Helper ===")
            print("1. Save new essay draft")
            print("2. Analyze existing essay")
            print("3. Back to main menu")
            
            choice = input("\nChoose an option: ")
            
            if choice == '1':
                self.essay_helper.save_essay()
            elif choice == '2':
                self.essay_helper.analyze_essay()
            elif choice == '3':
                break
            else:
                print("Invalid option. Please try again.")
    
    def setup_menu(self):
        """Setup and configuration menu"""
        while True:
            print("\n=== Setup & Configuration ===")
            print("1. Setup email notifications")
            print("2. Update user profile")
            print("3. Reset database")
            print("4. Back to main menu")
            
            choice = input("\nChoose an option: ")
            
            if choice == '1':
                self.deadline_notifier.setup_email()
            elif choice == '2':
                self.update_user_profile()
            elif choice == '3':
                confirm = input("Are you sure you want to reset all data? (yes/no): ")
                if confirm.lower() == 'yes':
                    os.remove(self.db.db_name)
                    self.db.init_database()
                    print("✅ Database reset successfully")
            elif choice == '4':
                break
            else:
                print("Invalid option. Please try again.")
    
    def update_user_profile(self):
        """Update user profile information"""
        print("\n=== Update User Profile ===")
        gpa = input("Your GPA: ")
        sat_score = input("SAT score: ")
        act_score = input("ACT score: ")
        major_interest = input("Major interest: ")
        location_pref = input("Location preference: ")
        budget = input("Budget for college (per year): ")
        
        query = '''
            INSERT OR REPLACE INTO user_profile 
            (id, gpa, sat_score, act_score, major_interest, location_preference, budget)
            VALUES (1, ?, ?, ?, ?, ?, ?)
        '''
        
        # Handle empty inputs
        params = []
        for value in [gpa, sat_score, act_score, major_interest, location_pref, budget]:
            if value.strip():
                try:
                    # Try to convert to number if it looks like one
                    if '.' in value or value.isdigit():
                        params.append(float(value) if '.' in value else int(value))
                    else:
                        params.append(value)
                except ValueError:
                    params.append(value)
            else:
                params.append(None)
        
        self.db.execute_query(query, params)
        print("✅ Profile updated successfully")
    
    def run(self):
        """Main application loop"""
        print("Welcome to the College Application Assistant!")
        print("This tool will help you manage your college application process.")
        
        while True:
            self.display_menu()
            choice = input("\nChoose an option (1-12): ")
            
            try:
                if choice == '1':
                    self.application_tracker_menu()
                elif choice == '2':
                    self.essay_helper_menu()
                elif choice == '3':
                    self.scholarship_finder.find_scholarships()
                elif choice == '4':
                    self.college_comparison.compare_colleges()
                elif choice == '5':
                    self.deadline_notifier.check_deadlines()
                elif choice == '6':
                    self.aid_estimator.estimate_aid()
                elif choice == '7':
                    print("Enter essay text to analyze:")
                    print("(Type 'END' on a new line when finished)")
                    lines = []
                    while True:
                        line = input()
                        if line.strip() == 'END':
                            break
                        lines.append(line)
                    text = '\n'.join(lines)
                    if text.strip():
                        self.essay_analyzer.analyze_readability(text)
                    else:
                        print("No text provided for analysis.")
                elif choice == '8':
                    self.resume_formatter.create_resume()
                elif choice == '9':
                    self.interview_bot.practice_interview()
                elif choice == '10':
                    self.major_quiz.take_quiz()
                elif choice == '11':
                    self.setup_menu()
                elif choice == '12':
                    print("\n🎓 Thank you for using College Application Assistant!")
                    print("Good luck with your college applications!")
                    break
                else:
                    print("❌ Invalid option. Please choose a number between 1-12.")
                    
            except KeyboardInterrupt:
                print("\n\nProgram interrupted by user.")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again or contact support if the problem persists.")

# Additional utility functions
def install_requirements():
    """Install required packages (run this first)"""
    required_packages = [
        'pandas',
        'requests',
        'beautifulsoup4',
        'textstat',
        'nltk',
        'reportlab'
    ]
    
    print("Installing required packages...")
    import subprocess
    import sys
    
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def create_sample_data():
    """Create sample data for testing"""
    # This function can be called to populate the database with sample data
    db = DatabaseManager()
    
    # Sample applications
    sample_apps = [
        ("Stanford University", "2024-01-01", "In Progress", True, 2, "SAT/ACT", 90, "Reach school"),
        ("UC Berkeley", "2024-01-15", "Not Started", True, 2, "SAT/ACT", 80, "Target school"),
        ("Cal State LA", "2024-03-01", "Not Started", False, 1, "SAT", 55, "Safety school"),
    ]
    
    for app in sample_apps:
        query = '''
            INSERT INTO applications 
            (college_name, deadline, status, essay_required, recommendations_required, 
             test_scores_required, application_fee, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        db.execute_query(query, app)
    
    print("✅ Sample data created successfully")

if __name__ == "__main__":
    # Uncomment the next line on first run to install required packages
    # install_requirements()
    
    # Uncomment to create sample data for testing
    # create_sample_data()
    
    # Run the main application
    app = CollegeApplicationAssistant()
    app.run()