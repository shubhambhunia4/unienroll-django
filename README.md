# 🎓 UniEnroll — University Enrollment & Academic Management System
### *Demo Institute of Technology (DIT) — Enterprise Academic & Financial Prototype*

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2%2B-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Logs%20%26%20Audit-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 📌 Overview

**UniEnroll** is a full-featured, modular university management and course registration web application engineered with **Django 5** and **MongoDB**. Designed to streamline academic workflows for students and administrators alike, UniEnroll handles everything from course discovery and credit validation to multi-tier fee calculation, online payment simulation, and immutable audit trails.

---

## ✨ Key Features

### 👨‍🎓 Student Portal
- **Interactive Course Registration**: Dynamic course catalog with schedule days, time slots, room locations, and credit tracking.
- **Cart & Enrollment Workflow**: Draft course cart, real-time credit limit enforcement (up to max semester credits), and prerequisite checks.
- **Fee Calculation & Breakdown**: Automated calculation dividing tuition per credit, examination fees, library charges, and infrastructure maintenance.
- **Integrated Payment Gateway**: Razorpay-simulated checkout with instant transaction verification, payment status tracking, and downloadable receipts.
- **Grades & Academic Transcripts**: View term-by-term assessment grades (`A+`, `A`, `B+`, `B`, `C`, `P`, `PENDING`).
- **Real-Time Notification Center**: Instant alerts for payments, announcements, course confirmations, and grade releases.

### 🛡️ Admin & Faculty Portal
- **Department & Course Management**: Configure departments, credit units, per-credit tuition, and classroom capacity.
- **Semester Management**: Open and close enrollment windows, activate academic terms, and set global credit caps.
- **Campus Announcements**: Broadcast notices categorized by `General`, `Urgent`, `Examinations`, or `Fees`.
- **Financial & Academic Analytics**: Real-time revenue statistics, student enrollment ratios, and seat occupancy graphs.
- **Audit Logging**: MongoDB-powered immutable audit logs for compliance, payment event streams, and security tracking.

### 🔌 RESTful API (v1)
- `GET /api/v1/health/` — System health and database connectivity probe.
- `GET /api/v1/courses/` — Filterable course listing with capacity and department tags.
- `GET /api/v1/student/transcript/` — Authenticated student transcript and GPA record.
- `GET /api/v1/admin/analytics/` — High-level enrollment and financial telemetry.
- `GET /api/v1/admin/audit-logs/` — Streamed audit events stored in MongoDB.
- `POST /api/v1/ai-advisor/` — Intelligent course advisory assistant.

---

## 🏗️ Architecture & Tech Stack

```text
UniEnroll Architecture
 ├── Frontend: HTML5, CSS3, Modern Responsive Layouts, Vanilla JavaScript
 ├── Application Layer: Django 5 (MTV Pattern), Gunicorn WSGI, ASGI
 ├── Relational Database: SQLite (Dev) / PostgreSQL (Prod) for transactional ACID compliance
 ├── Document Store: MongoDB 6.0+ (PyMongo) for event streams & audit logging
 └── Containerization: Docker & Docker Compose
```

| Technology | Purpose |
| :--- | :--- |
| **Python 3.12+** | Core programming runtime |
| **Django 5.x** | Web framework, ORM, Auth, and Admin interface |
| **Pillow** | Dynamic profile & media asset processing |
| **PyMongo** | High-performance MongoDB driver for audit logs |
| **python-dotenv** | Twelve-Factor App environment configuration |
| **Docker & Docker Compose** | Reproducible deployment and container orchestration |

---

## 📁 Folder Structure

```plaintext
Project 2026/
├── academics/             # Academic models (Departments, Courses, Semesters, Announcements)
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── accounts/              # Custom User model, Roles (Student/Admin), Notifications
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── config/                # Project settings, root URL dispatch, WSGI/ASGI, REST APIs
│   ├── api_views.py       # REST API endpoints
│   ├── context_processors.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── enrollment/            # Enrollment carts, status tracking, grade management
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── fees/                  # Fee breakdown calculation & invoice structures
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── payments/              # Payment processing, Razorpay integration, transaction records
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/                # Static assets (CSS styles, JS scripts, icons)
├── templates/             # Semantic HTML5 Jinja/Django templates
│   ├── academics/
│   ├── accounts/
│   ├── base.html
│   ├── enrollment/
│   ├── fees/
│   └── payments/
├── .env.example           # Environment variable template
├── .gitignore             # Standardized git exclusions (venv, .env, db.sqlite3)
├── Dockerfile             # Multi-stage production container build
├── docker-compose.yml     # Multi-container stack (Web + MongoDB)
├── manage.py              # Django management utility
├── requirements.txt       # Python project dependencies
└── README.md              # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.12+** installed on your system.
- **MongoDB** installed locally or running via Docker (MongoDB Compass recommended for viewing logs).
- *(Optional)* **Docker & Docker Compose** for containerized setup.

---

### 2. Local Setup (Standard)

#### Clone the repository:
```bash
git clone https://github.com/shubhambhunia4/unienroll-django.git
cd unienroll-django
```

#### Create and activate a virtual environment:
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### Install dependencies:
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables:
Copy the example environment configuration:
```bash
cp .env.example .env
```
Customize parameters inside `.env` if necessary:
```env
SECRET_KEY=your-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=unienroll_logs
```

#### Run Database Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Create Superuser (Admin Access):
```bash
python manage.py createsuperuser
```

#### Start the Development Server:
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

---

### 3. Running with Docker Compose

To launch the complete stack (Django Application + MongoDB container):

```bash
docker-compose up --build
```

The application will be accessible at:
- **Web App**: `http://localhost:8000`
- **MongoDB**: `localhost:27017` (Connect with **MongoDB Compass** using `mongodb://localhost:27017/` to inspect transaction and audit logs).

---

## 🔒 Security & Best Practices

- **Separation of Concerns**: Sensitive keys, database URIs, and debug flags are managed through `.env`.
- **Excluded Artifacts**: Secrets, SQLite databases, and virtual environments are strictly omitted from version control via `.gitignore`.
- **Role-Based Access Control**: Decorators and custom User model properties ensure Students cannot access administrative dashboards or modify system parameters.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — see the LICENSE file for details.
