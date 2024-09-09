import sys
import os
import subprocess
import tempfile
import base64
import glob
import hashlib
import re

# Work on crax RAT APK files only
# How to setup
# Install Java11
# sudo apt install openjdk-11-jdk
# cd;git clone https://github.com/skylot/jadx.git
# cd jadx
# ./gradlew dist
# cd ~/jadx/build/jadx/bin
# sudo ln -s $PWD/jadx /usr/bin/jadx

def check_jadx_installed():
    try:
        subprocess.run(['jadx', '-v'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Error: 'jadx' is not installed or not found in your PATH.")
        print("Please install jadx from https://github.com/skylot/jadx.git before running this script.")
        sys.exit(1)

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def decode_base64(encoded_str):
    padded_str = encoded_str + '=' * (-len(encoded_str) % 4)
    decoded_bytes = base64.b64decode(padded_str)
    return decoded_bytes.decode('utf-8')

def extract_ips_and_ports_from_apk(apk_path):
    md5_hash = calculate_md5(apk_path)
    print(f"Processing {apk_path}")
    
    print("[*] Working...")
    with tempfile.TemporaryDirectory() as temp_dir:
        result = subprocess.run(['jadx', '--no-res', '-d', temp_dir, apk_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            print("Error: jadx failed to decompile the APK.")
            return
        
        print("[*] Finding IP Addresses and Ports...")
        java_files = glob.glob(os.path.join(temp_dir, '**', '*.java'), recursive=True)
        client_host_pattern = re.compile(r'public\s+static\s+String\s+ClientHost\s*=\s*"([A-Za-z0-9+/=]+)"')
        client_port_pattern = re.compile(r'public\s+static\s+String\s+ClientPort\s*=\s*"([A-Za-z0-9+/=]+)"')

        for file_path in java_files:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                host_matches = client_host_pattern.findall(content)
                port_matches = client_port_pattern.findall(content)
                
                if host_matches and port_matches:
                    host_base64 = host_matches[0]
                    port_base64 = port_matches[0]
                    
                    try:
                        decoded_host = decode_base64(host_base64)
                        decoded_port = decode_base64(port_base64)
                        print(f"[{md5_hash}]: IP = {decoded_host}, Port = {decoded_port}\n")
                    except Exception as e:
                        print(f"Error decoding base64 strings: {e}")
                        continue

def main():
    check_jadx_installed()

    if len(sys.argv) != 2:
        print('Usage: python craxs.py /path/to/apk/folder_or_file')
        sys.exit(1)
    
    path = sys.argv[1]
    
    if os.path.isfile(path):
        # If a single file is provided
        extract_ips_and_ports_from_apk(path)
    elif os.path.isdir(path):
        # If a directory is provided
        files = glob.glob(os.path.join(path, '*.apk'))
        for file_path in files:
            if os.path.isfile(file_path):
                extract_ips_and_ports_from_apk(file_path)
    else:
        print('Invalid path. It should be a directory or a file.')
        sys.exit(1)

if __name__ == '__main__':
    main()
