#!/usr/bin/env python
import socket
import requests
import platform
import sys
import json
import time
import subprocess
import os

def get_network_info():
    print("\n=== SYSTEM INFORMATION ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    print("\n=== NETWORK INTERFACES ===")
    hostname = socket.gethostname()
    print(f"Hostname: {hostname}")
    
    try:
        # Get primary IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # This doesn't actually establish a connection
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
        print(f"Primary IP (interface with internet access): {primary_ip}")
    except Exception as e:
        print(f"Could not determine primary IP: {e}")
    
    # Get all IPs
    print("\nAll network interfaces:")
    all_ips = []
    try:
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ip not in all_ips:
                all_ips.append(ip)
                print(f"  {ip}")
    except Exception as e:
        print(f"Error getting all IPs: {e}")

def test_local_server():
    print("\n=== TESTING LOCAL FLASK SERVER ===")
    urls_to_test = [
        "http://localhost:8000/api/health",
        "http://127.0.0.1:8000/api/health",
        "http://0.0.0.0:8000/api/health",
    ]
    
    # Add all local IPs
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        urls_to_test.append(f"http://{local_ip}:8000/api/health")
        
        # Try to get all local IPs
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ":" not in ip:  # Skip IPv6 for simplicity
                urls_to_test.append(f"http://{ip}:8000/api/health")
    except Exception as e:
        print(f"Error getting additional IPs for testing: {e}")
    
    # Add Android emulator special IP
    urls_to_test.append("http://10.0.2.2:8000/api/health")
    
    # Remove duplicates
    urls_to_test = list(set(urls_to_test))
    
    for url in urls_to_test:
        print(f"\nTesting: {url}")
        try:
            start_time = time.time()
            response = requests.get(url, timeout=3)
            elapsed = time.time() - start_time
            print(f"  Status: {response.status_code}")
            print(f"  Time: {elapsed:.2f}s")
            if response.status_code == 200:
                print(f"  Response: {json.dumps(response.json(), indent=2)[:200]}...")
            else:
                print(f"  Response: {response.text[:100]}")
        except requests.exceptions.ConnectTimeout:
            print("  Result: Connection timed out")
        except requests.exceptions.ConnectionError as e:
            print(f"  Result: Connection error: {e}")
        except Exception as e:
            print(f"  Result: Error: {e}")

def check_firewall():
    print("\n=== CHECKING FIREWALL SETTINGS ===")
    try:
        if platform.system() == "Windows":
            # Check if port 8000 is listening
            print("Checking if port 8000 is open and listening:")
            result = subprocess.run(["netstat", "-an", "-p", "TCP"], capture_output=True, text=True)
            if ":8000" in result.stdout:
                print("  Port 8000 is LISTENING")
                # Extract the line with port 8000
                for line in result.stdout.splitlines():
                    if ":8000" in line:
                        print(f"  {line.strip()}")
            else:
                print("  Port 8000 is NOT listening")
                
            # Check Windows firewall status
            print("\nChecking Windows Firewall status:")
            firewall = subprocess.run(["netsh", "advfirewall", "show", "currentprofile"], 
                                     capture_output=True, text=True)
            if firewall.returncode == 0:
                for line in firewall.stdout.splitlines():
                    if "State" in line:
                        print(f"  {line.strip()}")
                    if "Firewall Policy" in line:
                        print(f"  {line.strip()}")
        else:
            # For Linux/Mac
            print("Checking if port 8000 is open and listening:")
            result = subprocess.run(["lsof", "-i", ":8000"], capture_output=True, text=True)
            print(result.stdout)
    except Exception as e:
        print(f"Could not check firewall settings: {e}")

def main():
    print("=== NETWORK DIAGNOSTICS TOOL ===")
    print("This tool helps diagnose network connectivity issues with the Flask server")
    
    get_network_info()
    test_local_server()
    check_firewall()
    
    print("\n=== DIAGNOSTIC RESULTS ===")
    print("If the server is running but cannot be reached from your mobile device:")
    print("1. Check that your mobile device is on the same WiFi network")
    print("2. Ensure Windows Firewall is not blocking port 8000")
    print("3. Try adding a firewall rule: netsh advfirewall firewall add rule name=\"Flask Server\" dir=in action=allow protocol=TCP localport=8000")
    print("4. If using an emulator, make sure it can access the host machine (10.0.2.2 is the special IP)")
    print("5. Try running the Flask server with administrator privileges")

if __name__ == "__main__":
    main() 