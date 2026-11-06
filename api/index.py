
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "tender_management_secret_key_2024"

# Vercel-এ /tmp ডিরেক্টরি ব্যবহার করতে হয়
DATA_FILE = "/tmp/tender_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "tenders": [], "bids": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>টেন্ডার ম্যানেজমেন্ট সিস্টেম</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #667eea; }
        .user-info { display: flex; gap: 15px; align-items: center; }
        .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; font-weight: bold; transition: all 0.3s; }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .btn-success { background: #48bb78; color: white; }
        .btn-success:hover { background: #38a169; }
        .btn-danger { background: #f56565; color: white; }
        .btn-danger:hover { background: #e53e3e; }
        .btn-secondary { background: #718096; color: white; }
        .btn-secondary:hover { background: #4a5568; }
        .content { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .tender-card { border: 1px solid #e2e8f0; padding: 20px; margin-bottom: 15px; border-radius: 8px; background: #f7fafc; }
        .tender-card h3 { color: #2d3748; margin-bottom: 10px; }
        .tender-meta { color: #718096; font-size: 14px; margin-bottom: 10px; }
        .tender-actions { margin-top: 15px; display: flex; gap: 10px; }
        .badge { padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .badge-open { background: #48bb78; color: white; }
        .badge-closed { background: #f56565; color: white; }
        .flash { padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .flash-success { background: #c6f6d5; color: #22543d; }
        .flash-error { background: #fed7d7; color: #742a2a; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #2d3748; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 10px; border: 1px solid #cbd5e0; border-radius: 5px; font-size: 14px; }
        .form-group textarea { min-height: 100px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 টেন্ডার ম্যানেজমেন্ট সিস্টেম</h1>
            <div class="user-info">
                {% if session.get('user') %}
                    <span>স্বাগতম, <strong>{{ session['user'] }}</strong> ({{ session['role'] }})</span>
                    {% if session['role'] == 'company' %}
                        <a href="/create_tender" class="btn btn-success">নতুন টেন্ডার তৈরি করুন</a>
                    {% endif %}
                    <a href="/logout" class="btn btn-danger">লগআউট</a>
                {% else %}
                    <a href="/login" class="btn btn-primary">লগইন</a>
                    <a href="/register" class="btn btn-success">রেজিস্টার</a>
                {% endif %}
            </div>
        </div>

        <div class="content">
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="flash flash-success">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <h2>সকল টেন্ডার</h2>
            <hr style="margin: 20px 0;">

            {% if tenders %}
                {% for tender in tenders %}
                    <div class="tender-card">
                        <h3>{{ tender.title }}</h3>
                        <div class="tender-meta">
                            <strong>কোম্পানি:</strong> {{ tender.company }} | 
                            <strong>বাজেট:</strong> ৳{{ tender.budget }} | 
                            <strong>ডেডলাইন:</strong> {{ tender.deadline }}
                            {% if tender.status == 'open' %}
                                <span class="badge badge-open">চলমান</span>
                            {% else %}
                                <span class="badge badge-closed">বন্ধ</span>
                            {% endif %}
                        </div>
                        <p>{{ tender.description }}</p>
                        <div class="tender-actions">
                            <a href="/tender/{{ tender.id }}" class="btn btn-primary">বিস্তারিত দেখুন</a>
                            {% if session.get('role') == 'vendor' and tender.status == 'open' %}
                                <a href="/bid/{{ tender.id }}" class="btn btn-success">বিড সাবমিট করুন</a>
                            {% endif %}
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <p style="text-align: center; color: #718096; padding: 40px;">কোনো টেন্ডার পাওয়া যায়নি।</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>লগইন - টেন্ডার ম্যানেজমেন্ট</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 400px; }
        .login-box h2 { text-align: center; color: #667eea; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #2d3748; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid #cbd5e0; border-radius: 5px; font-size: 14px; }
        .btn { width: 100%; padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; margin-top: 10px; }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .btn-secondary { background: #718096; color: white; }
        .btn-secondary:hover { background: #4a5568; }
        .flash-error { background: #fed7d7; color: #742a2a; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .text-center { text-align: center; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🔐 লগইন করুন</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="flash-error">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <div class="form-group">
                <label>ইউজারনেম</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>পাসওয়ার্ড</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary">লগইন</button>
            <a href="/" class="btn btn-secondary">হোমে ফিরুন</a>
        </form>
        <div class="text-center">
            <p>নতুন ইউজার? <a href="/register">রেজিস্টার করুন</a></p>
        </div>
    </div>
</body>
</html>
"""

REGISTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>রেজিস্টার - টেন্ডার ম্যানেজমেন্ট</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .register-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 450px; }
        .register-box h2 { text-align: center; color: #667eea; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #2d3748; }
        .form-group input, .form-group select { width: 100%; padding: 12px; border: 1px solid #cbd5e0; border-radius: 5px; font-size: 14px; }
        .btn { width: 100%; padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; margin-top: 10px; }
        .btn-success { background: #48bb78; color: white; }
        .btn-success:hover { background: #38a169; }
        .btn-secondary { background: #718096; color: white; }
        .btn-secondary:hover { background: #4a5568; }
        .flash-error { background: #fed7d7; color: #742a2a; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .text-center { text-align: center; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="register-box">
        <h2>📝 রেজিস্টার করুন</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="flash-error">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <div class="form-group">
                <label>ইউজারনেম</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>পাসওয়ার্ড</label>
                <input type="password" name="password" required>
            </div>
            <div class="form-group">
                <label>ইউজার টাইপ</label>
                <select name="role" required>
                    <option value="">নির্বাচন করুন</option>
                    <option value="company">কোম্পানি (টেন্ডার পাবলিশ করবে)</option>
                    <option value="vendor">ভেন্ডর (বিড সাবমিট করবে)</option>
                </select>
            </div>
            <button type="submit" class="btn btn-success">রেজিস্টার</button>
            <a href="/" class="btn btn-secondary">হোমে ফিরুন</a>
        </form>
        <div class="text-center">
            <p>ইতিমধ্যে অ্যাকাউন্ট আছে? <a href="/login">লগইন করুন</a></p>
        </div>
    </div>
</body>
</html>
"""

CREATE_TENDER_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>নতুন টেন্ডার তৈরি করুন</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        h2 { color: #667eea; margin-bottom: 30px; text-align: center; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #2d3748; }
        .form-group input, .form-group textarea { width: 100%; padding: 12px; border: 1px solid #cbd5e0; border-radius: 5px; font-size: 14px; }
        .form-group textarea { min-height: 120px; }
        .btn { padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; margin-right: 10px; }
        .btn-success { background: #48bb78; color: white; }
        .btn-success:hover { background: #38a169; }
        .btn-secondary { background: #718096; color: white; text-decoration: none; display: inline-block; }
        .btn-secondary:hover { background: #4a5568; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📋 নতুন টেন্ডার তৈরি করুন</h2>
        <form method="POST">
            <div class="form-group">
                <label>টেন্ডার শিরোনাম</label>
                <input type="text" name="title" required>
            </div>
            <div class="form-group">
                <label>বিবরণ</label>
                <textarea name="description" required></textarea>
            </div>
            <div class="form-group">
                <label>বাজেট (টাকা)</label>
                <input type="number" name="budget" required>
            </div>
            <div class="form-group">
                <label>ডেডলাইন</label>
                <input type="date" name="deadline" required>
            </div>
            <button type="submit" class="btn btn-success">টেন্ডার পাবলিশ করুন</button>
            <a href="/" class="btn btn-secondary">বাতিল</a>
        </form>
    </div>
</body>
</html>
"""

BID_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>বিড সাবমিট করুন</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        h2 { color: #667eea; margin-bottom: 20px; }
        .tender-info { background: #f7fafc; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 4px solid #667eea; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #2d3748; }
        .form-group input, .form-group textarea { width: 100%; padding: 12px; border: 1px solid #cbd5e0; border-radius: 5px; font-size: 14px; }
        .form-group textarea { min-height: 100px; }
        .btn { padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; margin-right: 10px; }
        .btn-success { background: #48bb78; color: white; }
        .btn-success:hover { background: #38a169; }
        .btn-secondary { background: #718096; color: white; text-decoration: none; display: inline-block; }
        .btn-secondary:hover { background: #4a5568; }
    </style>
</head>
<body>
    <div class="container">
        <h2>💼 বিড সাবমিট করুন</h2>
        <div class="tender-info">
            <h3>{{ tender.title }}</h3>
            <p><strong>কোম্পানি:</strong> {{ tender.company }}</p>
            <p><strong>বাজেট:</strong> ৳{{ tender.budget }}</p>
            <p><strong>বিবরণ:</strong> {{ tender.description }}</p>
        </div>
        <form method="POST">
            <div class="form-group">
                <label>আপনার প্রস্তাবিত মূল্য (টাকা)</label>
                <input type="number" name="bid_amount" required>
            </div>
            <div class="form-group">
                <label>প্রস্তাবনা বিবরণ</label>
                <textarea name="proposal" required placeholder="আপনার কোম্পানির যোগ্যতা এবং কাজের পরিকল্পনা লিখুন..."></textarea>
            </div>
            <button type="submit" class="btn btn-success">বিড সাবমিট করুন</button>
            <a href="/" class="btn btn-secondary">বাতিল</a>
        </form>
    </div>
</body>
</html>
"""

TENDER_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>টেন্ডার বিস্তারিত</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        h2 { color: #667eea; margin-bottom: 20px; }
        .tender-detail { background: #f7fafc; padding: 25px; border-radius: 8px; margin-bottom: 30px; }
        .tender-detail h3 { color: #2d3748; margin-bottom: 15px; }
        .tender-detail p { margin-bottom: 10px; line-height: 1.6; }
        .bids-section { margin-top: 30px; }
        .bids-section h3 { color: #2d3748; margin-bottom: 20px; }
        .bid-card { background: #edf2f7; padding: 20px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #48bb78; }
        .bid-card strong { color: #2d3748; }
        .btn { padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; text-decoration: none; display: inline-block; }
        .btn-secondary { background: #718096; color: white; }
        .btn-secondary:hover { background: #4a5568; }
        .badge { padding: 5px 15px; border-radius: 20px; font-size: 14px; font-weight: bold; }
        .badge-open { background: #48bb78; color: white; }
        .badge-closed { background: #f56565; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📄 টেন্ডার বিস্তারিত</h2>
        <div class="tender-detail">
            <h3>{{ tender.title }} 
                {% if tender.status == 'open' %}
                    <span class="badge badge-open">চলমান</span>
                {% else %}
                    <span class="badge badge-closed">বন্ধ</span>
                {% endif %}
            </h3>
            <p><strong>কোম্পানি:</strong> {{ tender.company }}</p>
            <p><strong>বাজেট:</strong> ৳{{ tender.budget }}</p>
            <p><strong>ডেডলাইন:</strong> {{ tender.deadline }}</p>
            <p><strong>বিবরণ:</strong></p>
            <p>{{ tender.description }}</p>
        </div>

        {% if session.get('role') == 'company' and session.get('user') == tender.company %}
            <div class="bids-section">
                <h3>📊 প্রাপ্ত বিড সমূহ ({{ bids|length }}টি)</h3>
                {% if bids %}
                    {% for bid in bids %}
                        <div class="bid-card">
                            <p><strong>ভেন্ডর:</strong> {{ bid.vendor }}</p>
                            <p><strong>প্রস্তাবিত মূল্য:</strong> ৳{{ bid.bid_amount }}</p>
                            <p><strong>প্রস্তাবনা:</strong> {{ bid.proposal }}</p>
                            <p><strong>সাবমিট তারিখ:</strong> {{ bid.submitted_at }}</p>
                        </div>
                    {% endfor %}
                {% else %}
                    <p style="text-align: center; color: #718096; padding: 20px;">এখনো কোনো বিড জমা পড়েনি।</p>
                {% endif %}
            </div>
        {% endif %}

        <a href="/" class="btn btn-secondary">হোমে ফিরুন</a>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    data = load_data()
    return render_template_string(HOME_TEMPLATE, tenders=data["tenders"])

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        data = load_data()

        if username in data["users"]:
            flash("এই ইউজারনেম ইতিমধ্যে নিবন্ধিত!")
            return redirect(url_for("register"))

        data["users"][username] = {
            "password": generate_password_hash(password),
            "role": role
        }
        save_data(data)

        flash("রেজিস্ট্রেশন সফল! এখন লগইন করুন।")
        return redirect(url_for("login"))

    return render_template_string(REGISTER_TEMPLATE)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        data = load_data()

        if username not in data["users"]:
            flash("ইউজারনেম বা পাসওয়ার্ড ভুল!")
            return redirect(url_for("login"))

        user = data["users"][username]
        if not check_password_hash(user["password"], password):
            flash("ইউজারনেম বা পাসওয়ার্ড ভুল!")
            return redirect(url_for("login"))

        session["user"] = username
        session["role"] = user["role"]
        flash(f"স্বাগতম, {username}!")
        return redirect(url_for("home"))

    return render_template_string(LOGIN_TEMPLATE)

@app.route("/logout")
def logout():
    session.clear()
    flash("সফলভাবে লগআউট হয়েছে!")
    return redirect(url_for("home"))

@app.route("/create_tender", methods=["GET", "POST"])
def create_tender():
    if "user" not in session or session["role"] != "company":
        flash("শুধুমাত্র কোম্পানি টেন্ডার তৈরি করতে পারবে!")
        return redirect(url_for("home"))

    if request.method == "POST":
        data = load_data()

        tender_id = len(data["tenders"]) + 1
        tender = {
            "id": tender_id,
            "title": request.form["title"],
            "description": request.form["description"],
            "budget": request.form["budget"],
            "deadline": request.form["deadline"],
            "company": session["user"],
            "status": "open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        data["tenders"].append(tender)
        save_data(data)

        flash("টেন্ডার সফলভাবে পাবলিশ হয়েছে!")
        return redirect(url_for("home"))

    return render_template_string(CREATE_TENDER_TEMPLATE)

@app.route("/bid/<int:tender_id>", methods=["GET", "POST"])
def submit_bid(tender_id):
    if "user" not in session or session["role"] != "vendor":
        flash("শুধুমাত্র ভেন্ডর বিড সাবমিট করতে পারবে!")
        return redirect(url_for("home"))

    data = load_data()
    tender = next((t for t in data["tenders"] if t["id"] == tender_id), None)

    if not tender:
        flash("টেন্ডার পাওয়া যায়নি!")
        return redirect(url_for("home"))

    if tender["status"] != "open":
        flash("এই টেন্ডার বন্ধ হয়ে গেছে!")
        return redirect(url_for("home"))

    if request.method == "POST":
        bid = {
            "tender_id": tender_id,
            "vendor": session["user"],
            "bid_amount": request.form["bid_amount"],
            "proposal": request.form["proposal"],
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        data["bids"].append(bid)
        save_data(data)

        flash("বিড সফলভাবে সাবমিট হয়েছে!")
        return redirect(url_for("home"))

    return render_template_string(BID_TEMPLATE, tender=tender)

@app.route("/tender/<int:tender_id>")
def tender_detail(tender_id):
    data = load_data()
    tender = next((t for t in data["tenders"] if t["id"] == tender_id), None)

    if not tender:
        flash("টেন্ডার পাওয়া যায়নি!")
        return redirect(url_for("home"))

    bids = [b for b in data["bids"] if b["tender_id"] == tender_id]

    return render_template_string(TENDER_DETAIL_TEMPLATE, tender=tender, bids=bids)

# Vercel serverless function handler
app_handler = app
