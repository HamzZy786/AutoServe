#!/usr/bin/env python3
"""
Chaos Monkey for AutoServe
Implements chaos engineering practices to test system resilience
"""

import random
import time
import argparse
import subprocess
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChaosMonkey:
    """Chaos engineering tool for testing AutoServe resilience"""
    
    def __init__(self, namespace: str = "autoserve", dry_run: bool = False):
        self.namespace = namespace
        self.dry_run = dry_run
        self.chaos_events = []
    
    def get_pods(self) -> List[Dict]:
        """Get list of pods in the namespace"""
        try:
            cmd = f"kubectl get pods -n {self.namespace} -o json"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to get pods: {result.stderr}")
                return []
            
            pods_data = json.loads(result.stdout)
            return pods_data.get('items', [])
        
        except Exception as e:
            logger.error(f"Error getting pods: {e}")
            return []
    
    def kill_random_pod(self, service_filter: Optional[str] = None) -> bool:
        """Kill a random pod"""
        pods = self.get_pods()
        
        if service_filter:
            pods = [p for p in pods if service_filter in p['metadata']['name']]
        
        if not pods:
            logger.warning("No pods found to kill")
            return False
        
        target_pod = random.choice(pods)
        pod_name = target_pod['metadata']['name']
        
        logger.info(f"🐒 Chaos Monkey: Killing pod {pod_name}")
        
        if self.dry_run:
            logger.info("DRY RUN: Would kill pod")
            return True
        
        try:
            cmd = f"kubectl delete pod {pod_name} -n {self.namespace}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_chaos_event("pod_kill", pod_name, "success")
                logger.info(f"✅ Successfully killed pod {pod_name}")
                return True
            else:
                logger.error(f"Failed to kill pod: {result.stderr}")
                self.log_chaos_event("pod_kill", pod_name, "failed")
                return False
        
        except Exception as e:
            logger.error(f"Error killing pod: {e}")
            return False
    
    def stress_cpu(self, pod_name: str, duration: int = 60) -> bool:
        """Apply CPU stress to a specific pod"""
        logger.info(f"🐒 Chaos Monkey: Applying CPU stress to {pod_name} for {duration}s")
        
        if self.dry_run:
            logger.info("DRY RUN: Would apply CPU stress")
            return True
        
        try:
            # Use stress-ng if available, fallback to yes command
            stress_cmd = f"timeout {duration} stress-ng --cpu 2 --timeout {duration}s || timeout {duration} yes > /dev/null &"
            cmd = f"kubectl exec -n {self.namespace} {pod_name} -- sh -c '{stress_cmd}'"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_chaos_event("cpu_stress", pod_name, "success", {"duration": duration})
                logger.info(f"✅ Applied CPU stress to {pod_name}")
                return True
            else:
                logger.error(f"Failed to apply CPU stress: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error applying CPU stress: {e}")
            return False
    
    def stress_memory(self, pod_name: str, memory_mb: int = 256, duration: int = 60) -> bool:
        """Apply memory stress to a specific pod"""
        logger.info(f"🐒 Chaos Monkey: Applying memory stress to {pod_name} ({memory_mb}MB for {duration}s)")
        
        if self.dry_run:
            logger.info("DRY RUN: Would apply memory stress")
            return True
        
        try:
            stress_cmd = f"timeout {duration} stress-ng --vm 1 --vm-bytes {memory_mb}M --timeout {duration}s"
            cmd = f"kubectl exec -n {self.namespace} {pod_name} -- sh -c '{stress_cmd}'"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_chaos_event("memory_stress", pod_name, "success", 
                                   {"memory_mb": memory_mb, "duration": duration})
                logger.info(f"✅ Applied memory stress to {pod_name}")
                return True
            else:
                logger.error(f"Failed to apply memory stress: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error applying memory stress: {e}")
            return False
    
    def network_partition(self, pod_name: str, target_ip: str, duration: int = 60) -> bool:
        """Simulate network partition"""
        logger.info(f"🐒 Chaos Monkey: Creating network partition for {pod_name} -> {target_ip}")
        
        if self.dry_run:
            logger.info("DRY RUN: Would create network partition")
            return True
        
        try:
            # Block traffic to target IP
            block_cmd = f"iptables -A OUTPUT -d {target_ip} -j DROP"
            restore_cmd = f"sleep {duration} && iptables -D OUTPUT -d {target_ip} -j DROP"
            
            cmd = f"kubectl exec -n {self.namespace} {pod_name} -- sh -c '{block_cmd} && {restore_cmd}' &"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            self.log_chaos_event("network_partition", pod_name, "initiated", 
                               {"target_ip": target_ip, "duration": duration})
            logger.info(f"✅ Network partition initiated for {pod_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating network partition: {e}")
            return False
    
    def simulate_disk_full(self, pod_name: str, size_mb: int = 100, duration: int = 60) -> bool:
        """Simulate disk space exhaustion"""
        logger.info(f"🐒 Chaos Monkey: Simulating disk full on {pod_name} ({size_mb}MB)")
        
        if self.dry_run:
            logger.info("DRY RUN: Would simulate disk full")
            return True
        
        try:
            # Create a large file to consume disk space
            fill_cmd = f"dd if=/dev/zero of=/tmp/chaos_fill bs=1M count={size_mb}"
            cleanup_cmd = f"sleep {duration} && rm -f /tmp/chaos_fill"
            
            cmd = f"kubectl exec -n {self.namespace} {pod_name} -- sh -c '{fill_cmd} && {cleanup_cmd}' &"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            self.log_chaos_event("disk_full", pod_name, "initiated", 
                               {"size_mb": size_mb, "duration": duration})
            logger.info(f"✅ Disk full simulation initiated for {pod_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error simulating disk full: {e}")
            return False
    
    def random_chaos(self, duration_minutes: int = 10, interval_seconds: int = 30):
        """Run random chaos experiments for specified duration"""
        logger.info(f"🐒 Starting random chaos for {duration_minutes} minutes")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        chaos_actions = [
            self.kill_random_pod,
            lambda: self.stress_random_pod("cpu"),
            lambda: self.stress_random_pod("memory"),
            lambda: self.simulate_disk_full_random()
        ]
        
        while datetime.now() < end_time:
            try:
                # Choose random chaos action
                action = random.choice(chaos_actions)
                action()
                
                # Wait before next chaos event
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Chaos experiments interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error during chaos experiment: {e}")
                time.sleep(interval_seconds)
        
        logger.info("🐒 Chaos experiments completed")
        self.print_chaos_summary()
    
    def stress_random_pod(self, stress_type: str = "cpu"):
        """Apply stress to a random pod"""
        pods = self.get_pods()
        if not pods:
            return
        
        target_pod = random.choice(pods)
        pod_name = target_pod['metadata']['name']
        
        if stress_type == "cpu":
            self.stress_cpu(pod_name, duration=random.randint(30, 120))
        elif stress_type == "memory":
            memory_mb = random.randint(128, 512)
            self.stress_memory(pod_name, memory_mb, duration=random.randint(30, 120))
    
    def simulate_disk_full_random(self):
        """Simulate disk full on a random pod"""
        pods = self.get_pods()
        if not pods:
            return
        
        target_pod = random.choice(pods)
        pod_name = target_pod['metadata']['name']
        size_mb = random.randint(50, 200)
        duration = random.randint(30, 120)
        
        self.simulate_disk_full(pod_name, size_mb, duration)
    
    def log_chaos_event(self, event_type: str, target: str, status: str, details: Dict = None):
        """Log chaos event for analysis"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "target": target,
            "status": status,
            "details": details or {}
        }
        self.chaos_events.append(event)
    
    def print_chaos_summary(self):
        """Print summary of chaos events"""
        logger.info("\n🐒 CHAOS SUMMARY:")
        logger.info(f"Total events: {len(self.chaos_events)}")
        
        event_types = {}
        for event in self.chaos_events:
            event_type = event['type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        for event_type, count in event_types.items():
            logger.info(f"  {event_type}: {count}")
    
    def export_chaos_report(self, filename: str = None):
        """Export chaos events to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chaos_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.chaos_events, f, indent=2)
        
        logger.info(f"📊 Chaos report exported to {filename}")

def main():
    parser = argparse.ArgumentParser(description="AutoServe Chaos Monkey")
    parser.add_argument("--namespace", "-n", default="autoserve", 
                       help="Kubernetes namespace")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without executing")
    
    subparsers = parser.add_subparsers(dest="command", help="Chaos commands")
    
    # Kill pod command
    kill_parser = subparsers.add_parser("kill", help="Kill random pod")
    kill_parser.add_argument("--service", help="Filter by service name")
    
    # Stress commands
    stress_parser = subparsers.add_parser("stress", help="Apply stress")
    stress_parser.add_argument("--pod", required=True, help="Pod name")
    stress_parser.add_argument("--type", choices=["cpu", "memory"], default="cpu")
    stress_parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    stress_parser.add_argument("--memory-mb", type=int, default=256, help="Memory stress in MB")
    
    # Random chaos command
    random_parser = subparsers.add_parser("random", help="Run random chaos")
    random_parser.add_argument("--duration", type=int, default=10, help="Duration in minutes")
    random_parser.add_argument("--interval", type=int, default=30, help="Interval between events")
    
    # Network partition command
    network_parser = subparsers.add_parser("network", help="Network partition")
    network_parser.add_argument("--pod", required=True, help="Pod name")
    network_parser.add_argument("--target-ip", required=True, help="Target IP to block")
    network_parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    chaos = ChaosMonkey(namespace=args.namespace, dry_run=args.dry_run)
    
    try:
        if args.command == "kill":
            chaos.kill_random_pod(service_filter=args.service)
        
        elif args.command == "stress":
            if args.type == "cpu":
                chaos.stress_cpu(args.pod, args.duration)
            elif args.type == "memory":
                chaos.stress_memory(args.pod, args.memory_mb, args.duration)
        
        elif args.command == "random":
            chaos.random_chaos(args.duration, args.interval)
        
        elif args.command == "network":
            chaos.network_partition(args.pod, args.target_ip, args.duration)
        
        # Export report
        chaos.export_chaos_report()
    
    except KeyboardInterrupt:
        logger.info("Chaos experiments interrupted")
    except Exception as e:
        logger.error(f"Chaos experiment failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
