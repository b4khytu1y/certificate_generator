import qrcode
import telebot
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import time

TOKEN = "8025483084:AAH_CgKKebA0UUi_mKEKzk82YenNSQ2Li4M"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Введите ваше ФИО для создания сертификата.")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_name = message.text.strip()
    bot.reply_to(message, "Введите название курса:")
    bot.register_next_step_handler(message, get_course, user_name)

def get_course(message, user_name):
    course_name = message.text.strip()
    
    try:
        cert_image = generate_certificate(user_name, course_name)
        cert_image.seek(0)
        bot.send_photo(message.chat.id, cert_image, caption="🎓 Ваш сертификат готов!")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при создании сертификата. Попробуйте снова.")
        print(f"Ошибка генерации сертификата: {e}")

def generate_certificate(name, course):
    """Создает сертификат с именем пользователя и названием курса"""
    
    width, height = 800, 600
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Указываем путь к шрифту (замени на свой)
    font_path = "arial.ttf"  
    try:
        font_title = ImageFont.truetype(font_path, 40)
        font_text = ImageFont.truetype(font_path, 30)
    except IOError:
        raise Exception("Не найден файл шрифта. Укажите правильный путь.")

    # Добавляем текст
    draw.text((width//2 - 100, 50), "СЕРТИФИКАТ", font=font_title, fill="black")
    draw.text((width//2 - 250, 150), "Настоящий сертификат подтверждает, что", font=font_text, fill="black")
    draw.text((width//2 - len(name) * 10, 200), name, font=font_text, fill="blue")
    draw.text((width//2 - 200, 250), "успешно прошел(а) курс:", font=font_text, fill="black")
    draw.text((width//2 - len(course) * 10, 300), f"«{course}»", font=font_text, fill="blue")

    # Генерируем QR-код
    qr_data = "https://www.youtube.com/playlist?list=PLybQ_CYZqJceLU0QO1sT2MkEUz8chpzPV"
    qr = qrcode.make(qr_data)
    qr = qr.resize((150, 150))  
    image.paste(qr, (width//2 - 75, 400))

    # Сохраняем в буфер
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# Основной цикл для защиты от сбоев
while True:
    try:
        print("Бот запущен и работает...")
        bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"⚠ Ошибка: {e}. Перезапуск через 5 секунд...")
        time.sleep(30)  
