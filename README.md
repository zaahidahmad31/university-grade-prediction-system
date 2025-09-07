# Project Setup

A web application for predicting university grades using machine learning.  
This project includes a Flask backend, a modern frontend, and integrates ML models for grade predictions.

---

## Preconditions

Before running the project, ensure you have:

- Python 3.8+ installed  
- Node.js 16+ and npm  
- MySQL (default) or PostgreSQL (update `.env` accordingly)  
- Optional: Redis for Celery task queue (if background tasks are needed)  

---

## Backend Setup

1. **Clone the repository**

```
git clone https://github.com/zaahidahmad31/university-grade-prediction-system.git
cd university-grade-prediction-system
```

2. **Install Python dependencies**
```
pip install -r requirements.txt
```

3. **Configure environment variables**

4. **Copy `.env.example` to `.env` and update database credentials**
```
DEV_DATABASE_URL=mysql+pymysql://root:Zaheed@oct19@localhost/university_grade_prediction_test_1
DATABASE_URL=mysql+pymysql://user:Zaheed@oct19@localhost/university_grade_prediction_test_1
```

5. **Start the backend server**
```
python wsgi.py
```

---

## Frontend Setup

1. **Navigate to the frontend folder**
   
```
cd frontend
```

3. **Install dependencies**
```
npm install
```

4. **Start the frontend development server**
```
npm run start
```
5. **Start the frontend development server**
```
http://localhost:3000
```
6. **"learning management system database.sql" run this code in mysql workbench**

# Project Credentials

## Database Credentials

**Default database access:**

- **Hostname:** localhost  
- **Username:** root  
- **Password:** Zaheed@oct19  

> You can change the database username and password on your database server. 
> If you do, update the `.env` file (`DEV_DATABASE_URL` and `DATABASE_URL`) so the backend can connect correctly.

## Admin Account

**Admin login for the application:**

- **Username:** admin  
- **Password:** hacker@119  

> The admin account can be used to manage users, view reports, and perform higher-level operations.

## Notes

- Students and faculty can register through the frontend registration form.  
- Make sure to keep credentials secure and do not commit real passwords to the repository.



# Project Structure
```
university-grade-prediction-system
├─ backend
│  ├─ api
│  │  ├─ admin
│  │  │  ├─ routes.py
│  │  │  └─ __init__.py
│  │  ├─ auth
│  │  │  ├─ routes.py
│  │  │  └─ __init__.py
│  │  ├─ common
│  │  │  ├─ routes.py
│  │  │  └─ __init__.py
│  │  ├─ faculty
│  │  │  ├─ routes.py
│  │  │  └─ __init__.py
│  │  ├─ prediction
│  │  │  ├─ routes.py
│  │  │  └─ __init__.py
│  │  ├─ student
│  │  │  ├─ routes.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ app.py
│  ├─ extensions.py
│  ├─ middleware
│  │  ├─ error_handler.py
│  │  └─ __init__.py
│  ├─ ml_integration
│  │  └─ __init__.py
│  ├─ models
│  │  └─ __init__.py
│  ├─ services
│  │  └─ __init__.py
│  ├─ tasks
│  ├─ utils
│  │  ├─ logger.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ config.py
├─ database
│  ├─ migrations
│  ├─ procedures
│  ├─ schema
│  └─ seeds
├─ deployment
│  ├─ kubernetes
│  ├─ nginx
│  ├─ systemd
│  └─ terraform
├─ docs
│  ├─ api
│  ├─ guides
│  ├─ images
│  └─ technical
├─ frontend
│  ├─ public
│  ├─ src
│  │  ├─ assets
│  │  │  ├─ fonts
│  │  │  ├─ images
│  │  │  └─ vendor
│  │  ├─ css
│  │  └─ js
│  │     ├─ api
│  │     ├─ auth
│  │     ├─ components
│  │     ├─ pages
│  │     └─ utils
│  └─ templates
│     ├─ admin
│     ├─ auth
│     ├─ components
│     ├─ errors
│     ├─ faculty
│     ├─ layouts
│     └─ student
├─ ml_models
├─ package.json
├─ README.md
├─ requirements.txt
├─ scripts
│  ├─ data
│  ├─ deployment
│  ├─ maintenance
│  └─ setup
├─ setup_project.py
├─ tests
│  ├─ e2e
│  ├─ fixtures
│  ├─ integration
│  └─ unit
└─ wsgi.py

```
