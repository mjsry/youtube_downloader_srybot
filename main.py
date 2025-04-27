from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters, InlineQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Bot
import os
import yt_dlp

bot_token = '7884166478:AAEOxwa2H7SQ03C12AQZq0S3mJEUgq0XIVg'
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keys = [
        [KeyboardButton('download')]
    ]
    keymarkup = ReplyKeyboardMarkup(
        keyboard=keys,
        resize_keyboard=True
    )

    txt = '''
سلام خوش اومدی :)
از طریق دکمه دانلود ویدوت رو با هر زیرنویسی که میخوای دانلود کن
    '''
    await update.message.reply_text(txt, reply_markup=keymarkup)

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_state[user_id] = 'downloading'

    txt = 'لینک ویدیو رو بفرست!'
    await update.message.reply_text(txt)

def quality_formats(link):
        cookies_path = os.path.join(os.getcwd(), 'cookies.txt')
        ydl_opts = {
        'cookies': cookies_path,
        #'proxy': 'PvMHOBNAzQ:DFTbCPY40E@77.93.143.103:34819',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            formats = info.get('formats', [])
            return formats


async def downloading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_input = update.effective_message.text.strip()

    if user_state[user_id] == 'downloading' :
        try :
            link = user_input
            keys = []
            formats = quality_formats(link)
            for format in formats :
                if format.get('height'):
                    btn_text = f'{format['height']}p'
                    btn_data = format['format_id']
                    keys.append([InlineKeyboardButton(text=btn_text,callback_data=btn_data)])

            markup = InlineKeyboardMarkup(keys)
            user_state[user_id] = 'select_quality'

            txt = 'کیفتی که میخوای رو انتخاب کن'
            await update.message.reply_text(txt, reply_markup=markup)

        except Exception as e:
            print(f'خطای غیرمنتظره: {e}')
            await update.message.reply_text('یه مشکلی پیش اومده دوباره امتحان کن')

def main():
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.Text('download'), download))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloading))

    app.run_polling()

main()