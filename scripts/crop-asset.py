"""Zoom into a region of a rendered asset — QA helper for the store images.

Usage (from the project root):
    python3 scripts/crop-asset.py store-assets/screenshots/en/screenshot-1-browser.png 1000 30 1280 130 4 out.png
"""
import sys

from PIL import Image


def main():
    src, x0, y0, x1, y1, zoom, dst = sys.argv[1:8]
    im = Image.open(src).convert('RGB').crop((int(x0), int(y0), int(x1), int(y1)))
    zoom = float(zoom)
    im = im.resize((int(im.width * zoom), int(im.height * zoom)), Image.NEAREST)
    im.save(dst)
    print('wrote', dst, im.size)


if __name__ == '__main__':
    main()
