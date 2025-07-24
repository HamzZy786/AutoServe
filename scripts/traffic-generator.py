#!/usr/bin/env python3
"""
Traffic Generator for AutoServe Platform

Generates realistic traffic patterns to test the ML-based scaling system.
"""

import time
import random
import requests
import threading
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrafficGenerator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.running = False
        
    def generate_traffic_pattern(self, pattern: str, duration: int, rps_base: int = 10):
        """Generate different traffic patterns"""
        patterns = {
            'constant': self._constant_pattern,
            'spike': self._spike_pattern,
            'gradual': self._gradual_pattern,
            'random': self._random_pattern,
            'realistic': self._realistic_pattern
        }
        
        if pattern not in patterns:
            raise ValueError(f"Unknown pattern: {pattern}. Available: {list(patterns.keys())}")
        
        return patterns[pattern](duration, rps_base)
    
    def _constant_pattern(self, duration: int, rps_base: int) -> List[int]:
        """Constant traffic rate"""
        return [rps_base] * duration
    
    def _spike_pattern(self, duration: int, rps_base: int) -> List[int]:
        """Traffic with sudden spikes"""
        rates = [rps_base] * duration
        # Add spikes at random intervals
        for _ in range(duration // 20):
            spike_start = random.randint(0, duration - 10)
            spike_multiplier = random.uniform(3, 8)
            for i in range(spike_start, min(spike_start + 5, duration)):
                rates[i] = int(rps_base * spike_multiplier)
        return rates
    
    def _gradual_pattern(self, duration: int, rps_base: int) -> List[int]:
        """Gradually increasing then decreasing traffic"""
        rates = []
        peak = duration // 2
        max_rate = rps_base * 5
        
        for i in range(duration):
            if i <= peak:
                rate = rps_base + (max_rate - rps_base) * (i / peak)
            else:
                rate = max_rate - (max_rate - rps_base) * ((i - peak) / (duration - peak))
            rates.append(int(rate))
        return rates
    
    def _random_pattern(self, duration: int, rps_base: int) -> List[int]:
        """Random traffic variations"""
        rates = []
        for _ in range(duration):
            multiplier = random.uniform(0.1, 5.0)
            rates.append(int(rps_base * multiplier))
        return rates
    
    def _realistic_pattern(self, duration: int, rps_base: int) -> List[int]:
        """Realistic daily traffic pattern"""
        rates = []
        hours_per_second = 24 / duration  # Map duration to 24 hours
        
        for i in range(duration):
            hour = (i * hours_per_second) % 24
            
            # Business hours (9-17) have higher traffic
            if 9 <= hour <= 17:
                base_multiplier = 3.0
            # Evening hours (18-22) moderate traffic
            elif 18 <= hour <= 22:
                base_multiplier = 2.0
            # Night hours (23-8) low traffic
            else:
                base_multiplier = 0.5
            
            # Add some randomness
            noise = random.uniform(0.8, 1.2)
            rate = int(rps_base * base_multiplier * noise)
            rates.append(max(1, rate))
        
        return rates
    
    def make_request(self, endpoint: str = "/health"):
        """Make a single HTTP request"""
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
            return response.status_code, response.elapsed.total_seconds()
        except Exception as e:
            logger.warning(f"Request failed: {e}")
            return 0, 0
    
    def generate_load(self, rps: int, duration: int = 60):
        """Generate load at specified RPS for given duration"""
        interval = 1.0 / rps if rps > 0 else 1.0
        start_time = time.time()
        request_count = 0
        success_count = 0
        total_response_time = 0
        
        logger.info(f"Starting load generation: {rps} RPS for {duration} seconds")
        
        while time.time() - start_time < duration and self.running:
            request_start = time.time()
            
            # Make request in separate thread to avoid blocking
            def make_async_request():
                nonlocal success_count, total_response_time
                status, response_time = self.make_request()
                if status == 200:
                    success_count += 1
                total_response_time += response_time
            
            thread = threading.Thread(target=make_async_request)
            thread.start()
            
            request_count += 1
            
            # Sleep to maintain RPS
            elapsed = time.time() - request_start
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)
        
        # Calculate statistics
        actual_duration = time.time() - start_time
        actual_rps = request_count / actual_duration
        avg_response_time = total_response_time / request_count if request_count > 0 else 0
        success_rate = (success_count / request_count * 100) if request_count > 0 else 0
        
        logger.info(f"Load generation complete:")
        logger.info(f"  Duration: {actual_duration:.1f}s")
        logger.info(f"  Target RPS: {rps}, Actual RPS: {actual_rps:.1f}")
        logger.info(f"  Total requests: {request_count}")
        logger.info(f"  Success rate: {success_rate:.1f}%")
        logger.info(f"  Avg response time: {avg_response_time*1000:.1f}ms")
        
        return {
            'duration': actual_duration,
            'target_rps': rps,
            'actual_rps': actual_rps,
            'total_requests': request_count,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time
        }
    
    def run_pattern(self, pattern: str, duration: int, rps_base: int = 10):
        """Run traffic generation with specified pattern"""
        self.running = True
        rates = self.generate_traffic_pattern(pattern, duration, rps_base)
        
        logger.info(f"Starting traffic pattern '{pattern}' for {duration} seconds")
        logger.info(f"Base RPS: {rps_base}, Pattern: {rates[:10]}...")
        
        results = []
        
        try:
            for i, rps in enumerate(rates):
                if not self.running:
                    break
                
                logger.info(f"Step {i+1}/{len(rates)}: {rps} RPS")
                result = self.generate_load(rps, 1)  # 1 second intervals
                results.append(result)
                
        except KeyboardInterrupt:
            logger.info("Traffic generation interrupted by user")
        finally:
            self.running = False
        
        # Summary statistics
        if results:
            total_requests = sum(r['total_requests'] for r in results)
            avg_success_rate = np.mean([r['success_rate'] for r in results])
            avg_response_time = np.mean([r['avg_response_time'] for r in results])
            
            logger.info(f"\n🎯 Traffic Generation Summary:")
            logger.info(f"  Pattern: {pattern}")
            logger.info(f"  Duration: {len(results)} seconds")
            logger.info(f"  Total requests: {total_requests}")
            logger.info(f"  Average success rate: {avg_success_rate:.1f}%")
            logger.info(f"  Average response time: {avg_response_time*1000:.1f}ms")
        
        return results
    
    def stop(self):
        """Stop traffic generation"""
        self.running = False

def main():
    parser = argparse.ArgumentParser(description="AutoServe Traffic Generator")
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL for the service')
    parser.add_argument('--pattern', default='realistic',
                       choices=['constant', 'spike', 'gradual', 'random', 'realistic'],
                       help='Traffic pattern to generate')
    parser.add_argument('--duration', type=int, default=300,
                       help='Duration in seconds')
    parser.add_argument('--rps', type=int, default=10,
                       help='Base requests per second')
    parser.add_argument('--endpoint', default='/health',
                       help='Endpoint to test')
    
    args = parser.parse_args()
    
    generator = TrafficGenerator(args.url)
    
    try:
        # Test connectivity
        status, _ = generator.make_request(args.endpoint)
        if status != 200:
            logger.error(f"Failed to connect to {args.url}{args.endpoint}")
            return
        
        logger.info(f"✅ Connected to {args.url}")
        logger.info(f"🚀 Starting traffic generation...")
        logger.info(f"   Pattern: {args.pattern}")
        logger.info(f"   Duration: {args.duration} seconds")
        logger.info(f"   Base RPS: {args.rps}")
        logger.info(f"   Endpoint: {args.endpoint}")
        logger.info("Press Ctrl+C to stop\n")
        
        generator.run_pattern(args.pattern, args.duration, args.rps)
        
    except KeyboardInterrupt:
        logger.info("\nStopping traffic generator...")
        generator.stop()
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
