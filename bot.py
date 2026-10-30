import os
import telebot
from yt_dlp import YoutubeDL

API_TOKEN = '9250046539:AAHSTU-RCvCZJOzZZozxsEsBIek4J1BBDco'

bot = telebot.TeleBot(API_TOKEN)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне чистую ссылку на видео, и я скачаю его для тебя. 📥")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    filename = None
    
    if not url.startswith('http'):
        bot.reply_to(message, "Пожалуйста, отправь корректную ссылку на видео. ⚠️")
        return

    status_msg = bot.reply_to(message, "Скачиваю видео, подожди немного... ⏳")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'max_filesize': 45 * 1024 * 1024,
        'quiet': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        bot.edit_message_text("Отправляю видео в чат... 🚀", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video)
            
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        bot.edit_message_text("Не удалось скачать видео. Возможно, ссылка защищена или формат не поддерживается. ❌", chat_id=message.chat.id, message_id=status_msg.message_id)
    
    finally:
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
