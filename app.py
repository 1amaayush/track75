import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables (only works locally with .env file)
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")  # Fallback for local

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["your_database_name"]  # Change to your actual DB name

# Example route
@app.route("/")
def index():
    return render_template("index.html")

# Example user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        db.users.insert_one({"username": username, "password": password})
        flash("Registration successful!")
        return redirect(url_for("login"))
    return render_template("register.html")

# Example login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.users.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            flash("Login successful!")
            return redirect(url_for("index"))
        flash("Invalid credentials")
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
