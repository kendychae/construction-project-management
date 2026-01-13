"""
Project Repository for Construction Project Manager.

This module provides data access layer for Project entities,
implementing CRUD operations against Firebase Firestore.

Author: Construction Solutions
"""

from datetime import datetime
from typing import List, Optional
import logging

from google.cloud.firestore_v1 import FieldFilter

from ..models.project import Project, ProjectStatus
from .firebase_service import FirebaseService

logger = logging.getLogger(__name__)


class ProjectRepository:
    """
    Repository class for Project CRUD operations.
    
    This class provides an abstraction layer between the application
    logic and the Firestore database, implementing the Repository pattern.
    
    Attributes:
        collection_name: Name of the Firestore collection for projects
        firebase: FirebaseService instance
    """
    
    def __init__(self, firebase: FirebaseService, collection_name: str = "projects"):
        """
        Initialize the ProjectRepository.
        
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
    
    def create(self, project: Project) -> Project:
        """
        Create a new project in the database.
        
        Args:
            project: Project instance to create
            
        Returns:
            Project with assigned ID
        """
        project.created_at = datetime.now()
        project.updated_at = datetime.now()
        
        # Add document to Firestore
        doc_ref = self.collection.add(project.to_dict())
        project.id = doc_ref[1].id
        
        logger.info(f"Created project: {project.name} (ID: {project.id})")
        return project
    
    def get_by_id(self, project_id: str) -> Optional[Project]:
        """
        Retrieve a project by its ID.
        
        Args:
            project_id: The Firestore document ID
            
        Returns:
            Project instance if found, None otherwise
        """
        doc = self.collection.document(project_id).get()
        
        if doc.exists:
            return Project.from_dict(doc.id, doc.to_dict())
        
        logger.warning(f"Project not found: {project_id}")
        return None
    
    def get_all(self) -> List[Project]:
        """
        Retrieve all projects from the database.
        
        Returns:
            List of all Project instances
        """
        docs = self.collection.stream()
        projects = [Project.from_dict(doc.id, doc.to_dict()) for doc in docs]
        
        logger.info(f"Retrieved {len(projects)} projects")
        return projects
    
    def get_by_status(self, status: ProjectStatus) -> List[Project]:
        """
        Retrieve projects filtered by status.
        
        Args:
            status: ProjectStatus to filter by
            
        Returns:
            List of matching Project instances
        """
        docs = self.collection.where(
            filter=FieldFilter("status", "==", status.value)
        ).stream()
        
        return [Project.from_dict(doc.id, doc.to_dict()) for doc in docs]
    
    def get_by_manager(self, manager_name: str) -> List[Project]:
        """
        Retrieve projects assigned to a specific project manager.
        
        Args:
            manager_name: Name of the project manager
            
        Returns:
            List of matching Project instances
        """
        docs = self.collection.where(
            filter=FieldFilter("project_manager", "==", manager_name)
        ).stream()
        
        return [Project.from_dict(doc.id, doc.to_dict()) for doc in docs]
    
    def update(self, project: Project) -> Project:
        """
        Update an existing project in the database.
        
        Args:
            project: Project instance with updated fields
            
        Returns:
            Updated Project instance
            
        Raises:
            ValueError: If project ID is not set
        """
        if not project.id:
            raise ValueError("Cannot update project without an ID")
        
        project.updated_at = datetime.now()
        
        self.collection.document(project.id).update(project.to_dict())
        
        logger.info(f"Updated project: {project.name} (ID: {project.id})")
        return project
    
    def delete(self, project_id: str) -> bool:
        """
        Delete a project from the database.
        
        Args:
            project_id: The Firestore document ID to delete
            
        Returns:
            True if deletion was successful
        """
        self.collection.document(project_id).delete()
        
        logger.info(f"Deleted project: {project_id}")
        return True
    
    def update_status(self, project_id: str, new_status: ProjectStatus) -> Optional[Project]:
        """
        Update only the status of a project.
        
        Args:
            project_id: The Firestore document ID
            new_status: New ProjectStatus to set
            
        Returns:
            Updated Project instance if found, None otherwise
        """
        project = self.get_by_id(project_id)
        
        if project:
            project.status = new_status
            return self.update(project)
        
        return None
    
    def search_by_name(self, search_term: str) -> List[Project]:
        """
        Search projects by name (case-sensitive prefix match).
        
        Note: Firestore has limited text search capabilities.
        For full-text search, consider using Algolia or Elasticsearch.
        
        Args:
            search_term: Search term to match against project names
            
        Returns:
            List of matching Project instances
        """
        # Firestore range query for prefix matching
        end_term = search_term + '\uf8ff'
        
        docs = self.collection.where(
            filter=FieldFilter("name", ">=", search_term)
        ).where(
            filter=FieldFilter("name", "<=", end_term)
        ).stream()
        
        return [Project.from_dict(doc.id, doc.to_dict()) for doc in docs]
