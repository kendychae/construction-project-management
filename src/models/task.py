"""
Task model for Construction Project Manager.

This module defines the Task entity representing individual tasks
within a construction project. Tasks are related to Projects through
the project_id foreign key.

Author: Construction Solutions
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class TaskStatus(Enum):
    """Enumeration of possible task statuses."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    
    @classmethod
    def from_string(cls, value: str) -> 'TaskStatus':
        """Convert string to TaskStatus enum."""
        for status in cls:
            if status.value == value:
                return status
        raise ValueError(f"Invalid task status: {value}")


class TaskPriority(Enum):
    """Enumeration of task priority levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def from_string(cls, value: str) -> 'TaskPriority':
        """Convert string to TaskPriority enum."""
        for priority in cls:
            if priority.value == value:
                return priority
        raise ValueError(f"Invalid task priority: {value}")


@dataclass
class Task:
    """
    Represents a task within a construction project.
    
    Tasks are linked to projects via the project_id field, establishing
    a one-to-many relationship between Projects and Tasks.
    
    Attributes:
        id: Unique identifier for the task (Firestore document ID)
        project_id: Reference to the parent project
        title: Task title/name
        description: Detailed task description
        status: Current task status
        priority: Task priority level
        assigned_to: Name of the person assigned to the task
        estimated_hours: Estimated hours to complete
        actual_hours: Actual hours spent
        due_date: Task due date
        completed_date: Date when task was completed
        materials_needed: List of materials required
        notes: Additional notes or comments
        created_at: Timestamp when task was created
        updated_at: Timestamp of last update
    """
    
    project_id: str
    title: str
    description: str
    assigned_to: str
    id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    materials_needed: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary for Firestore storage.
        
        Returns:
            Dict containing all task fields
        """
        return {
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assigned_to": self.assigned_to,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "due_date": self.due_date,
            "completed_date": self.completed_date,
            "materials_needed": self.materials_needed,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, doc_id: str, data: Dict[str, Any]) -> 'Task':
        """
        Create a Task instance from a Firestore document.
        
        Args:
            doc_id: The Firestore document ID
            data: Dictionary containing task data
            
        Returns:
            Task instance
        """
        return cls(
            id=doc_id,
            project_id=data.get("project_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            status=TaskStatus.from_string(data.get("status", "pending")),
            priority=TaskPriority.from_string(data.get("priority", "medium")),
            assigned_to=data.get("assigned_to", ""),
            estimated_hours=float(data.get("estimated_hours", 0)),
            actual_hours=float(data.get("actual_hours", 0)),
            due_date=data.get("due_date"),
            completed_date=data.get("completed_date"),
            materials_needed=data.get("materials_needed", ""),
            notes=data.get("notes", ""),
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at", datetime.now())
        )
    
    def mark_complete(self) -> None:
        """Mark the task as completed with current timestamp."""
        self.status = TaskStatus.COMPLETED
        self.completed_date = datetime.now()
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return (
            f"Task: {self.title}\n"
            f"  ID: {self.id}\n"
            f"  Project ID: {self.project_id}\n"
            f"  Status: {self.status.value}\n"
            f"  Priority: {self.priority.value}\n"
            f"  Assigned To: {self.assigned_to}\n"
            f"  Estimated Hours: {self.estimated_hours}\n"
            f"  Actual Hours: {self.actual_hours}"
        )
