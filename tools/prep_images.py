from PIL import Image
import os

os.makedirs("assets", exist_ok=True)

jobs = [
    ("img-mv8epsod-d5d81e88.png", "assets/hero-portrait.jpg", 1000),
    ("img-mv8eqcjh-521cda48.png", "assets/about-portrait.jpg", 900),
]

for src, dst, width in jobs:
    im = Image.open(os.path.join("media-output", src)).convert("RGB")
    if im.width > width:
        height = round(im.height * width / im.width)
        im = im.resize((width, height), Image.LANCZOS)
    im.save(dst, "JPEG", quality=84, optimize=True, progressive=True)
    print(dst, im.size, round(os.path.getsize(dst) / 1024), "KB")
