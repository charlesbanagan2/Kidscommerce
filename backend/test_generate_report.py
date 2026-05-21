"""
Test suite for DataIntegrityValidator.generate_report() method

Tests the comprehensive validation report generation functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from migration_service import DataIntegrityValidator


class TestGenerateReport:
    """Test suite for generate_report() method"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session"""
        return Mock()
    
    @pytest.fixture
    def validator(self, mock_db_session):
        """Create a DataIntegrityValidator instance with mock database"""
        return DataIntegrityValidator(mock_db_session)
    
    # ============================================
    # Tests for generate_report()
    # ============================================
    
    def test_generate_report_all_checks_pass(self, validator, mock_db_session):
        """Test report generation when all validation checks pass"""
        # Mock the database execute method for count queries
        mock_result_store = Mock()
        mock_result_store.scalar.return_value = 100
        
        mock_result_rider = Mock()
        mock_result_rider.scalar.return_value = 50
        
        mock_result_unified = Mock()
        mock_result_unified.scalar.return_value = 150
        
        # Set up the mock to return different results for each call
        mock_db_session.execute.side_effect = [
            mock_result_store,      # count_legacy_records - store_chat
            mock_result_rider,      # count_legacy_records - rider_chat
            mock_result_unified     # count_unified_records
        ]
        
        # Call the method
        report = validator.generate_report()
        
        # Verify overall status
        assert report['overall_status'] == 'PASSED'
        
        # Verify timestamp is present
        assert 'timestamp' in report
        assert report['timestamp'] is not None
        
        # Verify record count validation
        rc = report['validation_checks']['record_count_validation']
        assert rc['status'] == 'PASSED'
        assert rc['legacy_store_chat_count'] == 100
        assert rc['legacy_rider_chat_count'] == 50
        assert rc['legacy_total_count'] == 150
        assert rc['unified_count'] == 150
        assert rc['counts_match'] is True
        assert rc['difference'] == 0
        
        # Verify summary
        assert report['summary']['total_checks'] == 4
        assert report['summary']['passed_checks'] == 1
        assert report['summary']['failed_checks'] == 0
        assert report['summary']['not_run_checks'] == 3
        
        # Verify no discrepancies
        assert len(report['discrepancies']) == 0
    
    def test_generate_report_record_count_mismatch(self, validator, mock_db_session):
        """Test report generation when record counts don't match"""
        # Mock the database execute method for count queries
        mock_result_store = Mock()
        mock_result_store.scalar.return_value = 100
        
        mock_result_rider = Mock()
        mock_result_rider.scalar.return_value = 50
        
        mock_result_unified = Mock()
        mock_result_unified.scalar.return_value = 140  # Mismatch: should be 150
        
        # Set up the mock to return different results for each call
        mock_db_session.execute.side_effect = [
            mock_result_store,      # count_legacy_records - store_chat
            mock_result_rider,      # count_legacy_records - rider_chat
            mock_result_unified     # count_unified_records
        ]
        
        # Call the method
        report = validator.generate_report()
        
        # Verify overall status
        assert report['overall_status'] == 'FAILED'
        
        # Verify record count validation
        rc = report['validation_checks']['record_count_validation']
        assert rc['status'] == 'FAILED'
        assert rc['legacy_total_count'] == 150
        assert rc['unified_count'] == 140
        assert rc['counts_match'] is False
        assert rc['difference'] == -10
        
        # Verify summary
        assert report['summary']['passed_checks'] == 0
        assert report['summary']['failed_checks'] == 1
        
        # Verify discrepancies
        assert len(report['discrepancies']) == 1
        assert report['discrepancies'][0]['check'] == 'record_count_validation'
        assert report['discrepancies'][0]['issue'] == 'Record count mismatch'
    
    def test_generate_report_unified_has_extra_records(self, validator, mock_db_session):
        """Test report generation when unified table has extra records"""
        # Mock the database execute method for count queries
        mock_result_store = Mock()
        mock_result_store.scalar.return_value = 100
        
        mock_result_rider = Mock()
        mock_result_rider.scalar.return_value = 50
        
        mock_result_unified = Mock()
        mock_result_unified.scalar.return_value = 160  # Extra records
        
        # Set up the mock to return different results for each call
        mock_db_session.execute.side_effect = [
            mock_result_store,      # count_legacy_records - store_chat
            mock_result_rider,      # count_legacy_records - rider_chat
            mock_result_unified     # count_unified_records
        ]
        
        # Call the method
        report = validator.generate_report()
        
        # Verify overall status
        assert report['overall_status'] == 'FAILED'
        
        # Verify record count validation
        rc = report['validation_checks']['record_count_validation']
        assert rc['status'] == 'FAILED'
        assert rc['difference'] == 10  # Positive difference
        
        # Verify discrepancies
        assert len(report['discrepancies']) == 1
    
    def test_generate_report_empty_tables(self, validator, mock_db_session):
        """Test report generation when all tables are empty"""
        # Mock the database execute method to return 0
        mock_result_store = Mock()
        mock_result_store.scalar.return_value = 0
        
        mock_result_rider = Mock()
        mock_result_rider.scalar.return_value = 0
        
        mock_result_unified = Mock()
        mock_result_unified.scalar.return_value = 0
        
        # Set up the mock to return different results for each call
        mock_db_session.execute.side_effect = [
            mock_result_store,      # count_legacy_records - store_chat
            mock_result_rider,      # count_legacy_records - rider_chat
            mock_result_unified     # count_unified_records
        ]
        
        # Call the method
        report = validator.generate_report()
        
        # Verify overall status (should pass - both are 0)
        assert report['overall_status'] == 'PASSED'
        
        # Verify record count validation
        rc = report['validation_checks']['record_count_validation']
        assert rc['status'] == 'PASSED'
        assert rc['legacy_total_count'] == 0
        assert rc['unified_count'] == 0
        assert rc['counts_match'] is True
        assert rc['difference'] == 0
    
    def test_generate_report_database_error(self, validator, mock_db_session):
        """Test report generation when database query fails"""
        # Mock the database execute method to raise an exception
        mock_db_session.execute.side_effect = Exception("Database connection error")
        
        # Call the method
        report = validator.generate_report()
        
        # Verify overall status
        assert report['overall_status'] == 'FAILED'
        
        # Verify record count validation shows error
        rc = report['validation_checks']['record_count_validation']
        assert rc['status'] == 'FAILED'
        assert 'error' in rc
        
        # Verify summary
        assert report['summary']['failed_checks'] == 1
        
        # Verify discrepancies
        assert len(report['discrepancies']) == 1
        assert report['discrepancies'][0]['check'] == 'record_count_validation'
        assert report['discrepancies'][0]['issue'] == 'Validation error'
    
    def test_generate_report_structure(self, validator, mock_db_session):
        """Test that report has correct structure"""
        # Mock the database execute method
        mock_result_store = Mock()
        mock_result_store.scalar.return_value = 50
        
        mock_result_rider = Mock()
        mock_result_rider.scalar.return_value = 25
        
        mock_result_unified = Mock()
        mock_result_unified.scalar.return_value = 75
        
        mock_db_session.execute.side_effect = [
            mock_result_store,
            mock_result_rider,
            mock_result_unified
        ]
        
        # Call the method
        report = validator.generate_report()
        
        # Verify top-level keys
        assert 'overall_status' in report
        assert 'timestamp' in report
        assert 'validation_checks' in report
        assert 'discrepancies' in report
        assert 'summary' in report
        
        # Verify validation_checks structure
        assert 'record_count_validation' in report['validation_checks']
        assert 'sample_validation' in report['validation_checks']
        assert 'timestamp_validation' in report['validation_checks']
        assert 'is_read_validation' in report['validation_checks']
        
        # Verify summary structure
        assert 'total_checks' in report['summary']
        assert 'passed_checks' in report['summary']
        assert 'failed_checks' in report['summary']
        assert 'not_run_checks' in report['summary']
    
    def test_generate_report_not_implemented_checks(self, validator, mock_db_session):
        """Test that not-yet-implemented checks are marked as NOT_RUN"""
        # Mock the database execute method
        mock_result_store = Mock()
        mock_result_store.scalar.return_value = 100
        
        mock_result_rider = Mock()
        mock_result_rider.scalar.return_value = 50
        
        mock_result_unified = Mock()
        mock_result_unified.scalar.return_value = 150
        
        mock_db_session.execute.side_effect = [
            mock_result_store,
            mock_result_rider,
            mock_result_unified
        ]
        
        # Call the method
        report = validator.generate_report()
        
        # Verify not-yet-implemented checks are marked as NOT_RUN
        assert report['validation_checks']['sample_validation']['status'] == 'NOT_RUN'
        assert report['validation_checks']['timestamp_validation']['status'] == 'NOT_RUN'
        assert report['validation_checks']['is_read_validation']['status'] == 'NOT_RUN'
        
        # Verify not_run_checks count
        assert report['summary']['not_run_checks'] == 3
    
    def test_generate_report_large_numbers(self, validator, mock_db_session):
        """Test report generation with large record counts"""
        # Mock the database execute method
        mock_result_store = Mock()
        mock_result_store.scalar.return_value = 500000
        
        mock_result_rider = Mock()
        mock_result_rider.scalar.return_value = 300000
        
        mock_result_unified = Mock()
        mock_result_unified.scalar.return_value = 800000
        
        mock_db_session.execute.side_effect = [
            mock_result_store,
            mock_result_rider,
            mock_result_unified
        ]
        
        # Call the method
        report = validator.generate_report()
        
        # Verify overall status
        assert report['overall_status'] == 'PASSED'
        
        # Verify record count validation
        rc = report['validation_checks']['record_count_validation']
        assert rc['status'] == 'PASSED'
        assert rc['legacy_store_chat_count'] == 500000
        assert rc['legacy_rider_chat_count'] == 300000
        assert rc['legacy_total_count'] == 800000
        assert rc['unified_count'] == 800000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
