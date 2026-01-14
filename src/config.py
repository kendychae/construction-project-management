"""
Configuration module for Construction Project Manager.

This module handles application configuration including Firebase credentials,
authentication settings, and database settings. Sensitive credentials are 
loaded from environment variables or a local service account file.

Author: Construction Solutions
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class FirebaseConfig:
    """Firebase configuration settings."""
    
    project_id: str
    credentials_path: Optional[str] = None
    api_key: Optional[str] = None  # Required for Firebase Auth REST API
    
    @classmethod
    def from_environment(cls) -> 'FirebaseConfig':
        """
        Load Firebase configuration from environment variables.
        
        Environment Variables:
            FIREBASE_PROJECT_ID: The Firebase project ID
            FIREBASE_CREDENTIALS_PATH: Path to service account JSON file
            FIREBASE_API_KEY: Firebase Web API key (for authentication)
        
        Returns:
            FirebaseConfig: Configuration instance
            
        Raises:
            ValueError: If required environment variables are not set
        """
        project_id = os.getenv('FIREBASE_PROJECT_ID')
        credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        api_key = os.getenv('FIREBASE_API_KEY')
        
        if not project_id:
            raise ValueError(
                "FIREBASE_PROJECT_ID environment variable is required. "
                "Set it to your Firebase project ID."
            )
        
        if not credentials_path:
            raise ValueError(
                "FIREBASE_CREDENTIALS_PATH environment variable is required. "
                "Set it to the path of your Firebase service account JSON file."
            )
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Firebase credentials file not found at: {credentials_path}"
            )
        
        if not api_key:
            raise ValueError(
                "FIREBASE_API_KEY environment variable is required. "
                "Find it in Firebase Console > Project Settings > Web API Key."
            )
        
        return cls(
            project_id=project_id,
            credentials_path=credentials_path,
            api_key=api_key
        )


@dataclass
class AppConfig:
    """Application-wide configuration settings."""
    
    firebase: FirebaseConfig
    collection_projects: str = "projects"
    collection_tasks: str = "tasks"
    
    @classmethod
    def load(cls) -> 'AppConfig':
        """
        Load application configuration.
        
        Returns:
            AppConfig: Application configuration instance
        """
        return cls(
            firebase=FirebaseConfig.from_environment()
        )
