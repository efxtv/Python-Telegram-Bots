import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import nmap

bot = telegram.Bot(token='YOUR_TOKEN')
updater = Updater('YOUR_TOKEN', use_context=True)
dispatcher = updater.dispatcher

nm = nmap.PortScanner()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome there ! Please pass the IP or Host.")

def scan(update, context):
    try:
        target = update.message.text

        nm.scan(hosts=target, arguments='-T4 -F')

        scan_result = ''
        for host in nm.all_hosts():
            scan_result += f"Host: {host}\n"
            for proto in nm[host].all_protocols():
                ports = nm[host][proto].keys()
                for port in ports:
                    port_info = nm[host][proto][port]
                    scan_result += f"Port: {port} State: {port_info['state']} Service: {port_info['name']}"
                    if 'product' in port_info:
                        scan_result += f", Version: {port_info['product']}"
                    scan_result += "\n"

        context.bot.send_message(chat_id=update.effective_chat.id, text=scan_result)
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {str(e)}")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

message_handler = MessageHandler(Filters.text & ~Filters.command, scan)
dispatcher.add_handler(message_handler)

updater.start_polling()
updater.idle()
