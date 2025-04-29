from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import os
import yt_dlp

bot_token = '7884166478:AAEOxwa2H7SQ03C12AQZq0S3mJEUgq0XIVg'  # امنیتی: توکن رو روی گیت نذار
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
    await update.message.reply_text('لینک ویدیو رو بفرست!')

def quality_formats(link):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        return info.get('formats', [])

async def downloading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_input = update.effective_message.text.strip()

    if user_state.get(user_id) == 'downloading':
        try:
            link = user_input
            keys = []
            seen_height = set()
            formats = quality_formats(link)
            for format in formats:
                height = format.get('height')
                if height and height not in seen_height and int(height) >= 360 and format.get('ext') == 'mp4':
                    btn_text = f"{height}p"
                    btn_data = format['format_id']
                    keys.append([InlineKeyboardButton(text=btn_text, callback_data=btn_data)])
                    seen_height.add(height)

            markup = InlineKeyboardMarkup(keys)
            user_state[user_id] = {
                'state': 'select_quality',
                'link': link
            }

            await update.message.reply_text('کیفیت ویدیو رو انتخاب کن:', reply_markup=markup)

        except Exception as e:
            print(f'خطای غیرمنتظره: {e}')
            await update.message.reply_text('یه مشکلی پیش اومده، دوباره امتحان کن.')

async def quality_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_chat.id
    data = query.data
    if user_id not in user_state or user_state[user_id]['state'] != 'select_quality':
        await query.edit_message_text('یه مشکلی پیش اومده، دوباره امتحان کن.')
        return

    link = user_state[user_id]['link']
    msg = await query.edit_message_text('درحال دانلود ویدیو...')

    ydl_opts = {
        'format': f'{data}+bestaudio/best',
        'outtmpl': f'{user_id}_%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            temp_path = ydl.prepare_filename(info)

        # پیدا کردن فایل نهایی واقعی
        base_name = os.path.splitext(temp_path)[0]
        final_path = None
        for ext in ['.mp4', '.mkv', '.webm']:
            test_path = base_name + ext
            if os.path.exists(test_path):
                final_path = test_path
                break

        if final_path:
            await context.bot.send_video(chat_id=user_id, video=open(final_path, 'rb'), supports_streaming=True)
            os.remove(final_path)
        else:
            await context.bot.send_message(chat_id=user_id, text='فایل نهایی پیدا نشد.')

        await context.bot.delete_message(chat_id=user_id, message_id=msg.message_id)

    except Exception as e:
        print(f'خطا هنگام دانلود: {e}')
        await context.bot.send_message(chat_id=user_id, text='یه مشکلی موقع دانلود پیش اومد، دوباره امتحان کن.')

    user_state.pop(user_id, None)

def main():
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.Text('download'), download))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, downloading))
    app.add_handler(CallbackQueryHandler(quality_selected))

    app.run_polling()

main()
