import os
import base64
import hashlib
import tempfile
import glob
import re
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace this with your actual bot token
TELEGRAM_BOT_TOKEN = 'CHANGE_ME'

# If you want to use as public bot uncommnet CHAT_ID
# CHAT_ID = 'userid'

# Add bot to public Group and uncomment CHAT_ID
# CHAT_ID = '@username_group_channel'

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
    results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        result = subprocess.run(['jadx', '--no-res', '-d', temp_dir, apk_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            return "Error: jadx failed to decompile the APK."
        
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
                        message = (f"IP: {decoded_host}\n"
                                   f"Port: {decoded_port}\n"
                                   f"Join: @EFXTV")
                        results.append(message)
                    except Exception as e:
                        results.append(f"Error decoding base64 strings: {e}")
        
    return "\n\n".join(results) if results else "No IPs or Ports found."

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Send me an APK file and I'll extract the IP and port information.")

async def handle_document(update: Update, context: CallbackContext):
    file = update.message.document
    file_id = file.file_id
    file_name = file.file_name
    file_path = os.path.join(tempfile.gettempdir(), file_name)

    try:
        # Get the file object
        telegram_file = await context.bot.get_file(file_id)
        # Download the file
        await telegram_file.download_to_drive(file_path)
        # Process the APK file
        message = extract_ips_and_ports_from_apk(file_path)
        # Send the result back to the user
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Document.MimeType("application/vnd.android.package-archive"), handle_document))

    application.run_polling()

if __name__ == '__main__':
    main()

