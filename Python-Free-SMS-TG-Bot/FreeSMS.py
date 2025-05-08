import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import requests

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

ENTER_NUMBER, ENTER_MESSAGE = range(2)

TEXTBELT_API_URL = "https://textbelt.com/text"
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

TOKEN = 'your_telegram_bot_token'

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\! Welcome to the Free SMS Bot\. '
        'I can help you send SMS messages to any number\. '
        'Use /send to start sending an SMS\.'
    )

def send_sms_command(update: Update, context: CallbackContext) -> None:
    """Start the SMS sending process."""
    update.message.reply_text(
        'Please enter the phone number you want to send the SMS to '
        '(include country code, e.g., +1234567890):'
    )
    return ENTER_NUMBER

def receive_number(update: Update, context: CallbackContext) -> int:
    """Store the number and ask for the message."""
    phone_number = update.message.text
    context.user_data['phone_number'] = phone_number
    
    update.message.reply_text(
        f'Great! You want to send an SMS to {phone_number}. '
        'Now please enter your message:'
    )
    return ENTER_MESSAGE

def receive_message(update: Update, context: CallbackContext) -> int:
    """Send the SMS and show the result."""
    message = update.message.text
    phone_number = context.user_data['phone_number']
    
    update.message.reply_text(
        f'Sending your message to {phone_number}...'
    )
    
    if TWILIO_ENABLED:
        success, response = send_via_twilio(phone_number, message)
    else:
        success, response = send_via_textbelt(phone_number, message)
    
    if success:
        update.message.reply_text(
            f'✅ SMS sent successfully to {phone_number}!\n'
            f'Response: {response}'
        )
    else:
        update.message.reply_text(
            f'❌ Failed to send SMS to {phone_number}\n'
            f'Error: {response}\n'
            'Please try again later or use a different number.'
        )
    

def send_via_textbelt(phone_number: str, message: str) -> tuple:
    """Send SMS using TextBelt API."""
    try:
        response = requests.post(TEXTBELT_API_URL, {
            'phone': phone_number,
            'message': message,
        }).json()
        
        if response.get('success'):
            return True, "TextBelt: Message sent successfully"
        else:
            return False, f"TextBelt: {response.get('error', 'Unknown error')}"
    except Exception as e:
        return False, f"TextBelt API error: {str(e)}"

def send_via_twilio(phone_number: str, message: str) -> tuple:
    """Send SMS using Twilio API (requires trial account)."""
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        return True, f"Twilio: Message SID {message.sid}, Status: {message.status}"
    except Exception as e:
        return False, f"Twilio error: {str(e)}"

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the current operation."""
    update.message.reply_text('Operation cancelled.')

def main() -> None:
    """Start the bot."""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('send', send_sms_command)],
        states={
            ENTER_NUMBER: [MessageHandler(Filters.text & ~Filters.command, receive_number)],
            ENTER_MESSAGE: [MessageHandler(Filters.text & ~Filters.command, receive_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
