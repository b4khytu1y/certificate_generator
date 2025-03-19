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
    """Создает красивый сертификат с рамкой и фоном"""
    
    width, height = 1123, 794  # A4 (альбомный)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Фон с текстурой бумаги
    bg_texture = Image.open("paper_texture.jpg").resize((width, height))
    image.paste(bg_texture, (0, 0))

    font_path = "arial.ttf"  # Укажи путь к своему шрифту
    try:
        font_title = ImageFont.truetype(font_path, 70)
        font_text = ImageFont.truetype(font_path, 40)
        font_small = ImageFont.truetype(font_path, 30)
        font_bold = ImageFont.truetype(font_path, 50)
    except IOError:
        raise Exception("Не найден файл шрифта. Укажите правильный путь.")

    # Декоративные линии
    draw.line((50, 100, width - 50, 100), fill="gold", width=5)
    draw.line((50, height - 100, width - 50, height - 100), fill="gold", width=5)

    # Заголовок
    draw.text((width//2 - 200, 120), "СЕРТИФИКАТ", font=font_title, fill="black")

    # Основной текст
    draw.text((100, 220), f"Настоящий сертификат подтверждает, что", font=font_text, fill="black")
    draw.text((100, 280), f"{name}", font=font_bold, fill="blue")
    draw.text((100, 340), f"успешно прошел(а) курс:", font=font_text, fill="black")
    draw.text((100, 400), f"«{course}»", font=font_bold, fill="red")
    draw.text((100, 460), f"в объеме {hours} академических часов", font=font_text, fill="black")
    draw.text((100, 520), f"в период {date_range}", font=font_text, fill="black")

    # Регистрационный номер
    reg_number = f"№ ПК / JA / {random.randint(10000, 99999)}"
    draw.text((100, 680), f"Дата выдачи: {date_range.split()[-1]}", font=font_small, fill="red")
    draw.text((600, 680), f"Регистрационный номер: {reg_number}", font=font_small, fill="red")

    # QR-код
    qr_data = "https://www.yourverificationlink.com"
    qr = qrcode.make(qr_data)
    qr = qr.resize((150, 150))

    # Создаем золотую рамку для QR
    qr_x, qr_y = width - 220, height - 200
    border_size = 10
    draw.rectangle([qr_x - border_size, qr_y - border_size, qr_x + 150 + border_size, qr_y + 150 + border_size], outline="gold", width=5)
    image.paste(qr, (qr_x, qr_y))

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
