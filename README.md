# ☁️ MeAlembra

**A personal task manager and reminder application designed to help users organize their daily activities and never forget what matters.**

## About the Project

MeAlembra is a task management application developed as a personal software development project because the owner keeps forgetting things. 

Its main purpose is to allow users to create, organize, manage and complete tasks through a simple and intuitive interface.

The application is designed to provide persistent reminders, helping users stay focused on their responsibilities until their tasks are completed.

## Main Features

### Task Management
- Create reminders with a title, description, date and time.
- View pending tasks.
- Mark tasks as completed.
- Reschedule existing reminders.
- Delete tasks.

### Persistent Notifications
- Automatic notification configuration when a reminder is created.
- Default notification interval of 15 minutes.
- Notifications remain active until the associated task is completed.
- Background scheduling system using Python.

### User Personalization
- Four visual themes:
  - Pastel pink
  - Pastel blue
  - Neutral gray
  - Beige and pastel yellow
- Soft, minimal and responsive interface.

### Planned Features
- Task history.
- Automatic identification of frequently created tasks.
- Regular tasks section.
- Calendar view.
- User-specific preferences.
- Real push notifications through Web Push.
- Progressive Web App (PWA) installation.

## Technologies

| Area | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Database | SQLite |
| API Documentation | Swagger / OpenAPI | StackOverflow
| Task Scheduling | APScheduler |
| Version Control | Git and GitHub |
| Future Notifications | Web Push API |

## Project Structure

```text
MeAlembra/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   └── scheduler.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── .gitignore
├── README.md
└── CHANGELOG.md
```

## Running the Project

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
```

### 2. Access the backend directory

```bash
cd MeAlembra/backend
```

### 3. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install fastapi uvicorn apscheduler pywebpush
```

### 5. Start the backend

```bash
python -m uvicorn main:app --reload
```

### 6. Access the API documentation

Open:

```text
http://127.0.0.1:8000/docs
```

## Project Status

**In Development**

The backend currently supports task management, SQLite persistence, notification configuration and background scheduling simulation.

The frontend is under development. Real push notification delivery, user authentication and full PWA functionality are planned for future stages.

## Version Control

This project uses Git for version control.

Development changes are documented through commits and the project changelog.

## Author

Developed as a personal software development project.

**MeAlembra — Organize your tasks. Remember what matters.**