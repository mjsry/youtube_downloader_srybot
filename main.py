from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters, InlineQueryHandler, CallbackQueryHandler
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
        #'cookies': cookies_path,
        #'proxy': 'PvMHOBNAzQ:DFTbCPY40E@77.93.143.103:34819',
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
            seen_height = set()
            formats = quality_formats(link)
            for format in formats :
                height = format.get('height')
                if height and height not in seen_height and int(height) >= 360:
                    btn_text = f'{format['height']}p'
                    btn_data = format['format_id']
                    keys.append([InlineKeyboardButton(text=btn_text,callback_data=btn_data)])
                    seen_height.add(height)

            markup = InlineKeyboardMarkup(keys)
            user_state[user_id] = {
                'state': 'select_quality',
                'link': link
            }

            txt = 'کیفتی که میخوای رو انتخاب کن'
            await update.message.reply_text(txt, reply_markup=markup)

        except Exception as e:
            print(f'خطای غیرمنتظره: {e}')
            await update.message.reply_text('یه مشکلی پیش اومده دوباره امتحان کن')

async def quality_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_chat.id
    data = query.data
    if user_id not in user_state or user_state[user_id]['state'] != 'select_quality':
        await query.edit_message_text('یه مشکلی پیش اومده دوباره امتحان کن')
        return

    link = user_state[user_id]['link']
    await query.edit_message_text('درحال دانلود ویدیوتم...')

    ydl_opts = {
        'format': data,
        'outtmpl': f'{user_id}_%(title)s.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl :
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info)

        await context.bot.send_video(chat_id=user_id, video=open(file_path, 'rb'))
        os.remove(file_path)

    except Exception as e :
        txt = 'یه مشکلی موقع دانلود پیش اومد دوباره امتحان کن'
        await context.bot.send_message(chat_id=user_id, text=txt)

    user_state.pop(user_id, None)


def main():
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.Text('download'), download))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloading))
    app.add_handler(CallbackQueryHandler(quality_selected))

    app.run_polling()

main()