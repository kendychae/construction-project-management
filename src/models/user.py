"""
User model for Construction Project Manager.

This module defines the User entity for authentication purposes.
Users are stored in Firestore and authenticated via Firebase Auth.

Author: Construction Solutions
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class UserRole(Enum):
    """Enumeration of user roles for access control."""
    
    VIEWER = "viewer"
    MEMBER = "member"
    MANAGER = "manager"
    ADMIN = "admin"
    
    @classmethod
    def from_string(cls, value: str) -> 'UserRole':
        """Convert string to UserRole enum."""
        for role in cls:
            if role.value == value:
                return role
        raise ValueError(f"Invalid user role: {value}")


@dataclass
class User:
    """
    Represents an authenticated user in the system.
    
    Attributes:
        id: Unique identifier (Firebase Auth UID)
        email: User's email address
        display_name: User's display name
        role: User's access role
        created_at: When the user was created
        last_login: Last login timestamp
    """
    
    email: str
    display_name: str
    id: Optional[str] = None
    role: UserRole = UserRole.MEMBER
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the user to a dictionary for Firestore storage.
        
        Returns:
            Dict containing all user fields
        """
        return {
            "email": self.email,
            "display_name": self.display_name,
            "role": self.role.value,
            "created_at": self.created_at,
            "last_login": self.last_login
        }
    
    @classmethod
    def from_dict(cls, user_id: str, data: Dict[str, Any]) -> 'User':
        """
        Create a User instance from a Firestore document.
        
        Args:
            user_id: The Firebase Auth UID
            data: Dictionary containing user data
            
        Returns:
            User instance
        """
        return cls(
            id=user_id,
            email=data.get("email", ""),
            display_name=data.get("display_name", ""),
            role=UserRole.from_string(data.get("role", "member")),
            created_at=data.get("created_at", datetime.now()),
            last_login=data.get("last_login")
        )
    
    def __str__(self) -> str:
        """String representation of the user."""
        return f"User: {self.display_name} ({self.email}) - Role: {self.role.value}"
