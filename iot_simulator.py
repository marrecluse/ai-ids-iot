#!/usr/bin/env python3
"""
IoT Network Traffic Simulator
Generates simulated network traffic with attacks for AI-IDS testing
"""

import requests
import time
import random
import argparse
from datetime import datetime
from typing import Dict, List

API_URL = "http://localhost:8000/api/detect"

class TrafficPattern:
    """Generate network traffic patterns"""
    
    @staticmethod
    def benign() -> Dict:
        """Normal IoT traffic pattern"""
        return {
            "flow_duration": random.uniform(1000, 50000),
            "total_fwd_packets": random.randint(10, 100),
            "total_bwd_packets": random.randint(5, 80),
            "total_length_fwd_packets": random.uniform(500, 5000),
            "total_length_bwd_packets": random.uniform(300, 3000),
            "fwd_packet_length_mean": random.uniform(50, 500),
            "bwd_packet_length_mean": random.uniform(50, 400),
            "flow_bytes_per_sec": random.uniform(1000, 50000),
            "flow_packets_per_sec": random.uniform(10, 100)
        }
    
    @staticmethod
    def ddos() -> Dict:
        """DDoS attack pattern"""
        return {
            "flow_duration": random.uniform(100, 5000),
            "total_fwd_packets": random.randint(500, 2000),
            "total_bwd_packets": random.randint(0, 10),
            "total_length_fwd_packets": random.uniform(10000, 100000),
            "total_length_bwd_packets": random.uniform(0, 1000),
            "fwd_packet_length_mean": random.uniform(20, 100),
            "bwd_packet_length_mean": random.uniform(0, 50),
            "flow_bytes_per_sec": random.uniform(100000, 500000),
            "flow_packets_per_sec": random.uniform(500, 2000)
        }
    
    @staticmethod
    def port_scan() -> Dict:
        """Port scanning attack pattern"""
        return {
            "flow_duration": random.uniform(50, 500),
            "total_fwd_packets": random.randint(1, 5),
            "total_bwd_packets": random.randint(0, 2),
            "total_length_fwd_packets": random.uniform(40, 200),
            "total_length_bwd_packets": random.uniform(0, 100),
            "fwd_packet_length_mean": random.uniform(40, 60),
            "bwd_packet_length_mean": random.uniform(0, 50),
            "flow_bytes_per_sec": random.uniform(100, 1000),
            "flow_packets_per_sec": random.uniform(1, 10)
        }
    
    @staticmethod
    def bot() -> Dict:
        """Botnet attack pattern"""
        return {
            "flow_duration": random.uniform(10000, 100000),
            "total_fwd_packets": random.randint(100, 500),
            "total_bwd_packets": random.randint(50, 400),
            "total_length_fwd_packets": random.uniform(5000, 50000),
            "total_length_bwd_packets": random.uniform(3000, 40000),
            "fwd_packet_length_mean": random.uniform(50, 200),
            "bwd_packet_length_mean": random.uniform(50, 150),
            "flow_bytes_per_sec": random.uniform(500, 5000),
            "flow_packets_per_sec": random.uniform(5, 50)
        }

class IoTSimulator:
    """Main simulator class"""
    
    def __init__(self, num_devices: int = 3, attack_rate: float = 0.15):
        self.num_devices = num_devices
        self.attack_rate = attack_rate
        self.patterns = {
            'benign': TrafficPattern.benign,
            'ddos': TrafficPattern.ddos,
            'port_scan': TrafficPattern.port_scan,
            'bot': TrafficPattern.bot
        }
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'benign': 0,
            'attacks': 0
        }
    
    def generate_traffic(self) -> Dict:
        """Generate a traffic sample"""
        if random.random() < self.attack_rate:
            # Generate attack
            attack_type = random.choice(['ddos', 'port_scan', 'bot'])
            self.stats['attacks'] += 1
            return self.patterns[attack_type]()
        else:
            # Generate benign traffic
            self.stats['benign'] += 1
            return self.patterns['benign']()
    
    def send_traffic(self, traffic: Dict) -> bool:
        """Send traffic to API"""
        try:
            response = requests.post(API_URL, json=traffic, timeout=5)
            if response.status_code == 200:
                self.stats['successful'] += 1
                return True
            else:
                self.stats['failed'] += 1
                return False
        except Exception as e:
            self.stats['failed'] += 1
            print(f"❌ Error sending traffic: {e}")
            return False
    
    def print_stats(self):
        """Print current statistics"""
        total = self.stats['total_requests']
        if total == 0:
            return
        
        print(f"\n{'='*60}")
        print(f"📊 TRAFFIC STATISTICS")
        print(f"{'='*60}")
        print(f"Total Requests:     {total}")
        print(f"✅ Successful:      {self.stats['successful']} ({self.stats['successful']/total*100:.1f}%)")
        print(f"❌ Failed:          {self.stats['failed']} ({self.stats['failed']/total*100:.1f}%)")
        print(f"🟢 Benign Traffic:  {self.stats['benign']} ({self.stats['benign']/total*100:.1f}%)")
        print(f"🔴 Attack Traffic:  {self.stats['attacks']} ({self.stats['attacks']/total*100:.1f}%)")
        print(f"{'='*60}\n")
    
    def run(self, duration: int = None):
        """Run the simulator"""
        print("\n" + "="*60)
        print("🚀 STARTING IoT NETWORK TRAFFIC SIMULATOR")
        print("="*60)
        print(f"Active Devices:     {self.num_devices}")
        print(f"Attack Rate:        {self.attack_rate*100:.0f}%")
        print(f"Target API:         {API_URL}")
        print(f"Duration:           {'Continuous (Ctrl+C to stop)' if duration is None else f'{duration} seconds'}")
        print("="*60 + "\n")
        
        start_time = time.time()
        iteration = 0
        
        try:
            while True:
                iteration += 1
                
                # Generate and send traffic for each active device
                for device_num in range(self.num_devices):
                    traffic = self.generate_traffic()
                    self.send_traffic(traffic)
                    self.stats['total_requests'] += 1
                
                # Print progress
                if iteration % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = self.stats['total_requests'] / elapsed
                    print(f"⏱️  [{datetime.now().strftime('%H:%M:%S')}] "
                          f"Requests: {self.stats['total_requests']} | "
                          f"Rate: {rate:.1f} req/s | "
                          f"Success: {self.stats['successful']}")
                
                # Print statistics every 30 seconds
                if iteration % 100 == 0:
                    self.print_stats()
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # Small delay
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Simulator stopped by user")
        
        finally:
            print("\n" + "="*60)
            print("📈 FINAL STATISTICS")
            print("="*60)
            elapsed = time.time() - start_time
            print(f"Total Runtime:      {elapsed:.1f} seconds")
            print(f"Average Rate:       {self.stats['total_requests']/elapsed:.2f} req/s")
            self.print_stats()

def main():
    parser = argparse.ArgumentParser(description='IoT Network Traffic Simulator')
    parser.add_argument('--devices', type=int, default=3, 
                        help='Number of active devices (default: 3)')
    parser.add_argument('--attack-rate', type=float, default=0.15, 
                        help='Attack traffic rate 0-1 (default: 0.15)')
    parser.add_argument('--duration', type=int, default=None, 
                        help='Duration in seconds (default: continuous)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.devices < 1 or args.devices > 12:
        print("❌ Error: devices must be between 1 and 12")
        return
    
    if args.attack_rate < 0 or args.attack_rate > 1:
        print("❌ Error: attack-rate must be between 0 and 1")
        return
    
    # Create and run simulator
    simulator = IoTSimulator(num_devices=args.devices, attack_rate=args.attack_rate)
    simulator.run(duration=args.duration)

if __name__ == "__main__":
    main()
