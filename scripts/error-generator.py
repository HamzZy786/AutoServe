#!/usr/bin/env python3
"""
Error Generator for AutoServe
Generates various types of errors and failures for testing observability and alerting
"""

import random
import time
import argparse
import requests
import threading
import logging
from datetime import datetime
from typing import List, Dict
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorGenerator:
    """Generate various types of errors for testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.error_counts = {}
    
    def http_errors(self, duration_minutes: int = 5, rate_per_minute: int = 10):
        """Generate HTTP errors"""
        logger.info(f"🔥 Generating HTTP errors for {duration_minutes} minutes at {rate_per_minute}/min")
        
        error_endpoints = [
            "/api/nonexistent",  # 404
            "/api/users/999999",  # 404
            "/api/admin/restricted",  # 403 (if implemented)
        ]
        
        end_time = time.time() + (duration_minutes * 60)
        interval = 60 / rate_per_minute
        
        while time.time() < end_time:
            try:
                endpoint = random.choice(error_endpoints)
                url = f"{self.base_url}{endpoint}"
                
                response = self.session.get(url, timeout=5)
                
                self.log_error("http_error", {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
                
                logger.info(f"Generated HTTP {response.status_code} error on {endpoint}")
                
            except requests.exceptions.RequestException as e:
                self.log_error("http_connection_error", {"error": str(e)})
                logger.warning(f"Connection error: {e}")
            
            time.sleep(interval)
    
    def payload_errors(self, duration_minutes: int = 5, rate_per_minute: int = 5):
        """Generate payload/validation errors"""
        logger.info(f"🔥 Generating payload errors for {duration_minutes} minutes")
        
        invalid_payloads = [
            {"invalid": "json", "missing_required": True},  # Missing fields
            {"email": "not-an-email"},  # Invalid email
            {"username": ""},  # Empty required field
            {"password": "123"},  # Too short password
            {"age": -5},  # Invalid number
            {"data": "x" * 10000},  # Too large payload
        ]
        
        end_time = time.time() + (duration_minutes * 60)
        interval = 60 / rate_per_minute
        
        while time.time() < end_time:
            try:
                payload = random.choice(invalid_payloads)
                url = f"{self.base_url}/api/users/"
                
                response = self.session.post(url, json=payload, timeout=5)
                
                self.log_error("payload_error", {
                    "payload": payload,
                    "status_code": response.status_code,
                    "response": response.text[:200]  # First 200 chars
                })
                
                logger.info(f"Generated payload error: {response.status_code}")
                
            except Exception as e:
                logger.warning(f"Payload error generation failed: {e}")
            
            time.sleep(interval)
    
    def slow_requests(self, duration_minutes: int = 5, delay_seconds: float = 2.0):
        """Generate slow requests to test timeout handling"""
        logger.info(f"🐌 Generating slow requests for {duration_minutes} minutes")
        
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            try:
                # Add artificial delay parameter if your API supports it
                url = f"{self.base_url}/api/health"
                
                start_time = time.time()
                response = self.session.get(url, timeout=10)
                response_time = time.time() - start_time
                
                self.log_error("slow_request", {
                    "response_time": response_time,
                    "status_code": response.status_code
                })
                
                logger.info(f"Slow request completed in {response_time:.2f}s")
                
                # Artificial delay to simulate slow processing
                time.sleep(delay_seconds)
                
            except requests.exceptions.Timeout:
                self.log_error("timeout_error", {"timeout": True})
                logger.info("Request timed out (expected)")
            except Exception as e:
                logger.warning(f"Slow request failed: {e}")
            
            time.sleep(1)
    
    def concurrent_load(self, duration_minutes: int = 5, concurrent_requests: int = 10):
        """Generate concurrent load to stress the system"""
        logger.info(f"⚡ Generating concurrent load for {duration_minutes} minutes")
        
        def make_request():
            try:
                url = f"{self.base_url}/api/health"
                response = self.session.get(url, timeout=5)
                
                self.log_error("concurrent_request", {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
                
            except Exception as e:
                self.log_error("concurrent_error", {"error": str(e)})
        
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            threads = []
            
            for _ in range(concurrent_requests):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all requests to complete
            for thread in threads:
                thread.join()
            
            logger.info(f"Completed batch of {concurrent_requests} concurrent requests")
            time.sleep(5)  # Brief pause between batches
    
    def database_errors(self, duration_minutes: int = 5):
        """Generate database-related errors"""
        logger.info(f"💾 Generating database errors for {duration_minutes} minutes")
        
        # These would need to be implemented in your API
        database_stress_endpoints = [
            "/api/users/?limit=10000",  # Large result set
            "/api/metrics/?days=365",   # Long time range query
        ]
        
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            try:
                endpoint = random.choice(database_stress_endpoints)
                url = f"{self.base_url}{endpoint}"
                
                response = self.session.get(url, timeout=30)
                
                self.log_error("database_stress", {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
                
                logger.info(f"Database stress request: {response.status_code}")
                
            except requests.exceptions.Timeout:
                self.log_error("database_timeout", {"endpoint": endpoint})
                logger.info("Database query timed out")
            except Exception as e:
                logger.warning(f"Database stress failed: {e}")
            
            time.sleep(10)
    
    def authentication_errors(self, duration_minutes: int = 5):
        """Generate authentication and authorization errors"""
        logger.info(f"🔐 Generating auth errors for {duration_minutes} minutes")
        
        invalid_credentials = [
            {"username": "admin", "password": "wrongpassword"},
            {"username": "nonexistent", "password": "password123"},
            {"username": "", "password": ""},
            {"username": "admin", "password": ""},
        ]
        
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            try:
                creds = random.choice(invalid_credentials)
                url = f"{self.base_url}/api/auth/login"
                
                response = self.session.post(url, data=creds, timeout=5)
                
                self.log_error("auth_error", {
                    "username": creds["username"],
                    "status_code": response.status_code
                })
                
                logger.info(f"Auth error generated: {response.status_code}")
                
            except Exception as e:
                logger.warning(f"Auth error generation failed: {e}")
            
            time.sleep(5)
    
    def memory_leak_simulation(self, duration_minutes: int = 5):
        """Simulate memory leaks by keeping references"""
        logger.info(f"🧠 Simulating memory pressure for {duration_minutes} minutes")
        
        # Keep growing list to simulate memory leak
        memory_hog = []
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            try:
                # Add data to simulate memory growth
                chunk = "x" * 1024 * 1024  # 1MB chunk
                memory_hog.append(chunk)
                
                # Make some requests while consuming memory
                url = f"{self.base_url}/api/health"
                response = self.session.get(url, timeout=5)
                
                self.log_error("memory_pressure", {
                    "memory_chunks": len(memory_hog),
                    "status_code": response.status_code
                })
                
                logger.info(f"Memory pressure: {len(memory_hog)}MB allocated")
                
            except Exception as e:
                logger.warning(f"Memory pressure simulation failed: {e}")
            
            time.sleep(10)
        
        # Cleanup
        del memory_hog
        logger.info("Memory pressure simulation completed")
    
    def log_error(self, error_type: str, details: Dict):
        """Log error for analysis"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # In a real scenario, you might send this to your logging system
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "details": details
        }
        
        # Could send to Loki or other log aggregation system
        # requests.post("http://loki:3100/loki/api/v1/push", json=error_entry)
    
    def run_all_errors(self, duration_minutes: int = 10):
        """Run all error types concurrently"""
        logger.info(f"🔥 Running all error types for {duration_minutes} minutes")
        
        error_functions = [
            lambda: self.http_errors(duration_minutes, 5),
            lambda: self.payload_errors(duration_minutes, 3),
            lambda: self.slow_requests(duration_minutes, 1.0),
            lambda: self.authentication_errors(duration_minutes),
        ]
        
        threads = []
        for func in error_functions:
            thread = threading.Thread(target=func)
            threads.append(thread)
            thread.start()
        
        # Wait for all error generators to complete
        for thread in threads:
            thread.join()
        
        self.print_error_summary()
    
    def print_error_summary(self):
        """Print summary of generated errors"""
        logger.info("\n🔥 ERROR GENERATION SUMMARY:")
        logger.info(f"Total error types: {len(self.error_counts)}")
        
        for error_type, count in self.error_counts.items():
            logger.info(f"  {error_type}: {count}")
    
    def export_error_report(self, filename: str = None):
        """Export error statistics"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.error_counts, f, indent=2)
        
        logger.info(f"📊 Error report exported to {filename}")

def main():
    parser = argparse.ArgumentParser(description="AutoServe Error Generator")
    parser.add_argument("--base-url", default="http://localhost:8000",
                       help="Base URL of the AutoServe API")
    parser.add_argument("--duration", type=int, default=5,
                       help="Duration in minutes")
    
    subparsers = parser.add_subparsers(dest="command", help="Error types")
    
    # Individual error types
    subparsers.add_parser("http", help="Generate HTTP errors")
    subparsers.add_parser("payload", help="Generate payload errors")
    subparsers.add_parser("slow", help="Generate slow requests")
    subparsers.add_parser("concurrent", help="Generate concurrent load")
    subparsers.add_parser("database", help="Generate database errors")
    subparsers.add_parser("auth", help="Generate auth errors")
    subparsers.add_parser("memory", help="Simulate memory pressure")
    
    # Run all
    subparsers.add_parser("all", help="Run all error types")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    generator = ErrorGenerator(base_url=args.base_url)
    
    try:
        if args.command == "http":
            generator.http_errors(args.duration)
        elif args.command == "payload":
            generator.payload_errors(args.duration)
        elif args.command == "slow":
            generator.slow_requests(args.duration)
        elif args.command == "concurrent":
            generator.concurrent_load(args.duration)
        elif args.command == "database":
            generator.database_errors(args.duration)
        elif args.command == "auth":
            generator.authentication_errors(args.duration)
        elif args.command == "memory":
            generator.memory_leak_simulation(args.duration)
        elif args.command == "all":
            generator.run_all_errors(args.duration)
        
        generator.export_error_report()
    
    except KeyboardInterrupt:
        logger.info("Error generation interrupted")
    except Exception as e:
        logger.error(f"Error generation failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
