## Time Log

| Date       | Hours Worked |
| ---------- | ------------ |
| 2026-01-05 | 5            |
| 2026-01-06 | 5            |
| 2026-01-07 | 5            |
| 2026-01-08 | 5            |
| 2026-01-09 | 5            |
| 2026-01-10 | 5            |
| 2026-01-11 | 5            |
| 2026-01-12 | 5            |
| 2026-01-13 | 5            |
| 2026-01-14 | 5            |

# 🎬 Video Submission Guide

**Module #3 - Cloud Database**

---

## ⏱️ Target Video Length: 4-5 minutes

---

## 📹 BEFORE YOU RECORD

### Setup Checklist

- [ ] Webcam ON (your face must be visible)
- [ ] Screen recording software ready (OBS, Zoom, or Loom work great)
- [ ] Terminal open in VS Code
- [ ] Firebase Console open in browser (console.firebase.google.com)
- [ ] Your code files open in VS Code
- [ ] Environment variables set (FIREBASE_PROJECT_ID, FIREBASE_CREDENTIALS_PATH, FIREBASE_API_KEY)

---

## 🎥 RECORDING SCRIPT (Follow This Exactly)

### **PART 1: INTRO (20 seconds)**

Say this while showing your face:

> "Hi, I'm Kendahl Bingham. This is my Module 3 Cloud Database project. I built a Construction Project Manager using Python and Firebase. My app has ALL THREE additional requirements: user authentication, two related tables, AND real-time notifications."

---

### **PART 2: SHOW FIREBASE CONSOLE (45 seconds)**

**Show Database:**

1. Go to Firebase Console → **Firestore Database**
2. Point out: "I have THREE collections: `projects`, `tasks`, and `users`"
3. Click `tasks` → point to `project_id` field
4. Say: "This `project_id` links tasks to projects - that's my **TWO RELATED TABLES**"

**Show Authentication:**

1. Go to Firebase Console → **Authentication** → **Users**
2. Say: "Here are registered users - this is my **USER AUTHENTICATION** feature"

---

### **PART 3: DEMO THE APP (2-2.5 minutes)**

**Step 1: Run and Login**

```
python main.py
```

- Show the login screen
- Say: "First, I'll **register a new user** to show authentication works"
- Choose option 2 (Register)
- Enter email, name, password
- Say: "Registration successful - this proves **USER AUTHENTICATION**"

**Step 2: Show Real-Time Notifications**

- Say: "The app automatically started listening for changes"
- Go to Notifications menu (option 4)
- Say: "These are **REAL-TIME NOTIFICATIONS** - I get alerts when data changes in the cloud"

**Step 3: Show CRUD Operations**

- Go to Project Management (option 1)
- **CREATE**: Make a new project (quick data)
  - Say: "INSERT complete"
- **READ**: View all projects
  - Say: "QUERY complete"
- **UPDATE**: Update the project
  - Say: "MODIFY complete"
- **DELETE**: Delete the project
  - Say: "DELETE complete"

**Step 4: Show Dashboard**

- Main Menu → option 3 (Dashboard)
- Point out: "Shows my logged-in user and stats from the cloud"

**Step 5: Logout**

- Option 5 to logout
- Say: "Logged out successfully"

---

### **PART 4: CODE WALKTHROUGH (1-1.5 minutes)**

Show these files in VS Code:

#### File 1: `src/services/auth_service.py`

- Say: "This handles **USER AUTHENTICATION** using Firebase Auth REST API"
- Point to `login()` and `register()` methods

#### File 2: `src/services/notification_service.py`

- Say: "This is my **REAL-TIME NOTIFICATIONS** using Firestore snapshot listeners"
- Point to `start_listening()` and `on_snapshot()` callback

#### File 3: `src/models/task.py`

- Point to `project_id` field
- Say: "This links tasks to projects - **TWO RELATED TABLES**"

#### File 4: `src/services/project_repository.py`

- Scroll through `create()`, `update()`, `delete()`, `get_all()` methods
- Say: "All CRUD operations talking to Firestore"

---

### **PART 5: WRAP UP (15 seconds)**

Show your face and say:

> "That's my Cloud Database project with ALL THREE additional features: authentication, related tables, and real-time notifications. Thanks for watching!"

---

## ✅ FINAL CHECKLIST

Before submitting, verify your video shows:

| Requirement                              | Shown? |
| ---------------------------------------- | ------ |
| Your face is visible                     | ☐      |
| Firebase Console - Firestore collections | ☐      |
| Firebase Console - Authentication users  | ☐      |
| Register OR Login demo                   | ☐      |
| CREATE operation                         | ☐      |
| READ operation                           | ☐      |
| UPDATE operation                         | ☐      |
| DELETE operation                         | ☐      |
| Notifications menu                       | ☐      |
| Code: auth_service.py                    | ☐      |
| Code: notification_service.py            | ☐      |
| Code: task.py (project_id)               | ☐      |
| Video is 4-5 minutes                     | ☐      |

---

## 📤 AFTER RECORDING

1. Upload video to YouTube (unlisted), Loom, or school platform
2. Copy the video link
3. Post link to **Microsoft Teams** (5 points!)
4. Submit assignment with video link

---

## 💡 Quick Tips

- Practice once before recording
- Keep moving - don't spend too long on any section
- If something fails, explain what should happen
- Speak clearly and confidently
- Professors watch many videos - be concise!

---

## 🎯 KEY PHRASES TO SAY

Make sure you say these phrases during your demo:

1. ✅ "USER AUTHENTICATION" - when showing login/register
2. ✅ "TWO RELATED TABLES" - when showing project_id
3. ✅ "REAL-TIME NOTIFICATIONS" - when showing notification listener
4. ✅ "INSERT, MODIFY, DELETE, QUERY" - when doing CRUD

---

**You've implemented ALL requirements - now show it off! 🚀**
