import os
import sqlite3
import csv
import logging
from io import StringIO
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, session, send_file, make_response, redirect

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'tiny_titans_academy_secret_key_2026_super_secure')

DB_PATH = 'database.db'
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASSWORD', 'titans2026')

# Database Initialization
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create leads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            parent_name TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            school_college TEXT NOT NULL,
            interested_program TEXT NOT NULL,
            preferred_batch TEXT NOT NULL,
            status TEXT DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create blog_posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT DEFAULT 'Tiny Titans Team',
            category TEXT NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if blog posts table is empty to seed initial posts
    cursor.execute('SELECT COUNT(*) FROM blog_posts')
    count = cursor.fetchone()[0]
    
    if count == 0:
        seed_blogs = [
            (
                "Why Robotics and STEM Education are Essential for Kids in 2026",
                "robotics-stem-essential-kids-2026",
                "Discover how hands-on learning with robotics kits helps children develop logical thinking, creative design, and critical problem-solving skills.",
                """<h3>Introduction to Future Skills</h3>
<p>As we navigate 2026, technology has become an inseparable part of daily life. From smart devices to automated machines, the digital landscape is expanding exponentially. For kids growing up today, simply knowing how to use technology is no longer enough—they need to understand how it works. This is where <strong>STEM (Science, Technology, Engineering, and Math)</strong> and <strong>Robotics</strong> education play a transformative role.</p>

<h3>Developing Logic through Hands-on Building</h3>
<p>When children build robots, they are not just playing with toys. They are engaging in structural design, learning how gears mesh, and finding out how sensors interact with the physical environment. More importantly, they learn how to program these machines. Coding a robot teaches sequence, loops, and conditional logic in a tangible, immediate way. If the robot doesn't turn left, the child must debug their code, testing theories until they succeed.</p>

<h3>Key Benefits of Robotics Classes:</h3>
<ul>
  <li><strong>Enhanced Spatial Reasoning:</strong> Designing and assembling physical structures.</li>
  <li><strong>Logical Coding Foundations:</strong> Writing programs that run in the real world rather than just on a screen.</li>
  <li><strong>Resilience & Debugging:</strong> Understanding that failure is just another step toward finding a working solution.</li>
</ul>

<h3>The Tiny Titans Approach</h3>
<p>At Tiny Titans Tech Academy, we limit our school division batch sizes to just 12 students. This guarantees that our experienced mentors can guide each Titan Cadet and Titan Navigator individually, fostering their natural curiosity while introducing advanced engineering concepts at a comfortable pace.</p>""",
                "Tiny Titans Team",
                "School Programs",
                "/images/blog_robotics.png"
            ),
            (
                "Unlocking Career Acceleration with AI and Data Science in College",
                "unlocking-career-acceleration-ai-data-science-college",
                "An in-depth look at why AI, Python programming, and Data Analytics are essential career skillsets for current college students entering the industry.",
                """<h3>The Modern Shift in Hiring</h3>
<p>The corporate world is experiencing a major shift. Employers in domains ranging from banking and logistics to consumer goods are looking for candidates who can leverage data to make informed decisions. Static degrees are no longer enough; students need dynamic, practical tech skills. Python, Power BI, and Data Science are the core tools driving this industrial transition.</p>

<h3>Bridging the Academia-Industry Gap</h3>
<p>While college courses teach theoretical data models, they often miss real-world business contexts. For example, how do you perform retail inventory optimization? How does a bank analyze credit risk using Machine Learning? Tiny Titans Tech Academy offers dedicated professional tracks for college students to bridge this gap by centering the learning on actual industry domains like Consumer Packaged Goods (CPG), Life Sciences, and Financial Analytics.</p>

<h3>Essential Tools to Master:</h3>
<ol>
  <li><strong>Python Programming:</strong> The foundational language of modern data work and AI scripting.</li>
  <li><strong>Power BI & SQL:</strong> Key platforms for cleaning, querying, and visualizing real-world corporate databases.</li>
  <li><strong>Generative AI & Machine Learning:</strong> Engineering prompts, building models, and deploying automated analysis tools.</li>
</ol>

<h3>Why Portfolio Projects Matter</h3>
<p>Our curriculum is focused entirely on hands-on project execution. By building a verified portfolio of Jupyter Notebooks, Git repositories, and Power BI Dashboards, our graduates stand out in competitive job markets and secure premium placements and internships.</p>""",
                "Director of Programs",
                "College Programs",
                "/images/blog_coding.png"
            ),
            (
                "Understanding Generative AI: From Prompts to Deployment",
                "understanding-generative-ai-prompts-to-deployment",
                "An introductory guide explaining the fundamentals of Generative AI, prompt engineering, and its applications in modern businesses.",
                """<h3>The Rise of Generative AI</h3>
<p>Generative Artificial Intelligence is redefining productivity across sectors. Beyond simple chat tools, businesses are deploying AI agents to write code, design assets, summarize multi-thousand-page financial audits, and automate customer pipelines. Learning how to direct and build with these models is the ultimate competitive edge for any engineering or business student.</p>

<h3>Moving Beyond Simple Chat Prompts</h3>
<p>To truly master Generative AI, a student must move beyond basic queries. They need to understand concepts like:</p>
<ul>
  <li><strong>System Instructions & Role Prompting:</strong> Setting rigorous contexts for LLMs.</li>
  <li><strong>Retrieval-Augmented Generation (RAG):</strong> Connecting AI models to external company documents safely.</li>
  <li><strong>API Integration:</strong> Building applications that call AI services programmatically via Python.</li>
</ul>

<h3>The Future Skills Imperative</h3>
<p>Our Generative AI Professional Program walks students through the end-to-end cycle of building smart agents and AI applications. Starting with foundational prompt theory, students proceed to coding with LLM APIs, building local knowledge databases, and deploying working prototypes that can solve real-world problems.</p>""",
                "AI Research Lab Lead",
                "Technology Trends",
                "/images/blog_ai.png"
            )
        ]
        cursor.executemany('''
            INSERT INTO blog_posts (title, slug, summary, content, author, category, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', seed_blogs)
        conn.commit()
        logging.info("Successfully seeded initial blog posts.")
        
    conn.close()

# Initialize Database on Startup
init_db()

# Simulated Email Notification System
def send_email_notification(lead):
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = os.environ.get('SMTP_PORT', '587')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    recipient = os.environ.get('NOTIFICATION_EMAIL', 'info@tinytitans.in')
    
    subject = f"[New Lead Alert] {lead['student_name']} - Tiny Titans Tech Academy"
    body = f"""
    Tiny Titans Tech Academy - New Admission Query Received!
    
    -----------------------------------------------------
    Student Details:
    -----------------------------------------------------
    Name: {lead['student_name']}
    Age: {lead['age']}
    School / College: {lead['school_college']}
    
    -----------------------------------------------------
    Parent Details:
    -----------------------------------------------------
    Parent Name: {lead['parent_name']}
    Mobile Number: {lead['mobile_number']}
    Email: {lead['email']}
    
    -----------------------------------------------------
    Program & Batch Interest:
    -----------------------------------------------------
    Program: {lead['interested_program']}
    Preferred Batch: {lead['preferred_batch']}
    
    Received At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    -----------------------------------------------------
    """
    
    # 1. Log to server console
    logging.info(f"EMAIL NOTIFICATION SIMULATION:\n{body}")
    
    # 2. Log to a local file
    try:
        with open('email_notifications.log', 'a') as f:
            f.write(f"=== Date: {datetime.now().isoformat()} ===\n{body}\n=========================================\n\n")
    except Exception as e:
        logging.error(f"Failed to log email notifications to file: {e}")
        
    # 3. If SMTP configurations are present, send the actual email
    if smtp_host and smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            logging.info("Real SMTP Email notification sent successfully!")
        except Exception as e:
            logging.error(f"Failed to send real SMTP Email notification: {e}")

# ROUTING RULES
@app.route('/')
def root():
    return app.send_static_file('index.html')

# API Endpoints

# Submit Admission Form
@app.route('/api/admissions', methods=['POST'])
def submit_admission():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No data provided."}), 400
        
        # Validate fields
        required_fields = ['studentName', 'parentName', 'mobileNumber', 'email', 'age', 'schoolCollege', 'interestedProgram', 'preferredBatch']
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return jsonify({"success": False, "message": f"Field '{field}' is required."}), 400
        
        # Insert into SQLite db
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leads (student_name, parent_name, mobile_number, email, age, school_college, interested_program, preferred_batch)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['studentName'].strip(),
            data['parentName'].strip(),
            data['mobileNumber'].strip(),
            data['email'].strip(),
            int(data['age']),
            data['schoolCollege'].strip(),
            data['interestedProgram'].strip(),
            data['preferredBatch'].strip()
        ))
        conn.commit()
        
        # Fetch the inserted lead details to trigger notification
        lead_id = cursor.lastrowid
        cursor.execute('SELECT * FROM leads WHERE id = ?', (lead_id,))
        lead = dict(cursor.fetchone())
        conn.close()
        
        # Trigger email simulation
        send_email_notification(lead)
        
        return jsonify({"success": True, "message": "Your application was submitted successfully! We will contact you shortly."})
        
    except ValueError:
        return jsonify({"success": False, "message": "Invalid value provided. Please check age number."}), 400
    except Exception as e:
        logging.error(f"Error saving lead: {e}")
        return jsonify({"success": False, "message": "An internal server error occurred. Please try again later."}), 500

# Admin Authentication
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "Credentials required."}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if username == ADMIN_USER and password == ADMIN_PASS:
        session['admin_logged_in'] = True
        return jsonify({"success": True, "message": "Login successful."})
    else:
        return jsonify({"success": False, "message": "Invalid username or password."}), 401

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_logged_in', None)
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route('/api/admin/check-auth', methods=['GET'])
def check_auth():
    if session.get('admin_logged_in'):
        return jsonify({"authenticated": True})
    return jsonify({"authenticated": False}), 401

# Admin Leads List
@app.route('/api/admin/leads', methods=['GET'])
def get_leads():
    if not session.get('admin_logged_in'):
        return jsonify({"success": False, "message": "Unauthorized access."}), 401
    
    status_filter = request.args.get('status')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if status_filter:
        cursor.execute('SELECT * FROM leads WHERE status = ? ORDER BY created_at DESC', (status_filter,))
    else:
        cursor.execute('SELECT * FROM leads ORDER BY created_at DESC')
        
    leads = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({"success": True, "leads": leads})

# Admin Update Lead Status
@app.route('/api/admin/leads/status', methods=['POST'])
def update_lead_status():
    if not session.get('admin_logged_in'):
        return jsonify({"success": False, "message": "Unauthorized access."}), 401
    
    data = request.json
    if not data or 'leadId' not in data or 'status' not in data:
        return jsonify({"success": False, "message": "Missing leadId or status."}), 400
    
    lead_id = data['leadId']
    status = data['status']
    
    if status not in ['New', 'Contacted', 'Enrolled', 'Archived']:
        return jsonify({"success": False, "message": "Invalid status value."}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE leads SET status = ? WHERE id = ?', (status, lead_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Lead status updated successfully."})

# Export Leads to CSV
@app.route('/api/admin/leads/export', methods=['GET'])
def export_leads():
    if not session.get('admin_logged_in'):
        return redirect('/admin.html?error=unauthorized')
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, student_name, parent_name, mobile_number, email, age, school_college, interested_program, preferred_batch, status, created_at FROM leads ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Lead ID', 'Student Name', 'Parent Name', 'Mobile Number', 'Email Address', 'Age', 'School/College', 'Interested Program', 'Preferred Batch', 'Lead Status', 'Created At'])
    
    for row in rows:
        cw.writerow(list(row))
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=tinytitans_leads_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# Blog Endpoints
@app.route('/api/blog', methods=['GET'])
def get_blogs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, slug, summary, category, author, image_url, created_at FROM blog_posts ORDER BY created_at DESC')
    blogs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "blogs": blogs})

@app.route('/api/blog/<slug>', methods=['GET'])
def get_blog_by_slug(slug):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blog_posts WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({"success": True, "blog": dict(row)})
    return jsonify({"success": False, "message": "Blog post not found."}), 404

# Add Blog via Admin Panel
@app.route('/api/admin/blog', methods=['POST'])
def add_blog():
    if not session.get('admin_logged_in'):
        return jsonify({"success": False, "message": "Unauthorized access."}), 401
        
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided."}), 400
        
    title = data.get('title')
    summary = data.get('summary')
    content = data.get('content')
    category = data.get('category')
    image_url = data.get('imageUrl', '/images/gallery_coding.png')
    
    if not title or not summary or not content or not category:
        return jsonify({"success": False, "message": "Title, Summary, Content, and Category are required."}), 400
        
    # Generate unique slug from title
    slug = title.lower().replace(' ', '-').replace('/', '-').replace('?', '').replace('&', 'and')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO blog_posts (title, slug, summary, content, category, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, slug, summary, content, category, image_url))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Blog post published successfully!", "slug": slug})
    except sqlite3.IntegrityError:
        # Append dynamic suffix if slug collision occurs
        slug = f"{slug}-{int(datetime.now().timestamp())}"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO blog_posts (title, slug, summary, content, category, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, slug, summary, content, category, image_url))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Blog post published successfully!", "slug": slug})
    except Exception as e:
        logging.error(f"Failed to publish blog post: {e}")
        return jsonify({"success": False, "message": "Internal error publishing blog post."}), 500

if __name__ == '__main__':
    # Defaulting to localhost:8080
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
