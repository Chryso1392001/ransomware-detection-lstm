#!/usr/bin/env python3
"""
Forward ransomware alerts to Wazuh SIEM
Detection Server (192.168.81.142) → Wazuh (192.168.81.128)
"""

import json
import socket
import os
from datetime import datetime

class WazuhAlertForwarder:
    def __init__(self):
        self.wazuh_server = '192.168.81.128'
        self.syslog_port = 514
        self.json_log = '/var/log/ransomware/detector.json'
        self.text_log = '/var/log/ransomware/alerts.log'
    
    def send_alert(self, alert_data):
        """Send alert to Wazuh"""
        
        success = 0
        
        # Method 1: JSON log
        try:
            with open(self.json_log, 'a') as f:
                f.write(json.dumps(alert_data) + '\n')
            print(f"✓ JSON log: {self.json_log}")
            success += 1
        except Exception as e:
            print(f"✗ JSON log failed: {e}")
        
        # Method 2: Text log
        try:
            msg = f"{alert_data.get('timestamp')} [{alert_data.get('severity')}] {alert_data.get('verdict')}: {alert_data.get('source_ip')} → {alert_data.get('destination_ip')} (Confidence: {alert_data.get('confidence')})"
            with open(self.text_log, 'a') as f:
                f.write(msg + '\n')
            print(f"✓ Text log: {self.text_log}")
            success += 1
        except Exception as e:
            print(f"✗ Text log failed: {e}")
        
        # Method 3: Syslog
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(json.dumps(alert_data).encode('utf-8'), 
                       (self.wazuh_server, self.syslog_port))
            sock.close()
            print(f"✓ Syslog: {self.wazuh_server}:{self.syslog_port}")
            success += 1
        except Exception as e:
            print(f"✗ Syslog failed: {e}")
        
        return success > 0

if __name__ == '__main__':
    # Create log directory
    os.makedirs('/var/log/ransomware', exist_ok=True)
    
    forwarder = WazuhAlertForwarder()
    
    test_alert = {
        'timestamp': datetime.now().isoformat(),
        'alert_id': 'TEST-001',
        'verdict': 'RANSOMWARE',
        'severity': 'CRITICAL',
        'confidence': '94.5%',
        'source_ip': '192.168.81.100',
        'destination_ip': '10.0.0.50',
        'protocol': 'SMB',
        'model_scores': {'v1': '94.5%', 'v2': '87.2%'},
        'triggered_models': ['V1', 'V2'],
        'threat_type': 'Ryuk-like ransomware',
        'recommended_action': 'IMMEDIATE: Isolate host'
    }
    
    print("="*70)
    print("TESTING WAZUH ALERT FORWARDER")
    print("="*70)
    print()
    
    if forwarder.send_alert(test_alert):
        print()
        print("✅ Alert sent successfully!")
        print(f"Check Wazuh dashboard: http://192.168.81.128")
    else:
        print()
        print("⚠️  Some methods failed (check errors above)")
    
    print("="*70)
