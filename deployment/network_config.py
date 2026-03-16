import socket
import subprocess
import platform
import os

def get_network_info():
    """Get network information for deployment"""
    
    # Get local IP address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"
    
    # Get computer name
    computer_name = platform.node()
    
    # Get WiFi network name (Windows)
    wifi_name = "Unknown"
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'All User Profile' in line:
                        wifi_name = line.split(':')[1].strip()
                        break
    except:
        pass
    
    return {
        'local_ip': local_ip,
        'computer_name': computer_name,
        'wifi_network': wifi_name,
        'platform': platform.system()
    }

def configure_firewall():
    """Configure Windows firewall to allow Flask app"""
    if platform.system() != "Windows":
        return False
    
    try:
        # Add firewall rule for Flask app
        cmd = [
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            'name=Indoor Navigation Flask App',
            'dir=in', 'action=allow', 'protocol=TCP', 'localport=5000'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def generate_access_instructions(network_info):
    """Generate instructions for accessing the app"""
    
    instructions = f"""
========================================
INDOOR NAVIGATION SYSTEM - ACCESS GUIDE
========================================

Network Information:
- Computer: {network_info['computer_name']}
- Local IP: {network_info['local_ip']}
- WiFi Network: {network_info['wifi_network']}
- Platform: {network_info['platform']}

Access URLs:
- Local access: http://127.0.0.1:5000
- Network access: http://{network_info['local_ip']}:5000

QR Code URLs (for entrances):
- Entrance 1: http://{network_info['local_ip']}:5000/?entrance=1
- Entrance 2: http://{network_info['local_ip']}:5000/?entrance=2
- Entrance 3: http://{network_info['local_ip']}:5000/?entrance=3
- Entrance 4: http://{network_info['local_ip']}:5000/?entrance=4
- Entrance 5: http://{network_info['local_ip']}:5000/?entrance=5

Deployment Instructions:
1. Ensure all devices connect to the same WiFi network: {network_info['wifi_network']}
2. Start the server with: python app.py
3. Print QR codes from the 'qr_codes' folder
4. Place QR codes at the respective entrances
5. Users scan QR codes to start navigation

Troubleshooting:
- If mobile devices can't access the server:
  * Check Windows Firewall settings
  * Ensure all devices are on the same WiFi network
  * Try accessing http://{network_info['local_ip']}:5000 directly
  * Disable Windows Firewall temporarily for testing

For college WiFi deployment:
1. Connect your computer to college WiFi
2. Note the assigned IP address
3. Update QR codes with the new IP address
4. Ensure the college network allows device-to-device communication

========================================
    """
    
    return instructions

def save_config_file(network_info):
    """Save network configuration to file"""
    config_content = f"""# Network Configuration for Indoor Navigation System
# Generated automatically - do not edit manually

LOCAL_IP = "{network_info['local_ip']}"
COMPUTER_NAME = "{network_info['computer_name']}"
WIFI_NETWORK = "{network_info['wifi_network']}"
PLATFORM = "{network_info['platform']}"

# Flask Configuration
FLASK_HOST = LOCAL_IP
FLASK_PORT = 5000
FLASK_DEBUG = True

# QR Code Base URL
QR_BASE_URL = f"http://{{LOCAL_IP}}:{{FLASK_PORT}}"
"""
    
    with open('network_config.txt', 'w') as f:
        f.write(config_content)

def main():
    print("Configuring network settings for Indoor Navigation System...")
    
    # Get network information
    network_info = get_network_info()
    
    # Generate and display instructions
    instructions = generate_access_instructions(network_info)
    print(instructions)
    
    # Save configuration
    save_config_file(network_info)
    
    # Configure firewall (Windows only)
    if platform.system() == "Windows":
        print("Configuring Windows Firewall...")
        if configure_firewall():
            print("✓ Firewall rule added successfully")
        else:
            print("⚠ Failed to add firewall rule. You may need to run as administrator.")
            print("  Manual step: Allow port 5000 in Windows Firewall")
    
    # Save instructions to file
    with open('deployment_instructions.txt', 'w') as f:
        f.write(instructions)
    
    print(f"\nConfiguration saved to:")
    print(f"- network_config.txt")
    print(f"- deployment_instructions.txt")
    print(f"\nReady to deploy! Run 'python app.py' to start the server.")

if __name__ == "__main__":
    main()