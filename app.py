import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

app = Flask(__name__)

# Secure config from environment variables
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))
mongo_uri = os.environ.get("MONGODB_URI")
if not mongo_uri:
    raise RuntimeError("MONGODB_URI not set in environment variables.")

# MongoDB Atlas client
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=8000)
db = client.get_default_database()

# Collections
user_coll = db.users
attendance_coll = db.attendance

# Routes
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
            "created_at": datetime.utcnow(),
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
            return redirect(url_for("overview"))
        else:
            flash("Invalid credentials", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))

@app.route("/overview")
def overview():
    if "user_id" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))
    return render_template("overview.html", username=session.get("username"))

@app.route("/attendance")
def attendance():
    if "user_id" not in session:
        flash("Please log in to view attendance.", "error")
        return redirect(url_for("login"))
    records = attendance_coll.find({"user_id": session["user_id"]})
    return render_template("attendance.html", records=records)

@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Please log in to view your profile.", "error")
        return redirect(url_for("login"))
    user = user_coll.find_one({"_id": ObjectId(session["user_id"])})
    return render_template("profile.html", user=user)

# Health check for Azure
@app.route("/healthz")
def healthz():
    try:
        client.admin.command("ping")
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "detail": str(e)}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
