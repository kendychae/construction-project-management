"""
Project model for Construction Project Manager.

This module defines the Project entity representing a construction project
with its associated metadata and status tracking.

Author: Construction Solutions
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


class ProjectStatus(Enum):
    """Enumeration of possible project statuses."""
    
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    @classmethod
    def from_string(cls, value: str) -> 'ProjectStatus':
        """Convert string to ProjectStatus enum."""
        for status in cls:
            if status.value == value:
                return status
        raise ValueError(f"Invalid project status: {value}")


@dataclass
class Project:
    """
    Represents a construction project.
    
    Attributes:
        id: Unique identifier for the project (Firestore document ID)
        name: Project name/title
        description: Detailed project description
        client_name: Name of the client/customer
        location: Project site location/address
        status: Current project status
        budget: Project budget in dollars
        start_date: Planned or actual start date
        end_date: Planned or actual end date
        project_manager: Name of the assigned project manager
        created_at: Timestamp when project was created
        updated_at: Timestamp of last update
    """
    
    name: str
    description: str
    client_name: str
    location: str
    budget: float
    project_manager: str
    id: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the project to a dictionary for Firestore storage.
        
        Returns:
            Dict containing all project fields
        """
        return {
            "name": self.name,
            "description": self.description,
            "client_name": self.client_name,
            "location": self.location,
            "status": self.status.value,
            "budget": self.budget,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "project_manager": self.project_manager,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, doc_id: str, data: Dict[str, Any]) -> 'Project':
        """
        Create a Project instance from a Firestore document.
        
        Args:
            doc_id: The Firestore document ID
            data: Dictionary containing project data
            
        Returns:
            Project instance
        """
        return cls(
            id=doc_id,
            name=data.get("name", ""),
            description=data.get("description", ""),
            client_name=data.get("client_name", ""),
            location=data.get("location", ""),
            status=ProjectStatus.from_string(data.get("status", "planning")),
            budget=float(data.get("budget", 0)),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            project_manager=data.get("project_manager", ""),
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at", datetime.now())
        )
    
    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return (
            f"Project: {self.name}\n"
            f"  ID: {self.id}\n"
            f"  Client: {self.client_name}\n"
            f"  Location: {self.location}\n"
            f"  Status: {self.status.value}\n"
            f"  Budget: ${self.budget:,.2f}\n"
            f"  Manager: {self.project_manager}"
        )
