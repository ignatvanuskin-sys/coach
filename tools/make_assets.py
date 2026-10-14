"""Генерация брендовых ассетов: иконки, OG-картинка для соцсетей, WebP-версии фото.

Запуск из корня проекта:  python tools/make_assets.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

WINE = (110, 43, 39)
WINE_DEEP = (58, 20, 19)
CREAM = (251, 246, 240)
IVORY = (247, 234, 225)
GOLD = (228, 207, 166)
INK = (36, 31, 28)


def find_font(candidates, size):
    for name in candidates:
        path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def serif(size):
    return find_font(["georgia.ttf", "times.ttf", "constan.ttf", "cambria.ttc"], size)


def sans(size):
    return find_font(["arial.ttf", "segoeui.ttf", "tahoma.ttf", "verdana.ttf"], size)


def vertical_gradient(size, top, bottom):
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)
    height = size[1]
    for y in range(height):
        k = y / max(height - 1, 1)
        draw.line(
            [(0, y), (size[0], y)],
            fill=tuple(round(top[i] + (bottom[i] - top[i]) * k) for i in range(3)),
        )
    return img


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return mask


def make_icon(size, radius_ratio=0.22, path="icon.png"):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    plate = Image.new("RGBA", (size, size), WINE + (255,))
    img.paste(plate, (0, 0), rounded_mask((size, size), int(size * radius_ratio)))
    draw = ImageDraw.Draw(img)
    font = serif(int(size * 0.62))
    box = draw.textbbox((0, 0), "А", font=font)
    draw.text(
        ((size - (box[2] - box[0])) / 2 - box[0], (size - (box[3] - box[1])) / 2 - box[1] - size * 0.03),
        "А",
        font=font,
        fill=(243, 226, 206),
    )
    img.save(os.path.join(ASSETS, path))
    return path


def make_a(assets, src, out, width, quality=80):
    img = Image.open(os.path.join(assets, src)).convert("RGB")
    if img.width > width:
        height = round(img.height * width / img.width)
        img = img.resize((width, height), Image.LANCZOS)
    img.save(os.path.join(assets, out), "WEBP", quality=quality, method=6)
    return out, img.size, round(os.path.getsize(os.path.join(assets, out)) / 1024)


def make_og():
    W, H = 1200, 630
    canvas = vertical_gradient((W, H), WINE, WINE_DEEP)

    # фото справа: кроссфейд в фон тем же цветом (без видимой границы)
    photo = Image.open(os.path.join(ASSETS, "hero-portrait.jpg")).convert("RGB")
    target_w, target_h = 470, H
    ratio = max(target_w / photo.width, target_h / photo.height)
    resized = photo.resize((round(photo.width * ratio), round(photo.height * ratio)), Image.LANCZOS)
    left = (resized.width - target_w) // 2
    resized = resized.crop((left, 0, left + target_w, target_h))

    strip_x = W - target_w
    bg_strip = canvas.crop((strip_x, 0, W, H))
    fade_width = 300
    ramp = Image.new("L", (target_w, target_h), 0)
    ramp_draw = ImageDraw.Draw(ramp)
    for x in range(fade_width):
        ramp_draw.line([(x, 0), (x, target_h)], fill=round(255 * (1 - x / fade_width) ** 1.35))
    canvas.paste(resized, (strip_x, 0))
    canvas.paste(bg_strip, (strip_x, 0), ramp)

    draw = ImageDraw.Draw(canvas)
    x = 72
    draw.text((x, 74), "БИЗНЕС-КОУЧ · ACC ICF · АЛМАТЫ И ОНЛАЙН", font=sans(21), fill=GOLD)
    draw.text((x, 132), "Зарабатывай", font=serif(66), fill=IVORY)
    draw.text((x, 208), "больше —", font=serif(66), fill=IVORY)
    draw.text((x, 284), "и не выгорай", font=serif(66), fill=IVORY)
    draw.line([(x, 388), (x + 64, 388)], fill=GOLD, width=2)
    draw.text((x, 414), "Айгерим Серикова", font=serif(34), fill=IVORY)
    draw.text((x, 462), "Бизнес-коучинг для женщин-предпринимательниц", font=sans(21), fill=(214, 190, 176))
    draw.text((x, 492), "и экспертов · 600+ часов практики ICF", font=sans(21), fill=(214, 190, 176))
    draw.text((x, 552), "coach-five-flax.vercel.app", font=sans(19), fill=GOLD)

    canvas.save(os.path.join(ASSETS, "og-image.jpg"), "JPEG", quality=88, optimize=True, progressive=True)
    return round(os.path.getsize(os.path.join(ASSETS, "og-image.jpg")) / 1024)


if __name__ == "__main__":
    print("иконка 32:", make_icon(32, path="favicon-32.png"))
    make_icon(180, radius_ratio=0.2, path="apple-touch-icon.png")
    make_icon(192, radius_ratio=0.2, path="icon-192.png")
    make_icon(512, radius_ratio=0.2, path="icon-512.png")

    # .ico из 16/32/48
    base = Image.open(os.path.join(ASSETS, "favicon-32.png")).convert("RGBA")
    base.save(
        os.path.join(ASSETS, "favicon.ico"),
        sizes=[(16, 16), (32, 32), (48, 48)],
    )

    for spec in [
        ("hero-portrait.jpg", "hero-portrait.webp", 1000),
        ("hero-portrait.jpg", "hero-portrait-640.webp", 640),
        ("about-portrait.jpg", "about-portrait.webp", 900),
        ("about-portrait.jpg", "about-portrait-560.webp", 560),
    ]:
        name, size, kb = make_a(ASSETS, spec[0], spec[1], spec[2])
        print(f"{name}: {size[0]}x{size[1]}, {kb} КБ")

    print("og-image.jpg:", make_og(), "КБ")
