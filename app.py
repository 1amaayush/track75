from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# ---- MongoDB setup ----
# Read connection string from environment (Atlas or Cosmos DB in production)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)

# Use 'track75' database
db = client.track75
user_coll = db.users
attendance_coll = db.attendance
test_coll = db.test  # optional test collection

# ---- Routes ----
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if user_coll.find_one({"email": email}):
            flash("Email already registered!", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        user = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow()
        }
        user_coll.insert_one(user)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = user_coll.find_one({"email": email})
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("home"))

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "user_id" not in session:
        flash("Please log in to mark attendance.", "error")
        return redirect(url_for("login"))

    user = user_coll.find_one({"_id": ObjectId(session["user_id"])})
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("logout"))

    subjects = user.get("subjects", [])
    today = datetime.utcnow().date().isoformat()

    if request.method == "POST":
        class_data = []
        for subject in subjects:
            status = request.form.get(subject)
            class_data.append({"subject": subject, "status": status})

        attendance_coll.update_one(
            {"user_id": session["user_id"], "date": today},
            {"$set": {"classes": class_data}},
            upsert=True
        )

        flash("Attendance recorded successfully!", "success")
        return redirect(url_for("attendance"))

    return render_template("attendance.html", subjects=subjects, today=datetime.utcnow().date())

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("Please log in to access your profile.", "error")
        return redirect(url_for("login"))

    user = user_coll.find_one({"_id": ObjectId(session["user_id"])})

    if request.method == "POST":
        department = request.form["department"]
        subjects = []
        for i in range(1, 9):
            sub = request.form.get(f"subject{i}")
            if sub:
                subjects.append(sub.strip())

        user_coll.update_one(
            {"_id": ObjectId(session["user_id"])},
            {"$set": {"department": department, "subjects": subjects}}
        )
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)

@app.route("/overview")
def overview():
    if "user_id" not in session:
        flash("Please log in to view your overview.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    records = attendance_coll.find({"user_id": user_id})

    total_days = 0
    total_present = 0
    total_absent = 0
    total_classes = 0

    subject_data = {}

    for record in records:
        total_days += 1
        for entry in record.get("classes", []):
            subject = entry["subject"]
            status = entry["status"]

            if status in ["Cancelled", "No Lecture Today"]:
                continue

            if subject not in subject_data:
                subject_data[subject] = {"present": 0, "absent": 0}

            if status == "Present":
                subject_data[subject]["present"] += 1
                total_present += 1
            elif status == "Absent":
                subject_data[subject]["absent"] += 1
                total_absent += 1

            total_classes += 1

    for subject in subject_data:
        p = subject_data[subject]["present"]
        a = subject_data[subject]["absent"]
        total = p + a
        percent = round((p / total) * 100, 2) if total > 0 else 0
        subject_data[subject]["percent"] = percent

    overall_percent = round((total_present / total_classes) * 100, 2) if total_classes > 0 else 0

    return render_template("overview.html",
                           total_days=total_days,
                           total_present=total_present,
                           total_absent=total_absent,
                           total_classes=total_classes,
                           overall_percent=overall_percent,
                           subject_data=subject_data)

@app.route("/add-attendance", methods=["GET", "POST"])
def add_past_attendance():
    if "user_id" not in session:
        flash("Please log in to continue.", "error")
        return redirect(url_for("login"))

    user = user_coll.find_one({"_id": ObjectId(session["user_id"])})
    subjects = user.get("subjects", [])

    if request.method == "POST":
        selected_date = request.form["date"]
        class_data = []

        for subject in subjects:
            status = request.form.get(subject)
            class_data.append({"subject": subject, "status": status})

        attendance_coll.update_one(
            {"user_id": session["user_id"], "date": selected_date},
            {"$set": {"classes": class_data}},
            upsert=True
        )

        flash(f"Attendance for {selected_date} recorded.", "success")
        return redirect(url_for("overview"))

    return render_template("attendance.html", subjects=subjects, allow_date=True)

# ---- Local dev only ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
