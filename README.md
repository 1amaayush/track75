# Track75
# Track75

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-black.svg)
![MongoDB](https://img.shields.io/badge/mongodb-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)
![Deployment](https://img.shields.io/badge/deployment-ready-brightgreen.svg)

Track75 is a Flask + MongoDB web application designed to help students, roommates, or entire colleges track and calculate attendance in a simple, modern, and engaging way.  
The name comes from the infamous 75% minimum attendance rule in most Indian colleges.

---

## Features
- User Accounts — secure login/signup system
- Attendance Logging — mark Present / Absent / Cancelled for each subject
- MongoDB Storage — persistent, cloud-ready database
- Attendance Overview — total percentage & subject-wise stats
- Editable Past Records — update attendance if you missed logging a day
- Responsive UI — works on desktops, tablets, and mobiles

---

## Tech Stack
- **Backend:** [Flask](https://flask.palletsprojects.com/) (Python microframework)
- **Database:** [MongoDB](https://www.mongodb.com/) (local for development, Atlas for cloud)
- **Frontend:** HTML, CSS, JavaScript (Flask templates)
- **Deployment Ready:** Configured for [Render](https://render.com/) / Railway / Heroku
- **Version Control:** Git + GitHub

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Track75.git
cd Track75

**2. Create and activate a virtual environment**
bash
Copy
Edit
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
**3. Install dependencies**
bash
Copy
Edit
pip install -r requirements.txt
**4. Set environment variables**
Create a .env file in the root:

ini
Copy
Edit
SECRET_KEY=your_secret_key_here
MONGO_URI=your_mongodb_connection_string
**5. Run the application**
bash
Copy
Edit
python app.py
The app will run at: http://127.0.0.1:5000

**MongoDB Setup**
Install MongoDB Community Server for local development, or

Use MongoDB Atlas for cloud hosting

Update your .env file with the correct MONGO_URI

**Contributing**
Pull requests are welcome.
For major changes, open an issue first to discuss what you would like to add or modify.
