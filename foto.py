
import asyncio
import logging
import os
import io
import textwrap

import qrcode
from gtts import gTTS

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    BufferedInputFile
)
from aiogram.filters.command import CommandObject

from PIL import Image, ImageDraw, ImageFont, ImageOps


# ==========================================
# SOZLAMALAR
# ==========================================

TOKEN = "9138657279:AAGvUeUHj8jHc_PPl8yuFJxGcU3uG0MYB9g"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ==========================================
# SHRI FT
# ==========================================

def get_font(size):
    paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]

    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass

    return ImageFont.load_default()


# ==========================================
# START
# ==========================================

@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "Salom! 🚀 Bot tayyor.\n\n"
        "Buyruqlar (shunchaki yozing):\n\n"
        "🎙 /voice matn - Ovozli xabar yaratish\n"
        "📱 /qrcode matn - QR-kod yasash\n"
        "✨ /textsticker matn - Matndan stiker yasash\n\n"
        "📸 Rasmga ishlov berish uchun:\n"
        "Rasm yuborib, izohiga quyidagilardan birini yozing:\n\n"
        "• crop - 3:4 format\n"
        "• pdf - PDF qilish\n"
        "• bw - Oq-qora qilish\n"
        "• watermark - Watermark qo'shish\n\n"
        "ℹ️ /help - Yordam"
    )


@dp.message(Command("help"))
async def help_handler(message: Message):

    await message.answer(
        "🤖 BOT YORDAMI\n\n"
        "1. /voice Salom dunyo\n"
        "2. /qrcode https://google.com\n"
        "3. /textsticker Salom\n\n"
        "Rasmga ishlov berish:\n"
        "Rasm yuboring va caption yozing:\n\n"
        "crop - 3:4 kesish\n"
        "pdf - PDF hujjat\n"
        "bw - Oq-qora rasm\n"
        "watermark - BEKUZ watermark\n"
        "watermark BEKUZ - Maxsus watermark"
    )


# ==========================================
# VOICE - MATNDAN OVOZ YARATISH
# ==========================================

def generate_voice(text):

    output = io.BytesIO()

    tts = gTTS(
        text=text,
        lang="uz",
        slow=False
    )

    tts.write_to_fp(output)
    output.seek(0)

    return output.getvalue()


@dp.message(Command("voice"))
async def voice_handler(
    message: Message,
    command: CommandObject
):

    text = command.args

    if not text:
        await message.answer(
            "❌ Matn kiriting!\n\n"
            "Misol: /voice Salom dunyo"
        )
        return

    if len(text) > 3000:
        await message.answer("❌ Matn 3000 belgidan oshmasin.")
        return

    status = await message.answer("🎙 Ovoz tayyorlanmoqda...")

    try:
        audio = await asyncio.to_thread(
            generate_voice,
            text
        )

        await message.answer_audio(
            BufferedInputFile(
                audio,
                filename="voice.mp3"
            ),
            title="Matndan yaratilgan ovoz",
            caption="✅ Ovoz tayyor!"
        )

        await status.delete()

    except Exception:
        logging.exception("Voice xatosi")

        await status.edit_text(
            "❌ Ovoz yaratilmadi. Internet yoki TTS xizmatini tekshiring."
        )


# ==========================================
# QR CODE
# ==========================================

@dp.message(Command("qrcode"))
async def qr_handler(
    message: Message,
    command: CommandObject
):

    text = command.args

    if not text:
        await message.answer(
            "❌ QR uchun matn kiriting!\n\n"
            "Misol: /qrcode https://google.com"
        )
        return

    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )

        qr.add_data(text)
        qr.make(fit=True)

        image = qr.make_image(
            fill_color="black",
            back_color="white"
        ).convert("RGB")

        buffer = io.BytesIO()

        image.save(buffer, format="PNG")

        await message.answer_photo(
            BufferedInputFile(
                buffer.getvalue(),
                filename="qrcode.png"
            ),
            caption="✅ QR-kod tayyor!"
        )

    except Exception:
        logging.exception("QR xatosi")
        await message.answer("❌ QR yaratishda xatolik.")


# ==========================================
# TEXT STICKER
# ==========================================

def create_sticker(text):

    SIZE = 512

    image = Image.new(
        "RGBA",
        (SIZE, SIZE),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (12, 12, 500, 500),
        radius=55,
        fill=(20, 30, 65, 255),
        outline=(0, 200, 255, 255),
        width=8
    )

    font_size = 55
    max_width = 420
    max_height = 400

    words = text.split()
    if not words:
        words = [text]

    while True:

        font = get_font(font_size)
        lines = []
        current = ""

        for word in words:

            test = (current + " " + word).strip()

            box = draw.textbbox(
                (0, 0),
                test,
                font=font
            )

            if box[2] - box[0] <= max_width:
                current = test

            else:
                if current:
                    lines.append(current)

                current = word

        if current:
            lines.append(current)

        line_height = font_size + 15

        if (
            len(lines) * line_height <= max_height
            and all(
                draw.textbbox(
                    (0, 0),
                    line,
                    font=font
                )[2] <= max_width + 20
                for line in lines
            )
        ):
            break

        font_size -= 2

        if font_size < 14:
            break

    total_height = len(lines) * line_height
    y = (SIZE - total_height) // 2

    for line in lines:

        box = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        width = box[2] - box[0]
        x = (SIZE - width) // 2

        draw.text(
            (x + 3, y + 3),
            line,
            font=font,
            fill=(0, 0, 0, 180)
        )

        draw.text(
            (x, y),
            line,
            font=font,
            fill="white",
            stroke_width=2,
            stroke_fill=(0, 200, 255, 255)
        )

        y += line_height

    output = io.BytesIO()

    image.save(output, format="PNG")

    return output.getvalue()


@dp.message(Command("textsticker"))
async def sticker_handler(
    message: Message,
    command: CommandObject
):

    text = command.args

    if not text:
        await message.answer(
            "❌ Matn yozing!\n\n"
            "Misol: /textsticker Salom dunyo"
        )
        return

    if len(text) > 2000:
        await message.answer("❌ Matn juda uzun.")
        return

    try:

        png = create_sticker(text)

        await message.answer_document(
            BufferedInputFile(
                png,
                filename="sticker.png"
            ),
            caption="✨ PNG stiker tayyor!"
        )

    except Exception:
        logging.exception("Sticker xatosi")
        await message.answer("❌ Stiker yaratilmadi.")


# ==========================================
# RASMNI 3:4 CROP QILISH
# ==========================================

def crop_3_4(image):

    width, height = image.size

    ratio = 3 / 4

    if width / height > ratio:

        new_width = int(height * ratio)

        left = (width - new_width) // 2

        image = image.crop((
            left,
            0,
            left + new_width,
            height
        ))

    else:

        new_height = int(width / ratio)

        top = (height - new_height) // 2

        image = image.crop((
            0,
            top,
            width,
            top + new_height
        ))

    return image


# ==========================================
# WATERMARK
# ==========================================

def add_watermark(image, watermark_text="BEKUZ"):

    image = image.convert("RGBA")

    layer = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(layer)

    font = get_font(
        max(20, image.width // 18)
    )

    box = draw.textbbox(
        (0, 0),
        watermark_text,
        font=font
    )

    text_width = box[2] - box[0]
    text_height = box[3] - box[1]

    x = image.width - text_width - 25
    y = image.height - text_height - 25

    draw.text(
        (x, y),
        watermark_text,
        font=font,
        fill=(255, 255, 255, 170),
        stroke_width=2,
        stroke_fill=(0, 0, 0, 150)
    )

    return Image.alpha_composite(
        image,
        layer
    )


# ==========================================
# RASMNI QAYTA ISHLASH
# ==========================================

@dp.message(F.photo)
async def photo_handler(message: Message):

    caption = (message.caption or "").strip()

    parts = caption.split(maxsplit=1)

    mode = parts[0].lower() if parts else "crop"

    watermark_text = (
        parts[1] if len(parts) > 1 else "BEKUZ"
    )

    if mode not in [
        "crop",
        "pdf",
        "bw",
        "watermark"
    ]:

        await message.answer(
            "❌ Noto'g'ri buyruq!\n\n"
            "crop, pdf, bw yoki watermark yozing."
        )
        return

    status = await message.answer(
        "⏳ Rasm qayta ishlanmoqda..."
    )

    try:

        photo = message.photo[-1]

        file = await bot.get_file(photo.file_id)

        buffer = io.BytesIO()

        await bot.download_file(
            file.file_path,
            destination=buffer
        )

        buffer.seek(0)

        image = Image.open(buffer)

        image = ImageOps.exif_transpose(
            image
        ).convert("RGB")

        # CROP
        if mode == "crop":

            image = crop_3_4(image)

            jpg = io.BytesIO()

            image.save(
                jpg,
                format="JPEG",
                quality=95
            )

            jpg.seek(0)

            await message.answer_photo(
                BufferedInputFile(
                    jpg.getvalue(),
                    filename="crop.jpg"
                ),
                caption="✅ Rasm 3:4 formatda kesildi!"
            )

        # PDF
        elif mode == "pdf":

            pdf = io.BytesIO()

            image.save(
                pdf,
                format="PDF",
                resolution=100
            )

            await message.answer_document(
                BufferedInputFile(
                    pdf.getvalue(),
                    filename="image.pdf"
                ),
                caption="📄 PDF tayyor!"
            )

        # BLACK AND WHITE
        elif mode == "bw":

            image = ImageOps.grayscale(image)

            jpg = io.BytesIO()

            image.save(
                jpg,
                format="JPEG",
                quality=95
            )

            await message.answer_photo(
                BufferedInputFile(
                    jpg.getvalue(),
                    filename="black_white.jpg"
                ),
                caption="⚫⚪ Oq-qora rasm tayyor!"
            )

        # WATERMARK
        elif mode == "watermark":

            image = add_watermark(
                image,
                watermark_text
            )

            png = io.BytesIO()

            image.save(
                png,
                format="PNG"
            )

            await message.answer_document(
                BufferedInputFile(
                    png.getvalue(),
                    filename="watermark.png"
                ),
                caption="💧 Watermark qo'shildi!"
            )

        await status.delete()

    except Exception:

        logging.exception("Rasm ishlashda xatolik")

        await status.edit_text(
            "❌ Rasmni qayta ishlashda xatolik yuz berdi."
        )


# ==========================================
# BOTNI ISHGA TUSHIRISH
# ==========================================

async def main():

    if TOKEN == "9138657279:AAGvUeUHj8jHc_PPl8yuFJxGcU3uG0MYB9g":
        raise RuntimeError(
            "Avval TOKEN qiymatiga BotFather tokenini yozing!"
        )

    print("================================")
    print(" BOT MUVAFFAQIYATLI ISHGA TUSHDI")
    print("================================")

    await dp.start_polling(bot)


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Bot to'xtatildi.")
