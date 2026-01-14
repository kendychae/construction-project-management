"""
Notification Service for Construction Project Manager.

This module provides real-time notification functionality using 
Firestore snapshot listeners. When data changes in the cloud,
the application is notified immediately.

Author: Construction Solutions
"""

import logging
import threading
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .firebase_service import FirebaseService

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of document changes detected by listeners."""
    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"


@dataclass
class Notification:
    """
    Represents a real-time notification from Firestore.
    
    Attributes:
        change_type: Type of change (added, modified, removed)
        collection: Name of the collection that changed
        document_id: ID of the changed document
        data: The document data (for added/modified)
        timestamp: When the notification was received
    """
    change_type: ChangeType
    collection: str
    document_id: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        """Format notification as a user-friendly string."""
        action = {
            ChangeType.ADDED: "➕ NEW",
            ChangeType.MODIFIED: "📝 UPDATED",
            ChangeType.REMOVED: "🗑️ DELETED"
        }.get(self.change_type, "CHANGED")
        
        return f"[{action}] {self.collection}: {self.document_id}"


class NotificationService:
    """
    Service for real-time notifications using Firestore listeners.
    
    This class sets up snapshot listeners on Firestore collections
    to receive immediate notifications when data changes in the cloud.
    
    Attributes:
        firebase: FirebaseService instance
        listeners: Dictionary of active listener unsubscribe functions
        notifications: List of received notifications
        callbacks: List of callback functions to call on notifications
    """
    
    def __init__(self, firebase: FirebaseService):
        """
        Initialize the NotificationService.
        
        Args:
            firebase: Initialized FirebaseService instance
        """
        self.firebase = firebase
        self._listeners: Dict[str, Callable] = {}
        self._notifications: List[Notification] = []
        self._callbacks: List[Callable[[Notification], None]] = []
        self._max_notifications = 50  # Keep last 50 notifications
        self._enabled = True
        self._initial_load_complete: Dict[str, bool] = {}
    
    @property
    def notifications(self) -> List[Notification]:
        """Get list of recent notifications."""
        return self._notifications.copy()
    
    @property
    def unread_count(self) -> int:
        """Get count of notifications."""
        return len(self._notifications)
    
    def add_callback(self, callback: Callable[[Notification], None]) -> None:
        """
        Add a callback function to be called when notifications arrive.
        
        Args:
            callback: Function that takes a Notification parameter
        """
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Notification], None]) -> None:
        """
        Remove a previously added callback function.
        
        Args:
            callback: The callback function to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def start_listening(self, collection_name: str) -> bool:
        """
        Start listening for changes on a Firestore collection.
        
        Sets up a real-time snapshot listener that fires whenever
        documents are added, modified, or removed from the collection.
        
        Args:
            collection_name: Name of the Firestore collection to watch
            
        Returns:
            True if listener was started successfully
        """
        if collection_name in self._listeners:
            logger.warning(f"Already listening to collection: {collection_name}")
            return False
        
        try:
            collection_ref = self.firebase.db.collection(collection_name)
            self._initial_load_complete[collection_name] = False
            
            def on_snapshot(doc_snapshot, changes, read_time):
                """Handle snapshot updates from Firestore."""
                # Skip initial load to avoid flooding with existing data
                if not self._initial_load_complete.get(collection_name, False):
                    self._initial_load_complete[collection_name] = True
                    logger.info(f"Initial snapshot loaded for: {collection_name}")
                    return
                
                if not self._enabled:
                    return
                
                for change in changes:
                    change_type = ChangeType.MODIFIED
                    if change.type.name == "ADDED":
                        change_type = ChangeType.ADDED
                    elif change.type.name == "REMOVED":
                        change_type = ChangeType.REMOVED
                    
                    notification = Notification(
                        change_type=change_type,
                        collection=collection_name,
                        document_id=change.document.id,
                        data=change.document.to_dict() if change.type.name != "REMOVED" else None
                    )
                    
                    self._add_notification(notification)
            
            # Start the listener
            unsubscribe = collection_ref.on_snapshot(on_snapshot)
            self._listeners[collection_name] = unsubscribe
            
            logger.info(f"Started listening to collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start listener for {collection_name}: {str(e)}")
            return False
    
    def stop_listening(self, collection_name: str) -> bool:
        """
        Stop listening for changes on a collection.
        
        Args:
            collection_name: Name of the collection to stop watching
            
        Returns:
            True if listener was stopped successfully
        """
        if collection_name not in self._listeners:
            return False
        
        try:
            # Call the unsubscribe function
            self._listeners[collection_name]()
            del self._listeners[collection_name]
            
            if collection_name in self._initial_load_complete:
                del self._initial_load_complete[collection_name]
            
            logger.info(f"Stopped listening to collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop listener for {collection_name}: {str(e)}")
            return False
    
    def stop_all_listeners(self) -> None:
        """Stop all active collection listeners."""
        for collection_name in list(self._listeners.keys()):
            self.stop_listening(collection_name)
    
    def _add_notification(self, notification: Notification) -> None:
        """
        Add a notification and trigger callbacks.
        
        Args:
            notification: The notification to add
        """
        self._notifications.append(notification)
        
        # Trim to max size
        if len(self._notifications) > self._max_notifications:
            self._notifications = self._notifications[-self._max_notifications:]
        
        # Log the notification
        logger.info(f"Notification: {notification}")
        
        # Trigger callbacks
        for callback in self._callbacks:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Callback error: {str(e)}")
    
    def clear_notifications(self) -> None:
        """Clear all stored notifications."""
        self._notifications.clear()
    
    def enable(self) -> None:
        """Enable notification processing."""
        self._enabled = True
        logger.info("Notifications enabled")
    
    def disable(self) -> None:
        """Disable notification processing (listeners stay active)."""
        self._enabled = False
        logger.info("Notifications disabled")
    
    def get_active_listeners(self) -> List[str]:
        """
        Get list of collections currently being monitored.
        
        Returns:
            List of collection names with active listeners
        """
        return list(self._listeners.keys())
    
    def print_recent_notifications(self, count: int = 10) -> None:
        """
        Print recent notifications to console.
        
        Args:
            count: Number of recent notifications to display
        """
        recent = self._notifications[-count:] if self._notifications else []
        
        if not recent:
            print("\n📭 No recent notifications")
            return
        
        print(f"\n📬 RECENT NOTIFICATIONS ({len(recent)})")
        print("-" * 50)
        
        for notif in recent:
            time_str = notif.timestamp.strftime("%H:%M:%S")
            print(f"  [{time_str}] {notif}")
        
        print("-" * 50)
