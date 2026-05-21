"""
Rollback Service for Unified Chat Migration
Handles disaster recovery by restoring legacy tables from backups
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.orm import Session


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RollbackResult:
    """Result of rollback operation"""
    success: bool
    reason: str
    legacy_tables_restored: bool
    unified_table_cleared: bool
    timestamp: str
    errors: list


class RollbackService:
    """
    Service for rolling back the unified chat migration.
    Restores legacy tables from backups and clears the unified table.
    """
    
    def __init__(self, db_session: Session, backup_paths: Dict[str, str]):
        """
        Initialize rollback service.
        
        Args:
            db_session: SQLAlchemy database session
            backup_paths: Dictionary with backup file paths
                         {'store_chat': 'path/to/store_backup.sql',
                          'rider_chat': 'path/to/rider_backup.sql'}
        """
        self.db_session = db_session
        self.backup_paths = backup_paths
        logger.info(f"RollbackService initialized with backup paths: {backup_paths}")
    
    def restore_legacy_tables(self) -> bool:
        """
        Restore StoreChatMessage and RiderChatMessage tables from backup files.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting legacy table restoration...")
        
        try:
            # Verify backup files exist
            for table_name, backup_path in self.backup_paths.items():
                if not os.path.exists(backup_path):
                    logger.error(f"Backup file not found: {backup_path}")
                    return False
                
                if os.path.getsize(backup_path) == 0:
                    logger.error(f"Backup file is empty: {backup_path}")
                    return False
                
                logger.info(f"Verified backup file: {backup_path} ({os.path.getsize(backup_path)} bytes)")
            
            # Restore StoreChatMessage table
            if 'store_chat' in self.backup_paths:
                logger.info("Restoring StoreChatMessage table...")
                success = self._restore_table_from_backup(
                    'store_chat_message',
                    self.backup_paths['store_chat']
                )
                if not success:
                    logger.error("Failed to restore StoreChatMessage table")
                    return False
                logger.info("StoreChatMessage table restored successfully")
            
            # Restore RiderChatMessage table
            if 'rider_chat' in self.backup_paths:
                logger.info("Restoring RiderChatMessage table...")
                success = self._restore_table_from_backup(
                    'rider_chat_message',
                    self.backup_paths['rider_chat']
                )
                if not success:
                    logger.error("Failed to restore RiderChatMessage table")
                    return False
                logger.info("RiderChatMessage table restored successfully")
            
            logger.info("All legacy tables restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring legacy tables: {str(e)}", exc_info=True)
            return False
    
    def _restore_table_from_backup(self, table_name: str, backup_path: str) -> bool:
        """
        Restore a single table from backup file.
        
        Args:
            table_name: Name of the table to restore
            backup_path: Path to the backup SQL file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read backup file
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_sql = f.read()
            
            if not backup_sql.strip():
                logger.error(f"Backup file is empty: {backup_path}")
                return False
            
            # Drop existing table if it exists
            logger.info(f"Dropping existing table: {table_name}")
            self.db_session.execute(text(f'DROP TABLE IF EXISTS {table_name} CASCADE'))
            self.db_session.commit()
            
            # Execute backup SQL to restore table
            logger.info(f"Executing backup SQL for table: {table_name}")
            
            # Split SQL into individual statements and execute
            statements = [stmt.strip() for stmt in backup_sql.split(';') if stmt.strip()]
            
            for stmt in statements:
                if stmt:
                    self.db_session.execute(text(stmt))
            
            self.db_session.commit()
            
            # Verify table was restored
            result = self.db_session.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            )
            count = result.scalar()
            logger.info(f"Table {table_name} restored with {count} records")
            
            return True
            
        except Exception as e:
            logger.error(f"Error restoring table {table_name}: {str(e)}", exc_info=True)
            self.db_session.rollback()
            return False
    
    def clear_unified_table(self) -> bool:
        """
        Clear all records from the ChatMessage table.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting unified table cleanup...")
        
        try:
            # Count records before deletion
            result = self.db_session.execute(
                text("SELECT COUNT(*) FROM chat_message")
            )
            count_before = result.scalar()
            logger.info(f"ChatMessage table has {count_before} records before cleanup")
            
            # Truncate the table (faster than DELETE)
            logger.info("Truncating chat_message table...")
            self.db_session.execute(text("TRUNCATE TABLE chat_message CASCADE"))
            self.db_session.commit()
            
            # Verify table is empty
            result = self.db_session.execute(
                text("SELECT COUNT(*) FROM chat_message")
            )
            count_after = result.scalar()
            
            if count_after == 0:
                logger.info(f"ChatMessage table cleared successfully ({count_before} records removed)")
                return True
            else:
                logger.error(f"ChatMessage table still has {count_after} records after truncate")
                return False
            
        except Exception as e:
            logger.error(f"Error clearing unified table: {str(e)}", exc_info=True)
            self.db_session.rollback()
            return False
    
    def execute_rollback(self, reason: str) -> RollbackResult:
        """
        Execute complete rollback workflow.
        
        This method orchestrates the full rollback process:
        1. Clear the unified ChatMessage table
        2. Restore legacy tables from backups
        3. Log all operations
        
        Args:
            reason: Reason for triggering the rollback
            
        Returns:
            RollbackResult with success status and detailed logs
        """
        timestamp = datetime.utcnow().isoformat()
        logger.info("=" * 80)
        logger.info(f"ROLLBACK INITIATED at {timestamp}")
        logger.info(f"Reason: {reason}")
        logger.info("=" * 80)
        
        errors = []
        legacy_tables_restored = False
        unified_table_cleared = False
        
        try:
            # Step 1: Clear unified table
            logger.info("Step 1: Clearing unified ChatMessage table...")
            unified_table_cleared = self.clear_unified_table()
            
            if not unified_table_cleared:
                error_msg = "Failed to clear unified ChatMessage table"
                logger.error(error_msg)
                errors.append(error_msg)
            
            # Step 2: Restore legacy tables
            logger.info("Step 2: Restoring legacy tables from backups...")
            legacy_tables_restored = self.restore_legacy_tables()
            
            if not legacy_tables_restored:
                error_msg = "Failed to restore legacy tables from backups"
                logger.error(error_msg)
                errors.append(error_msg)
            
            # Determine overall success
            success = unified_table_cleared and legacy_tables_restored
            
            if success:
                logger.info("=" * 80)
                logger.info("ROLLBACK COMPLETED SUCCESSFULLY")
                logger.info(f"Timestamp: {timestamp}")
                logger.info(f"Reason: {reason}")
                logger.info("=" * 80)
            else:
                logger.error("=" * 80)
                logger.error("ROLLBACK FAILED")
                logger.error(f"Timestamp: {timestamp}")
                logger.error(f"Errors: {errors}")
                logger.error("=" * 80)
            
            return RollbackResult(
                success=success,
                reason=reason,
                legacy_tables_restored=legacy_tables_restored,
                unified_table_cleared=unified_table_cleared,
                timestamp=timestamp,
                errors=errors
            )
            
        except Exception as e:
            error_msg = f"Unexpected error during rollback: {str(e)}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            
            return RollbackResult(
                success=False,
                reason=reason,
                legacy_tables_restored=legacy_tables_restored,
                unified_table_cleared=unified_table_cleared,
                timestamp=timestamp,
                errors=errors
            )
