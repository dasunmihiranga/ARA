from typing import Dict, Any, List, Optional, Union
import json
from datetime import datetime, timedelta
import os
from pathlib import Path
import uuid
import asyncio
from threading import Lock

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class SessionManager:
    """Manages research session data and state."""

    def __init__(
        self,
        session_dir: str = "data/sessions",
        session_ttl: int = 86400,  # 24 hours
        max_sessions: int = 100
    ):
        """
        Initialize the session manager.

        Args:
            session_dir: Directory to store session files
            session_ttl: Session time-to-live in seconds
            max_sessions: Maximum number of active sessions
        """
        self.session_dir = Path(session_dir)
        self.session_ttl = session_ttl
        self.max_sessions = max_sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()
        self._ensure_session_dir()
        self._load_sessions()

    def _ensure_session_dir(self) -> None:
        """Ensure session directory exists."""
        try:
            self.session_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating session directory: {str(e)}")
            raise

    def _load_sessions(self) -> None:
        """Load existing sessions from disk."""
        try:
            for session_file in self.session_dir.glob("*.json"):
                try:
                    with open(session_file, "r") as f:
                        session_data = json.load(f)
                        session_id = session_file.stem
                        self.sessions[session_id] = session_data
                except Exception as e:
                    logger.error(f"Error loading session {session_file}: {str(e)}")
                    continue

            # Clean up expired sessions
            self._cleanup_expired()
        except Exception as e:
            logger.error(f"Error loading sessions: {str(e)}")

    def _save_session(self, session_id: str) -> None:
        """
        Save session to disk.

        Args:
            session_id: Session ID
        """
        try:
            session_file = self.session_dir / f"{session_id}.json"
            with open(session_file, "w") as f:
                json.dump(self.sessions[session_id], f)
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {str(e)}")
            raise

    def _cleanup_expired(self) -> None:
        """Remove expired sessions."""
        try:
            now = datetime.utcnow()
            expired = []
            for session_id, session_data in self.sessions.items():
                last_updated = datetime.fromisoformat(session_data["last_updated"])
                if (now - last_updated).total_seconds() > self.session_ttl:
                    expired.append(session_id)

            for session_id in expired:
                self.delete_session(session_id)
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {str(e)}")

    def _enforce_session_limit(self) -> None:
        """Enforce maximum session limit."""
        try:
            if len(self.sessions) > self.max_sessions:
                # Remove oldest sessions
                sessions_by_age = sorted(
                    self.sessions.items(),
                    key=lambda x: datetime.fromisoformat(x[1]["last_updated"])
                )
                for session_id, _ in sessions_by_age[:len(sessions_by_age) - self.max_sessions]:
                    self.delete_session(session_id)
        except Exception as e:
            logger.error(f"Error enforcing session limit: {str(e)}")

    def create_session(
        self,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session.

        Args:
            metadata: Optional session metadata

        Returns:
            Session ID
        """
        try:
            with self.lock:
                session_id = str(uuid.uuid4())
                now = datetime.utcnow().isoformat()

                self.sessions[session_id] = {
                    "id": session_id,
                    "created_at": now,
                    "last_updated": now,
                    "metadata": metadata or {},
                    "data": {},
                    "history": []
                }

                self._enforce_session_limit()
                self._save_session(session_id)
                return session_id

        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        try:
            if session_id not in self.sessions:
                return None

            session_data = self.sessions[session_id]
            last_updated = datetime.fromisoformat(session_data["last_updated"])
            if (datetime.utcnow() - last_updated).total_seconds() > self.session_ttl:
                self.delete_session(session_id)
                return None

            return session_data

        except Exception as e:
            logger.error(f"Error getting session {session_id}: {str(e)}")
            return None

    def update_session(
        self,
        session_id: str,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update session data.

        Args:
            session_id: Session ID
            data: Optional session data to update
            metadata: Optional metadata to update

        Returns:
            Updated session data or None if not found
        """
        try:
            if session_id not in self.sessions:
                return None

            with self.lock:
                session = self.sessions[session_id]
                now = datetime.utcnow().isoformat()

                if data:
                    session["data"].update(data)
                if metadata:
                    session["metadata"].update(metadata)

                session["last_updated"] = now
                session["history"].append({
                    "timestamp": now,
                    "data": data,
                    "metadata": metadata
                })

                self._save_session(session_id)
                return session

        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found
        """
        try:
            if session_id not in self.sessions:
                return False

            with self.lock:
                session_file = self.session_dir / f"{session_id}.json"
                if session_file.exists():
                    session_file.unlink()
                del self.sessions[session_id]
                return True

        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False

    def list_sessions(
        self,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List active sessions.

        Args:
            metadata_filter: Optional metadata filter

        Returns:
            List of session data
        """
        try:
            sessions = []
            for session_id, session_data in self.sessions.items():
                if metadata_filter:
                    if not all(
                        session_data["metadata"].get(k) == v
                        for k, v in metadata_filter.items()
                    ):
                        continue

                sessions.append({
                    "id": session_id,
                    "created_at": session_data["created_at"],
                    "last_updated": session_data["last_updated"],
                    "metadata": session_data["metadata"]
                })

            return sessions

        except Exception as e:
            logger.error(f"Error listing sessions: {str(e)}")
            return []

    def get_session_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get session history.

        Args:
            session_id: Session ID
            limit: Optional history limit

        Returns:
            Session history or None if not found
        """
        try:
            if session_id not in self.sessions:
                return None

            history = self.sessions[session_id]["history"]
            if limit:
                history = history[-limit:]
            return history

        except Exception as e:
            logger.error(f"Error getting session history {session_id}: {str(e)}")
            return None

    def clear_expired(self) -> int:
        """
        Clear expired sessions.

        Returns:
            Number of sessions cleared
        """
        try:
            count = 0
            for session_id in list(self.sessions.keys()):
                if self.get_session(session_id) is None:
                    count += 1
            return count

        except Exception as e:
            logger.error(f"Error clearing expired sessions: {str(e)}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get session statistics.

        Returns:
            Dictionary with session statistics
        """
        try:
            return {
                "total_sessions": len(self.sessions),
                "max_sessions": self.max_sessions,
                "session_ttl": self.session_ttl,
                "active_sessions": len([
                    s for s in self.sessions.values()
                    if (datetime.utcnow() - datetime.fromisoformat(s["last_updated"])).total_seconds() <= self.session_ttl
                ])
            }
        except Exception as e:
            logger.error(f"Error getting session stats: {str(e)}")
            return {
                "total_sessions": 0,
                "max_sessions": self.max_sessions,
                "session_ttl": self.session_ttl,
                "active_sessions": 0
            } 