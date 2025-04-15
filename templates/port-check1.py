#!/usr/bin/env python3

import socket
import json
import sys
import subprocess

def get_local_ip(dest_host):
    """Get the local IP address used to reach the destination"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((dest_host, 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"

def check_tcp(host, port, timeout=5):
    """Check TCP port connectivity"""
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

def check_udp(host, port, timeout=4):
    """Just send UDP packet and return nothing"""
    try:
        cmd = f'echo -n "{port} is open" | nc -u -w1 {host} {port}'
        subprocess.run(
            cmd,
            shell=True,
            timeout=timeout
        )
    except Exception:
        pass  # Suppress all exceptions


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: port_check.py <dest:proto:port,...> [<dest:proto:port,...> ...]")
        sys.exit(1)

    results = []

    for arg in sys.argv[1:]:
        try:
            destination, port_specs_str = arg.split(':', 1)
            port_specs = port_specs_str.split(',')

            source = get_local_ip(destination)

            for spec in port_specs:
                try:
                    proto, port = spec.split(':')
                    port = int(port)

                    if proto.lower() == 'tcp':
                        state = check_tcp(destination, port)
                        results.append({
                            'source': source,
                            'destination': destination,
                            'protocol': 'TCP',
                            'port': port,
                            'state': state
                        })
                    elif proto.lower() == 'udp':
                        check_udp(destination, port)
                        # No result recording for UDP
                    else:
                        results.append({
                            'destination': destination,
                            'protocol': proto,
                            'port': port,
                            'state': 'invalid-protocol'
                        })
                except ValueError:
                    results.append({
                        'destination': destination,
                        'error': f"Invalid port spec: {spec}"
                    })
        except ValueError:
            results.append({
                'error': f"Invalid destination format: {arg}"
            })

    print(json.dumps(results, indent=2))
