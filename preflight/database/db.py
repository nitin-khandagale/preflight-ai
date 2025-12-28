"""
Database module for saving preflight execution data.
Handles storage of runs, invariants, and failure details.
"""

import sqlite3
import hashlib
import uuid
from datetime import datetime
from pathlib import Path


class Database:
    def __init__(self, db_path: str = None):
        """Initialize database connection and create tables if needed."""
        if db_path is None:
            # Use default path from config
            from preflight.config import Config
            db_path = Config.get_db_path()
        
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    datetime TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    model_version TEXT,
                    model_url TEXT,
                    api_key_hash TEXT,
                    num_invariants INTEGER,
                    gate_decision TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create invariants table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invariants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    invariant_name TEXT NOT NULL,
                    invariant_result TEXT NOT NULL,
                    num_prompts_tested INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)
            
            # Create failures table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS failures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    invariant_name TEXT NOT NULL,
                    prompt_text TEXT NOT NULL,
                    model_response TEXT NOT NULL,
                    behavior_detected TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)
            
            conn.commit()

    def _hash_api_key(self, api_key: str) -> str:
        """Hash API key using SHA-256."""
        if not api_key:
            return None
        return hashlib.sha256(api_key.encode()).hexdigest()

    def save_run(self, model_name: str, model_version: str = None, 
                 model_url: str = None, api_key: str = None, 
                 num_invariants: int = 0, run_id: str = None) -> str:
        """
        Save a new run record.
        
        Returns:
            The run_id (generated if not provided)
        """
        if not run_id:
            run_id = str(uuid.uuid4())
        
        run_datetime = datetime.now().isoformat()
        api_key_hash = self._hash_api_key(api_key)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO runs 
                (run_id, datetime, model_name, model_version, model_url, 
                 api_key_hash, num_invariants)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (run_id, run_datetime, model_name, model_version, 
                  model_url, api_key_hash, num_invariants))
            conn.commit()
        
        return run_id

    def save_invariant(self, run_id: str, invariant_name: str, 
                      invariant_result: str, num_prompts_tested: int = 0):
        """Save invariant test result for a run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO invariants 
                (run_id, invariant_name, invariant_result, num_prompts_tested)
                VALUES (?, ?, ?, ?)
            """, (run_id, invariant_name, invariant_result, num_prompts_tested))
            conn.commit()

    def save_failure(self, run_id: str, invariant_name: str, 
                    prompt_text: str, model_response: str, 
                    behavior_detected: str = None):
        """Save a prompt failure detail."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO failures 
                (run_id, invariant_name, prompt_text, model_response, behavior_detected)
                VALUES (?, ?, ?, ?, ?)
            """, (run_id, invariant_name, prompt_text, model_response, behavior_detected))
            conn.commit()

    def update_gate_decision(self, run_id: str, gate_decision: str):
        """Update gate decision for a run."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE runs SET gate_decision = ? WHERE run_id = ?
            """, (gate_decision, run_id))
            conn.commit()

    def get_run(self, run_id: str) -> dict:
        """Get complete run details including invariants and failures."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get run
            cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
            run = dict(cursor.fetchone() or {})
            
            if not run:
                return None
            
            # Get invariants
            cursor.execute(
                "SELECT invariant_name, invariant_result, num_prompts_tested FROM invariants WHERE run_id = ?",
                (run_id,)
            )
            run['invariants'] = [dict(row) for row in cursor.fetchall()]
            
            # Get failures
            cursor.execute(
                "SELECT invariant_name, prompt_text, model_response, behavior_detected FROM failures WHERE run_id = ?",
                (run_id,)
            )
            run['failures'] = [dict(row) for row in cursor.fetchall()]
            
            return run

    def _connect(self):
        """Context manager for database connections."""
        class DBConnection:
            def __init__(self, db_path):
                self.db_path = db_path
                self.conn = None
            
            def __enter__(self):
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row
                return self.conn
            
            def __exit__(self, *args):
                if self.conn:
                    self.conn.close()
        
        return DBConnection(self.db_path)
