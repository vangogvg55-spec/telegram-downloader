import os
import telebot
from yt_dlp import YoutubeDL

# ВСТАВЬ СВОЙ ТОКЕН СЮДА (внутри кавычек)
API_TOKEN = '9250046539:AAH8syMpYMIlh78oAIo3xu2-tBCmgd8xgOE'

bot = telebot.TeleBot(API_TOKEN)

# Папка, куда временно будут качаться видео на сервере
DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на видео из TikTok, YouTube или VK, и я скачаю его для тебя. 📥")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    
    # Проверяем, похож ли текст на ссылку
    if not url.startswith('http'):
        bot.reply_to(message, "Пожалуйста, отправь корректную ссылку на видео. ⚠️")
        return

    status_msg = bot.reply_to(message, "Скачиваю видео, подожди немного... ⏳")

    # Настройки для скачивания видео через yt-dlp
    ydl_opts = {
    'format': 'best[ext=mp4]/best', # берем уже готовое mp4 видео, склейка не нужна!
    'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
    'max_filesize': 45 * 1024 * 1024,
    'quiet': True
}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Если расширение изменилось в процессе (например, mkv вместо mp4)
            if not os.path.exists(filename):
                filename = filename.rsplit('.', 1)[0] + '.mp4'

        # Отправляем видео пользователю
        bot.edit_message_text("Отправляю видео в чат... 🚀", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video)
            
        # Удаляем сообщение со статусом и временный файл с сервера
        bot.delete_message(message.chat.id, status_msg.message_id)
        os.remove(filename)

    except Exception as e:
        error_text = str(e)
        if "File is too large" in error_text or "max-filesize" in error_text:
            bot.edit_message_text("Ошибка: Видео слишком весит (больше 45 МБ). Telegram не позволяет мне отправлять такие большие файлы. 🛑", chat_id=message.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text("Не удалось скачать видео. Возможно, ссылка не поддерживается или защищена. ❌", chat_id=message.chat.id, message_id=status_msg.message_id)
            if os.path.exists(filename):
                os.remove(filename)

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
