# Forex Trading Journal & Performance Optimizer

## Overview
The **Forex Trading Journal & Performance Optimizer** is a powerful, data-driven tool designed to help traders **track, analyze, and improve** their trading performance.  
Unlike generic journals, this application focuses on **behavioral patterns, strategy drift detection, and personalized performance optimization**—giving traders actionable insights to enhance profitability and discipline.

This project was developed as part of my academic mini-project submission, with the aim of **solving real-world trading challenges** and **demonstrating backend engineering expertise**.

---

## 🎯 Key Features
- **Automatic Trade Tracking**  
  Upload your trade history (CSV) and automatically parse & store trades in the database.
  
- **Comprehensive Dashboard**  
  Visual representation of key performance metrics (win rate, profit factor, drawdown, etc.).

- **Performance Analytics**  
  Identify:
  - Most profitable trading sessions
  - Most losing days
  - Best & worst-performing currency pairs
  - Risk-to-reward consistency

- **Strategy Tracking**  
  Monitor and compare the performance of multiple strategies over time.

- **Calendar View**  
  Color-coded profit/loss view for quick trend spotting.

- **Detailed Insights**  
  Behavioral patterns, overtrading detection, and consistency analysis.

---

## 🛠 Tech Stack
**Backend**: Django (Python)  
**Database**: SQLite3 (Development), PostgreSQL (Production)  
**Frontend**: Django Templates (with potential for React/Vue integration)  
**Data Visualization**: Matplotlib / Plotly  
**Deployment**: Docker + Gunicorn + Nginx  
**Caching**: Redis (Optional for performance optimization)  

---

## 📂 Project Structure

Journal/
│
├── journal/ # Main application logic
│ ├── models.py # Database models
│ ├── views.py # Application views
│ ├── urls.py # Route definitions
│ ├── utils/ # Data processing utilities
│
├── templates/ # HTML templates
├── static/ # CSS, JS, images
├── manage.py # Django entry point
└── requirements.txt # Dependencies


##  Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Black-Acid/forexJournal.git
cd forex-journal


## Create a Virtual Environment
python -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate    # windows

## Install dependencies
pip install -r requirements.txt


## Configure Environment Variables
# Create a .env file in the root directory:
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
SECRET_KEY=your-secret-key


## Run Migrations & Start Server
python manage.py migrate
python manage.py runserver