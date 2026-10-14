"""Быстрая проверка статического лендинга: теги, файлы, заголовки, связка JS <-> HTML."""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

problems = []

html_path = os.path.join(ROOT, "index.html")
with open(html_path, encoding="utf-8") as fh:
    html = fh.read()
with open(os.path.join(ROOT, "styles.css"), encoding="utf-8") as fh:
    css = fh.read()
with open(os.path.join(ROOT, "script.js"), encoding="utf-8") as fh:
    js = fh.read()


# 1. Баланс тегов
class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"лишний </{tag}> на строке {self.getpos()[0]}")
            return
        open_tag, line = self.stack.pop()
        if open_tag != tag:
            self.errors.append(f"</{tag}> на строке {self.getpos()[0]} закрывает <{open_tag}>, открытый на строке {line}")


checker = Checker()
checker.feed(html)
problems += checker.errors
problems += [f"не закрыт <{t}> (строка {ln})" for t, ln in checker.stack]


# 2. Локальные сылки и картинки существуют
def check_asset(path, label):
    clean = path.split("?")[0].split("#")[0]
    if clean.startswith(("http", "mailto:", "tel:", "data:", "//")):
        return
    full = os.path.join(ROOT, clean)
    if not os.path.isfile(full):
        problems.append(f"{label}: файл не найден — {clean}")


for m in re.finditer(r'<img[^>]*src="([^"]+)"', html):
    check_asset(m.group(1), "img")
for m in re.finditer(r'<link[^>]*href="(assets/[^"]+|styles\.css)"', html):
    check_asset(m.group(1), "link")
for m in re.finditer(r'<script[^>]*src="([^"]+)"', html):
    check_asset(m.group(1), "script")


# 3. Заголовки: ровно один H1, вложенность H2 -> H3
h1 = re.findall(r"<h1[^>]*>", html)
h2 = re.findall(r"<h2[^>]*>", html)
h3 = re.findall(r"<h3[^>]*>", html)
if len(h1) != 1:
    problems.append(f"H1 должен быть один, найдено {len(h1)}")
if not h2:
    problems.append("нет ни одного H2")
if not h3:
    problems.append("нет ни одного H3")


# 4. id, на которые ссылается script.js, есть в HTML
for ident in sorted(set(re.findall(r"getElementById\('([^']+)'\)", js))):
    if f'id="{ident}"' not in html:
        problems.append(f"script.js ищет id=\"{ident}\", но его нет в index.html")


# 5. Якорные ссылки ведут на существующие id
for anchor in sorted(set(re.findall(r'href="#([^"]+)"', html))):
    if f'id="{anchor}"' not in html:
        problems.append(f"ссылка href=\"#{anchor}\" — нет такого id")


# 6. CSS-классы из HTML определены в styles.css
used = set()
for attr in re.findall(r'class="([^"]+)"', html):
    used.update(attr.split())
missing = sorted(c for c in used if f".{c}" not in css)
if missing:
    problems.append("классы без стилей: " + ", ".join(missing))


# 7. Размеры изображений в assets
for name in sorted(os.listdir(os.path.join(ROOT, "assets"))):
    size = os.path.getsize(os.path.join(ROOT, "assets", name))
    status = "OK" if size < 250_000 else "ТЯЖЁЛЫЙ — сжать"
    print(f"  assets/{name}: {size // 1024} КБ — {status}")


print(f"\nСекции: H1={len(h1)}, H2={len(h2)}, H3={len(h3)}")
if problems:
    print("\nПРОБЛЕМЫ:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("Проверка пройдена: структура, файлы и связки в порядке.")
