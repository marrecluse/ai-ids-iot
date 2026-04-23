#!/usr/bin/env python3
"""
IoT Network Traffic Simulator
Generates realistic IoT device traffic and simulates various attack scenarios
Muhammad Abdul Rahman (B01821977)
"""

import random
import time
import requests
import json
from datetime import datetime
from typing import Dict, List
import threading

# API endpoint
API_URL = "http://localhost:8000/api/detect"

class IoTDevice:
    """Simulated IoT device."""
    
    def __init__(self, device_id: str, device_type: str, ip: str):
        self.device_id = device_id
        self.device_type = device_type
        self.ip = ip
        self.is_compromised = False
        self.last_activity = datetime.now()
    
    def generate_normal_traffic(self) -> Dict:
        """Generate normal benign traffic pattern."""
        return {
            "flow_duration": random.uniform(1000, 10000),
            "total_fwd_packets": random.randint(5, 50),
            "total_bwd_packets": random.randint(3, 45),
            "flow_bytes_per_sec": random.uniform(100, 1000),
            "flow_packets_per_sec": random.uniform(0.1, 2.0),
            "flow_iat_mean": random.uniform(100, 1000),
            "flow_iat_std": random.uniform(50, 500),
            "fwd_iat_total": random.uniform(1000, 10000),
            "bwd_iat_total": random.uniform(1000, 9000)
        }
    
    def generate_ddos_traffic(self) -> Dict:
        """Generate DDoS attack traffic pattern."""
        return {
            "flow_duration": random.uniform(100000, 500000),
            "total_fwd_packets": random.randint(10000, 100000),
            "total_bwd_packets": random.randint(9000, 95000),
            "flow_bytes_per_sec": random.uniform(100000, 1000000),
            "flow_packets_per_sec": random.uniform(200, 2000),
            "flow_iat_mean": random.uniform(0.5, 5.0),
            "flow_iat_std": random.uniform(0.1, 2.0),
            "fwd_iat_total": random.uniform(100000, 500000),
            "bwd_iat_total": random.uniform(100000, 480000)
        }
    
    def generate_portscan_traffic(self) -> Dict:
        """Generate port scan traffic pattern."""
        return {
            "flow_duration": random.uniform(10, 100),
            "total_fwd_packets": random.randint(1, 3),
            "total_bwd_packets": random.randint(0, 1),
            "flow_bytes_per_sec": random.uniform(50, 150),
            "flow_packets_per_sec": random.uniform(5, 20),
            "flow_iat_mean": random.uniform(5, 20),
            "flow_iat_std": random.uniform(2, 10),
            "fwd_iat_total": random.uniform(10, 100),
            "bwd_iat_total": random.uniform(0, 50)
        }
    
    def generate_bot_traffic(self) -> Dict:
        """Generate bot/botnet traffic pattern."""
        return {
            "flow_duration": random.uniform(5000, 20000),
            "total_fwd_packets": random.randint(50, 200),
            "total_bwd_packets": random.randint(45, 190),
            "flow_bytes_per_sec": random.uniform(500, 5000),
            "flow_packets_per_sec": random.uniform(5, 50),
            "flow_iat_mean": random.uniform(100, 500),
            "flow_iat_std": random.uniform(10, 50),  # Low variance = regular intervals
            "fwd_iat_total": random.uniform(5000, 20000),
            "bwd_iat_total": random.uniform(4500, 19000)
        }

class IoTNetworkSimulator:
    """Simulates an IoT network with multiple devices."""
    
    def __init__(self):
        self.devices: List[IoTDevice] = []
        self.running = False
        self.attack_probability = 0.05  # 5% chance of attack
        self.stats = {
            'total_flows': 0,
            'benign_flows': 0,
            'attack_flows': 0,
            'ddos_attacks': 0,
            'portscan_attacks': 0,
            'bot_attacks': 0,
            'api_calls_success': 0,
            'api_calls_failed': 0
        }
        
        self._initialize_devices()
    
    def _initialize_devices(self):
        """Initialize simulated IoT devices."""
        devices_config = [
            ("dev_001", "Camera", "192.168.1.10"),
            ("dev_002", "Thermostat", "192.168.1.11"),
            ("dev_003", "Lock", "192.168.1.12"),
            ("dev_004", "Sensor", "192.168.1.13"),
            ("dev_005", "Light", "192.168.1.14"),
            ("dev_006", "Light", "192.168.1.15"),
            ("dev_007", "Speaker", "192.168.1.16"),
            ("dev_008", "Hub", "192.168.1.17"),
            ("dev_009", "TV", "192.168.1.18"),
            ("dev_010", "Garage", "192.168.1.19"),
            ("dev_011", "Plug", "192.168.1.20"),
            ("dev_012", "Plug", "192.168.1.21"),
        ]
        
        for dev_id, dev_type, ip in devices_config:
            self.devices.append(IoTDevice(dev_id, dev_type, ip))
        
        print(f"✅ Initialized {len(self.devices)} IoT devices")
    
    def send_to_api(self, traffic_data: Dict, device: IoTDevice) -> Dict:
        """Send traffic data to API for detection."""
        try:
            response = requests.post(
                API_URL,
                json=traffic_data,
                timeout=5
            )
            
            if response.status_code == 200:
                self.stats['api_calls_success'] += 1
                return response.json()
            else:
                self.stats['api_calls_failed'] += 1
                return None
                
        except requests.exceptions.RequestException as e:
            self.stats['api_calls_failed'] += 1
            return None
    
    def simulate_device_traffic(self, device: IoTDevice):
        """Simulate traffic from a single device."""
        while self.running:
            # Decide if this flow is an attack
            is_attack = random.random() < self.attack_probability
            
            if is_attack:
                # Choose attack type
                attack_type = random.choice(['ddos', 'portscan', 'bot'])
                
                if attack_type == 'ddos':
                    traffic = device.generate_ddos_traffic()
                    self.stats['ddos_attacks'] += 1
                    attack_name = "DDoS"
                elif attack_type == 'portscan':
                    traffic = device.generate_portscan_traffic()
                    self.stats['portscan_attacks'] += 1
                    attack_name = "Port Scan"
                else:
                    traffic = device.generate_bot_traffic()
                    self.stats['bot_attacks'] += 1
                    attack_name = "Bot"
                
                self.stats['attack_flows'] += 1
                
                print(f"🚨 [{device.device_id}] Generating {attack_name} attack traffic...")
            else:
                traffic = device.generate_normal_traffic()
                self.stats['benign_flows'] += 1
            
            self.stats['total_flows'] += 1
            
            # Send to API
            result = self.send_to_api(traffic, device)
            
            if result:
                if result.get('is_malicious'):
                    print(f"⚠️  [{device.device_id}] DETECTED: {result['attack_type']} "
                          f"(Confidence: {result['confidence']*100:.1f}%) "
                          f"Action: {result['recommended_action'].upper()}")
                else:
                    print(f"✅ [{device.device_id}] Normal traffic (Confidence: {result['confidence']*100:.1f}%)")
            
            # Random delay between flows (1-10 seconds)
            time.sleep(random.uniform(1, 10))
    
    def print_stats(self):
        """Print simulation statistics."""
        while self.running:
            time.sleep(30)  # Print stats every 30 seconds
            
            print("\n" + "="*70)
            print("📊 SIMULATION STATISTICS")
            print("="*70)
            print(f"Total Flows Generated:  {self.stats['total_flows']}")
            print(f"  ├─ Benign:            {self.stats['benign_flows']} ({self.stats['benign_flows']/max(self.stats['total_flows'],1)*100:.1f}%)")
            print(f"  └─ Attacks:           {self.stats['attack_flows']} ({self.stats['attack_flows']/max(self.stats['total_flows'],1)*100:.1f}%)")
            print(f"\nAttack Breakdown:")
            print(f"  ├─ DDoS:              {self.stats['ddos_attacks']}")
            print(f"  ├─ Port Scans:        {self.stats['portscan_attacks']}")
            print(f"  └─ Bot Activity:      {self.stats['bot_attacks']}")
            print(f"\nAPI Status:")
            print(f"  ├─ Successful calls:  {self.stats['api_calls_success']}")
            print(f"  └─ Failed calls:      {self.stats['api_calls_failed']}")
            print("="*70 + "\n")
    
    def start(self, num_active_devices: int = 3):
        """Start the simulation."""
        print("\n" + "="*70)
        print("🚀 STARTING IOT NETWORK SIMULATOR")
        print("="*70)
        print(f"Total devices: {len(self.devices)}")
        print(f"Active devices: {num_active_devices}")
        print(f"Attack probability: {self.attack_probability*100}%")
        print(f"API endpoint: {API_URL}")
        print("="*70 + "\n")
        
        # Check API availability
        try:
            health_check = requests.get("http://localhost:8000/health", timeout=5)
            if health_check.status_code == 200:
                print("✅ Backend API is online\n")
            else:
                print("⚠️  Backend API returned unexpected status\n")
        except:
            print("❌ WARNING: Cannot connect to backend API!")
            print("   Make sure backend is running: python main_api.py\n")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return
        
        self.running = True
        
        # Start stats printer thread
        stats_thread = threading.Thread(target=self.print_stats, daemon=True)
        stats_thread.start()
        
        # Start device simulation threads
        active_devices = random.sample(self.devices, min(num_active_devices, len(self.devices)))
        threads = []
        
        for device in active_devices:
            thread = threading.Thread(
                target=self.simulate_device_traffic,
                args=(device,),
                daemon=True
            )
            thread.start()
            threads.append(thread)
            print(f"✅ Started simulation for {device.device_id} ({device.device_type})")
        
        print(f"\n🔄 Simulation running... Press Ctrl+C to stop\n")
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping simulation...")
            self.running = False
            time.sleep(2)
            
            # Print final stats
            print("\n" + "="*70)
            print("📊 FINAL STATISTICS")
            print("="*70)
            print(f"Total Flows:     {self.stats['total_flows']}")
            print(f"Benign Flows:    {self.stats['benign_flows']}")
            print(f"Attack Flows:    {self.stats['attack_flows']}")
            print(f"  ├─ DDoS:       {self.stats['ddos_attacks']}")
            print(f"  ├─ PortScan:   {self.stats['portscan_attacks']}")
            print(f"  └─ Bot:        {self.stats['bot_attacks']}")
            print(f"API Success:     {self.stats['api_calls_success']}")
            print(f"API Failures:    {self.stats['api_calls_failed']}")
            print("="*70 + "\n")
            print("✅ Simulation stopped")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='IoT Network Traffic Simulator')
    parser.add_argument(
        '--devices',
        type=int,
        default=3,
        help='Number of active devices (default: 3)'
    )
    parser.add_argument(
        '--attack-rate',
        type=float,
        default=0.05,
        help='Attack probability 0-1 (default: 0.05 = 5%%)'
    )
    
    args = parser.parse_args()
    
    # Create and start simulator
    simulator = IoTNetworkSimulator()
    simulator.attack_probability = args.attack_rate
    simulator.start(num_active_devices=args.devices)

if __name__ == '__main__':
    main()
