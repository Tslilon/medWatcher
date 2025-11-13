#!/usr/bin/env python3
"""
Network Setup Checker for Harrison's Watch App
Run this to find your Mac's IP address for the Watch app
"""

import socket
import subprocess
import sys
import requests
from pathlib import Path

def get_local_ip():
    """Get the Mac's local IP address"""
    try:
        # Try to get IP from en0 (WiFi)
        result = subprocess.run(['ipconfig', 'getifaddr', 'en0'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        
        # Fallback method
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return None

def check_api_running(ip):
    """Check if the API is running and accessible"""
    try:
        response = requests.get(f"http://{ip}:8000/health", timeout=2)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None

def check_firewall():
    """Check if firewall might be blocking"""
    try:
        result = subprocess.run(['sudo', 'pfctl', '-s', 'info'], 
                              capture_output=True, text=True)
        return "Enabled" in result.stdout
    except:
        return None

def main():
    print("=" * 60)
    print("🏥 HARRISON'S WATCH APP - NETWORK SETUP CHECKER")
    print("=" * 60)
    print()
    
    # Step 1: Get IP
    print("📡 Step 1: Finding your Mac's IP address...")
    ip = get_local_ip()
    if ip:
        print(f"   ✅ Found: {ip}")
        print()
    else:
        print("   ❌ Could not determine IP address")
        print("   Try running: ipconfig getifaddr en0")
        sys.exit(1)
    
    # Step 2: Check API
    print("🔍 Step 2: Checking if API server is running...")
    is_running, health_data = check_api_running(ip)
    if is_running:
        print(f"   ✅ API is running and accessible!")
        print(f"   📊 Status: {health_data.get('status', 'unknown')}")
        print(f"   📚 Documents: {health_data.get('vector_store_count', 0)}")
        print()
    else:
        print("   ⚠️  API server not responding")
        print("   Make sure the API is running:")
        print("   cd \"/Users/maayan/medicinal rag/backend\"")
        print("   source venv/bin/activate")
        print("   python main.py")
        print()
    
    # Step 3: Configuration
    print("⚙️  Step 3: Watch App Configuration")
    print("=" * 60)
    print()
    print("In your Xcode project, update APIClient.swift:")
    print()
    print("   📝 Change this line:")
    print(f'   private let baseURL = "http://{ip}:8000"')
    print()
    print("=" * 60)
    print()
    
    # Step 4: Testing
    print("🧪 Step 4: Test from iPhone")
    print("=" * 60)
    print()
    print("Before building the Watch app, test connectivity:")
    print()
    print("Option A - Safari on iPhone:")
    print(f"   Open: http://{ip}:8000/health")
    print()
    print("Option B - Shortcuts app on iPhone:")
    print(f"   1. Create new shortcut")
    print(f"   2. Add 'Get contents of URL'")
    print(f"   3. Enter: http://{ip}:8000/api/search")
    print(f"   4. Method: POST")
    print(f"   5. Add JSON body with query")
    print()
    print("=" * 60)
    print()
    
    # Summary
    if is_running:
        print("✅ ALL CHECKS PASSED - Ready to build Watch app!")
    else:
        print("⚠️  START THE API SERVER FIRST")
    print()
    print("Next steps:")
    print("1. Open WATCH_APP_GUIDE.md")
    print("2. Follow the Xcode setup instructions")
    print("3. Update the IP address in APIClient.swift")
    print("4. Build and run on your Watch")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()

