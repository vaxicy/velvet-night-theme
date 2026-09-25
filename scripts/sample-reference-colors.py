"""Copy the real installed-Chrome capture into the repo and sample its UI colors.

Chrome paints some UI elements itself (Google wordmark, shortcut tiles, omnibox
glyphs, the Customize pill ...). Those colors must come from a real install, not
from theme variables, so this script samples them once and prints hex values that
scripts/generate-store-assets.py hardcodes.

Run from the project root:  python3 scripts/sample-reference-colors.py <capture.png>
"""
import hashlib
import os
import shutil
import sys

from PIL import Image

REF = "store-assets/references/real-browser-capture.png"
CROPS = "store-assets/references/crops"


def hexof(im, x, y):
    px = im.convert("RGB").getpixel((int(x), int(y)))
    return "#%02X%02X%02X" % px


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    src = sys.argv[1]
    os.makedirs(os.path.dirname(REF), exist_ok=True)
    shutil.copyfile(src, REF)
    # the repo path holds non-ASCII characters, so verify the copy really landed
    assert os.path.exists(REF) and os.path.getsize(REF) == os.path.getsize(src), "copy failed"
    assert md5(src) == md5(REF), "copy mismatch"
    print("reference:", REF, os.path.getsize(REF), "bytes")

    im = Image.open(REF)
    w, h = im.size
    print("size:", w, h)

    points = {
        "tab strip (inactive area)": (300, 8),
        "tab strip near right": (640, 8),
        "active tab": (700, 20),
        "active tab left edge": (668, 20),
        "toolbar": (860, 48),
        "toolbar left": (20, 48),
        "omnibox body": (400, 48),
        "omnibox placeholder text": (330, 48),
        "bookmark bar": (500, 80),
        "bookmark bar far right": (1000, 80),
        "ntp background": (120, 300),
        "ntp background 2": (900, 250),
        "google wordmark": (500, 213),
        "google wordmark 2": (560, 205),
        "ntp search box": (500, 300),
        "shortcut label": (476, 397),
        "customize pill bg": (990, 628),
        "window title text": (880, 16),
    }
    for name, (x, y) in points.items():
        print("%-28s (%4d,%3d) %s" % (name, x, y, hexof(im, x, y)))

    # horizontal runs: shows exactly where each strip / element starts and ends
    rgb = im.convert("RGB")

    def extreme(x0, y0, x1, y1, mode):
        best, val = None, None
        for y in range(y0, y1):
            for x in range(x0, x1):
                px = rgb.getpixel((x, y))
                lum = 0.299 * px[0] + 0.587 * px[1] + 0.114 * px[2]
                if val is None or (lum > val if mode == "bright" else lum < val):
                    best, val = px, lum
        return "#%02X%02X%02X" % best

    for label, box, mode in [
        ("nav icons (brightest glyph)", (10, 38, 120, 58), "bright"),
        ("omnibox G chip (brightest)", (126, 34, 168, 62), "bright"),
        ("omnibox placeholder (brightest)", (175, 40, 500, 58), "bright"),
        ("bookmark row (brightest)", (0, 66, 600, 92), "bright"),
        ("inactive tab text (brightest)", (33, 10, 171, 28), "bright"),
        ("active tab text (brightest)", (764, 10, 900, 28), "bright"),
        ("NTP Images text (brightest)", (1008, 108, 1052, 128), "bright"),
        ("NTP apps grid (brightest)", (1052, 106, 1072, 128), "bright"),
        ("shortcut label (brightest)", (435, 388, 485, 406), "bright"),
        ("window control glyph (darkest)", (1044, 10, 1080, 26), "dark"),
        ("shortcut tile (center)", (450, 355, 472, 370), "bright"),
        ("customize pill label (brightest)", (990, 612, 1066, 632), "bright"),
    ]:
        print("%-34s %s" % (label, extreme(*box, mode)))

    def runs(y, x0=0, x1=None):
        x1 = x1 or w
        out, start, prev = [], x0, rgb.getpixel((x0, y))
        for x in range(x0 + 1, x1):
            cur = rgb.getpixel((x, y))
            if max(abs(a - b) for a, b in zip(cur, prev)) > 6:
                if x - start >= 3:
                    out.append((start, x - 1, "#%02X%02X%02X" % prev))
                start, prev = x, cur
        out.append((start, x1 - 1, "#%02X%02X%02X" % prev))
        return out

    def vruns(x, y0=0, y1=None):
        y1 = y1 or h
        out, start, prev = [], y0, rgb.getpixel((x, y0))
        for y in range(y0 + 1, y1):
            cur = rgb.getpixel((x, y))
            if max(abs(a - b) for a, b in zip(cur, prev)) > 6:
                if y - start >= 3:
                    out.append((start, y - 1, "#%02X%02X%02X" % prev))
                start, prev = y, cur
        out.append((start, y1 - 1, "#%02X%02X%02X" % prev))
        return out

    for y in (8, 18, 30, 40, 50, 60, 70, 80, 88):
        print("row y=%-3d" % y, runs(y))
    for x in (60, 500, 1050):
        print("col x=%-4d" % x, vruns(x, 0, 130))
    for y in (105, 118, 130, 200, 215, 240, 290, 300, 310, 350, 362, 375, 397, 620, 630):
        print("ntp y=%-3d" % y, runs(y, 100, 1080))
    print("col x=490 ntp", vruns(490, 130, 420))
    print("col x=490 pill", vruns(490, 600, 646))

    os.makedirs(CROPS, exist_ok=True)
    crops = {
        "top-strip": (0, 0, 1080, 95, 2),
        "wordmark": (400, 170, 680, 255, 3),
        "search": (255, 265, 830, 420, 2),
        "right-top": (900, 90, 1080, 430, 3),
        "pill": (880, 590, 1080, 646, 4),
        "tab-active": (620, 0, 900, 70, 3),
        "toolbar-left": (0, 30, 320, 100, 3),
    }
    for name, (x0, y0, x1, y1, zoom) in crops.items():
        box = im.convert("RGB").crop((x0, y0, min(x1, w), min(y1, h)))
        box = box.resize((box.width * zoom, box.height * zoom), Image.NEAREST)
        out = os.path.join(CROPS, name + ".png")
        box.save(out)
        print("crop:", out, box.size)


if __name__ == "__main__":
    main()
