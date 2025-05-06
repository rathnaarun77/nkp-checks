import argparse
import socket
import json
import sys

def get_local_ip():
    try:
        # Connect to a dummy external address to determine the correct local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"  # Fallback

def check_tcp(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=5):
            return 'open'
    except (socket.timeout, socket.error):
        return 'closed'

def main():
    parser = argparse.ArgumentParser(description='Check TCP port 443 connectivity to specified destinations.')
    parser.add_argument('--source_role', type=str, required=True, help='Source role (e.g., management)')
    args = parser.parse_args()

    source_ip = get_local_ip()

    input_line = sys.stdin.read().strip()
    if not input_line:
        print("No destinations provided.", file=sys.stderr)
        sys.exit(1)

    destinations = input_line.split(',')
    port = 443
    results = []

    for dest in destinations:
        if ':' not in dest:
            continue  # skip malformed entry

        role, ip = dest.split(':', 1)
        ip = ip.strip()

        state = check_tcp(ip, port)
        results.append({
            'source': f'{args.source_role}({source_ip})',
            'destination': f'{role}({ip})',
            'protocol': 'TCP',
            'port': port,
            'state': state
        })

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()