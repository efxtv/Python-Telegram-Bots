import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import datetime
import time

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

def start(update, context):
    update.message.reply_text("Welcome to EFXTV Age Calculator Bot!")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide your date of birth in DD/MM/YYYY format?")
    
def get_dob(update, context):
    dob = update.message.text
    context.user_data['dob'] = dob
    time.sleep(1)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide your time of birth in HH:MM format?")
    
def get_tob(update, context):
    tob = update.message.text
    context.user_data['tob'] = tob
    time.sleep(1)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you. Please wait...")
    time.sleep(1)
    calculate_age(update, context)
    
def calculate_age(update, context):
    try:
        dob_str = context.user_data.get('dob')
        tob_str = context.user_data.get('tob')
        
        if not dob_str or not tob_str:
            raise ValueError("Date of birth or time of birth is missing.")
        
        dob = datetime.datetime.strptime(dob_str, '%d/%m/%Y')
        tob = datetime.datetime.strptime(tob_str, '%H:%M')
        
        now = datetime.datetime.now()
        age = now - dob
        
        total_hours = age.total_seconds() / 3600
        total_minutes = age.total_seconds() / 60
        total_seconds = age.total_seconds()
        age_in_months = (now.year - dob.year) * 12 + now.month - dob.month
        age_in_years = age_in_months // 12
        remaining_months = age_in_months % 12
        
        age_in_days = age.days
        
        day_of_birth = dob.strftime("%A")
        
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"You have lived total hours: {total_hours:.2f}")
        time.sleep(1)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"You have lived total minutes: {total_minutes:.2f}")
        time.sleep(1)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"You have lived total seconds: {total_seconds:.2f}")
        time.sleep(1)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your age in months: {age_in_months}")
        time.sleep(1)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your age in years: {age_in_years}Y {remaining_months}M {age_in_days}D")
        time.sleep(1)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"The day you were born on: {day_of_birth}")
        time.sleep(1)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please follow us on @python_telegram_bot_source_codes")
        time.sleep(1)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Kindly pass '/start' to start again")
    except ValueError as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
    finally:
        context.user_data.clear()
        
updater = Updater(TOKEN, use_context=True)

dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.regex(r'^\d{2}/\d{2}/\d{4}$'), get_dob))
dp.add_handler(MessageHandler(Filters.regex(r'^\d{2}:\d{2}$'), get_tob))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, calculate_age))

updater.start_polling()
updater.idle()
