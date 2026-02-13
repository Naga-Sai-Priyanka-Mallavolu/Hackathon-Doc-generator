from crewai.tools import BaseTool
from typing import Any, Optional, Type
from pydantic import BaseModel, Field
import os
import json
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Text, Float, String
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class DocGenTaskRecord(Base):
    """Matches the existing 'docgen' table schema."""
    __tablename__ = 'docgen'
    id = Column(Integer, primary_key=True)
    task_description = Column(String(255), index=True)
    metadata_json = Column(Text)
    datetime = Column(String(255))
    score = Column(Float)

class PostgreSQLStorageInputs(BaseModel):
    task_name: str = Field(..., description="The name of the task being logged.")
    agent_role: str = Field(..., description="The role of the agent who performed the task.")
    result: str = Field(..., description="The result/output of the task to be persisted.")
    confidence: Optional[float] = Field(None, description="Optional confidence score for the task result.")

class PostgreSQLStorage(BaseTool):
    name: str = "postgres_storage"
    description: str = (
        "A tool to persist task results and metadata into the 'docgen' table in PostgreSQL. "
        "Use this for long-term record keeping of important documentation steps."
    )
    args_schema: Type[BaseModel] = PostgreSQLStorageInputs
    
    _engine: Any = None
    _Session: Any = None

    def __init__(self, **data):
        super().__init__(**data)
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            logging.warning("DATABASE_URL not found. PostgreSQL Storage will be inactive.")
            return

        print(f"[POSTGRES_STORAGE_TOOL] INITIALIZING WITH DATABASE: {db_url.split('@')[-1] if '@' in db_url else 'unknown'}")
        try:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            
            self._engine = create_engine(db_url)
            # Create if not exists
            Base.metadata.create_all(self._engine)
            self._Session = sessionmaker(bind=self._engine)
            logging.info("PostgreSQL Storage initialized using 'docgen' table.")
        except Exception as e:
            logging.error(f"Failed to initialize PostgreSQL Storage: {e}")

    def _run(self, task_name: str, agent_role: str, result: str, confidence: Optional[float] = None) -> str:
        print(f"\n[POSTGRES_STORAGE_TOOL] CALLING SAVE FOR TASK: {task_name}")
        if not self._Session:
            return "Error: Database storage is not initialized (check DATABASE_URL)."

        session = self._Session()
        try:
            # Map inputs to the 'docgen' schema
            # We combine task_name and agent_role for the description
            desc = f"{agent_role}: {task_name}"
            
            # We store the result in metadata_json
            # If it's a string, we still JSON-wrap it to stay consistent with SharedMemory
            meta = {
                "agent": agent_role,
                "task": task_name,
                "result": result,
                "confidence": confidence or 1.0
            }
            
            # Upsert logic based on description
            existing = session.query(DocGenTaskRecord).filter_by(task_description=desc).first()
            now = datetime.now().isoformat()
            
            if existing:
                existing.metadata_json = json.dumps(meta)
                existing.datetime = now
                existing.score = float(confidence or 1.0)
            else:
                new_entry = DocGenTaskRecord(
                    task_description=desc,
                    metadata_json=json.dumps(meta),
                    datetime=now,
                    score=float(confidence or 1.0)
                )
                session.add(new_entry)
            
            session.commit()
            return f"Successfully saved task '{task_name}' results to PostgreSQL 'docgen' table."
        except Exception as e:
            session.rollback()
            return f"Failed to save to PostgreSQL: {e}"
        finally:
            session.close()

if __name__ == "__main__":
    # Test script
    tool = PostgreSQLStorage()
    print(tool._run(
        task_name="Integration Test",
        agent_role="Verifier",
        result="Direct tool call test.",
        confidence=0.98
    ))
