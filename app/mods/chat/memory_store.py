"""
In-memory store for short-term chat memory
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from threading import Lock
import uuid


@dataclass
class MemoryEntry:
    """Single memory entry with metadata"""
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    ttl_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if memory entry has expired"""
        if self.ttl_seconds is None:
            return False
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)


class InMemoryStore:
    """Thread-safe in-memory store for chat sessions"""
    
    def __init__(self, default_ttl: int = 3600):  # 1 hour default
        self._store: Dict[str, Dict[str, MemoryEntry]] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new memory session"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        with self._lock:
            self._store[session_id] = {}
        
        return session_id
    
    def store(self, session_id: str, key: str, value: Any, 
              ttl_seconds: Optional[int] = None, metadata: Optional[Dict] = None) -> None:
        """Store a value in session memory"""
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl
        
        entry = MemoryEntry(
            content=value,
            ttl_seconds=ttl_seconds,
            metadata=metadata or {}
        )
        
        with self._lock:
            if session_id not in self._store:
                self._store[session_id] = {}
            self._store[session_id][key] = entry
    
    def retrieve(self, session_id: str, key: str) -> Optional[Any]:
        """Retrieve a value from session memory"""
        with self._lock:
            if session_id not in self._store:
                return None
            
            if key not in self._store[session_id]:
                return None
            
            entry = self._store[session_id][key]
            
            # Check if expired
            if entry.is_expired():
                del self._store[session_id][key]
                return None
            
            return entry.content
    
    def get_all(self, session_id: str) -> Dict[str, Any]:
        """Get all non-expired entries for a session"""
        with self._lock:
            if session_id not in self._store:
                return {}
            
            result = {}
            expired_keys = []
            
            for key, entry in self._store[session_id].items():
                if entry.is_expired():
                    expired_keys.append(key)
                else:
                    result[key] = entry.content
            
            # Clean up expired entries
            for key in expired_keys:
                del self._store[session_id][key]
            
            return result
    
    def delete(self, session_id: str, key: str) -> bool:
        """Delete a specific key from session memory"""
        with self._lock:
            if session_id not in self._store:
                return False
            
            if key in self._store[session_id]:
                del self._store[session_id][key]
                return True
            
            return False
    
    def clear_session(self, session_id: str) -> bool:
        """Clear all memory for a session"""
        with self._lock:
            if session_id in self._store:
                del self._store[session_id]
                return True
            return False
    
    def cleanup_expired(self) -> int:
        """Clean up all expired entries across all sessions"""
        cleaned_count = 0
        
        with self._lock:
            sessions_to_remove = []
            
            for session_id, session_data in self._store.items():
                expired_keys = []
                
                for key, entry in session_data.items():
                    if entry.is_expired():
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del session_data[key]
                    cleaned_count += 1
                
                # Remove empty sessions
                if not session_data:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self._store[session_id]
        
        return cleaned_count
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        with self._lock:
            return len(self._store)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory store statistics"""
        with self._lock:
            total_entries = sum(len(session) for session in self._store.values())
            return {
                "active_sessions": len(self._store),
                "total_entries": total_entries,
                "sessions": {
                    session_id: len(entries) 
                    for session_id, entries in self._store.items()
                }
            }


memory_store = InMemoryStore()