"""
Migration Service for Unified Chat System

This module provides the MigrationService class for migrating chat data from
legacy dual-table architecture (StoreChatMessage and RiderChatMessage) to the
unified single-table architecture (ChatMessage).

Requirements: 11.1, 11.2, 11.3, 11.4
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path


# ============================================
# TRANSFORMATION FUNCTIONS
# ============================================

def transform_store_chat_message(legacy_msg) -> Dict:
    """Transform StoreChatMessage to ChatMessage format.
    
    Converts a StoreChatMessage record to the unified ChatMessage format by:
    - Mapping sender_role and buyer_id/seller_id to sender_id/receiver_id
    - Preserving message, created_at, is_read, and product_id
    - Setting order_id to NULL
    
    Args:
        legacy_msg: StoreChatMessage record with attributes:
                   - buyer_id: ID of the buyer
                   - seller_id: ID of the seller
                   - sender_role: 'buyer' or 'seller'
                   - message: Message text
                   - product_id: Product ID (can be None)
                   - is_read: Boolean read status
                   - created_at: Timestamp of message creation
    
    Returns:
        Dictionary with ChatMessage fields:
        {
            'sender_id': int,
            'receiver_id': int,
            'message': str,
            'product_id': int or None,
            'order_id': None,
            'is_read': bool,
            'created_at': datetime
        }
    
    Requirements: 1.2, 1.3, 1.4, 1.5
    """
    # Handle sender_role='buyer' case: sender_id=buyer_id, receiver_id=seller_id
    if legacy_msg.sender_role == 'buyer':
        sender_id = legacy_msg.buyer_id
        receiver_id = legacy_msg.seller_id
    # Handle sender_role='seller' case: sender_id=seller_id, receiver_id=buyer_id
    else:  # sender_role == 'seller'
        sender_id = legacy_msg.seller_id
        receiver_id = legacy_msg.buyer_id
    
    return {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'message': legacy_msg.message,
        'product_id': legacy_msg.product_id,
        'order_id': None,  # StoreChatMessage has no order_id
        'is_read': legacy_msg.is_read,
        'created_at': legacy_msg.created_at
    }


def transform_rider_chat_message(legacy_msg) -> Dict:
    """Transform RiderChatMessage to ChatMessage format.
    
    Converts a RiderChatMessage record to the unified ChatMessage format by:
    - Mapping sender_role and buyer_id/rider_id to sender_id/receiver_id
    - Preserving message, created_at, is_read, and order_id
    - Setting product_id to NULL
    
    Args:
        legacy_msg: RiderChatMessage record with attributes:
                   - buyer_id: ID of the buyer
                   - rider_id: ID of the rider
                   - sender_role: 'buyer' or 'rider'
                   - message: Message text
                   - order_id: Order ID (can be None)
                   - is_read: Boolean read status
                   - created_at: Timestamp of message creation
    
    Returns:
        Dictionary with ChatMessage fields:
        {
            'sender_id': int,
            'receiver_id': int,
            'message': str,
            'product_id': None,
            'order_id': int or None,
            'is_read': bool,
            'created_at': datetime
        }
    
    Requirements: 2.2, 2.3, 2.4, 2.5
    """
    # Handle sender_role='buyer' case: sender_id=buyer_id, receiver_id=rider_id
    if legacy_msg.sender_role == 'buyer':
        sender_id = legacy_msg.buyer_id
        receiver_id = legacy_msg.rider_id
    # Handle sender_role='rider' case: sender_id=rider_id, receiver_id=buyer_id
    else:  # sender_role == 'rider'
        sender_id = legacy_msg.rider_id
        receiver_id = legacy_msg.buyer_id
    
    return {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'message': legacy_msg.message,
        'product_id': None,  # RiderChatMessage has no product_id
        'order_id': legacy_msg.order_id,
        'is_read': legacy_msg.is_read,
        'created_at': legacy_msg.created_at
    }


class MigrationResult:
    """Result object for migration operations."""
    
    def __init__(self):
        self.success_count = 0
        self.error_count = 0
        self.errors = []  # List of (record_id, error_message) tuples
        self.total_records = 0
        self.start_time = None
        self.end_time = None
    
    def add_error(self, record_id, error_message):
        """Add an error to the result."""
        self.error_count += 1
        self.errors.append((record_id, error_message))
    
    def to_dict(self):
        """Convert result to dictionary for logging."""
        return {
            'success_count': self.success_count,
            'error_count': self.error_count,
            'total_records': self.total_records,
            'errors': self.errors,
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else None
        }


class MigrationService:
    """Service for migrating chat data from legacy tables to unified table.
    
    This service handles:
    - Creating timestamped backups of legacy tables
    - Verifying backup files are readable and non-empty
    - Logging all backup operations with timestamps
    - Migrating StoreChatMessage and RiderChatMessage to ChatMessage
    """
    
    def __init__(self, db_session, backup_dir: Optional[str] = None, batch_size: int = 1000):
        """Initialize migration service.
        
        Args:
            db_session: SQLAlchemy database session
            backup_dir: Directory to store backup files (default: ./backups)
            batch_size: Number of records to process per batch (default: 1000)
        """
        self.db = db_session
        self.backup_dir = backup_dir or os.path.join(os.path.dirname(__file__), 'backups')
        self.batch_size = batch_size
        
        # Ensure backup directory exists
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def create_backups(self) -> Dict[str, str]:
        """Create timestamped backups of StoreChatMessage and RiderChatMessage tables.
        
        This method exports both legacy tables to SQL files with timestamps in the filename.
        Format: {table_name}_backup_{timestamp}.sql
        
        Returns:
            Dict with backup file paths:
            {
                'store_chat_backup': '/path/to/store_chat_message_backup_20240115_143022.sql',
                'rider_chat_backup': '/path/to/rider_chat_message_backup_20240115_143022.sql'
            }
        
        Requirements: 11.1, 11.2, 11.3
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_paths = {}
        
        self.logger.info("=" * 60)
        self.logger.info("Starting backup creation for legacy chat tables")
        self.logger.info("=" * 60)
        
        # Backup StoreChatMessage table
        store_chat_backup = self._backup_table(
            table_name='store_chat_message',
            backup_filename=f'store_chat_message_backup_{timestamp}.sql',
            timestamp=timestamp
        )
        if store_chat_backup:
            backup_paths['store_chat_backup'] = store_chat_backup
            self.logger.info(f"✓ StoreChatMessage backup created: {store_chat_backup}")
        else:
            self.logger.error("✗ Failed to create StoreChatMessage backup")
        
        # Backup RiderChatMessage table
        rider_chat_backup = self._backup_table(
            table_name='rider_chat_message',
            backup_filename=f'rider_chat_message_backup_{timestamp}.sql',
            timestamp=timestamp
        )
        if rider_chat_backup:
            backup_paths['rider_chat_backup'] = rider_chat_backup
            self.logger.info(f"✓ RiderChatMessage backup created: {rider_chat_backup}")
        else:
            self.logger.error("✗ Failed to create RiderChatMessage backup")
        
        self.logger.info("=" * 60)
        self.logger.info(f"Backup creation completed. {len(backup_paths)} backups created.")
        self.logger.info("=" * 60)
        
        return backup_paths
    
    def _backup_table(self, table_name: str, backup_filename: str, timestamp: str) -> Optional[str]:
        """Backup a single table to SQL file.
        
        Args:
            table_name: Name of the table to backup
            backup_filename: Name of the backup file
            timestamp: Timestamp string for logging
        
        Returns:
            Full path to backup file if successful, None otherwise
        """
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            self.logger.info(f"Creating backup for table '{table_name}'...")
            
            # Query all records from the table
            from sqlalchemy import text
            result = self.db.execute(text(f'SELECT * FROM {table_name}'))
            rows = result.fetchall()
            columns = result.keys()
            
            record_count = len(rows)
            self.logger.info(f"  Found {record_count} records in {table_name}")
            
            # Generate SQL INSERT statements
            with open(backup_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"-- Backup of {table_name}\n")
                f.write(f"-- Created: {timestamp}\n")
                f.write(f"-- Records: {record_count}\n")
                f.write(f"-- Generated by MigrationService\n\n")
                
                # Write table structure comment
                f.write(f"-- Table: {table_name}\n")
                f.write(f"-- Columns: {', '.join(columns)}\n\n")
                
                # Write INSERT statements
                if record_count > 0:
                    for row in rows:
                        # Build INSERT statement
                        column_list = ', '.join(columns)
                        
                        # Format values, handling NULL and string escaping
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, str):
                                # Escape single quotes in strings
                                escaped_value = value.replace("'", "''")
                                values.append(f"'{escaped_value}'")
                            elif isinstance(value, datetime):
                                values.append(f"'{value.isoformat()}'")
                            elif isinstance(value, bool):
                                values.append('TRUE' if value else 'FALSE')
                            else:
                                values.append(str(value))
                        
                        value_list = ', '.join(values)
                        f.write(f"INSERT INTO {table_name} ({column_list}) VALUES ({value_list});\n")
                else:
                    f.write(f"-- No records to backup\n")
            
            self.logger.info(f"  Backup written to: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"  Error backing up {table_name}: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def verify_backups(self, backup_paths: Dict[str, str]) -> bool:
        """Verify that backup files are readable and non-empty.
        
        Args:
            backup_paths: Dictionary of backup file paths from create_backups()
        
        Returns:
            True if all backups are valid, False otherwise
        
        Requirements: 11.4
        """
        self.logger.info("=" * 60)
        self.logger.info("Verifying backup files")
        self.logger.info("=" * 60)
        
        all_valid = True
        
        for backup_name, backup_path in backup_paths.items():
            self.logger.info(f"Verifying {backup_name}: {backup_path}")
            
            # Check if file exists
            if not os.path.exists(backup_path):
                self.logger.error(f"  ✗ File does not exist")
                all_valid = False
                continue
            
            # Check if file is readable
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file is non-empty
                if len(content) == 0:
                    self.logger.error(f"  ✗ File is empty")
                    all_valid = False
                    continue
                
                # Check file size
                file_size = os.path.getsize(backup_path)
                self.logger.info(f"  ✓ File is readable and non-empty ({file_size} bytes)")
                
                # Count INSERT statements as a sanity check
                insert_count = content.count('INSERT INTO')
                self.logger.info(f"  ✓ Contains {insert_count} INSERT statements")
                
            except Exception as e:
                self.logger.error(f"  ✗ Error reading file: {str(e)}")
                all_valid = False
                continue
        
        self.logger.info("=" * 60)
        if all_valid:
            self.logger.info("✓ All backup files verified successfully")
        else:
            self.logger.error("✗ Some backup files failed verification")
        self.logger.info("=" * 60)
        
        return all_valid
    
    def migrate_store_chat_messages(self, batch_size: int = 1000, max_retries: int = 3) -> Dict[str, any]:
        """Migrate all StoreChatMessage records to ChatMessage table with batch processing.
        
        This method:
        1. Reads records from StoreChatMessage in batches ordered by id
        2. Transforms each record using transform_store_chat_message()
        3. Inserts transformed records into ChatMessage table
        4. Commits each batch independently to prevent transaction timeouts
        5. Adds 100ms pause between batches to allow other database operations
        6. Retries failed batches up to 3 times before logging error
        7. Logs success count and error count with record IDs
        
        Args:
            batch_size: Number of records to process per batch (default: 1000)
            max_retries: Maximum number of retries for failed batches (default: 3)
        
        Returns:
            Dictionary with migration results:
            {
                'success': bool,
                'total_records': int,
                'migrated_count': int,
                'error_count': int,
                'errors': List[Dict] with 'record_id' and 'error' keys,
                'batches_processed': int,
                'batches_failed': int,
                'duration_seconds': float
            }
        
        Requirements: 1.1, 1.6, 1.7, 1.8, 12.4, 12.5, 12.6, 12.7
        """
        start_time = time.time()
        
        self.logger.info("=" * 60)
        self.logger.info("Starting StoreChatMessage migration")
        self.logger.info("=" * 60)
        
        try:
            from sqlalchemy import text
            
            # Import models - need to get them from the app context
            # We'll query directly using table names
            
            # Count total records
            result = self.db.execute(text('SELECT COUNT(*) FROM store_chat_message'))
            total_records = result.scalar()
            self.logger.info(f"Total StoreChatMessage records to migrate: {total_records}")
            
            if total_records == 0:
                self.logger.info("No records to migrate")
                return {
                    'success': True,
                    'total_records': 0,
                    'migrated_count': 0,
                    'error_count': 0,
                    'errors': [],
                    'batches_processed': 0,
                    'batches_failed': 0,
                    'duration_seconds': time.time() - start_time
                }
            
            migrated_count = 0
            error_count = 0
            errors: List[Dict] = []
            batches_processed = 0
            batches_failed = 0
            
            # Calculate number of batches
            num_batches = (total_records + batch_size - 1) // batch_size
            self.logger.info(f"Processing {num_batches} batches of {batch_size} records each")
            
            # Process records in batches
            for batch_num in range(num_batches):
                offset = batch_num * batch_size
                batch_start_time = time.time()
                
                self.logger.info(f"\nBatch {batch_num + 1}/{num_batches} (offset: {offset}, size: {batch_size})")
                
                # Retry logic for failed batches
                batch_success = False
                retry_count = 0
                
                while retry_count <= max_retries and not batch_success:
                    try:
                        # Read batch of records from StoreChatMessage ordered by id
                        query = text('''
                            SELECT id, buyer_id, seller_id, sender_role, message, 
                                   product_id, is_read, created_at
                            FROM store_chat_message
                            ORDER BY id ASC
                            LIMIT :limit OFFSET :offset
                        ''')
                        
                        result = self.db.execute(query, {'limit': batch_size, 'offset': offset})
                        rows = result.fetchall()
                        
                        if not rows:
                            self.logger.info(f"  No records found in this batch")
                            batch_success = True
                            break
                        
                        batch_migrated = 0
                        batch_errors = 0
                        
                        # Transform and insert each record
                        for row in rows:
                            try:
                                record_id = row[0]
                                
                                # Transform the record
                                transformed = {
                                    'sender_id': row[2] if row[3] == 'seller' else row[1],  # seller_id if sender_role='seller' else buyer_id
                                    'receiver_id': row[1] if row[3] == 'seller' else row[2],  # buyer_id if sender_role='seller' else seller_id
                                    'message': row[4],
                                    'product_id': row[5],
                                    'order_id': None,
                                    'is_read': row[6],
                                    'created_at': row[7]
                                }
                                
                                # Insert into ChatMessage table
                                insert_query = text('''
                                    INSERT INTO chat_message 
                                    (sender_id, receiver_id, message, product_id, order_id, is_read, created_at)
                                    VALUES (:sender_id, :receiver_id, :message, :product_id, :order_id, :is_read, :created_at)
                                ''')
                                
                                self.db.execute(insert_query, transformed)
                                batch_migrated += 1
                                
                            except Exception as e:
                                batch_errors += 1
                                error_msg = str(e)
                                errors.append({
                                    'record_id': record_id,
                                    'error': error_msg
                                })
                                self.logger.warning(f"    Error migrating record {record_id}: {error_msg}")
                        
                        # Commit batch independently
                        self.db.commit()
                        batch_success = True
                        
                        migrated_count += batch_migrated
                        error_count += batch_errors
                        batches_processed += 1
                        
                        batch_duration = time.time() - batch_start_time
                        self.logger.info(f"  ✓ Batch {batch_num + 1} completed: {batch_migrated} migrated, {batch_errors} errors ({batch_duration:.2f}s)")
                        
                    except Exception as e:
                        retry_count += 1
                        error_msg = str(e)
                        
                        if retry_count <= max_retries:
                            self.logger.warning(f"  ⚠ Batch {batch_num + 1} failed (attempt {retry_count}/{max_retries}): {error_msg}")
                            self.logger.info(f"  Retrying batch {batch_num + 1}...")
                            self.db.rollback()
                            time.sleep(0.5)  # Wait before retry
                        else:
                            self.logger.error(f"  ✗ Batch {batch_num + 1} failed after {max_retries} retries: {error_msg}")
                            batches_failed += 1
                            batch_success = True  # Exit retry loop
                            error_count += batch_size  # Count all records in batch as errors
                            errors.append({
                                'record_id': f'batch_{batch_num + 1}',
                                'error': f'Batch failed after {max_retries} retries: {error_msg}'
                            })
                
                # Pause between batches to allow other database operations
                if batch_num < num_batches - 1:
                    self.logger.info(f"  Pausing 100ms before next batch...")
                    time.sleep(0.1)
            
            duration = time.time() - start_time
            
            self.logger.info("=" * 60)
            self.logger.info("StoreChatMessage migration completed")
            self.logger.info(f"  Total records: {total_records}")
            self.logger.info(f"  Migrated: {migrated_count}")
            self.logger.info(f"  Errors: {error_count}")
            self.logger.info(f"  Batches processed: {batches_processed}")
            self.logger.info(f"  Batches failed: {batches_failed}")
            self.logger.info(f"  Duration: {duration:.2f} seconds")
            
            if error_count > 0:
                self.logger.warning(f"\nError details:")
                for error in errors[:10]:  # Show first 10 errors
                    self.logger.warning(f"  Record {error['record_id']}: {error['error']}")
                if len(errors) > 10:
                    self.logger.warning(f"  ... and {len(errors) - 10} more errors")
            
            self.logger.info("=" * 60)
            
            return {
                'success': error_count == 0,
                'total_records': total_records,
                'migrated_count': migrated_count,
                'error_count': error_count,
                'errors': errors,
                'batches_processed': batches_processed,
                'batches_failed': batches_failed,
                'duration_seconds': duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error("=" * 60)
            self.logger.error(f"StoreChatMessage migration failed: {str(e)}")
            self.logger.error("=" * 60)
            import traceback
            self.logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'total_records': 0,
                'migrated_count': 0,
                'error_count': 0,
                'errors': [{'record_id': 'migration', 'error': str(e)}],
                'batches_processed': 0,
                'batches_failed': 0,
                'duration_seconds': duration
            }



class DataIntegrityValidator:
    """Service for validating data integrity after migration.
    
    This service handles:
    - Counting records in legacy and unified tables
    - Verifying record counts match
    - Sampling and verifying message content
    - Generating validation reports
    
    Requirements: 3.1, 3.2, 3.3
    """
    
    def __init__(self, db_session):
        """Initialize data integrity validator.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def count_legacy_records(self) -> Dict[str, int]:
        """Count records in StoreChatMessage and RiderChatMessage tables.
        
        This method queries both legacy tables and returns the record counts.
        
        Returns:
            Dictionary with record counts:
            {
                'store_chat': int,      # Count of StoreChatMessage records
                'rider_chat': int,      # Count of RiderChatMessage records
                'total': int            # Total count (store_chat + rider_chat)
            }
        
        Requirements: 3.1
        """
        self.logger.info("=" * 60)
        self.logger.info("Counting legacy chat records")
        self.logger.info("=" * 60)
        
        try:
            from sqlalchemy import text
            
            # Count StoreChatMessage records
            result = self.db.execute(text('SELECT COUNT(*) FROM store_chat_message'))
            store_chat_count = result.scalar() or 0
            self.logger.info(f"StoreChatMessage records: {store_chat_count}")
            
            # Count RiderChatMessage records
            result = self.db.execute(text('SELECT COUNT(*) FROM rider_chat_message'))
            rider_chat_count = result.scalar() or 0
            self.logger.info(f"RiderChatMessage records: {rider_chat_count}")
            
            # Calculate total
            total_count = store_chat_count + rider_chat_count
            self.logger.info(f"Total legacy records: {total_count}")
            self.logger.info("=" * 60)
            
            return {
                'store_chat': store_chat_count,
                'rider_chat': rider_chat_count,
                'total': total_count
            }
            
        except Exception as e:
            self.logger.error(f"Error counting legacy records: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.logger.info("=" * 60)
            return {
                'store_chat': 0,
                'rider_chat': 0,
                'total': 0
            }
    
    def count_unified_records(self) -> int:
        """Count records in ChatMessage table.
        
        This method queries the unified ChatMessage table and returns the record count.
        
        Returns:
            Integer count of ChatMessage records
        
        Requirements: 3.2
        """
        self.logger.info("=" * 60)
        self.logger.info("Counting unified chat records")
        self.logger.info("=" * 60)
        
        try:
            from sqlalchemy import text
            
            # Count ChatMessage records
            result = self.db.execute(text('SELECT COUNT(*) FROM chat_message'))
            unified_count = result.scalar() or 0
            self.logger.info(f"ChatMessage records: {unified_count}")
            self.logger.info("=" * 60)
            
            return unified_count
            
        except Exception as e:
            self.logger.error(f"Error counting unified records: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.logger.info("=" * 60)
            return 0
    
    def validate_record_counts(self) -> bool:
        """Verify that unified record count equals sum of legacy counts.
        
        This method compares the total count of records in the unified ChatMessage table
        with the sum of records in the legacy StoreChatMessage and RiderChatMessage tables.
        
        Returns:
            True if counts match (validation passed), False otherwise
        
        Requirements: 3.3
        """
        self.logger.info("=" * 60)
        self.logger.info("Validating record counts")
        self.logger.info("=" * 60)
        
        try:
            # Get legacy counts
            legacy_counts = self.count_legacy_records()
            legacy_total = legacy_counts['total']
            
            # Get unified count
            unified_count = self.count_unified_records()
            
            # Compare counts
            self.logger.info(f"Legacy total: {legacy_total}")
            self.logger.info(f"Unified total: {unified_count}")
            
            if unified_count == legacy_total:
                self.logger.info("✓ Record counts match - validation PASSED")
                self.logger.info("=" * 60)
                return True
            else:
                difference = unified_count - legacy_total
                self.logger.error(f"✗ Record count mismatch - validation FAILED")
                self.logger.error(f"  Difference: {difference} records")
                if difference > 0:
                    self.logger.error(f"  Unified table has {difference} extra records")
                else:
                    self.logger.error(f"  Unified table is missing {abs(difference)} records")
                self.logger.info("=" * 60)
                return False
                
        except Exception as e:
            self.logger.error(f"Error validating record counts: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.logger.info("=" * 60)
            return False
    
    def generate_report(self) -> Dict[str, any]:
        """Generate comprehensive validation report with pass/fail status and detailed statistics.
        
        This method creates a complete validation report that includes:
        - Pass/fail status for each validation check
        - Record counts: legacy total, unified total, match status
        - Sample validation results with error details (when sample_and_verify is implemented)
        - Timestamp accuracy statistics (when validate_timestamps is implemented)
        - is_read status match statistics (when validate_is_read_status is implemented)
        - List of all discrepancies with record IDs if validation fails
        
        Returns:
            Dictionary with comprehensive validation report:
            {
                'overall_status': 'PASSED' or 'FAILED',
                'timestamp': str,  # ISO 8601 format
                'validation_checks': {
                    'record_count_validation': {
                        'status': 'PASSED' or 'FAILED',
                        'legacy_store_chat_count': int,
                        'legacy_rider_chat_count': int,
                        'legacy_total_count': int,
                        'unified_count': int,
                        'counts_match': bool,
                        'difference': int  # unified - legacy (0 if match)
                    },
                    'sample_validation': {
                        'status': 'NOT_RUN' or 'PASSED' or 'FAILED',
                        'sample_size': int,
                        'errors': List[Dict]  # List of validation errors
                    },
                    'timestamp_validation': {
                        'status': 'NOT_RUN' or 'PASSED' or 'FAILED',
                        'errors': List[Dict]  # List of timestamp errors
                    },
                    'is_read_validation': {
                        'status': 'NOT_RUN' or 'PASSED' or 'FAILED',
                        'errors': List[Dict]  # List of is_read status errors
                    }
                },
                'discrepancies': List[Dict],  # All discrepancies with record IDs
                'summary': {
                    'total_checks': int,
                    'passed_checks': int,
                    'failed_checks': int,
                    'not_run_checks': int
                }
            }
        
        Requirements: 3.7, 3.8
        """
        self.logger.info("=" * 80)
        self.logger.info("GENERATING DATA INTEGRITY VALIDATION REPORT")
        self.logger.info("=" * 80)
        
        timestamp = datetime.now().isoformat()
        discrepancies = []
        
        # Initialize report structure
        report = {
            'overall_status': 'PASSED',
            'timestamp': timestamp,
            'validation_checks': {
                'record_count_validation': {},
                'sample_validation': {'status': 'NOT_RUN', 'sample_size': 0, 'errors': []},
                'timestamp_validation': {'status': 'NOT_RUN', 'errors': []},
                'is_read_validation': {'status': 'NOT_RUN', 'errors': []}
            },
            'discrepancies': [],
            'summary': {
                'total_checks': 4,
                'passed_checks': 0,
                'failed_checks': 0,
                'not_run_checks': 3  # sample, timestamp, is_read validations not yet implemented
            }
        }
        
        # ============================================
        # Check 1: Record Count Validation
        # ============================================
        self.logger.info("\n[1/4] Running record count validation...")
        
        try:
            # Get legacy counts
            legacy_counts = self.count_legacy_records()
            
            # Get unified count
            unified_count = self.count_unified_records()
            
            # Validate counts match
            counts_match = (unified_count == legacy_counts['total'])
            difference = unified_count - legacy_counts['total']
            
            # Populate record count validation results
            report['validation_checks']['record_count_validation'] = {
                'status': 'PASSED' if counts_match else 'FAILED',
                'legacy_store_chat_count': legacy_counts['store_chat'],
                'legacy_rider_chat_count': legacy_counts['rider_chat'],
                'legacy_total_count': legacy_counts['total'],
                'unified_count': unified_count,
                'counts_match': counts_match,
                'difference': difference
            }
            
            if counts_match:
                self.logger.info("  ✓ Record count validation PASSED")
                report['summary']['passed_checks'] += 1
            else:
                self.logger.error("  ✗ Record count validation FAILED")
                report['summary']['failed_checks'] += 1
                report['overall_status'] = 'FAILED'
                
                # Add discrepancy
                discrepancies.append({
                    'check': 'record_count_validation',
                    'issue': 'Record count mismatch',
                    'details': f"Legacy total: {legacy_counts['total']}, Unified total: {unified_count}, Difference: {difference}",
                    'record_ids': None  # No specific record IDs for count mismatch
                })
                
        except Exception as e:
            self.logger.error(f"  ✗ Record count validation ERROR: {str(e)}")
            report['validation_checks']['record_count_validation'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            report['summary']['failed_checks'] += 1
            report['overall_status'] = 'FAILED'
            
            discrepancies.append({
                'check': 'record_count_validation',
                'issue': 'Validation error',
                'details': str(e),
                'record_ids': None
            })
        
        # ============================================
        # Check 2: Sample Validation (placeholder for task 3.2)
        # ============================================
        self.logger.info("\n[2/4] Sample validation check...")
        
        # Check if sample_and_verify method exists
        if hasattr(self, 'sample_and_verify'):
            try:
                self.logger.info("  Running sample_and_verify()...")
                sample_errors = self.sample_and_verify(sample_size=100)
                
                sample_passed = len(sample_errors) == 0
                
                report['validation_checks']['sample_validation'] = {
                    'status': 'PASSED' if sample_passed else 'FAILED',
                    'sample_size': 100,
                    'errors': sample_errors
                }
                
                if sample_passed:
                    self.logger.info("  ✓ Sample validation PASSED")
                    report['summary']['passed_checks'] += 1
                    report['summary']['not_run_checks'] -= 1
                else:
                    self.logger.error(f"  ✗ Sample validation FAILED ({len(sample_errors)} errors)")
                    report['summary']['failed_checks'] += 1
                    report['summary']['not_run_checks'] -= 1
                    report['overall_status'] = 'FAILED'
                    
                    # Add discrepancies
                    for error in sample_errors:
                        discrepancies.append({
                            'check': 'sample_validation',
                            'issue': 'Sample validation error',
                            'details': error.get('details', str(error)),
                            'record_ids': error.get('record_id', None)
                        })
                        
            except Exception as e:
                self.logger.error(f"  ✗ Sample validation ERROR: {str(e)}")
                report['validation_checks']['sample_validation'] = {
                    'status': 'FAILED',
                    'sample_size': 100,
                    'error': str(e),
                    'errors': []
                }
                report['summary']['failed_checks'] += 1
                report['summary']['not_run_checks'] -= 1
                report['overall_status'] = 'FAILED'
        else:
            self.logger.info("  ⚠ Sample validation NOT IMPLEMENTED (task 3.2)")
        
        # ============================================
        # Check 3: Timestamp Validation (placeholder for task 3.2)
        # ============================================
        self.logger.info("\n[3/4] Timestamp validation check...")
        
        # Check if validate_timestamps method exists
        if hasattr(self, 'validate_timestamps'):
            try:
                self.logger.info("  Running validate_timestamps()...")
                timestamp_errors = self.validate_timestamps()
                
                timestamp_passed = len(timestamp_errors) == 0
                
                report['validation_checks']['timestamp_validation'] = {
                    'status': 'PASSED' if timestamp_passed else 'FAILED',
                    'errors': timestamp_errors
                }
                
                if timestamp_passed:
                    self.logger.info("  ✓ Timestamp validation PASSED")
                    report['summary']['passed_checks'] += 1
                    report['summary']['not_run_checks'] -= 1
                else:
                    self.logger.error(f"  ✗ Timestamp validation FAILED ({len(timestamp_errors)} errors)")
                    report['summary']['failed_checks'] += 1
                    report['summary']['not_run_checks'] -= 1
                    report['overall_status'] = 'FAILED'
                    
                    # Add discrepancies
                    for error in timestamp_errors:
                        discrepancies.append({
                            'check': 'timestamp_validation',
                            'issue': 'Timestamp accuracy error',
                            'details': error.get('details', str(error)),
                            'record_ids': error.get('record_id', None)
                        })
                        
            except Exception as e:
                self.logger.error(f"  ✗ Timestamp validation ERROR: {str(e)}")
                report['validation_checks']['timestamp_validation'] = {
                    'status': 'FAILED',
                    'error': str(e),
                    'errors': []
                }
                report['summary']['failed_checks'] += 1
                report['summary']['not_run_checks'] -= 1
                report['overall_status'] = 'FAILED'
        else:
            self.logger.info("  ⚠ Timestamp validation NOT IMPLEMENTED (task 3.2)")
        
        # ============================================
        # Check 4: is_read Status Validation (placeholder for task 3.2)
        # ============================================
        self.logger.info("\n[4/4] is_read status validation check...")
        
        # Check if validate_is_read_status method exists
        if hasattr(self, 'validate_is_read_status'):
            try:
                self.logger.info("  Running validate_is_read_status()...")
                is_read_errors = self.validate_is_read_status()
                
                is_read_passed = len(is_read_errors) == 0
                
                report['validation_checks']['is_read_validation'] = {
                    'status': 'PASSED' if is_read_passed else 'FAILED',
                    'errors': is_read_errors
                }
                
                if is_read_passed:
                    self.logger.info("  ✓ is_read status validation PASSED")
                    report['summary']['passed_checks'] += 1
                    report['summary']['not_run_checks'] -= 1
                else:
                    self.logger.error(f"  ✗ is_read status validation FAILED ({len(is_read_errors)} errors)")
                    report['summary']['failed_checks'] += 1
                    report['summary']['not_run_checks'] -= 1
                    report['overall_status'] = 'FAILED'
                    
                    # Add discrepancies
                    for error in is_read_errors:
                        discrepancies.append({
                            'check': 'is_read_validation',
                            'issue': 'is_read status mismatch',
                            'details': error.get('details', str(error)),
                            'record_ids': error.get('record_id', None)
                        })
                        
            except Exception as e:
                self.logger.error(f"  ✗ is_read status validation ERROR: {str(e)}")
                report['validation_checks']['is_read_validation'] = {
                    'status': 'FAILED',
                    'error': str(e),
                    'errors': []
                }
                report['summary']['failed_checks'] += 1
                report['summary']['not_run_checks'] -= 1
                report['overall_status'] = 'FAILED'
        else:
            self.logger.info("  ⚠ is_read status validation NOT IMPLEMENTED (task 3.2)")
        
        # ============================================
        # Finalize Report
        # ============================================
        report['discrepancies'] = discrepancies
        
        # Print summary
        self.logger.info("\n" + "=" * 80)
        self.logger.info("VALIDATION REPORT SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Overall Status: {report['overall_status']}")
        self.logger.info(f"Timestamp: {timestamp}")
        self.logger.info(f"\nValidation Checks:")
        self.logger.info(f"  Total checks: {report['summary']['total_checks']}")
        self.logger.info(f"  Passed: {report['summary']['passed_checks']}")
        self.logger.info(f"  Failed: {report['summary']['failed_checks']}")
        self.logger.info(f"  Not run: {report['summary']['not_run_checks']}")
        
        self.logger.info(f"\nRecord Counts:")
        rc = report['validation_checks']['record_count_validation']
        if 'legacy_total_count' in rc:
            self.logger.info(f"  Legacy StoreChatMessage: {rc['legacy_store_chat_count']}")
            self.logger.info(f"  Legacy RiderChatMessage: {rc['legacy_rider_chat_count']}")
            self.logger.info(f"  Legacy Total: {rc['legacy_total_count']}")
            self.logger.info(f"  Unified ChatMessage: {rc['unified_count']}")
            self.logger.info(f"  Counts Match: {rc['counts_match']}")
            if not rc['counts_match']:
                self.logger.info(f"  Difference: {rc['difference']}")
        
        if len(discrepancies) > 0:
            self.logger.info(f"\nDiscrepancies Found: {len(discrepancies)}")
            for i, disc in enumerate(discrepancies[:10], 1):  # Show first 10
                self.logger.info(f"  {i}. [{disc['check']}] {disc['issue']}")
                self.logger.info(f"     Details: {disc['details']}")
                if disc['record_ids']:
                    self.logger.info(f"     Record IDs: {disc['record_ids']}")
            
            if len(discrepancies) > 10:
                self.logger.info(f"  ... and {len(discrepancies) - 10} more discrepancies")
        else:
            self.logger.info("\nNo discrepancies found")
        
        self.logger.info("=" * 80)
        
        return report
    
    def sample_and_verify(self, sample_size: int = 100) -> List[Dict[str, any]]:
        """Randomly sample messages from legacy tables and verify content matches in ChatMessage.
        
        This method:
        1. Randomly samples up to sample_size messages from StoreChatMessage and RiderChatMessage
        2. For each sample, finds the corresponding record in ChatMessage by matching:
           - sender_id, receiver_id, message, and created_at
        3. Verifies message content matches exactly
        4. Verifies timestamps are preserved within 1 second accuracy
        5. Verifies is_read status matches
        6. Returns list of validation errors with record IDs
        
        Args:
            sample_size: Number of messages to sample (default: 100)
        
        Returns:
            List of validation error dictionaries. Empty list if all validations pass.
            Each error dict contains:
            {
                'source_table': str,        # 'store_chat_message' or 'rider_chat_message'
                'source_id': int,           # ID from legacy table
                'error_type': str,          # 'not_found', 'content_mismatch', 'timestamp_mismatch', 'is_read_mismatch'
                'details': str              # Detailed error description
            }
        
        Requirements: 3.4, 3.5, 3.6
        """
        self.logger.info("=" * 60)
        self.logger.info(f"Sampling and verifying {sample_size} messages")
        self.logger.info("=" * 60)
        
        validation_errors = []
        
        try:
            from sqlalchemy import text
            
            # Get total counts to determine sample distribution
            legacy_counts = self.count_legacy_records()
            store_chat_count = legacy_counts['store_chat']
            rider_chat_count = legacy_counts['rider_chat']
            total_count = legacy_counts['total']
            
            if total_count == 0:
                self.logger.info("No records to sample")
                self.logger.info("=" * 60)
                return validation_errors
            
            # Calculate sample sizes proportionally
            if total_count <= sample_size:
                # Sample all records if total is less than sample_size
                store_sample_size = store_chat_count
                rider_sample_size = rider_chat_count
                self.logger.info(f"Total records ({total_count}) <= sample size ({sample_size}), sampling all records")
            else:
                # Distribute sample size proportionally
                store_sample_size = int((store_chat_count / total_count) * sample_size)
                rider_sample_size = sample_size - store_sample_size
            
            self.logger.info(f"Sampling {store_sample_size} from StoreChatMessage")
            self.logger.info(f"Sampling {rider_sample_size} from RiderChatMessage")
            
            # Sample and verify StoreChatMessage records
            if store_sample_size > 0:
                self.logger.info("\nValidating StoreChatMessage samples...")
                store_errors = self._sample_and_verify_store_chat(store_sample_size)
                validation_errors.extend(store_errors)
                self.logger.info(f"  StoreChatMessage validation: {len(store_errors)} errors found")
            
            # Sample and verify RiderChatMessage records
            if rider_sample_size > 0:
                self.logger.info("\nValidating RiderChatMessage samples...")
                rider_errors = self._sample_and_verify_rider_chat(rider_sample_size)
                validation_errors.extend(rider_errors)
                self.logger.info(f"  RiderChatMessage validation: {len(rider_errors)} errors found")
            
            # Summary
            self.logger.info("=" * 60)
            if len(validation_errors) == 0:
                self.logger.info("✓ Sample validation PASSED - all samples match")
            else:
                self.logger.error(f"✗ Sample validation FAILED - {len(validation_errors)} errors found")
                self.logger.error("\nError summary:")
                
                # Group errors by type
                error_types = {}
                for error in validation_errors:
                    error_type = error['error_type']
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                
                for error_type, count in error_types.items():
                    self.logger.error(f"  {error_type}: {count} errors")
                
                # Show first 5 errors
                self.logger.error("\nFirst 5 errors:")
                for error in validation_errors[:5]:
                    self.logger.error(f"  [{error['source_table']}:{error['source_id']}] {error['error_type']}: {error['details']}")
                
                if len(validation_errors) > 5:
                    self.logger.error(f"  ... and {len(validation_errors) - 5} more errors")
            
            self.logger.info("=" * 60)
            
            return validation_errors
            
        except Exception as e:
            self.logger.error(f"Error during sample validation: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.logger.info("=" * 60)
            
            # Return error indicating validation failed
            return [{
                'source_table': 'validation',
                'source_id': 0,
                'error_type': 'validation_error',
                'details': f'Sample validation failed: {str(e)}'
            }]
    
    def _sample_and_verify_store_chat(self, sample_size: int) -> List[Dict[str, any]]:
        """Sample and verify StoreChatMessage records.
        
        Args:
            sample_size: Number of records to sample
        
        Returns:
            List of validation errors
        """
        errors = []
        
        try:
            from sqlalchemy import text
            
            # Randomly sample records from StoreChatMessage
            query = text('''
                SELECT id, buyer_id, seller_id, sender_role, message, 
                       product_id, is_read, created_at
                FROM store_chat_message
                ORDER BY RANDOM()
                LIMIT :limit
            ''')
            
            result = self.db.execute(query, {'limit': sample_size})
            samples = result.fetchall()
            
            self.logger.info(f"  Sampled {len(samples)} records from StoreChatMessage")
            
            # Verify each sample
            for sample in samples:
                source_id = sample[0]
                buyer_id = sample[1]
                seller_id = sample[2]
                sender_role = sample[3]
                message = sample[4]
                product_id = sample[5]
                is_read = sample[6]
                created_at = sample[7]
                
                # Determine sender_id and receiver_id based on sender_role
                if sender_role == 'buyer':
                    expected_sender_id = buyer_id
                    expected_receiver_id = seller_id
                else:  # sender_role == 'seller'
                    expected_sender_id = seller_id
                    expected_receiver_id = buyer_id
                
                # Find corresponding record in ChatMessage
                # Match by sender_id, receiver_id, message, and created_at (within 1 second)
                find_query = text('''
                    SELECT id, sender_id, receiver_id, message, product_id, order_id, 
                           is_read, created_at
                    FROM chat_message
                    WHERE sender_id = :sender_id
                      AND receiver_id = :receiver_id
                      AND message = :message
                      AND ABS(EXTRACT(EPOCH FROM (created_at - :created_at))) <= 1
                    LIMIT 1
                ''')
                
                find_result = self.db.execute(find_query, {
                    'sender_id': expected_sender_id,
                    'receiver_id': expected_receiver_id,
                    'message': message,
                    'created_at': created_at
                })
                
                unified_record = find_result.fetchone()
                
                if not unified_record:
                    # Record not found in ChatMessage
                    errors.append({
                        'source_table': 'store_chat_message',
                        'source_id': source_id,
                        'error_type': 'not_found',
                        'details': f'No matching record found in ChatMessage for sender_id={expected_sender_id}, receiver_id={expected_receiver_id}'
                    })
                    continue
                
                # Verify message content matches exactly
                unified_message = unified_record[3]
                if unified_message != message:
                    errors.append({
                        'source_table': 'store_chat_message',
                        'source_id': source_id,
                        'error_type': 'content_mismatch',
                        'details': f'Message content mismatch. Expected: "{message[:50]}...", Got: "{unified_message[:50]}..."'
                    })
                
                # Verify timestamps are preserved within 1 second accuracy
                unified_created_at = unified_record[7]
                time_diff = abs((unified_created_at - created_at).total_seconds())
                if time_diff > 1:
                    errors.append({
                        'source_table': 'store_chat_message',
                        'source_id': source_id,
                        'error_type': 'timestamp_mismatch',
                        'details': f'Timestamp difference: {time_diff:.2f} seconds (exceeds 1 second threshold)'
                    })
                
                # Verify is_read status matches
                unified_is_read = unified_record[6]
                if unified_is_read != is_read:
                    errors.append({
                        'source_table': 'store_chat_message',
                        'source_id': source_id,
                        'error_type': 'is_read_mismatch',
                        'details': f'is_read status mismatch. Expected: {is_read}, Got: {unified_is_read}'
                    })
                
                # Verify product_id is preserved
                unified_product_id = unified_record[4]
                if unified_product_id != product_id:
                    errors.append({
                        'source_table': 'store_chat_message',
                        'source_id': source_id,
                        'error_type': 'product_id_mismatch',
                        'details': f'product_id mismatch. Expected: {product_id}, Got: {unified_product_id}'
                    })
                
                # Verify order_id is NULL for StoreChatMessage migrations
                unified_order_id = unified_record[5]
                if unified_order_id is not None:
                    errors.append({
                        'source_table': 'store_chat_message',
                        'source_id': source_id,
                        'error_type': 'order_id_mismatch',
                        'details': f'order_id should be NULL for StoreChatMessage migrations. Got: {unified_order_id}'
                    })
            
            return errors
            
        except Exception as e:
            self.logger.error(f"  Error sampling StoreChatMessage: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return [{
                'source_table': 'store_chat_message',
                'source_id': 0,
                'error_type': 'sampling_error',
                'details': f'Error sampling StoreChatMessage: {str(e)}'
            }]
    
    def _sample_and_verify_rider_chat(self, sample_size: int) -> List[Dict[str, any]]:
        """Sample and verify RiderChatMessage records.
        
        Args:
            sample_size: Number of records to sample
        
        Returns:
            List of validation errors
        """
        errors = []
        
        try:
            from sqlalchemy import text
            
            # Randomly sample records from RiderChatMessage
            query = text('''
                SELECT id, buyer_id, rider_id, sender_role, message, 
                       order_id, is_read, created_at
                FROM rider_chat_message
                ORDER BY RANDOM()
                LIMIT :limit
            ''')
            
            result = self.db.execute(query, {'limit': sample_size})
            samples = result.fetchall()
            
            self.logger.info(f"  Sampled {len(samples)} records from RiderChatMessage")
            
            # Verify each sample
            for sample in samples:
                source_id = sample[0]
                buyer_id = sample[1]
                rider_id = sample[2]
                sender_role = sample[3]
                message = sample[4]
                order_id = sample[5]
                is_read = sample[6]
                created_at = sample[7]
                
                # Determine sender_id and receiver_id based on sender_role
                if sender_role == 'buyer':
                    expected_sender_id = buyer_id
                    expected_receiver_id = rider_id
                else:  # sender_role == 'rider'
                    expected_sender_id = rider_id
                    expected_receiver_id = buyer_id
                
                # Find corresponding record in ChatMessage
                # Match by sender_id, receiver_id, message, and created_at (within 1 second)
                find_query = text('''
                    SELECT id, sender_id, receiver_id, message, product_id, order_id, 
                           is_read, created_at
                    FROM chat_message
                    WHERE sender_id = :sender_id
                      AND receiver_id = :receiver_id
                      AND message = :message
                      AND ABS(EXTRACT(EPOCH FROM (created_at - :created_at))) <= 1
                    LIMIT 1
                ''')
                
                find_result = self.db.execute(find_query, {
                    'sender_id': expected_sender_id,
                    'receiver_id': expected_receiver_id,
                    'message': message,
                    'created_at': created_at
                })
                
                unified_record = find_result.fetchone()
                
                if not unified_record:
                    # Record not found in ChatMessage
                    errors.append({
                        'source_table': 'rider_chat_message',
                        'source_id': source_id,
                        'error_type': 'not_found',
                        'details': f'No matching record found in ChatMessage for sender_id={expected_sender_id}, receiver_id={expected_receiver_id}'
                    })
                    continue
                
                # Verify message content matches exactly
                unified_message = unified_record[3]
                if unified_message != message:
                    errors.append({
                        'source_table': 'rider_chat_message',
                        'source_id': source_id,
                        'error_type': 'content_mismatch',
                        'details': f'Message content mismatch. Expected: "{message[:50]}...", Got: "{unified_message[:50]}..."'
                    })
                
                # Verify timestamps are preserved within 1 second accuracy
                unified_created_at = unified_record[7]
                time_diff = abs((unified_created_at - created_at).total_seconds())
                if time_diff > 1:
                    errors.append({
                        'source_table': 'rider_chat_message',
                        'source_id': source_id,
                        'error_type': 'timestamp_mismatch',
                        'details': f'Timestamp difference: {time_diff:.2f} seconds (exceeds 1 second threshold)'
                    })
                
                # Verify is_read status matches
                unified_is_read = unified_record[6]
                if unified_is_read != is_read:
                    errors.append({
                        'source_table': 'rider_chat_message',
                        'source_id': source_id,
                        'error_type': 'is_read_mismatch',
                        'details': f'is_read status mismatch. Expected: {is_read}, Got: {unified_is_read}'
                    })
                
                # Verify order_id is preserved
                unified_order_id = unified_record[5]
                if unified_order_id != order_id:
                    errors.append({
                        'source_table': 'rider_chat_message',
                        'source_id': source_id,
                        'error_type': 'order_id_mismatch',
                        'details': f'order_id mismatch. Expected: {order_id}, Got: {unified_order_id}'
                    })
                
                # Verify product_id is NULL for RiderChatMessage migrations
                unified_product_id = unified_record[4]
                if unified_product_id is not None:
                    errors.append({
                        'source_table': 'rider_chat_message',
                        'source_id': source_id,
                        'error_type': 'product_id_mismatch',
                        'details': f'product_id should be NULL for RiderChatMessage migrations. Got: {unified_product_id}'
                    })
            
            return errors
            
        except Exception as e:
            self.logger.error(f"  Error sampling RiderChatMessage: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return [{
                'source_table': 'rider_chat_message',
                'source_id': 0,
                'error_type': 'sampling_error',
                'details': f'Error sampling RiderChatMessage: {str(e)}'
            }]


class RollbackService:
    """Service for rolling back migration and restoring legacy chat system.
    
    This service handles:
    - Restoring legacy tables from backup files
    - Clearing the unified ChatMessage table
    - Orchestrating full rollback workflow
    - Logging all rollback operations
    
    Requirements: 11.5, 11.6, 11.7, 11.8
    """
    
    def __init__(self, db_session, backup_paths: Dict[str, str]):
        """Initialize rollback service.
        
        Args:
            db_session: SQLAlchemy database session
            backup_paths: Dictionary of backup file paths from MigrationService.create_backups()
                         Format: {'store_chat_backup': '/path/to/file.sql', 
                                  'rider_chat_backup': '/path/to/file.sql'}
        """
        self.db = db_session
        self.backup_paths = backup_paths
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def restore_legacy_tables(self) -> bool:
        """Restore StoreChatMessage and RiderChatMessage tables from backup files.
        
        This method:
        1. Truncates existing legacy tables
        2. Reads SQL INSERT statements from backup files
        3. Executes INSERT statements to restore data
        4. Commits the transaction
        
        Returns:
            True if restoration successful, False otherwise
        
        Requirements: 11.5
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting restoration of legacy tables from backups")
        self.logger.info("=" * 60)
        
        try:
            from sqlalchemy import text
            
            # Restore StoreChatMessage table
            if 'store_chat_backup' in self.backup_paths:
                store_backup_path = self.backup_paths['store_chat_backup']
                self.logger.info(f"Restoring StoreChatMessage from: {store_backup_path}")
                
                # Truncate existing table
                self.logger.info("  Truncating store_chat_message table...")
                self.db.execute(text('TRUNCATE TABLE store_chat_message CASCADE'))
                self.db.commit()
                
                # Read and execute backup SQL
                with open(store_backup_path, 'r', encoding='utf-8') as f:
                    backup_sql = f.read()
                
                # Extract and execute INSERT statements
                insert_statements = [
                    line.strip() 
                    for line in backup_sql.split('\n') 
                    if line.strip().startswith('INSERT INTO')
                ]
                
                self.logger.info(f"  Executing {len(insert_statements)} INSERT statements...")
                for i, statement in enumerate(insert_statements, 1):
                    try:
                        self.db.execute(text(statement))
                        if i % 100 == 0:
                            self.logger.info(f"    Progress: {i}/{len(insert_statements)} records restored")
                    except Exception as e:
                        self.logger.error(f"    Error executing statement {i}: {str(e)}")
                        self.logger.error(f"    Statement: {statement[:100]}...")
                        raise
                
                self.db.commit()
                self.logger.info(f"  ✓ StoreChatMessage restored: {len(insert_statements)} records")
            else:
                self.logger.warning("  ⚠ No StoreChatMessage backup found, skipping")
            
            # Restore RiderChatMessage table
            if 'rider_chat_backup' in self.backup_paths:
                rider_backup_path = self.backup_paths['rider_chat_backup']
                self.logger.info(f"Restoring RiderChatMessage from: {rider_backup_path}")
                
                # Truncate existing table
                self.logger.info("  Truncating rider_chat_message table...")
                self.db.execute(text('TRUNCATE TABLE rider_chat_message CASCADE'))
                self.db.commit()
                
                # Read and execute backup SQL
                with open(rider_backup_path, 'r', encoding='utf-8') as f:
                    backup_sql = f.read()
                
                # Extract and execute INSERT statements
                insert_statements = [
                    line.strip() 
                    for line in backup_sql.split('\n') 
                    if line.strip().startswith('INSERT INTO')
                ]
                
                self.logger.info(f"  Executing {len(insert_statements)} INSERT statements...")
                for i, statement in enumerate(insert_statements, 1):
                    try:
                        self.db.execute(text(statement))
                        if i % 100 == 0:
                            self.logger.info(f"    Progress: {i}/{len(insert_statements)} records restored")
                    except Exception as e:
                        self.logger.error(f"    Error executing statement {i}: {str(e)}")
                        self.logger.error(f"    Statement: {statement[:100]}...")
                        raise
                
                self.db.commit()
                self.logger.info(f"  ✓ RiderChatMessage restored: {len(insert_statements)} records")
            else:
                self.logger.warning("  ⚠ No RiderChatMessage backup found, skipping")
            
            self.logger.info("=" * 60)
            self.logger.info("✓ Legacy tables restored successfully")
            self.logger.info("=" * 60)
            return True
            
        except Exception as e:
            self.logger.error("=" * 60)
            self.logger.error(f"✗ Error restoring legacy tables: {str(e)}")
            self.logger.error("=" * 60)
            import traceback
            self.logger.error(traceback.format_exc())
            self.db.rollback()
            return False
    
    def clear_unified_table(self) -> bool:
        """Clear all records from the ChatMessage table.
        
        This method truncates the chat_message table to remove all migrated data.
        
        Returns:
            True if clearing successful, False otherwise
        
        Requirements: 11.6
        """
        self.logger.info("=" * 60)
        self.logger.info("Clearing unified ChatMessage table")
        self.logger.info("=" * 60)
        
        try:
            from sqlalchemy import text
            
            # Count records before clearing
            result = self.db.execute(text('SELECT COUNT(*) FROM chat_message'))
            record_count = result.scalar()
            self.logger.info(f"  Found {record_count} records in chat_message table")
            
            # Truncate table
            self.logger.info("  Truncating chat_message table...")
            self.db.execute(text('TRUNCATE TABLE chat_message CASCADE'))
            self.db.commit()
            
            # Verify table is empty
            result = self.db.execute(text('SELECT COUNT(*) FROM chat_message'))
            remaining_count = result.scalar()
            
            if remaining_count == 0:
                self.logger.info(f"  ✓ ChatMessage table cleared: {record_count} records removed")
                self.logger.info("=" * 60)
                self.logger.info("✓ Unified table cleared successfully")
                self.logger.info("=" * 60)
                return True
            else:
                self.logger.error(f"  ✗ Table not empty: {remaining_count} records remaining")
                self.logger.info("=" * 60)
                return False
            
        except Exception as e:
            self.logger.error("=" * 60)
            self.logger.error(f"✗ Error clearing unified table: {str(e)}")
            self.logger.error("=" * 60)
            import traceback
            self.logger.error(traceback.format_exc())
            self.db.rollback()
            return False
    
    def execute_rollback(self, reason: str) -> Dict[str, any]:
        """Execute complete rollback workflow.
        
        This method orchestrates the full rollback process:
        1. Log the rollback reason
        2. Clear the unified ChatMessage table
        3. Restore legacy tables from backups
        4. Verify restoration was successful
        
        Args:
            reason: Explanation for why rollback is being triggered
        
        Returns:
            Dictionary with rollback results:
            {
                'success': bool,
                'reason': str,
                'timestamp': str,
                'cleared_unified': bool,
                'restored_legacy': bool,
                'logs': List[str]
            }
        
        Requirements: 11.7, 11.8
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logs = []
        
        self.logger.info("=" * 60)
        self.logger.info("INITIATING ROLLBACK PROCEDURE")
        self.logger.info("=" * 60)
        self.logger.info(f"Timestamp: {timestamp}")
        self.logger.info(f"Reason: {reason}")
        self.logger.info("=" * 60)
        
        logs.append(f"[{timestamp}] Rollback initiated")
        logs.append(f"[{timestamp}] Reason: {reason}")
        
        # Step 1: Clear unified table
        self.logger.info("Step 1/2: Clearing unified ChatMessage table...")
        cleared_unified = self.clear_unified_table()
        
        if cleared_unified:
            logs.append(f"[{timestamp}] ✓ Unified table cleared successfully")
        else:
            logs.append(f"[{timestamp}] ✗ Failed to clear unified table")
            self.logger.error("Rollback failed at Step 1: Could not clear unified table")
            return {
                'success': False,
                'reason': reason,
                'timestamp': timestamp,
                'cleared_unified': False,
                'restored_legacy': False,
                'logs': logs
            }
        
        # Step 2: Restore legacy tables
        self.logger.info("Step 2/2: Restoring legacy tables from backups...")
        restored_legacy = self.restore_legacy_tables()
        
        if restored_legacy:
            logs.append(f"[{timestamp}] ✓ Legacy tables restored successfully")
        else:
            logs.append(f"[{timestamp}] ✗ Failed to restore legacy tables")
            self.logger.error("Rollback failed at Step 2: Could not restore legacy tables")
            return {
                'success': False,
                'reason': reason,
                'timestamp': timestamp,
                'cleared_unified': cleared_unified,
                'restored_legacy': False,
                'logs': logs
            }
        
        # Rollback completed successfully
        success = cleared_unified and restored_legacy
        
        self.logger.info("=" * 60)
        if success:
            self.logger.info("✓ ROLLBACK COMPLETED SUCCESSFULLY")
            self.logger.info("  - Unified table cleared")
            self.logger.info("  - Legacy tables restored")
            self.logger.info("  - System restored to pre-migration state")
            logs.append(f"[{timestamp}] ✓ Rollback completed successfully")
        else:
            self.logger.error("✗ ROLLBACK FAILED")
            self.logger.error("  - System may be in inconsistent state")
            self.logger.error("  - Manual intervention required")
            logs.append(f"[{timestamp}] ✗ Rollback failed - manual intervention required")
        self.logger.info("=" * 60)
        
        return {
            'success': success,
            'reason': reason,
            'timestamp': timestamp,
            'cleared_unified': cleared_unified,
            'restored_legacy': restored_legacy,
            'logs': logs
        }
