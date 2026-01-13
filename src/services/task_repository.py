"""
Task Repository for Construction Project Manager.

This module provides data access layer for Task entities,
implementing CRUD operations against Firebase Firestore.

Tasks are related to Projects via the project_id field,
establishing a one-to-many relationship.

Author: Construction Solutions
"""

from datetime import datetime
from typing import List, Optional
import logging

from google.cloud.firestore_v1 import FieldFilter

from ..models.task import Task, TaskStatus, TaskPriority
from .firebase_service import FirebaseService

logger = logging.getLogger(__name__)


class TaskRepository:
    """
    Repository class for Task CRUD operations.
    
    This class provides an abstraction layer between the application
    logic and the Firestore database for Task entities.
    
    Attributes:
        collection_name: Name of the Firestore collection for tasks
        firebase: FirebaseService instance
    """
    
    def __init__(self, firebase: FirebaseService, collection_name: str = "tasks"):
        """
        Initialize the TaskRepository.
        
        Args:
            firebase: Initialized FirebaseService instance
            collection_name: Name of the Firestore collection
        """
        self.firebase = firebase
        self.collection_name = collection_name
    
    @property
    def collection(self):
        """Get the Firestore collection reference."""
        return self.firebase.db.collection(self.collection_name)
    
    def create(self, task: Task) -> Task:
        """
        Create a new task in the database.
        
        Args:
            task: Task instance to create
            
        Returns:
            Task with assigned ID
        """
        task.created_at = datetime.now()
        task.updated_at = datetime.now()
        
        # Add document to Firestore
        doc_ref = self.collection.add(task.to_dict())
        task.id = doc_ref[1].id
        
        logger.info(f"Created task: {task.title} (ID: {task.id})")
        return task
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """
        Retrieve a task by its ID.
        
        Args:
            task_id: The Firestore document ID
            
        Returns:
            Task instance if found, None otherwise
        """
        doc = self.collection.document(task_id).get()
        
        if doc.exists:
            return Task.from_dict(doc.id, doc.to_dict())
        
        logger.warning(f"Task not found: {task_id}")
        return None
    
    def get_all(self) -> List[Task]:
        """
        Retrieve all tasks from the database.
        
        Returns:
            List of all Task instances
        """
        docs = self.collection.stream()
        tasks = [Task.from_dict(doc.id, doc.to_dict()) for doc in docs]
        
        logger.info(f"Retrieved {len(tasks)} tasks")
        return tasks
    
    def get_by_project(self, project_id: str) -> List[Task]:
        """
        Retrieve all tasks for a specific project.
        
        This method demonstrates the relationship between
        the Projects and Tasks collections.
        
        Args:
            project_id: The parent project's document ID
            
        Returns:
            List of Task instances belonging to the project
        """
        docs = self.collection.where(
            filter=FieldFilter("project_id", "==", project_id)
        ).stream()
        
        tasks = [Task.from_dict(doc.id, doc.to_dict()) for doc in docs]
        logger.info(f"Retrieved {len(tasks)} tasks for project: {project_id}")
        
        return tasks
    
    def get_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Retrieve tasks filtered by status.
        
        Args:
            status: TaskStatus to filter by
            
        Returns:
            List of matching Task instances
        """
        docs = self.collection.where(
            filter=FieldFilter("status", "==", status.value)
        ).stream()
        
        return [Task.from_dict(doc.id, doc.to_dict()) for doc in docs]
    
    def get_by_priority(self, priority: TaskPriority) -> List[Task]:
        """
        Retrieve tasks filtered by priority.
        
        Args:
            priority: TaskPriority to filter by
            
        Returns:
            List of matching Task instances
        """
        docs = self.collection.where(
            filter=FieldFilter("priority", "==", priority.value)
        ).stream()
        
        return [Task.from_dict(doc.id, doc.to_dict()) for doc in docs]
    
    def get_by_assignee(self, assignee_name: str) -> List[Task]:
        """
        Retrieve tasks assigned to a specific person.
        
        Args:
            assignee_name: Name of the assigned person
            
        Returns:
            List of matching Task instances
        """
        docs = self.collection.where(
            filter=FieldFilter("assigned_to", "==", assignee_name)
        ).stream()
        
        return [Task.from_dict(doc.id, doc.to_dict()) for doc in docs]
    
    def update(self, task: Task) -> Task:
        """
        Update an existing task in the database.
        
        Args:
            task: Task instance with updated fields
            
        Returns:
            Updated Task instance
            
        Raises:
            ValueError: If task ID is not set
        """
        if not task.id:
            raise ValueError("Cannot update task without an ID")
        
        task.updated_at = datetime.now()
        
        self.collection.document(task.id).update(task.to_dict())
        
        logger.info(f"Updated task: {task.title} (ID: {task.id})")
        return task
    
    def delete(self, task_id: str) -> bool:
        """
        Delete a task from the database.
        
        Args:
            task_id: The Firestore document ID to delete
            
        Returns:
            True if deletion was successful
        """
        self.collection.document(task_id).delete()
        
        logger.info(f"Deleted task: {task_id}")
        return True
    
    def delete_by_project(self, project_id: str) -> int:
        """
        Delete all tasks belonging to a specific project.
        
        This is useful when deleting a project and its associated tasks.
        
        Args:
            project_id: The parent project's document ID
            
        Returns:
            Number of tasks deleted
        """
        tasks = self.get_by_project(project_id)
        
        for task in tasks:
            if task.id:
                self.delete(task.id)
        
        logger.info(f"Deleted {len(tasks)} tasks for project: {project_id}")
        return len(tasks)
    
    def update_status(self, task_id: str, new_status: TaskStatus) -> Optional[Task]:
        """
        Update only the status of a task.
        
        Args:
            task_id: The Firestore document ID
            new_status: New TaskStatus to set
            
        Returns:
            Updated Task instance if found, None otherwise
        """
        task = self.get_by_id(task_id)
        
        if task:
            task.status = new_status
            if new_status == TaskStatus.COMPLETED:
                task.completed_date = datetime.now()
            return self.update(task)
        
        return None
    
    def log_hours(self, task_id: str, hours: float) -> Optional[Task]:
        """
        Add hours to the actual_hours field of a task.
        
        Args:
            task_id: The Firestore document ID
            hours: Number of hours to add
            
        Returns:
            Updated Task instance if found, None otherwise
        """
        task = self.get_by_id(task_id)
        
        if task:
            task.actual_hours += hours
            return self.update(task)
        
        return None
    
    def get_overdue_tasks(self) -> List[Task]:
        """
        Retrieve all tasks that are past their due date.
        
        Returns:
            List of overdue Task instances
        """
        now = datetime.now()
        
        docs = self.collection.where(
            filter=FieldFilter("due_date", "<", now)
        ).where(
            filter=FieldFilter("status", "!=", TaskStatus.COMPLETED.value)
        ).stream()
        
        return [Task.from_dict(doc.id, doc.to_dict()) for doc in docs]
