#!/usr/bin/env python3

import socket
import json
import sys
import subprocess

def get_local_ip(dest_host):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((dest_host, 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"

def check_tcp(host, port, timeout=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return 'open'
    except socket.timeout:
        return 'timeout'
    except ConnectionRefusedError:
        return 'closed'
    except Exception as e:
        return f'error: {str(e)}'
    finally:
        s.close()

def check_udp(host, port, timeout=2):
    try:
        cmd = f'echo -n "{port} is open" | nc -u -w1 {host} {port}'
        subprocess.run(cmd, shell=True, timeout=timeout)
    except Exception:
        pass

def check_common_registries(results, source_role, source_ip):
    registries = [
        "docker.io", "gcr.io", "k8s.gcr.io", "mcr.microsoft.com",
        "nvcr.io", "quay.io", "us.gcr.io", "registry.k8s.io",
        "ghcr.io", "github.io", "github.com",
        "chatbot.api.d2iq.com", "auth.api.d2iq.com"
    ]
    for registry in registries:
        state = check_tcp(registry, 443)
        results.append({
            'source': f'{source_role}({source_ip})',
            'destination': f'{registry}',
            'protocol': 'TCP',
            'port': 443,
            'state': state
        })

def parse_input_file(file_path, source_role):
    checks = []
    current_role = None

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.endswith(':'):
                current_role = line[:-1].strip()
                continue

            if current_role == source_role:
                parts = line.split(':')
                if len(parts) != 4:
                    checks.append({'error': f'Invalid line format: {line}'})
                    continue

                dest_role, dest_host, proto, port = parts
                try:
                    checks.append({
                        'destination_role': dest_role,
                        'destination': dest_host,
                        'protocol': proto.lower(),
                        'port': int(port)
                    })
                except ValueError:
                    checks.append({'error': f'Invalid port number: {port}'})
    return checks

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: port_check.py <input_file> <source_role>")
        sys.exit(1)

    input_file = sys.argv[1]
    source_role = sys.argv[2]

    checks = parse_input_file(input_file, source_role)
    results = []

    for check in checks:
        if 'error' in check:
            results.append(check)
            continue

        destination = check['destination']
        dest_label = f"{check['destination_role']}({destination})"
        proto = check['protocol']
        port = check['port']
        source_ip = get_local_ip(destination)
        source_label = f"{source_role}({source_ip})"

        if proto == 'tcp':
            state = check_tcp(destination, port)
            results.append({
                'source': source_label,
                'destination': dest_label,
                'protocol': 'TCP',
                'port': port,
                'state': state
            })
        elif proto == 'udp':
            check_udp(destination, port)
            # Optionally add a result for UDP (currently suppressed)
        else:
            results.append({
                'source': source_label,
                'destination': dest_label,
                'protocol': proto,
                'port': port,
                'state': 'invalid-protocol'
            })

    # Add common registry checks
    source_ip = get_local_ip("docker.io")
    check_common_registries(results, source_role, source_ip)

    print(json.dumps(results, indent=2))
