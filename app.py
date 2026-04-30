from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import Flask, render_template, request, jsonify
import pandas as pd
from openai import OpenAI
from flask import redirect, session

# Initialize app
app = Flask(__name__)


client = OpenAI()


app.secret_key = "supersecretkey"
# -----------------------------
# AI FUNCTION (only one version)
# -----------------------------
def get_ai_insights(data):
    prompt = f"""
    Analyze this transaction data:

    {data}

    Return STRICTLY in this format:

    Fraud Alerts:
    - ...

    Spending Patterns:
    - ...

    Suggestions:
    - ...
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# -----------------------------
# ROUTES
# -----------------------------

# Home route
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')


# File upload + AI analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files['file']

        if not file:
            return jsonify({"error": "No file uploaded"})

        # Read CSV properly
        df = pd.read_csv(file.stream)

        # Take small sample for AI (faster + cheaper)
        data_sample = df.head(20).to_string()

        # Get AI response
        ai_result = get_ai_insights(data_sample)

        return jsonify({"result": ai_result})

    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()

    if not data or 'content' not in data:
        return jsonify({"error": "No content provided"})

    content = data['content']

    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(content, styles['Normal']))

    doc.build(elements)

    return jsonify({"message": "PDF generated"})    


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)