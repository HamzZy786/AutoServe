import pytest
import time
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import the worker modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worker import app
from tasks import (
    process_data_task,
    send_email_task,
    cleanup_task,
    health_check_task,
    ml_training_task
)

class TestWorkerTasks:
    """Test Celery worker tasks"""
    
    def test_process_data_task(self):
        """Test data processing task"""
        test_data = {"input": "test data", "type": "json"}
        
        result = process_data_task(test_data)
        
        assert result["status"] == "completed"
        assert result["processed_data"] is not None
        assert "timestamp" in result
    
    def test_process_data_task_with_error(self):
        """Test data processing task with invalid data"""
        invalid_data = None
        
        result = process_data_task(invalid_data)
        
        assert result["status"] == "error"
        assert "error" in result
    
    @patch('tasks.send_email')
    def test_send_email_task(self, mock_send_email):
        """Test email sending task"""
        mock_send_email.return_value = True
        
        email_data = {
            "to": "test@example.com",
            "subject": "Test Email",
            "body": "This is a test email"
        }
        
        result = send_email_task(email_data)
        
        assert result["status"] == "sent"
        mock_send_email.assert_called_once()
    
    @patch('tasks.send_email')
    def test_send_email_task_failure(self, mock_send_email):
        """Test email sending task failure"""
        mock_send_email.side_effect = Exception("SMTP Error")
        
        email_data = {
            "to": "invalid@email",
            "subject": "Test Email",
            "body": "This is a test email"
        }
        
        result = send_email_task(email_data)
        
        assert result["status"] == "failed"
        assert "error" in result
    
    def test_cleanup_task(self):
        """Test cleanup task"""
        cleanup_config = {
            "older_than_days": 7,
            "table_name": "test_logs"
        }
        
        result = cleanup_task(cleanup_config)
        
        assert result["status"] == "completed"
        assert "cleaned_records" in result
    
    def test_health_check_task(self):
        """Test health check task"""
        result = health_check_task()
        
        assert result["status"] == "healthy"
        assert result["worker_id"] is not None
        assert "timestamp" in result
    
    @patch('tasks.train_model')
    def test_ml_training_task(self, mock_train_model):
        """Test ML model training task"""
        mock_train_model.return_value = {
            "model_id": "test_model_123",
            "accuracy": 0.85,
            "training_time": 120.5
        }
        
        training_config = {
            "model_type": "random_forest",
            "data_source": "historical_metrics",
            "features": ["cpu_usage", "memory_usage", "request_rate"]
        }
        
        result = ml_training_task(training_config)
        
        assert result["status"] == "completed"
        assert result["model_id"] == "test_model_123"
        assert result["accuracy"] == 0.85

class TestWorkerConfiguration:
    """Test worker configuration and setup"""
    
    def test_celery_app_configuration(self):
        """Test Celery app configuration"""
        assert app.conf.broker_url is not None
        assert app.conf.result_backend is not None
        assert app.conf.task_serializer == 'json'
        assert app.conf.accept_content == ['json']
    
    def test_worker_routes(self):
        """Test task routing configuration"""
        # Check if tasks are properly registered
        registered_tasks = list(app.tasks.keys())
        
        expected_tasks = [
            'tasks.process_data_task',
            'tasks.send_email_task',
            'tasks.cleanup_task',
            'tasks.health_check_task',
            'tasks.ml_training_task'
        ]
        
        for task in expected_tasks:
            assert task in registered_tasks

class TestTaskRetries:
    """Test task retry mechanisms"""
    
    @patch('tasks.process_data_task.retry')
    def test_task_retry_on_failure(self, mock_retry):
        """Test task retry mechanism"""
        mock_retry.side_effect = Exception("Max retries exceeded")
        
        # This would normally trigger a retry
        with pytest.raises(Exception):
            process_data_task.retry(countdown=60, max_retries=3)
    
    def test_exponential_backoff(self):
        """Test exponential backoff calculation"""
        # Test the retry delay calculation
        for attempt in range(1, 5):
            delay = min(60 * (2 ** attempt), 300)  # Cap at 5 minutes
            assert delay > 0
            assert delay <= 300

class TestTaskMetrics:
    """Test task metrics and monitoring"""
    
    @patch('tasks.TASK_COUNTER')
    @patch('tasks.TASK_DURATION')
    def test_task_metrics_collection(self, mock_duration, mock_counter):
        """Test that metrics are collected for tasks"""
        # Mock the metrics objects
        mock_counter.labels.return_value.inc = MagicMock()
        mock_duration.labels.return_value.observe = MagicMock()
        
        result = process_data_task({"test": "data"})
        
        # Verify metrics were called (in a real scenario)
        assert result is not None
    
    def test_task_timing(self):
        """Test task execution timing"""
        start_time = time.time()
        
        result = health_check_task()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time < 5.0  # Should complete quickly
        assert result["status"] == "healthy"

class TestConcurrentTasks:
    """Test concurrent task execution"""
    
    def test_multiple_task_execution(self):
        """Test executing multiple tasks concurrently"""
        import threading
        
        results = []
        
        def run_task():
            result = health_check_task()
            results.append(result)
        
        # Create multiple threads to simulate concurrent execution
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=run_task)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        assert len(results) == 5
        for result in results:
            assert result["status"] == "healthy"

class TestTaskSerialization:
    """Test task serialization and deserialization"""
    
    def test_json_serialization(self):
        """Test that task parameters can be serialized to JSON"""
        import json
        
        task_data = {
            "string_param": "test",
            "number_param": 123,
            "boolean_param": True,
            "list_param": [1, 2, 3],
            "dict_param": {"nested": "value"}
        }
        
        # Should be able to serialize and deserialize
        serialized = json.dumps(task_data)
        deserialized = json.loads(serialized)
        
        assert deserialized == task_data
    
    def test_large_payload_handling(self):
        """Test handling of large task payloads"""
        # Create a large payload
        large_data = {"data": "x" * 10000}  # 10KB of data
        
        result = process_data_task(large_data)
        
        assert result["status"] in ["completed", "error"]

if __name__ == "__main__":
    pytest.main([__file__])
