#!/usr/bin/env python3

import sys
import re
import json

LOG_FILE = "/tmp/netcat-listeners.log"  # Fixed log file path

def parse_log_file():
    try:
        with open(LOG_FILE, 'r') as f:
            content = f.read()
        return re.findall(r'(\d+)\s+is open', content)
    except FileNotFoundError:
        return []

def create_json_entries(ports_found, expected_ports, source_ip, destination_ip):
    entries = []
    for port in expected_ports:
        state = "open" if str(port) in ports_found else "closed"
        entries.append({
            "source": source_ip,
            "destination": destination_ip,
            "protocol": "UDP",
            "port": int(port),
            "state": state
        })
    return entries

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: format_netcat_output.py <source_ip> <destination_ip> <port1,port2,...>")
        sys.exit(1)

    source = sys.argv[1]
    destination = sys.argv[2]
    expected_ports = [int(p) for p in sys.argv[3].split(',')]

    ports_found = parse_log_file()
    json_output = create_json_entries(ports_found, expected_ports, source, destination)

    print(json.dumps(json_output, indent=2))
