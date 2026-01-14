"""
Authentication Service for Construction Project Manager.

This module provides user authentication functionality using Firebase Auth.
It supports user registration, login, and session management.

Author: Construction Solutions
"""

import logging
import requests
from datetime import datetime
from typing import Optional, Tuple
from dataclasses import dataclass

from ..models.user import User, UserRole
from .firebase_service import FirebaseService

logger = logging.getLogger(__name__)


@dataclass
class AuthSession:
    """Represents an authenticated user session."""
    user: User
    id_token: str
    refresh_token: str


class AuthService:
    """
    Service class for user authentication operations.
    
    This class handles user registration, login, and session management
    using Firebase Authentication REST API and Firestore for user profiles.
    
    Attributes:
        firebase: FirebaseService instance
        api_key: Firebase Web API key for REST authentication
        current_session: Current authenticated session
    """
    
    def __init__(self, firebase: FirebaseService, api_key: str):
        """
        Initialize the AuthService.
        
        Args:
            firebase: Initialized FirebaseService instance
            api_key: Firebase Web API key (from Firebase Console > Project Settings)
        """
        self.firebase = firebase
        self.api_key = api_key
        self.current_session: Optional[AuthSession] = None
        self._users_collection = "users"
    
    @property
    def users_collection(self):
        """Get the Firestore users collection reference."""
        return self.firebase.db.collection(self._users_collection)
    
    @property
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return self.current_session is not None
    
    @property
    def current_user(self) -> Optional[User]:
        """Get the currently authenticated user."""
        return self.current_session.user if self.current_session else None
    
    def register(self, email: str, password: str, display_name: str) -> Tuple[bool, str]:
        """
        Register a new user account.
        
        Creates a Firebase Auth account and stores user profile in Firestore.
        
        Args:
            email: User's email address
            password: User's password (min 6 characters)
            display_name: User's display name
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Create user in Firebase Auth using REST API
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            data = response.json()
            
            if "error" in data:
                error_message = data["error"].get("message", "Registration failed")
                logger.error(f"Registration failed: {error_message}")
                return False, self._format_auth_error(error_message)
            
            # Extract user ID and tokens
            user_id = data["localId"]
            id_token = data["idToken"]
            refresh_token = data["refreshToken"]
            
            # Create user profile in Firestore
            user = User(
                id=user_id,
                email=email,
                display_name=display_name,
                role=UserRole.MEMBER,
                created_at=datetime.now(),
                last_login=datetime.now()
            )
            
            self.users_collection.document(user_id).set(user.to_dict())
            
            # Set current session
            self.current_session = AuthSession(
                user=user,
                id_token=id_token,
                refresh_token=refresh_token
            )
            
            logger.info(f"User registered successfully: {email}")
            return True, f"Welcome, {display_name}! Account created successfully."
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during registration: {str(e)}")
            return False, "Network error. Please check your connection."
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return False, f"Registration failed: {str(e)}"
    
    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Authenticate with Firebase Auth REST API
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            data = response.json()
            
            if "error" in data:
                error_message = data["error"].get("message", "Login failed")
                logger.error(f"Login failed: {error_message}")
                return False, self._format_auth_error(error_message)
            
            # Extract user ID and tokens
            user_id = data["localId"]
            id_token = data["idToken"]
            refresh_token = data["refreshToken"]
            
            # Get user profile from Firestore
            user_doc = self.users_collection.document(user_id).get()
            
            if user_doc.exists:
                user = User.from_dict(user_id, user_doc.to_dict())
            else:
                # Create profile if it doesn't exist (for users created outside app)
                user = User(
                    id=user_id,
                    email=email,
                    display_name=email.split("@")[0],
                    role=UserRole.MEMBER,
                    created_at=datetime.now()
                )
                self.users_collection.document(user_id).set(user.to_dict())
            
            # Update last login
            user.last_login = datetime.now()
            self.users_collection.document(user_id).update({"last_login": user.last_login})
            
            # Set current session
            self.current_session = AuthSession(
                user=user,
                id_token=id_token,
                refresh_token=refresh_token
            )
            
            logger.info(f"User logged in: {email}")
            return True, f"Welcome back, {user.display_name}!"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during login: {str(e)}")
            return False, "Network error. Please check your connection."
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, f"Login failed: {str(e)}"
    
    def logout(self) -> None:
        """
        Log out the current user.
        
        Clears the current session.
        """
        if self.current_session:
            logger.info(f"User logged out: {self.current_session.user.email}")
        self.current_session = None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user profile by their ID.
        
        Args:
            user_id: Firebase Auth UID
            
        Returns:
            User instance if found, None otherwise
        """
        doc = self.users_collection.document(user_id).get()
        
        if doc.exists:
            return User.from_dict(user_id, doc.to_dict())
        return None
    
    def _format_auth_error(self, error_code: str) -> str:
        """
        Convert Firebase Auth error codes to user-friendly messages.
        
        Args:
            error_code: Firebase Auth error code
            
        Returns:
            User-friendly error message
        """
        error_messages = {
            "EMAIL_EXISTS": "This email is already registered. Try logging in.",
            "INVALID_EMAIL": "Please enter a valid email address.",
            "WEAK_PASSWORD": "Password must be at least 6 characters.",
            "EMAIL_NOT_FOUND": "No account found with this email.",
            "INVALID_PASSWORD": "Incorrect password. Please try again.",
            "INVALID_LOGIN_CREDENTIALS": "Invalid email or password.",
            "USER_DISABLED": "This account has been disabled.",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many failed attempts. Try again later."
        }
        
        return error_messages.get(error_code, f"Authentication error: {error_code}")
