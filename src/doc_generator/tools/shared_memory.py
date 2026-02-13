"""
Shared In-Memory Store for the Documentation Generator Pipeline.
Now backed by PostgreSQL using the existing 'docgen' table schema.
"""

import json
import threading
import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine, Column, Integer, Text, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class SharedMemoryState(Base):
    """
    SQLAlchemy model for the existing 'docgen' table structure.
    Used to store shared state between agents.
    """
    __tablename__ = 'docgen'
    id = Column(Integer, primary_key=True)
    task_description = Column(String(255), index=True) # Used as the "key"
    metadata_json = Column(Text)                      # Used as the "value" (JSON string)
    datetime = Column(String(255))                    # Timestamp
    score = Column(Float)                             # Placeholder score (1.0)

class SharedMemory:
    """Singleton store backed by the 'docgen' table in PostgreSQL."""

    _instance: Optional["SharedMemory"] = None
    _lock = threading.Lock()
    _engine = None
    _Session = None

    def __new__(cls) -> "SharedMemory":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_db()
            return cls._instance

    def _init_db(self):
        """Initialize the database connection and ensure tables exist."""
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            logging.warning("DATABASE_URL not found. SharedMemory will not be persistent.")
            return

        try:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            
            self._engine = create_engine(db_url)
            # Create if not exists (won't overwrite existing columns)
            Base.metadata.create_all(self._engine)
            self._Session = sessionmaker(bind=self._engine)
            print(f"[SHARED_MEMORY] Connected to PostgreSQL: {db_url.split('@')[-1] if '@' in db_url else 'unknown'}")
        except Exception as e:
            print(f"[SHARED_MEMORY] ERROR: Failed to initialize DB: {e}")

    # ── write ──────────────────────────────────────────────────────────
    def set(self, key: str, value: Any) -> None:
        """Store a value mapping key to 'task_description' and value to 'metadata_json'."""
        if not self._Session:
            return

        session = self._Session()
        try:
            print(f"[SHARED_MEMORY] Setting key: {key} (value size: {len(str(value))})")
            # We treat task_description as the unique key for our shared memory
            existing = session.query(SharedMemoryState).filter_by(task_description=key).first()
            val_str = json.dumps(value)
            now = datetime.now().isoformat()
            
            if existing:
                existing.metadata_json = val_str
                existing.datetime = now
            else:
                new_entry = SharedMemoryState(
                    task_description=key,
                    metadata_json=val_str,
                    datetime=now,
                    score=1.0
                )
                session.add(new_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Error setting key '{key}' in docgen table: {e}")
        finally:
            session.close()

    # ── read ───────────────────────────────────────────────────────────
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve the value stored under 'task_description'."""
        if not self._Session:
            return default

        session = self._Session()
        try:
            entry = session.query(SharedMemoryState).filter_by(task_description=key).first()
            if entry and entry.metadata_json:
                return json.loads(entry.metadata_json)
            return default
        except Exception as e:
            logging.error(f"Error getting key '{key}' from docgen table: {e}")
            return default
        finally:
            session.close()

    def get_all(self) -> Dict[str, Any]:
        """Return the entire store from PostgreSQL."""
        if not self._Session:
            return {}

        session = self._Session()
        try:
            entries = session.query(SharedMemoryState).all()
            result = {}
            for entry in entries:
                try:
                    result[entry.task_description] = json.loads(entry.metadata_json)
                except:
                    result[entry.task_description] = entry.metadata_json
            return result
        except Exception as e:
            logging.error(f"Error getting all data from docgen table: {e}")
            return {}
        finally:
            session.close()

    def keys(self) -> List[str]:
        """Return all task_descriptions currently in the table."""
        if not self._Session:
            return []

        session = self._Session()
        try:
            data = session.query(SharedMemoryState.task_description).all()
            return [d[0] for d in data if d[0]]
        except Exception as e:
            logging.error(f"Error listing keys from docgen table: {e}")
            return []
        finally:
            session.close()

    def append_to_list(self, key: str, value: Any) -> None:
        """Append a value to a list stored under 'task_description'."""
        if not self._Session:
            return

        session = self._Session()
        try:
            existing = session.query(SharedMemoryState).filter_by(task_description=key).first()
            now = datetime.now().isoformat()
            
            if existing:
                try:
                    current_list = json.loads(existing.metadata_json)
                except:
                    current_list = [existing.metadata_json]
                    
                if not isinstance(current_list, list):
                    current_list = [current_list]
                
                current_list.append(value)
                existing.metadata_json = json.dumps(current_list)
                existing.datetime = now
            else:
                new_entry = SharedMemoryState(
                    task_description=key,
                    metadata_json=json.dumps([value]),
                    datetime=now,
                    score=1.0
                )
                session.add(new_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Error appending to list '{key}' in docgen table: {e}")
        finally:
            session.close()

    # ── helpers ────────────────────────────────────────────────────────
    def clear(self, keep_traces: bool = True) -> None:
        """Wipe the docgen table (optionally keeps traces)."""
        if not self._Session:
            return

        session = self._Session()
        try:
            print(f"[SHARED_MEMORY] Clearing data from docgen table (keeping traces: {keep_traces})...")
            query = session.query(SharedMemoryState)
            if keep_traces:
                # Delete everything EXCEPT trace-related keys
                query = query.filter(~SharedMemoryState.task_description.like('agent_traces%'))
            
            query.delete(synchronize_session=False)
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Error clearing docgen table: {e}")
        finally:
            session.close()

    def summary(self) -> str:
        """Return a human-readable summary of what is stored."""
        data = self.get_all()
        lines = ["=== Shared Memory (PostgreSQL: docgen) ==="]
        for key, value in data.items():
            if isinstance(value, str):
                lines.append(f"  {key}: {len(value)} chars")
            elif isinstance(value, (list, dict)):
                lines.append(f"  {key}: {type(value).__name__} with {len(value)} items")
            else:
                lines.append(f"  {key}: {type(value).__name__}")
        return "\n".join(lines)

    def to_json(self) -> str:
        """Serialize the store to a JSON string."""
        return json.dumps(self.get_all(), indent=2, default=str)

    @classmethod
    def reset(cls) -> None:
        """Destroy the singleton (for testing)."""
        with cls._lock:
            cls._instance = None

if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.INFO)
    mem = SharedMemory()
    print("Testing persistence with 'docgen' table...")
    mem.set("test_key", {"status": "success", "data": "Persistent via docgen table"})
    val = mem.get("test_key")
    print(f"Retrieved: {val}")
    if val and val.get("status") == "success":
        print("SUCCESS: Persistence working correctly.")
    else:
        print("FAILURE: Persistence issues.")
