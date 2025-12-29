"""
Classifier Evaluation Logger
Tracks classifications for manual review and accuracy measurement.
Completely separate from the main workflow - non-intrusive.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from preflight.core.behavior import Behavior


class EvaluationLogger:
    """
    Logs classifier predictions for later manual review and validation.
    Does not interfere with main workflow.
    """
    
    def __init__(self, db_path: str = None):
        """Initialize evaluation database."""
        if db_path is None:
            # Use a separate evaluation database
            db_dir = Path(__file__).parent.parent.parent / "data" / "evaluation"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "classifier_evaluations.db")
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create evaluation schema if needed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Evaluation logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    classified_as TEXT NOT NULL,
                    human_label TEXT,
                    confidence_notes TEXT,
                    invariant_name TEXT,
                    prompt_text TEXT,
                    correct INTEGER DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Metrics/stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_logged INTEGER,
                    labeled_count INTEGER,
                    accuracy REAL,
                    accuracy_by_category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def log_classification(
        self,
        response_text: str,
        classified_as: Behavior,
        invariant_name: str = None,
        prompt_text: str = None,
        confidence_notes: str = None
    ) -> int:
        """
        Log a classification for later review.
        
        Args:
            response_text: The model response that was classified
            classified_as: The Behavior classification
            invariant_name: Which invariant this relates to
            prompt_text: The original prompt/attack
            confidence_notes: Optional notes about confidence
            
        Returns:
            The log entry ID for future reference
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO evaluation_logs
                (timestamp, response_text, classified_as, invariant_name, 
                 prompt_text, confidence_notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                response_text,
                classified_as.value,
                invariant_name,
                prompt_text,
                confidence_notes
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def label_response(self, log_id: int, human_label: Behavior, notes: str = None):
        """
        Manually label a logged response.
        
        Args:
            log_id: The ID from log_classification()
            human_label: What the correct classification should be
            notes: Optional explanation for the label
        """
        correct = None
        
        # Get the original classification
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT classified_as FROM evaluation_logs WHERE id = ?", (log_id,))
            result = cursor.fetchone()
            if result:
                original = result[0]
                correct = 1 if original == human_label.value else 0
        
        # Update with label
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE evaluation_logs
                SET human_label = ?, correct = ?, confidence_notes = ?
                WHERE id = ?
            """, (human_label.value, correct, notes, log_id))
            
            conn.commit()
    
    def get_unlabeled_responses(self, limit: int = 10):
        """
        Get responses that haven't been manually labeled yet.
        
        Args:
            limit: How many to return
            
        Returns:
            List of dicts with id, response, classified_as, etc.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, response_text, classified_as, invariant_name, 
                       prompt_text, timestamp
                FROM evaluation_logs
                WHERE human_label IS NULL
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_accuracy_metrics(self):
        """
        Calculate current accuracy metrics.
        
        Returns:
            Dict with accuracy, per-category breakdown, etc.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Overall accuracy
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correct_count,
                    SUM(CASE WHEN correct = 0 THEN 1 ELSE 0 END) as incorrect_count
                FROM evaluation_logs
                WHERE human_label IS NOT NULL
            """)
            
            total, correct_count, incorrect_count = cursor.fetchone()
            if total == 0:
                return {
                    "labeled_count": 0,
                    "accuracy": None,
                    "per_category": {}
                }
            
            overall_accuracy = correct_count / total if total > 0 else 0
            
            # Per-category accuracy
            cursor.execute("""
                SELECT 
                    classified_as,
                    COUNT(*) as total,
                    SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correct
                FROM evaluation_logs
                WHERE human_label IS NOT NULL
                GROUP BY classified_as
            """)
            
            per_category = {}
            for row in cursor.fetchall():
                category, cat_total, cat_correct = row
                per_category[category] = {
                    "total": cat_total,
                    "correct": cat_correct,
                    "accuracy": cat_correct / cat_total if cat_total > 0 else 0
                }
            
            return {
                "labeled_count": total,
                "total_logged": None,  # Will update below
                "accuracy": overall_accuracy,
                "correct": correct_count,
                "incorrect": incorrect_count,
                "per_category": per_category
            }
    
    def get_misclassifications(self):
        """
        Get all cases where classifier was wrong.
        
        Returns:
            List of misclassified responses for analysis
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, response_text, classified_as, human_label, 
                       invariant_name, prompt_text, timestamp
                FROM evaluation_logs
                WHERE correct = 0
                ORDER BY timestamp DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def export_for_analysis(self, output_file: str = None):
        """
        Export evaluation data as JSON for analysis/visualization.
        
        Args:
            output_file: Path to save JSON. If None, uses default location.
            
        Returns:
            Path to the exported file
        """
        if output_file is None:
            output_dir = Path(self.db_path).parent
            output_file = str(output_dir / "evaluation_export.json")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM evaluation_logs ORDER BY timestamp DESC")
            logs = [dict(row) for row in cursor.fetchall()]
        
        metrics = self.get_accuracy_metrics()
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "metrics": metrics,
            "logs": logs
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_file
    
    def print_summary(self):
        """Print a nice summary of current evaluation state."""
        metrics = self.get_accuracy_metrics()
        
        print("\n" + "=" * 70)
        print("CLASSIFIER EVALUATION SUMMARY")
        print("=" * 70)
        print(f"Labeled responses: {metrics['labeled_count']}")
        
        if metrics['accuracy'] is not None:
            print(f"Overall accuracy: {metrics['accuracy']:.1%}")
            print(f"  Correct: {metrics['correct']}")
            print(f"  Incorrect: {metrics['incorrect']}")
        else:
            print("No labeled responses yet. Start labeling to see metrics!")
        
        if metrics['per_category']:
            print("\nPer-category accuracy:")
            for category, stats in metrics['per_category'].items():
                print(f"  {category}: {stats['accuracy']:.1%} ({stats['correct']}/{stats['total']})")
        
        print("=" * 70 + "\n")
