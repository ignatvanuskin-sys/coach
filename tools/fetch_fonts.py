"""Скачивает шрифты Google Fonts в assets/fonts и собирает локальный fonts.css.

Зачем: сайт перестаёт ходить на fonts.googleapis.com и fonts.gstatic.com —
меньше соединений, полный контроль кэша и никаких сторонних запросов с IP посетителя.

Запуск из корня проекта:  python tools/fetch_fonts.py
"""
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "fonts")

CSS_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Cormorant+Garamond:wght@400;500;600"
    "&family=Manrope:wght@400;500;600;700"
    "&display=swap"
)
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
KEEP_SUBSETS = {"cyrillic", "cyrillic-ext", "latin"}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    css = get(CSS_URL).decode("utf-8")

    blocks = re.findall(r"(?s)/\*\s*([a-z\-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css)
    out_rules = []
    downloaded = 0
    total_bytes = 0

    for subset, block in blocks:
        if subset not in KEEP_SUBSETS:
            continue

        family = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
        style = re.search(r"font-style:\s*(\w+)", block).group(1)
        src = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
        unicode_range = re.search(r"unicode-range:\s*([^;]+);", block).group(1)

        slug = family.lower().replace(" ", "-")
        fname = f"{slug}-{weight}-{style}-{subset}.woff2"
        path = os.path.join(OUT_DIR, fname)
        if not os.path.isfile(path):
            data = get(src)
            with open(path, "wb") as fh:
                fh.write(data)
            downloaded += 1
        size = os.path.getsize(path)
        total_bytes += size

        out_rules.append(
            "@font-face{\n"
            f"  font-family:'{family}';\n"
            f"  font-style:{style};\n"
            f"  font-weight:{weight};\n"
            "  font-display:swap;\n"
            f"  src:url('{fname}') format('woff2');\n"
            f"  unicode-range:{unicode_range};\n"
            "}"
        )

    header = (
        "/* Локальные шрифты Cormorant Garamond и Manrope (подмножества cyrillic, cyrillic-ext, latin).\n"
        "   Файлы собраны скриптом tools/fetch_fonts.py — править вручную не нужно. */\n\n"
    )
    with open(os.path.join(OUT_DIR, "fonts.css"), "w", encoding="utf-8") as fh:
        fh.write(header + "\n".join(out_rules) + "\n")

    print(f"скачано новых файлов: {downloaded}, всего правил @font-face: {len(out_rules)}")
    print(f"суммарный вес шрифтов: {round(total_bytes / 1024)} КБ")


if __name__ == "__main__":
    main()
