"""
Command Line Interface for Construction Project Manager.

This module provides an interactive CLI for managing construction
projects and tasks using the cloud-based Firestore database.
Includes user authentication and real-time notifications.

Author: Construction Solutions
"""

import sys
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import AppConfig
from src.services.firebase_service import FirebaseService
from src.services.project_repository import ProjectRepository
from src.services.task_repository import TaskRepository
from src.services.auth_service import AuthService
from src.services.notification_service import NotificationService, Notification
from src.models.project import Project, ProjectStatus
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.user import User


class ConstructionManagerCLI:
    """
    Interactive command-line interface for the Construction Project Manager.
    
    This class provides a menu-driven interface for performing CRUD
    operations on projects and tasks, with user authentication and
    real-time notifications.
    """
    
    def __init__(self):
        """Initialize the CLI with database connections."""
        self.firebase: Optional[FirebaseService] = None
        self.project_repo: Optional[ProjectRepository] = None
        self.task_repo: Optional[TaskRepository] = None
        self.auth_service: Optional[AuthService] = None
        self.notification_service: Optional[NotificationService] = None
        self.config: Optional[AppConfig] = None
        self.running = True
        self._notification_display_enabled = True
    
    def _on_notification(self, notification: Notification) -> None:
        """
        Callback function for real-time notifications.
        
        This is called automatically when data changes in Firestore.
        
        Args:
            notification: The notification received from Firestore
        """
        if self._notification_display_enabled:
            print(f"\n🔔 REAL-TIME UPDATE: {notification}")
            print("   (Data changed in cloud database)")
    
    def initialize(self) -> bool:
        """
        Initialize the Firebase connection and repositories.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            print("\n" + "=" * 60)
            print("   CONSTRUCTION PROJECT MANAGER")
            print("   Cloud Database Management System")
            print("=" * 60)
            
            self.config = AppConfig.load()
            
            self.firebase = FirebaseService()
            self.firebase.initialize(
                self.config.firebase.credentials_path,
                self.config.firebase.project_id
            )
            
            self.project_repo = ProjectRepository(self.firebase)
            self.task_repo = TaskRepository(self.firebase)
            
            # Initialize authentication service
            self.auth_service = AuthService(
                self.firebase,
                self.config.firebase.api_key
            )
            
            # Initialize notification service for real-time updates
            self.notification_service = NotificationService(self.firebase)
            self.notification_service.add_callback(self._on_notification)
            
            print("\n✓ Connected to Firebase successfully!")
            return True
            
        except ValueError as e:
            print(f"\n✗ Configuration Error: {e}")
            print("\nPlease set the following environment variables:")
            print("  - FIREBASE_PROJECT_ID: Your Firebase project ID")
            print("  - FIREBASE_CREDENTIALS_PATH: Path to service account JSON")
            print("  - FIREBASE_API_KEY: Firebase Web API key")
            return False
        except Exception as e:
            print(f"\n✗ Initialization Error: {e}")
            return False
    
    # ==================== AUTHENTICATION ====================
    
    def display_auth_menu(self) -> None:
        """Display the authentication menu."""
        print("\n" + "-" * 40)
        print("AUTHENTICATION")
        print("-" * 40)
        print("1. Login")
        print("2. Register New Account")
        print("3. Exit")
        print("-" * 40)
    
    def handle_login(self) -> bool:
        """
        Handle user login.
        
        Returns:
            True if login was successful
        """
        print("\n--- LOGIN ---\n")
        
        email = self.get_input("Email: ")
        password = self.get_input("Password: ")
        
        success, message = self.auth_service.login(email, password)
        
        if success:
            print(f"\n✓ {message}")
            return True
        else:
            print(f"\n✗ {message}")
            return False
    
    def handle_register(self) -> bool:
        """
        Handle new user registration.
        
        Returns:
            True if registration was successful
        """
        print("\n--- REGISTER NEW ACCOUNT ---\n")
        
        email = self.get_input("Email: ")
        display_name = self.get_input("Display Name: ")
        
        print("\nPassword must be at least 6 characters.")
        password = self.get_input("Password: ")
        confirm_password = self.get_input("Confirm Password: ")
        
        if password != confirm_password:
            print("\n✗ Passwords do not match. Please try again.")
            return False
        
        if len(password) < 6:
            print("\n✗ Password must be at least 6 characters.")
            return False
        
        success, message = self.auth_service.register(email, password, display_name)
        
        if success:
            print(f"\n✓ {message}")
            return True
        else:
            print(f"\n✗ {message}")
            return False
    
    def run_auth_flow(self) -> bool:
        """
        Run the authentication flow.
        
        Returns:
            True if user is authenticated, False to exit
        """
        while True:
            self.display_auth_menu()
            choice = input("Enter choice: ").strip()
            
            if choice == '1':
                if self.handle_login():
                    return True
            elif choice == '2':
                if self.handle_register():
                    return True
            elif choice == '3':
                return False
            else:
                print("\n✗ Invalid choice. Please try again.")
    
    # ==================== MAIN MENU ====================
    
    def display_main_menu(self) -> None:
        """Display the main menu options."""
        user = self.auth_service.current_user
        print("\n" + "-" * 40)
        print(f"MAIN MENU | Logged in as: {user.display_name}")
        print("-" * 40)
        print("1. Project Management")
        print("2. Task Management")
        print("3. View Dashboard")
        print("4. Notifications")
        print("5. Logout")
        print("-" * 40)
    
    def display_project_menu(self) -> None:
        """Display the project management menu."""
        print("\n" + "-" * 40)
        print("PROJECT MANAGEMENT")
        print("-" * 40)
        print("1. Create New Project")
        print("2. View All Projects")
        print("3. View Project Details")
        print("4. Update Project")
        print("5. Delete Project")
        print("6. Filter by Status")
        print("7. Back to Main Menu")
        print("-" * 40)
    
    def display_task_menu(self) -> None:
        """Display the task management menu."""
        print("\n" + "-" * 40)
        print("TASK MANAGEMENT")
        print("-" * 40)
        print("1. Create New Task")
        print("2. View All Tasks")
        print("3. View Tasks by Project")
        print("4. Update Task")
        print("5. Delete Task")
        print("6. Update Task Status")
        print("7. Log Hours")
        print("8. Back to Main Menu")
        print("-" * 40)
    
    def display_notification_menu(self) -> None:
        """Display the notification management menu."""
        print("\n" + "-" * 40)
        print("NOTIFICATIONS (Real-Time Updates)")
        print("-" * 40)
        listeners = self.notification_service.get_active_listeners()
        print(f"Active Listeners: {', '.join(listeners) if listeners else 'None'}")
        print("-" * 40)
        print("1. Start Listening to Projects")
        print("2. Start Listening to Tasks")
        print("3. Stop All Listeners")
        print("4. View Recent Notifications")
        print("5. Clear Notifications")
        print("6. Toggle Notification Display")
        print("7. Back to Main Menu")
        print("-" * 40)
    
    def get_input(self, prompt: str, required: bool = True) -> str:
        """Get user input with optional validation."""
        while True:
            value = input(prompt).strip()
            if value or not required:
                return value
            print("This field is required. Please enter a value.")
    
    def get_float_input(self, prompt: str, default: float = 0.0) -> float:
        """Get float input with validation."""
        while True:
            value = input(prompt).strip()
            if not value:
                return default
            try:
                return float(value)
            except ValueError:
                print("Please enter a valid number.")
    
    def get_date_input(self, prompt: str) -> Optional[datetime]:
        """Get date input with validation."""
        value = input(prompt).strip()
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Using no date.")
            return None
    
    # ==================== NOTIFICATION OPERATIONS ====================
    
    def run_notification_menu(self) -> None:
        """Handle the notification management menu loop."""
        while True:
            self.display_notification_menu()
            choice = input("Enter choice: ").strip()
            
            if choice == '1':
                if self.notification_service.start_listening("projects"):
                    print("\n✓ Now listening for project changes!")
                    print("  You'll see real-time updates when projects change.")
                else:
                    print("\n⚠ Already listening to projects.")
            elif choice == '2':
                if self.notification_service.start_listening("tasks"):
                    print("\n✓ Now listening for task changes!")
                    print("  You'll see real-time updates when tasks change.")
                else:
                    print("\n⚠ Already listening to tasks.")
            elif choice == '3':
                self.notification_service.stop_all_listeners()
                print("\n✓ All listeners stopped.")
            elif choice == '4':
                self.notification_service.print_recent_notifications()
            elif choice == '5':
                self.notification_service.clear_notifications()
                print("\n✓ Notifications cleared.")
            elif choice == '6':
                self._notification_display_enabled = not self._notification_display_enabled
                status = "enabled" if self._notification_display_enabled else "disabled"
                print(f"\n✓ Real-time notification display {status}.")
            elif choice == '7':
                break
            else:
                print("\n✗ Invalid choice. Please try again.")
    
    # ==================== PROJECT OPERATIONS ====================
    
    def create_project(self) -> None:
        """Create a new construction project."""
        print("\n--- CREATE NEW PROJECT ---\n")
        
        name = self.get_input("Project Name: ")
        description = self.get_input("Description: ")
        client_name = self.get_input("Client Name: ")
        location = self.get_input("Location/Address: ")
        budget = self.get_float_input("Budget ($): ")
        project_manager = self.get_input("Project Manager: ")
        
        print("\nStatus Options: planning, in_progress, on_hold, completed, cancelled")
        status_input = self.get_input("Status (default: planning): ", required=False) or "planning"
        
        try:
            status = ProjectStatus.from_string(status_input)
        except ValueError:
            status = ProjectStatus.PLANNING
            print("Invalid status. Using 'planning'.")
        
        start_date = self.get_date_input("Start Date (YYYY-MM-DD, optional): ")
        end_date = self.get_date_input("End Date (YYYY-MM-DD, optional): ")
        
        project = Project(
            name=name,
            description=description,
            client_name=client_name,
            location=location,
            budget=budget,
            project_manager=project_manager,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        created_project = self.project_repo.create(project)
        print(f"\n✓ Project created successfully!")
        print(f"  Project ID: {created_project.id}")
    
    def view_all_projects(self) -> None:
        """Display all projects in the database."""
        print("\n--- ALL PROJECTS ---\n")
        
        projects = self.project_repo.get_all()
        
        if not projects:
            print("No projects found.")
            return
        
        for project in projects:
            print(f"\n{project}")
            print("-" * 40)
    
    def view_project_details(self) -> None:
        """View detailed information about a specific project."""
        project_id = self.get_input("\nEnter Project ID: ")
        
        project = self.project_repo.get_by_id(project_id)
        
        if project:
            print(f"\n--- PROJECT DETAILS ---\n")
            print(project)
            
            # Show associated tasks
            tasks = self.task_repo.get_by_project(project_id)
            if tasks:
                print(f"\n--- ASSOCIATED TASKS ({len(tasks)}) ---")
                for task in tasks:
                    print(f"  • {task.title} [{task.status.value}] - {task.assigned_to}")
        else:
            print("\n✗ Project not found.")
    
    def update_project(self) -> None:
        """Update an existing project."""
        project_id = self.get_input("\nEnter Project ID to update: ")
        
        project = self.project_repo.get_by_id(project_id)
        
        if not project:
            print("\n✗ Project not found.")
            return
        
        print(f"\nUpdating: {project.name}")
        print("(Press Enter to keep current value)\n")
        
        name = input(f"Name [{project.name}]: ").strip() or project.name
        description = input(f"Description [{project.description[:30]}...]: ").strip() or project.description
        client_name = input(f"Client [{project.client_name}]: ").strip() or project.client_name
        location = input(f"Location [{project.location}]: ").strip() or project.location
        
        budget_input = input(f"Budget [${project.budget:,.2f}]: ").strip()
        budget = float(budget_input) if budget_input else project.budget
        
        project_manager = input(f"Manager [{project.project_manager}]: ").strip() or project.project_manager
        
        print(f"\nCurrent Status: {project.status.value}")
        print("Options: planning, in_progress, on_hold, completed, cancelled")
        status_input = input("New Status: ").strip()
        
        if status_input:
            try:
                status = ProjectStatus.from_string(status_input)
            except ValueError:
                status = project.status
                print("Invalid status. Keeping current.")
        else:
            status = project.status
        
        # Update project fields
        project.name = name
        project.description = description
        project.client_name = client_name
        project.location = location
        project.budget = budget
        project.project_manager = project_manager
        project.status = status
        
        self.project_repo.update(project)
        print("\n✓ Project updated successfully!")
    
    def delete_project(self) -> None:
        """Delete a project and its associated tasks."""
        project_id = self.get_input("\nEnter Project ID to delete: ")
        
        project = self.project_repo.get_by_id(project_id)
        
        if not project:
            print("\n✗ Project not found.")
            return
        
        print(f"\nProject: {project.name}")
        confirm = input("Are you sure you want to delete this project and all its tasks? (yes/no): ")
        
        if confirm.lower() == 'yes':
            # Delete associated tasks first
            deleted_tasks = self.task_repo.delete_by_project(project_id)
            self.project_repo.delete(project_id)
            print(f"\n✓ Project deleted successfully!")
            print(f"  Also deleted {deleted_tasks} associated tasks.")
        else:
            print("\nDeletion cancelled.")
    
    def filter_projects_by_status(self) -> None:
        """Filter and display projects by status."""
        print("\nStatus Options: planning, in_progress, on_hold, completed, cancelled")
        status_input = self.get_input("Enter status to filter: ")
        
        try:
            status = ProjectStatus.from_string(status_input)
            projects = self.project_repo.get_by_status(status)
            
            if projects:
                print(f"\n--- PROJECTS WITH STATUS: {status.value.upper()} ---\n")
                for project in projects:
                    print(f"  • {project.name} (ID: {project.id})")
                    print(f"    Client: {project.client_name} | Manager: {project.project_manager}")
            else:
                print(f"\nNo projects found with status: {status.value}")
                
        except ValueError:
            print("\n✗ Invalid status.")
    
    # ==================== TASK OPERATIONS ====================
    
    def create_task(self) -> None:
        """Create a new task for a project."""
        print("\n--- CREATE NEW TASK ---\n")
        
        # Show available projects
        projects = self.project_repo.get_all()
        if not projects:
            print("No projects available. Please create a project first.")
            return
        
        print("Available Projects:")
        for p in projects:
            print(f"  • {p.id}: {p.name}")
        
        project_id = self.get_input("\nProject ID: ")
        
        # Verify project exists
        if not self.project_repo.get_by_id(project_id):
            print("\n✗ Project not found.")
            return
        
        title = self.get_input("Task Title: ")
        description = self.get_input("Description: ")
        assigned_to = self.get_input("Assigned To: ")
        
        print("\nPriority Options: low, medium, high, critical")
        priority_input = self.get_input("Priority (default: medium): ", required=False) or "medium"
        
        try:
            priority = TaskPriority.from_string(priority_input)
        except ValueError:
            priority = TaskPriority.MEDIUM
            print("Invalid priority. Using 'medium'.")
        
        estimated_hours = self.get_float_input("Estimated Hours: ")
        due_date = self.get_date_input("Due Date (YYYY-MM-DD, optional): ")
        materials_needed = self.get_input("Materials Needed (optional): ", required=False)
        notes = self.get_input("Notes (optional): ", required=False)
        
        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            priority=priority,
            estimated_hours=estimated_hours,
            due_date=due_date,
            materials_needed=materials_needed,
            notes=notes
        )
        
        created_task = self.task_repo.create(task)
        print(f"\n✓ Task created successfully!")
        print(f"  Task ID: {created_task.id}")
    
    def view_all_tasks(self) -> None:
        """Display all tasks in the database."""
        print("\n--- ALL TASKS ---\n")
        
        tasks = self.task_repo.get_all()
        
        if not tasks:
            print("No tasks found.")
            return
        
        for task in tasks:
            print(f"\n{task}")
            print("-" * 40)
    
    def view_tasks_by_project(self) -> None:
        """View all tasks for a specific project."""
        project_id = self.get_input("\nEnter Project ID: ")
        
        project = self.project_repo.get_by_id(project_id)
        
        if not project:
            print("\n✗ Project not found.")
            return
        
        tasks = self.task_repo.get_by_project(project_id)
        
        print(f"\n--- TASKS FOR: {project.name} ---\n")
        
        if not tasks:
            print("No tasks found for this project.")
            return
        
        for task in tasks:
            print(f"\n{task}")
            print("-" * 40)
    
    def update_task(self) -> None:
        """Update an existing task."""
        task_id = self.get_input("\nEnter Task ID to update: ")
        
        task = self.task_repo.get_by_id(task_id)
        
        if not task:
            print("\n✗ Task not found.")
            return
        
        print(f"\nUpdating: {task.title}")
        print("(Press Enter to keep current value)\n")
        
        title = input(f"Title [{task.title}]: ").strip() or task.title
        description = input(f"Description [{task.description[:30]}...]: ").strip() or task.description
        assigned_to = input(f"Assigned To [{task.assigned_to}]: ").strip() or task.assigned_to
        
        hours_input = input(f"Estimated Hours [{task.estimated_hours}]: ").strip()
        estimated_hours = float(hours_input) if hours_input else task.estimated_hours
        
        materials = input(f"Materials [{task.materials_needed[:30] if task.materials_needed else 'None'}]: ").strip()
        if materials:
            task.materials_needed = materials
        
        notes = input(f"Notes [{task.notes[:30] if task.notes else 'None'}]: ").strip()
        if notes:
            task.notes = notes
        
        # Update task fields
        task.title = title
        task.description = description
        task.assigned_to = assigned_to
        task.estimated_hours = estimated_hours
        
        self.task_repo.update(task)
        print("\n✓ Task updated successfully!")
    
    def delete_task(self) -> None:
        """Delete a task."""
        task_id = self.get_input("\nEnter Task ID to delete: ")
        
        task = self.task_repo.get_by_id(task_id)
        
        if not task:
            print("\n✗ Task not found.")
            return
        
        print(f"\nTask: {task.title}")
        confirm = input("Are you sure you want to delete this task? (yes/no): ")
        
        if confirm.lower() == 'yes':
            self.task_repo.delete(task_id)
            print("\n✓ Task deleted successfully!")
        else:
            print("\nDeletion cancelled.")
    
    def update_task_status(self) -> None:
        """Update the status of a task."""
        task_id = self.get_input("\nEnter Task ID: ")
        
        task = self.task_repo.get_by_id(task_id)
        
        if not task:
            print("\n✗ Task not found.")
            return
        
        print(f"\nTask: {task.title}")
        print(f"Current Status: {task.status.value}")
        print("\nStatus Options: pending, in_progress, completed, blocked, cancelled")
        
        status_input = self.get_input("New Status: ")
        
        try:
            new_status = TaskStatus.from_string(status_input)
            self.task_repo.update_status(task_id, new_status)
            print(f"\n✓ Status updated to: {new_status.value}")
        except ValueError:
            print("\n✗ Invalid status.")
    
    def log_hours(self) -> None:
        """Log hours worked on a task."""
        task_id = self.get_input("\nEnter Task ID: ")
        
        task = self.task_repo.get_by_id(task_id)
        
        if not task:
            print("\n✗ Task not found.")
            return
        
        print(f"\nTask: {task.title}")
        print(f"Current Hours: {task.actual_hours} / {task.estimated_hours} estimated")
        
        hours = self.get_float_input("Hours to add: ")
        
        if hours > 0:
            self.task_repo.log_hours(task_id, hours)
            print(f"\n✓ Logged {hours} hours. New total: {task.actual_hours + hours}")
        else:
            print("\nNo hours logged.")
    
    # ==================== DASHBOARD ====================
    
    def view_dashboard(self) -> None:
        """Display a summary dashboard."""
        print("\n" + "=" * 60)
        print("   CONSTRUCTION PROJECT DASHBOARD")
        print("=" * 60)
        
        user = self.auth_service.current_user
        print(f"\n👤 USER: {user.display_name} ({user.email})")
        print(f"   Role: {user.role.value}")
        
        projects = self.project_repo.get_all()
        tasks = self.task_repo.get_all()
        
        # Project statistics
        print(f"\n📊 PROJECT STATISTICS")
        print(f"   Total Projects: {len(projects)}")
        
        status_counts = {}
        for p in projects:
            status = p.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"   • {status}: {count}")
        
        # Task statistics
        print(f"\n📋 TASK STATISTICS")
        print(f"   Total Tasks: {len(tasks)}")
        
        task_status_counts = {}
        for t in tasks:
            status = t.status.value
            task_status_counts[status] = task_status_counts.get(status, 0) + 1
        
        for status, count in task_status_counts.items():
            print(f"   • {status}: {count}")
        
        # Budget summary
        total_budget = sum(p.budget for p in projects)
        print(f"\n💰 TOTAL BUDGET: ${total_budget:,.2f}")
        
        # Hours summary
        total_estimated = sum(t.estimated_hours for t in tasks)
        total_actual = sum(t.actual_hours for t in tasks)
        print(f"\n⏱️  HOURS")
        print(f"   Estimated: {total_estimated:.1f}")
        print(f"   Actual: {total_actual:.1f}")
        
        # Notification status
        listeners = self.notification_service.get_active_listeners()
        print(f"\n🔔 ACTIVE LISTENERS: {', '.join(listeners) if listeners else 'None'}")
        print(f"   Pending Notifications: {self.notification_service.unread_count}")
        
        print("\n" + "=" * 60)
    
    # ==================== MAIN LOOP ====================
    
    def run_project_menu(self) -> None:
        """Handle the project management menu loop."""
        while True:
            self.display_project_menu()
            choice = input("Enter choice: ").strip()
            
            if choice == '1':
                self.create_project()
            elif choice == '2':
                self.view_all_projects()
            elif choice == '3':
                self.view_project_details()
            elif choice == '4':
                self.update_project()
            elif choice == '5':
                self.delete_project()
            elif choice == '6':
                self.filter_projects_by_status()
            elif choice == '7':
                break
            else:
                print("\n✗ Invalid choice. Please try again.")
    
    def run_task_menu(self) -> None:
        """Handle the task management menu loop."""
        while True:
            self.display_task_menu()
            choice = input("Enter choice: ").strip()
            
            if choice == '1':
                self.create_task()
            elif choice == '2':
                self.view_all_tasks()
            elif choice == '3':
                self.view_tasks_by_project()
            elif choice == '4':
                self.update_task()
            elif choice == '5':
                self.delete_task()
            elif choice == '6':
                self.update_task_status()
            elif choice == '7':
                self.log_hours()
            elif choice == '8':
                break
            else:
                print("\n✗ Invalid choice. Please try again.")
    
    def run(self) -> None:
        """Main application loop."""
        if not self.initialize():
            return
        
        # Run authentication flow first
        print("\n" + "=" * 60)
        print("   Please login or register to continue")
        print("=" * 60)
        
        if not self.run_auth_flow():
            print("\nGoodbye!")
            return
        
        # Start real-time listeners after authentication
        print("\n✓ Starting real-time notifications...")
        self.notification_service.start_listening("projects")
        self.notification_service.start_listening("tasks")
        print("  Listening for changes to projects and tasks.")
        
        while self.running:
            self.display_main_menu()
            choice = input("Enter choice: ").strip()
            
            if choice == '1':
                self.run_project_menu()
            elif choice == '2':
                self.run_task_menu()
            elif choice == '3':
                self.view_dashboard()
            elif choice == '4':
                self.run_notification_menu()
            elif choice == '5':
                self.auth_service.logout()
                print("\n✓ Logged out successfully.")
                print("Thank you for using Construction Project Manager!")
                print("Goodbye!\n")
                self.running = False
            else:
                print("\n✗ Invalid choice. Please try again.")
        
        # Cleanup
        if self.notification_service:
            self.notification_service.stop_all_listeners()
        if self.firebase:
            self.firebase.close()


def main():
    """Entry point for the application."""
    cli = ConstructionManagerCLI()
    cli.run()


if __name__ == "__main__":
    main()
