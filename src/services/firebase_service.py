"""
Firebase Service for Construction Project Manager.

This module provides the core Firebase/Firestore connection and
initialization functionality.

Author: Construction Solutions
"""

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirebaseService:
    """
    Singleton service class for Firebase/Firestore connection management.
    
    This class handles the initialization and lifecycle of the Firebase
    Admin SDK connection. It implements the Singleton pattern to ensure
    only one Firebase app instance exists.
    
    Attributes:
        _instance: Singleton instance
        _db: Firestore database client
        _initialized: Flag indicating if Firebase has been initialized
    """
    
    _instance: Optional['FirebaseService'] = None
    _db: Optional[Client] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, credentials_path: str, project_id: str) -> None:
        """
        Initialize Firebase Admin SDK with service account credentials.
        
        Args:
            credentials_path: Path to the service account JSON file
            project_id: Firebase project ID
            
        Raises:
            FileNotFoundError: If credentials file doesn't exist
            ValueError: If Firebase is already initialized
        """
        if self._initialized:
            logger.warning("Firebase is already initialized. Skipping re-initialization.")
            return
        
        try:
            # Load credentials from service account file
            cred = credentials.Certificate(credentials_path)
            
            # Initialize the Firebase app
            firebase_admin.initialize_app(cred, {
                'projectId': project_id
            })
            
            # Get Firestore client
            self._db = firestore.client()
            self._initialized = True
            
            logger.info(f"Firebase initialized successfully for project: {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise
    
    @property
    def db(self) -> Client:
        """
        Get the Firestore database client.
        
        Returns:
            Firestore client instance
            
        Raises:
            RuntimeError: If Firebase has not been initialized
        """
        if not self._initialized or self._db is None:
            raise RuntimeError(
                "Firebase has not been initialized. "
                "Call initialize() first with valid credentials."
            )
        return self._db
    
    @property
    def is_initialized(self) -> bool:
        """Check if Firebase has been initialized."""
        return self._initialized
    
    def close(self) -> None:
        """
        Clean up Firebase resources.
        
        This should be called when the application is shutting down.
        """
        if self._initialized:
            try:
                firebase_admin.delete_app(firebase_admin.get_app())
                self._initialized = False
                self._db = None
                logger.info("Firebase connection closed.")
            except Exception as e:
                logger.error(f"Error closing Firebase connection: {str(e)}")
