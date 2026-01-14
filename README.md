# Construction Project Manager

## Cloud Database Application

A professional construction project management system built with Python and Google Firebase Firestore. This application demonstrates cloud database integration with full CRUD operations and relational data modeling.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Overview

Construction Project Manager is a command-line application designed for construction companies to manage their projects and associated tasks. The application leverages Google Firebase Firestore as a cloud-based NoSQL database, providing real-time data synchronization and scalable storage.

### Key Features

- **User Authentication**: Secure login and registration with Firebase Auth
- **Project Management**: Create, read, update, and delete construction projects
- **Task Management**: Manage tasks linked to specific projects
- **Relational Data**: Two related collections (Projects ↔ Tasks) with referential integrity
- **Real-Time Notifications**: Instant alerts when cloud data changes
- **Status Tracking**: Track project and task progress through multiple status stages
- **Time Logging**: Log actual hours worked against estimated hours
- **Dashboard View**: Summary statistics for quick project oversight

---

## Cloud Database Requirements Fulfilled

### Basic Requirements

| Requirement               | Implementation                                      |
| ------------------------- | --------------------------------------------------- |
| ✅ Cloud database service | Google Firebase Firestore                           |
| ✅ At least one table     | Three collections: `projects`, `tasks`, and `users` |
| ✅ Insert data            | `create()` methods in repositories                  |
| ✅ Modify data            | `update()` methods in repositories                  |
| ✅ Delete data            | `delete()` methods in repositories                  |
| ✅ Query/Retrieve data    | `get_all()`, `get_by_id()`, `get_by_status()`, etc. |

### Additional Requirements (ALL THREE Implemented!)

| Requirement                   | Implementation                                          |
| ----------------------------- | ------------------------------------------------------- |
| ✅ Real-time notifications    | `NotificationService` with Firestore snapshot listeners |
| ✅ Two or more related tables | Projects ↔ Tasks linked via `project_id` foreign key    |
| ✅ User authentication        | `AuthService` using Firebase Auth REST API              |

---

## Technology Stack

- **Language**: Python 3.9+
- **Cloud Database**: Google Firebase Firestore
- **Authentication**: Firebase Auth (REST API)
- **SDK**: firebase-admin, requests
- **Architecture**: Repository Pattern, Singleton Pattern

---

## Project Structure

```
ConstructionProjectManager/
├── src/
│   ├── __init__.py
│   ├── config.py                  # Configuration management
│   ├── cli.py                     # Command-line interface with auth
│   ├── models/
│   │   ├── __init__.py
│   │   ├── project.py             # Project data model
│   │   ├── task.py                # Task data model
│   │   └── user.py                # User data model for auth
│   └── services/
│       ├── __init__.py
│       ├── firebase_service.py    # Firebase connection singleton
│       ├── auth_service.py        # User authentication service
│       ├── notification_service.py # Real-time notifications
│       ├── project_repository.py  # Project CRUD operations
│       └── task_repository.py     # Task CRUD operations
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Setup Instructions

### Prerequisites

1. Python 3.9 or higher installed
2. A Google Firebase account (free tier available)
3. pip package manager

### Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" and follow the wizard
3. Navigate to **Build > Firestore Database**
4. Click "Create database" and select a location
5. Start in **test mode** for development (remember to secure for production)

### Get Service Account Credentials

1. In Firebase Console, click the gear icon → **Project settings**
2. Go to **Service accounts** tab
3. Click **Generate new private key**
4. Save the JSON file securely (DO NOT commit to version control)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ConstructionProjectManager

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Set the following environment variables:

```bash
# Windows PowerShell
$env:FIREBASE_PROJECT_ID = "your-project-id"
$env:FIREBASE_CREDENTIALS_PATH = "C:\path\to\serviceAccountKey.json"
$env:FIREBASE_API_KEY = "your-web-api-key"

# Windows Command Prompt
set FIREBASE_PROJECT_ID=your-project-id
set FIREBASE_CREDENTIALS_PATH=C:\path\to\serviceAccountKey.json
set FIREBASE_API_KEY=your-web-api-key

# macOS/Linux
export FIREBASE_PROJECT_ID="your-project-id"
export FIREBASE_CREDENTIALS_PATH="/path/to/serviceAccountKey.json"
export FIREBASE_API_KEY="your-web-api-key"
```

> **Note**: Find your Web API Key in Firebase Console → Project Settings → General → Web API Key

### Enable Firebase Authentication

1. In Firebase Console, go to **Build → Authentication**
2. Click **Get Started**
3. Enable **Email/Password** sign-in method

### Running the Application

```bash
python -m src.cli
```

---

## Usage Examples

### Creating a Project

```
--- CREATE NEW PROJECT ---

Project Name: Downtown Office Complex
Description: 15-story commercial office building with underground parking
Client Name: Metro Development Corp
Location/Address: 500 Main Street, Downtown
Budget ($): 15000000
Project Manager: John Smith
Status (default: planning): planning
Start Date (YYYY-MM-DD, optional): 2024-03-01
End Date (YYYY-MM-DD, optional): 2025-09-30

✓ Project created successfully!
  Project ID: abc123xyz
```

### Creating a Task

```
--- CREATE NEW TASK ---

Available Projects:
  • abc123xyz: Downtown Office Complex

Project ID: abc123xyz
Task Title: Foundation Excavation
Description: Excavate and prepare foundation area including soil testing
Assigned To: Mike Johnson
Priority (default: medium): high
Estimated Hours: 240
Due Date (YYYY-MM-DD, optional): 2024-04-15
Materials Needed (optional): Excavators, dump trucks, soil testing equipment
Notes (optional): Coordinate with city for permits

✓ Task created successfully!
  Task ID: task456def
```

### Dashboard View

```
============================================================
   CONSTRUCTION PROJECT DASHBOARD
============================================================

📊 PROJECT STATISTICS
   Total Projects: 5
   • planning: 2
   • in_progress: 2
   • completed: 1

📋 TASK STATISTICS
   Total Tasks: 23
   • pending: 8
   • in_progress: 10
   • completed: 5

💰 TOTAL BUDGET: $45,500,000.00

⏱️  HOURS
   Estimated: 12,450.0
   Actual: 8,234.5

============================================================
```

---

## Database Schema

### Projects Collection

| Field           | Type      | Description                                          |
| --------------- | --------- | ---------------------------------------------------- |
| name            | string    | Project name                                         |
| description     | string    | Detailed description                                 |
| client_name     | string    | Client/customer name                                 |
| location        | string    | Site address                                         |
| status          | string    | planning, in_progress, on_hold, completed, cancelled |
| budget          | number    | Budget in dollars                                    |
| start_date      | timestamp | Project start date                                   |
| end_date        | timestamp | Project end date                                     |
| project_manager | string    | Assigned manager                                     |
| created_at      | timestamp | Record creation time                                 |
| updated_at      | timestamp | Last update time                                     |

### Tasks Collection

| Field            | Type      | Description                                         |
| ---------------- | --------- | --------------------------------------------------- |
| project_id       | string    | Reference to parent project (foreign key)           |
| title            | string    | Task title                                          |
| description      | string    | Task description                                    |
| status           | string    | pending, in_progress, completed, blocked, cancelled |
| priority         | string    | low, medium, high, critical                         |
| assigned_to      | string    | Person assigned                                     |
| estimated_hours  | number    | Estimated hours to complete                         |
| actual_hours     | number    | Hours actually spent                                |
| due_date         | timestamp | Task due date                                       |
| completed_date   | timestamp | When task was completed                             |
| materials_needed | string    | Required materials                                  |
| notes            | string    | Additional notes                                    |
| created_at       | timestamp | Record creation time                                |
| updated_at       | timestamp | Last update time                                    |

---

## Architecture Highlights

### Repository Pattern

The application uses the Repository pattern to abstract database operations from business logic. This provides:

- Clean separation of concerns
- Easier unit testing
- Database-agnostic business logic

### Singleton Pattern

The `FirebaseService` class implements the Singleton pattern to ensure only one database connection exists throughout the application lifecycle.

### Data Classes

Python dataclasses are used for models, providing:

- Automatic `__init__`, `__repr__`, and `__eq__` methods
- Type hints for better IDE support
- Clean, readable code

---

## Video Demonstration

[Link to 4-5 minute demonstration video]

The demonstration covers:

1. Firebase console and database structure overview
2. Running the application
3. Creating a new project
4. Adding tasks to the project
5. Updating project status
6. Viewing the dashboard
7. Querying tasks by project
8. Deleting records

---

## Security Considerations

⚠️ **Important**: The service account JSON file contains sensitive credentials.

- **Never** commit the service account file to version control
- Add `serviceAccountKey.json` to `.gitignore`
- Use environment variables for configuration
- In production, consider using secret management services

---

## Future Enhancements

- [ ] Real-time notifications when data changes
- [ ] User authentication and role-based access
- [ ] Web-based user interface
- [ ] Mobile application
- [ ] Report generation (PDF/Excel)
- [ ] Integration with project scheduling tools

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Author

Developed as a demonstration of cloud database integration for construction project management.

## Acknowledgments

- Google Firebase documentation
- Python firebase-admin SDK
- Construction industry best practices for project management
