from flask import Flask, render_template, request
from predict import predict_placement
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file
from flask import session, redirect, url_for
import sqlite3
app = Flask(__name__)
app.secret_key = "placement_project_secret"

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "students.db")


# -------------------------
# INIT DATABASE
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            cgpa REAL,
            dsa_skill INTEGER,
            communication INTEGER,
            internships INTEGER,
            projects INTEGER,
            aptitude INTEGER,
            resume_score INTEGER,
            mock_interview INTEGER,
            result TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------------
# HOME PAGE
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")
#----------login--------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["user"] = "admin"
            return redirect("/admin")   # ✅ FIXED HERE
        else:
            return "Invalid Credentials"

    return render_template("login.html")
# -------------------------
# PREDICT + SAVE TO DB
# -------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        student_name = request.form["student_name"]

        cgpa = float(request.form["cgpa"])
        dsa_skill = int(request.form["dsa_skill"])
        communication = int(request.form["communication"])
        internships = int(request.form["internships"])
        projects = int(request.form["projects"])
        aptitude = int(request.form["aptitude"])
        resume_score = int(request.form["resume_score"])
        mock_interview = int(request.form["mock_interview"])

        # ML prediction
        prediction, probability, suggestions = predict_placement(
            cgpa,
            dsa_skill,
            communication,
            internships,
            projects,
            aptitude,
            resume_score,
            mock_interview
        )

        result = "PLACED" if prediction == 1 else "NOT PLACED"

        readiness_score = (
            cgpa * 10 +
            dsa_skill * 5 +
            communication * 5 +
            internships * 10 +
            projects * 5 +
            aptitude * 0.5 +
            resume_score * 0.5 +
            mock_interview * 5
        )

        eligible_companies = []

        if cgpa >= 6:
            eligible_companies += ["TCS", "Infosys", "Wipro"]

        if cgpa >= 7:
            eligible_companies += ["Accenture", "Capgemini"]

        if cgpa >= 8 and dsa_skill >= 8 and aptitude >= 80:
            eligible_companies += ["Amazon", "Microsoft"]

        if cgpa >= 8.5 and internships >= 2 and projects >= 3:
            eligible_companies.append("Google")

        # -------------------------
        # SAVE TO SQLITE
        # -------------------------
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students (
                student_name, cgpa, dsa_skill, communication,
                internships, projects, aptitude,
                resume_score, mock_interview, result
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_name, cgpa, dsa_skill, communication,
            internships, projects, aptitude,
            resume_score, mock_interview, result
        ))

        conn.commit()
        conn.close()

        print("✅ Saved to SQLite database")

        return render_template(
            "index.html",
            student_name=student_name,
            result=result,
            probability=round(probability, 2),
            readiness_score=round(readiness_score, 2),
            eligible_companies=eligible_companies,
            suggestions=suggestions
        )

    except Exception as e:
        return f"Error: {str(e)}"


# -------------------------
# ADMIN DASHBOARD
@app.route("/admin")
def admin_dashboard():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()

    conn.close()

    # Convert tuple → dictionary (IMPORTANT FIX)
    students = [
        {
            "id": row[0],
            "student_name": row[1],
            "cgpa": row[2],
            "dsa_skill": row[3],
            "communication": row[4],
            "internships": row[5],
            "projects": row[6],
            "aptitude": row[7],
            "resume_score": row[8],
            "mock_interview": row[9],
            "result": row[10]
        }
        for row in rows
    ]

    # STATS
    total = len(students)
    placed = sum(1 for s in students if s["result"] == "PLACED")
    not_placed = total - placed

    stats = {
        "total": total,
        "placed": placed,
        "not_placed": not_placed,
        "percentage": round((placed / total) * 100, 2) if total > 0 else 0
    }

    return render_template(
        "admin_dashboard.html",
        students=students,
        stats=stats
    )
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")



#----download report---------

@app.route("/download_report")
def download_report():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    conn.close()

    file_path = "placement_report.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, 770, "Student Placement Report")

    # Header line
    c.setFont("Helvetica", 10)
    c.drawString(50, 750, "-" * 90)

    # Column headers
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 720, "Name")
    c.drawString(140, 720, "CGPA")
    c.drawString(200, 720, "DSA")
    c.drawString(260, 720, "Internships")
    c.drawString(350, 720, "Projects")
    c.drawString(450, 720, "Result")

    y = 700
    c.setFont("Helvetica", 10)

    for row in data:

        # Convert safely to string
        name = str(row[1])
        cgpa = str(row[2])
        dsa = str(row[3])
        internships = str(row[5])
        projects = str(row[6])

        # Convert result properly
        result = "PLACED" if str(row[9]) == "1" or str(row[9]) == "PLACED" else "NOT PLACED"

        # Write to PDF
        c.drawString(50, y, name)
        c.drawString(140, y, cgpa)
        c.drawString(200, y, dsa)
        c.drawString(260, y, internships)
        c.drawString(350, y, projects)
        c.drawString(450, y, result)

        y -= 20

        # Page break handling
        if y < 50:
            c.showPage()
            y = 750
            c.setFont("Helvetica", 10)

    c.save()

    return send_file(file_path, as_attachment=True)
# RUN APP
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)