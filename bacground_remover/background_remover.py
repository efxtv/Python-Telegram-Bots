import os
import cv2
import numpy as np
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = 'CHANGE_ME'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome! Send me an image and I will remove its background.')

def handle_image(update: Update, context: CallbackContext) -> None:
    photo_file = update.message.photo[-1].get_file()
    filename = os.path.join('downloads', 'image.jpg')
    photo_file.download(filename)
    
    processed_image = remove_background(filename)
    
    update.message.reply_photo(photo=open(processed_image, 'rb'))

def remove_background(image_path):
    image = cv2.imread(image_path)
    
    mask = np.zeros(image.shape[:2], np.uint8)
    backgroundModel = np.zeros((1, 65), np.float64)
    foregroundModel = np.zeros((1, 65), np.float64)
    rect = (50, 50, image.shape[1] - 50, image.shape[0] - 50)
    cv2.grabCut(image, mask, rect, backgroundModel, foregroundModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    image = image * mask2[:, :, np.newaxis]

    output_path = os.path.join('downloads', 'processed_image.jpg')
    cv2.imwrite(output_path, image)

    return output_path

def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.command, handle_image))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
