from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import (Flask,render_template,request,jsonify,redirect,session,send_file)
import pandas as pd
from openai import OpenAI
from flask import redirect, session
import os
import html
import webbrowser
from threading import Timer
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# Initialize app
app = Flask(__name__)
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


client = OpenAI()

# ---------------- LOGIN ----------------

@app.route('/')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect('/')

        return render_template(
            'login.html',
            error="Invalid Username or Password"
        )

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- PAGES ----------------

@app.route('/upload')
def upload():

    if 'user' not in session:
        return redirect('/login')

    return render_template("upload.html")


@app.route('/analysis')
def analysis():

    if 'user' not in session:
        return redirect('/login')

    return render_template("analysis.html")


@app.route('/reports')
def reports():

    if 'user' not in session:
        return redirect('/login')

    return render_template("reports.html")


@app.route('/history')
def history():

    if 'user' not in session:
        return redirect('/login')

    return render_template("history.html")


@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect('/login')

    return render_template("profile.html")


def get_ai_insights(data):
    return """
Fraud Alerts:
- High-value transaction detected
- Multiple transactions in a short time

Spending Patterns:
- Most spending is on shopping and food
- Weekend spending is higher

Suggestions:
- Enable transaction alerts
- Review high-value transactions
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

# File upload + AI analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files.get('file')

        if not file:
            return jsonify({"error": "No file uploaded"})

        # Read CSV
        try:
            df = pd.read_csv(file.stream, encoding='utf-8')
        except UnicodeDecodeError:
            file.stream.seek(0)
            df = pd.read_csv(file.stream, encoding='latin-1')

        # Sample data for AI
        data_sample = df.head(20).to_string()

        # Get AI response
        ai_result = get_ai_insights(data_sample)

        # Return JSON
        return jsonify({
            "success": True,
            "result": ai_result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route("/download", methods=["POST"])
def download():

    data = request.get_json()

    if not data:
        return "No Data"

    content = data.get("content", "")

    if not os.path.exists("reports"):
        os.makedirs("reports")

    filename = os.path.join("reports", "AI_Report.pdf")

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    safe_content = html.escape(content)
    safe_content = safe_content.replace("\n", "<br/>")

    elements = []

    elements.append(
        Paragraph("AI PAYMENT ANALYSIS REPORT", styles["Title"])
    )

    elements.append(
        Paragraph("<br/>", styles["Normal"])
    )

    elements.append(
        Paragraph(safe_content, styles["BodyText"])
    )

    doc.build(elements)

    return send_file(filename, as_attachment=True)  


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == '__main__':
    
    Timer(1, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=False)