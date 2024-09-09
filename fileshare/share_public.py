import argparse
import os
import asyncio
from telegram import Bot
from telegram.error import TelegramError

BOT_TOKEN = 'YOUR_BOT_TOKEN'
CHAT_ID = '@USERNAE_OF_GROUP_CHANNEL'

async def send_file(bot, file_path):
    try:
        with open(file_path, 'rb') as file:
            await bot.send_document(chat_id=CHAT_ID, document=file, caption=f'Sending {file_path}')
        print(f'Successfully sent: {file_path}')
    except TelegramError as e:
        print(f'Failed to send {file_path}. Error: {e}')
    except FileNotFoundError:
        print(f'File not found: {file_path}')

async def main(files):
    bot = Bot(token=BOT_TOKEN)
    if files and files[0] == '*':
        for filename in os.listdir('.'):
            if os.path.isfile(filename):
                await send_file(bot, filename)
    else:
        for file_path in files:
            await send_file(bot, file_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send files to a public Telegram bot.')
    parser.add_argument('files', nargs='*', help='Files to send. Use "*" to send all files in the directory.')

    args = parser.parse_args()
    asyncio.run(main(args.files))
