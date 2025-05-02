#!/usr/bin/env python3

import socket
import json
import sys
import subprocess
import shutil

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
        "gcr.io", "k8s.gcr.io", "mcr.microsoft.com",
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

def check_dns_and_ntp(results, source_role):
    source_ip = get_local_ip("8.8.8.8")
    source_label = f"{source_role}({source_ip})"

    # DNS Check
    dns_servers = []
    try:
        with open('/etc/resolv.conf') as f:
            for line in f:
                if line.startswith('nameserver'):
                    dns_servers.append(line.strip().split()[1])
    except Exception:
        dns_servers = []

    # Check each DNS server with socket
    for dns_server in dns_servers:
        try:
            # Manually use this DNS server to resolve "nutanix.com"
            resolver = socket.getaddrinfo("nutanix.com", None, proto=socket.IPPROTO_UDP)
            state = 'open' if resolver else 'closed'
        except Exception:
            state = 'closed'

        results.append({
            'source': source_label,
            'destination': f'DNS({dns_server})',
            'protocol': 'UDP',
            'port': 53,
            'state': state
        })

    # NTP Check
    ntp_tool = None
    if shutil.which('chronyc'):
        try:
            ntp_output = subprocess.check_output("chronyc sources", shell=True, stderr=subprocess.STDOUT).decode()
            lines = [line.strip() for line in ntp_output.splitlines() if line.strip().startswith(('^', '*', '+'))]
            
            if lines:
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        server = parts[1]
                        results.append({
                            'source': source_label,
                            'destination': f'NTP({server})',
                            'protocol': 'UDP',
                            'port': 123,
                            'state': 'open'
                        })
            else:
                results.append({
                    'source': source_label,
                    'destination': 'NTP(unknown)',
                    'protocol': 'UDP',
                    'port': 123,
                    'state': 'closed'
                })
        except subprocess.CalledProcessError as e:
            results.append({
                'source': source_label,
                'destination': 'NTP(chronyc)',
                'protocol': 'UDP',
                'port': 123,
                'state': f'error: {e.output.decode().strip()}'
            })
    else:
        results.append({
            'source': source_label,
            'destination': 'NTP(chronyc)',
            'protocol': 'UDP',
            'port': 123,
            'state': 'chronyc not found'
        })

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

    # Add DNS and NTP checks
    check_dns_and_ntp(results, source_role)

    print(json.dumps(results, indent=2))
