import argparse
import socket
import json
import re
import sys

def check_tcp(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=5):
            return 'open'
    except (socket.timeout, socket.error):
        return 'closed'

def main():
    parser = argparse.ArgumentParser(description='Check port connectivity for each host.')
    parser.add_argument('--source_ip', type=str, required=True, help='Source IP address')
    args = parser.parse_args()

    # Read hosts from stdin
    hosts = sys.stdin.read().strip().splitlines()

    ports = [8843, 6443]
    results = []

    for host_entry in hosts:
        match = re.match(r'^(.*)\((.*)\)$', host_entry.strip())
        if not match:
            continue  # Skip malformed lines

        hostname, ip = match.groups()

        for port in ports:
            state = check_tcp(ip, port)
            results.append({
                'source': f'management({args.source_ip})',
                'destination': f'{hostname}({ip})',
                'protocol': 'TCP',
                'port': port,
                'state': state
            })

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
