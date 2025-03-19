import qrcode
import telebot
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import time

bot = telebot.TeleBot('')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Введите ваше ФИО:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_name = message.text.strip()
    bot.reply_to(message, "Введите название курса:")
    bot.register_next_step_handler(message, get_course, user_name)

def get_course(message, user_name):
    course_name = message.text.strip()
    bot.reply_to(message, "Введите количество академических часов:")
    bot.register_next_step_handler(message, get_hours, user_name, course_name)

def get_hours(message, user_name, course_name):
    hours = message.text.strip()
    bot.reply_to(message, "Введите даты (например, 10.02.2025 - 22.02.2025):")
    bot.register_next_step_handler(message, generate_certificate, user_name, course_name, hours)

def generate_certificate(message, name, course, hours):
    date_range = message.text.strip()
    
    try:
        cert_image = create_certificate_image(name, course, hours, date_range)
        cert_image.seek(0)
        bot.send_photo(message.chat.id, cert_image, caption="🎓 Ваш сертификат готов!")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при создании сертификата. Попробуйте снова.")
        print(f"Ошибка генерации сертификата: {e}")

def create_certificate_image(name, course, hours, date_range):
    """Создает сертификат с нужными данными"""
    
    width, height = 1123, 794  # A4 (альбомный)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    font_path = "arial.ttf"  # Укажи путь к своему шрифту
    try:
        font_title = ImageFont.truetype(font_path, 60)
        font_text = ImageFont.truetype(font_path, 40)
        font_small = ImageFont.truetype(font_path, 30)
    except IOError:
        raise Exception("Не найден файл шрифта. Укажите правильный путь.")

    # Рисуем заголовок
    draw.text((width//2 - 200, 50), "СЕРТИФИКАТ", font=font_title, fill="black")

    # Основной текст
    draw.text((100, 200), f"Настоящий сертификат подтверждает, что", font=font_text, fill="black")
    draw.text((100, 250), f"{name}", font=font_text, fill="blue")
    draw.text((100, 300), f"успешно прошел(а) курс:", font=font_text, fill="black")
    draw.text((100, 350), f"«{course}»", font=font_text, fill="blue")
    draw.text((100, 400), f"в объеме {hours} академических часов", font=font_text, fill="black")
    draw.text((100, 450), f"в период {date_range}", font=font_text, fill="black")

    # Регистрационный номер
    reg_number = f"№ ПК / JA / {random.randint(10000, 99999)}"
    draw.text((100, 600), f"Дата выдачи: {date_range.split()[-1]}", font=font_small, fill="red")
    draw.text((600, 600), f"Регистрационный номер: {reg_number}", font=font_small, fill="red")

    # QR-код
    qr_data = "https://www.yourverificationlink.com"  # Сюда можно добавить проверку подлинности
    qr = qrcode.make(qr_data)
    qr = qr.resize((150, 150))
    image.paste(qr, (width - 200, height - 200))

    # Сохраняем в буфер
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

@bot.message_handler(commands=['stop'])
def stop_bot(message):
    bot.reply_to(message, "Бот отключается. До встречи! 👋")
    exit()

print("Бот запущен...")
while True:
    try:
        bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}. Перезапуск через 5 секунд...")
        time.sleep(5)
