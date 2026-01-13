"""
Demo Script for Construction Project Manager.

This script demonstrates the core CRUD functionality of the application
without requiring user interaction. Useful for testing and demonstration.

Usage:
    1. Set environment variables:
       - FIREBASE_PROJECT_ID
       - FIREBASE_CREDENTIALS_PATH
    2. Run: python demo.py

Author: Construction Solutions
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import AppConfig
from src.services.firebase_service import FirebaseService
from src.services.project_repository import ProjectRepository
from src.services.task_repository import TaskRepository
from src.models.project import Project, ProjectStatus
from src.models.task import Task, TaskStatus, TaskPriority


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def run_demo():
    """Run the demonstration of all CRUD operations."""
    
    print_section("CONSTRUCTION PROJECT MANAGER - DEMO")
    
    # ==================== INITIALIZATION ====================
    print("Initializing Firebase connection...")
    
    try:
        config = AppConfig.load()
        firebase = FirebaseService()
        firebase.initialize(
            config.firebase.credentials_path,
            config.firebase.project_id
        )
        print("✓ Connected to Firebase successfully!\n")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("\nPlease ensure environment variables are set:")
        print("  - FIREBASE_PROJECT_ID")
        print("  - FIREBASE_CREDENTIALS_PATH")
        return
    
    # Initialize repositories
    project_repo = ProjectRepository(firebase)
    task_repo = TaskRepository(firebase)
    
    # ==================== CREATE OPERATIONS ====================
    print_section("1. CREATE OPERATIONS")
    
    # Create a new project
    print("Creating a new construction project...")
    
    project = Project(
        name="Riverside Commercial Plaza",
        description="Mixed-use development with retail and office space",
        client_name="Riverside Development LLC",
        location="1200 River Road, Riverside, CA",
        budget=8500000.00,
        project_manager="Sarah Johnson",
        status=ProjectStatus.PLANNING,
        start_date=datetime.now() + timedelta(days=30),
        end_date=datetime.now() + timedelta(days=365)
    )
    
    created_project = project_repo.create(project)
    print(f"✓ Project created!")
    print(f"  ID: {created_project.id}")
    print(f"  Name: {created_project.name}")
    print(f"  Budget: ${created_project.budget:,.2f}")
    
    # Create tasks for the project
    print("\nCreating tasks for the project...")
    
    tasks_data = [
        {
            "title": "Site Survey and Assessment",
            "description": "Complete topographical survey and soil analysis",
            "assigned_to": "Mike Chen",
            "priority": TaskPriority.HIGH,
            "estimated_hours": 40,
            "due_date": datetime.now() + timedelta(days=14)
        },
        {
            "title": "Permit Applications",
            "description": "Submit building permits to city planning department",
            "assigned_to": "Lisa Wang",
            "priority": TaskPriority.CRITICAL,
            "estimated_hours": 20,
            "due_date": datetime.now() + timedelta(days=21)
        },
        {
            "title": "Foundation Design Review",
            "description": "Review and approve foundation engineering plans",
            "assigned_to": "Robert Smith",
            "priority": TaskPriority.MEDIUM,
            "estimated_hours": 16,
            "due_date": datetime.now() + timedelta(days=45)
        }
    ]
    
    created_tasks = []
    for task_data in tasks_data:
        task = Task(
            project_id=created_project.id,
            **task_data
        )
        created_task = task_repo.create(task)
        created_tasks.append(created_task)
        print(f"  ✓ Task created: {created_task.title} (ID: {created_task.id})")
    
    # ==================== READ OPERATIONS ====================
    print_section("2. READ OPERATIONS")
    
    # Retrieve the project by ID
    print(f"Retrieving project by ID: {created_project.id}")
    retrieved_project = project_repo.get_by_id(created_project.id)
    print(f"  Found: {retrieved_project.name}")
    print(f"  Status: {retrieved_project.status.value}")
    print(f"  Manager: {retrieved_project.project_manager}")
    
    # Retrieve all tasks for the project
    print(f"\nRetrieving tasks for project...")
    project_tasks = task_repo.get_by_project(created_project.id)
    print(f"  Found {len(project_tasks)} tasks:")
    for task in project_tasks:
        print(f"    • {task.title} [{task.priority.value}]")
    
    # Query tasks by priority
    print("\nQuerying high priority tasks...")
    high_priority_tasks = task_repo.get_by_priority(TaskPriority.HIGH)
    print(f"  Found {len(high_priority_tasks)} high priority tasks")
    
    # ==================== UPDATE OPERATIONS ====================
    print_section("3. UPDATE OPERATIONS")
    
    # Update project status
    print("Updating project status to 'in_progress'...")
    retrieved_project.status = ProjectStatus.IN_PROGRESS
    retrieved_project.budget = 9000000.00  # Budget revision
    updated_project = project_repo.update(retrieved_project)
    print(f"  ✓ Project updated!")
    print(f"    New Status: {updated_project.status.value}")
    print(f"    New Budget: ${updated_project.budget:,.2f}")
    
    # Update task status and log hours
    print("\nUpdating first task status and logging hours...")
    first_task = created_tasks[0]
    task_repo.update_status(first_task.id, TaskStatus.IN_PROGRESS)
    task_repo.log_hours(first_task.id, 8.5)
    
    updated_task = task_repo.get_by_id(first_task.id)
    print(f"  ✓ Task '{updated_task.title}' updated!")
    print(f"    Status: {updated_task.status.value}")
    print(f"    Hours logged: {updated_task.actual_hours}")
    
    # ==================== QUERY OPERATIONS ====================
    print_section("4. QUERY OPERATIONS")
    
    # Filter projects by status
    print("Filtering projects by status 'in_progress'...")
    in_progress_projects = project_repo.get_by_status(ProjectStatus.IN_PROGRESS)
    print(f"  Found {len(in_progress_projects)} in-progress projects")
    
    # Filter tasks by status
    print("\nFiltering tasks by status 'in_progress'...")
    in_progress_tasks = task_repo.get_by_status(TaskStatus.IN_PROGRESS)
    print(f"  Found {len(in_progress_tasks)} in-progress tasks")
    
    # Get all projects
    print("\nListing all projects in database...")
    all_projects = project_repo.get_all()
    print(f"  Total projects: {len(all_projects)}")
    for p in all_projects[:5]:  # Show first 5
        print(f"    • {p.name} [{p.status.value}]")
    
    # ==================== DELETE OPERATIONS ====================
    print_section("5. DELETE OPERATIONS")
    
    print(f"Deleting demo project and its tasks...")
    
    # Delete tasks first (referential integrity)
    deleted_count = task_repo.delete_by_project(created_project.id)
    print(f"  ✓ Deleted {deleted_count} tasks")
    
    # Delete the project
    project_repo.delete(created_project.id)
    print(f"  ✓ Deleted project: {created_project.name}")
    
    # Verify deletion
    verify_project = project_repo.get_by_id(created_project.id)
    if verify_project is None:
        print("  ✓ Verified: Project no longer exists in database")
    
    # ==================== CLEANUP ====================
    print_section("DEMO COMPLETE")
    
    print("All CRUD operations demonstrated successfully!")
    print("\nOperations performed:")
    print("  ✓ CREATE - Projects and Tasks")
    print("  ✓ READ   - By ID, by project, by status, by priority")
    print("  ✓ UPDATE - Status changes, budget updates, hour logging")
    print("  ✓ DELETE - Tasks and Projects with cascading delete")
    print("\nRelational feature demonstrated:")
    print("  ✓ Tasks linked to Projects via project_id foreign key")
    
    # Close Firebase connection
    firebase.close()
    print("\n✓ Firebase connection closed.")


if __name__ == "__main__":
    run_demo()
