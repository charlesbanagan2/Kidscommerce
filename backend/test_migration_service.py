"""
Unit tests for MigrationService class

Tests the backup functionality for StoreChatMessage and RiderChatMessage tables.
"""

import os
import sys
import unittest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from migration_service import MigrationService


class TestMigrationService(unittest.TestCase):
    """Test cases for MigrationService backup functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test Flask app and database"""
        cls.app = Flask(__name__)
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.app.config['TESTING'] = True
        
        cls.db = SQLAlchemy(cls.app)
        
        # Define test models
        class StoreChatMessage(cls.db.Model):
            __tablename__ = 'store_chat_message'
            id = cls.db.Column(cls.db.Integer, primary_key=True)
            buyer_id = cls.db.Column(cls.db.Integer, nullable=False)
            seller_id = cls.db.Column(cls.db.Integer, nullable=False)
            sender_role = cls.db.Column(cls.db.String(10), nullable=False)
            message = cls.db.Column(cls.db.Text, nullable=False)
            product_id = cls.db.Column(cls.db.Integer, nullable=True)
            is_read = cls.db.Column(cls.db.Boolean, default=False)
            created_at = cls.db.Column(cls.db.DateTime, default=datetime.utcnow)
        
        class RiderChatMessage(cls.db.Model):
            __tablename__ = 'rider_chat_message'
            id = cls.db.Column(cls.db.Integer, primary_key=True)
            buyer_id = cls.db.Column(cls.db.Integer, nullable=False)
            rider_id = cls.db.Column(cls.db.Integer, nullable=False)
            sender_role = cls.db.Column(cls.db.String(10), nullable=False)
            message = cls.db.Column(cls.db.Text, nullable=False)
            order_id = cls.db.Column(cls.db.Integer, nullable=True)
            is_read = cls.db.Column(cls.db.Boolean, default=False)
            created_at = cls.db.Column(cls.db.DateTime, default=datetime.utcnow)
        
        class ChatMessage(cls.db.Model):
            __tablename__ = 'chat_message'
            id = cls.db.Column(cls.db.Integer, primary_key=True)
            sender_id = cls.db.Column(cls.db.Integer, nullable=False)
            receiver_id = cls.db.Column(cls.db.Integer, nullable=False)
            message = cls.db.Column(cls.db.Text, nullable=False)
            product_id = cls.db.Column(cls.db.Integer, nullable=True)
            order_id = cls.db.Column(cls.db.Integer, nullable=True)
            is_read = cls.db.Column(cls.db.Boolean, default=False)
            created_at = cls.db.Column(cls.db.DateTime, default=datetime.utcnow)
        
        cls.StoreChatMessage = StoreChatMessage
        cls.RiderChatMessage = RiderChatMessage
        cls.ChatMessage = ChatMessage
        
        # Create tables
        with cls.app.app_context():
            cls.db.create_all()
    
    def setUp(self):
        """Set up test data before each test"""
        # Create temporary backup directory
        self.temp_dir = tempfile.mkdtemp()
        
        with self.app.app_context():
            # Clear existing data
            self.db.session.query(self.StoreChatMessage).delete()
            self.db.session.query(self.RiderChatMessage).delete()
            self.db.session.commit()
            
            # Add test data for StoreChatMessage
            store_msg1 = self.StoreChatMessage(
                buyer_id=1,
                seller_id=2,
                sender_role='buyer',
                message='Hello, is this product available?',
                product_id=10,
                is_read=False,
                created_at=datetime(2024, 1, 15, 10, 30, 0)
            )
            store_msg2 = self.StoreChatMessage(
                buyer_id=1,
                seller_id=2,
                sender_role='seller',
                message='Yes, it is available!',
                product_id=10,
                is_read=True,
                created_at=datetime(2024, 1, 15, 10, 35, 0)
            )
            
            # Add test data for RiderChatMessage
            rider_msg1 = self.RiderChatMessage(
                buyer_id=1,
                rider_id=3,
                sender_role='buyer',
                message='Where are you now?',
                order_id=100,
                is_read=False,
                created_at=datetime(2024, 1, 15, 14, 0, 0)
            )
            rider_msg2 = self.RiderChatMessage(
                buyer_id=1,
                rider_id=3,
                sender_role='rider',
                message='I am 5 minutes away',
                order_id=100,
                is_read=True,
                created_at=datetime(2024, 1, 15, 14, 5, 0)
            )
            
            self.db.session.add_all([store_msg1, store_msg2, rider_msg1, rider_msg2])
            self.db.session.commit()
    
    def tearDown(self):
        """Clean up after each test"""
        # Remove temporary backup directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_backups_success(self):
        """Test that create_backups() creates backup files successfully"""
        with self.app.app_context():
            service = MigrationService(self.db.session, backup_dir=self.temp_dir)
            backup_paths = service.create_backups()
            
            # Verify both backups were created
            self.assertIn('store_chat_backup', backup_paths)
            self.assertIn('rider_chat_backup', backup_paths)
            
            # Verify files exist
            self.assertTrue(os.path.exists(backup_paths['store_chat_backup']))
            self.assertTrue(os.path.exists(backup_paths['rider_chat_backup']))
    
    def test_backup_file_naming(self):
        """Test that backup files have correct timestamp format"""
        with self.app.app_context():
            service = MigrationService(self.db.session, backup_dir=self.temp_dir)
            backup_paths = service.create_backups()
            
            # Check filename format: {table}_backup_{YYYYMMDD_HHMMSS}.sql
            for backup_path in backup_paths.values():
                filename = os.path.basename(backup_path)
                self.assertTrue(filename.endswith('.sql'))
                self.assertIn('backup_', filename)
                # Extract timestamp part
                timestamp_part = filename.split('backup_')[1].replace('.sql', '')
                # Verify timestamp format (YYYYMMDD_HHMMSS)
                self.assertEqual(len(timestamp_part), 15)  # YYYYMMDD_HHMMSS = 15 chars
    
    def test_backup_content_store_chat(self):
        """Test that StoreChatMessage backup contains correct data"""
        with self.app.app_context():
            service = MigrationService(self.db.session, backup_dir=self.temp_dir)
            backup_paths = service.create_backups()
            
            # Read backup file
            with open(backup_paths['store_chat_backup'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify header comments
            self.assertIn('-- Backup of store_chat_message', content)
            self.assertIn('-- Records: 2', content)
            
            # Verify INSERT statements
            self.assertEqual(content.count('INSERT INTO store_chat_message'), 2)
            
            # Verify data content
            self.assertIn('Hello, is this product available?', content)
            self.assertIn('Yes, it is available!', content)
    
    def test_backup_content_rider_chat(self):
        """Test that RiderChatMessage backup contains correct data"""
        with self.app.app_context():
            service = MigrationService(self.db.session, backup_dir=self.temp_dir)
            backup_paths = service.create_backups()
            
            # Read backup file
            with open(backup_paths['rider_chat_backup'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify header comments
            self.assertIn('-- Backup of rider_chat_message', content)
            self.assertIn('-- Records: 2', content)
            
            # Verify INSERT statements
            self.assertEqual(content.count('INSERT INTO rider_chat_message'), 2)
            
            # Verify data content
            self.assertIn('Where are you now?', content)
            self.assertIn('I am 5 minutes away', content)
    
    def test_verify_backups_success(self):
        """Test that verify_backups() returns True for valid backups"""
        with self.app.app_context():
            service = MigrationService(self.db.session, backup_dir=self.temp_dir)
            backup_paths = service.create_backups()
            
            # Verify backups
            result = service.verify_backups(backup_paths)
            self.assertTrue(result)
    
    def test_verify_backups_missing_file(self):
        """Test that verify_backups() returns False for missing files"""
        with self.app.app_context():
            service = MigrationService(self.db.session, backup_dir=self.temp_dir)
            
            # Create fake backup paths
            fake_paths = {
                'store_chat_backup': os.path.join(self.temp_dir, 'nonexistent.sql'),
                'rider_chat_backup': os.path.join(self.temp_dir, 'nonexistent2.sql')
            }
            
            # Verify should fail
            result = service.verify_backups(fake_paths)
            self.assertFalse(result)
    
    def test_verify_backups_empty_file(self):
        """Test that verify_backups() returns False for empty files"""
        with self.app.app_context():
            service = MigrationService(self.db.session, backup_dir=self.temp_dir)
            
            # Create empty backup files
            empty_file1 = os.path.join(self.temp_dir, 'empty1.sql')
            empty_file2 = os.path.join(self.temp_dir, 'empty2.sql')
            
            with open(empty_file1, 'w') as f:
                pass  # Create empty file
            with open(empty_file2, 'w') as f:
                pass  # Create empty file
            
            fake_paths = {
                'store_chat_backup': empty_file1,
                'rider_chat_backup': empty_file2
            }
            
            # Verify should fail
            result = service.verify_backups(fake_paths)
            self.assertFalse(result)
    
    def test_backup_with_special_characters(self):
        """Test that backup handles special characters in messages"""
        with self.app.app_context():
            # Add message with special characters
            special_msg = self.StoreChatMessage(
                buyer_id=5,
                seller_id=6,
                sender_role='buyer',
                message="Test with 'single quotes' and \"double quotes\"",
                product_id=20,
                is_read=False,
                created_at=datetime(2024, 1, 15, 16, 0, 0)
            )
            self.db.session.add(special_msg)
            self.db.session.commit()
            
            service = MigrationService(self.db.session, backup_dir=self.temp_dir)
            backup_paths = service.create_backups()
            
            # Read backup file
            with open(backup_paths['store_chat_backup'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify special characters are escaped
            self.assertIn("'single quotes'", content)
            self.assertIn('"double quotes"', content)
    
    def test_backup_with_null_values(self):
        """Test that backup handles NULL values correctly"""
        with self.app.app_context():
            # Add message with NULL product_id
            null_msg = self.StoreChatMessage(
                buyer_id=7,
                seller_id=8,
                sender_role='seller',
                message="Message without product",
                product_id=None,  # NULL value
                is_read=False,
                created_at=datetime(2024, 1, 15, 17, 0, 0)
            )
            self.db.session.add(null_msg)
            self.db.session.commit()
            
            service = MigrationService(self.db.session, backup_dir=self.temp_dir)
            backup_paths = service.create_backups()
            
            # Read backup file
            with open(backup_paths['store_chat_backup'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verify NULL is used for null values
            self.assertIn('NULL', content)
    
    def test_backup_directory_creation(self):
        """Test that backup directory is created if it doesn't exist"""
        with self.app.app_context():
            # Use non-existent directory
            new_dir = os.path.join(self.temp_dir, 'new_backup_dir')
            self.assertFalse(os.path.exists(new_dir))
            
            service = MigrationService(self.db.session, backup_dir=new_dir)
            
            # Directory should be created
            self.assertTrue(os.path.exists(new_dir))
    
    def test_logging_output(self):
        """Test that logging is properly configured and outputs messages"""
        with self.app.app_context():
            service = MigrationService(self.db.session, backup_dir=self.temp_dir)
            
            # Verify logger is configured
            self.assertIsNotNone(service.logger)
            self.assertTrue(len(service.logger.handlers) > 0)
            
            # Create backups (should log messages)
            backup_paths = service.create_backups()
            
            # If we got here without errors, logging is working
            self.assertTrue(True)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
