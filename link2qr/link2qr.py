import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import qrcode
from io import BytesIO

TELEGRAM_TOKEN = 'CHANGE_ME_TOKEN'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Give me a link 🙂️")

async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(user_input)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(buffer, filename='qr.png'))
    await update.message.reply_text("Here is your QR code. You can scan it at scanqr.org")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()

