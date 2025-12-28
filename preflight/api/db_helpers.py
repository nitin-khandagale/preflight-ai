"""Database helper methods for API."""

from preflight.database import Database
from typing import List, Dict, Optional


def get_all_runs(limit: int = 10, offset: int = 0) -> tuple[List[Dict], int]:
    """
    Get all runs with pagination.
    
    Args:
        limit: Number of runs to return
        offset: Skip this many runs
        
    Returns:
        Tuple of (runs_list, total_count)
    """
    db = Database()
    
    with db._connect() as conn:
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM runs")
        total = cursor.fetchone()[0]
        
        # Get paginated results
        cursor.execute(
            """
            SELECT run_id, model_name, datetime, gate_decision 
            FROM runs 
            ORDER BY datetime DESC 
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )
        
        columns = ["run_id", "model_name", "datetime", "gate_decision"]
        runs = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return runs, total


def get_run_by_id(run_id: str) -> Optional[Dict]:
    """
    Get complete run details by run_id.
    
    Args:
        run_id: The run ID
        
    Returns:
        Complete run details or None
    """
    db = Database()
    return db.get_run(run_id)
