"""Export the chosen logo (candidate G, folded velvet swatch) as the theme icon.

Trims the transparent margin, re-centres the artwork on a square canvas and
writes both the store icon (store-assets/icon.png) and the copy used by the
README (logo/logo128.png). Run from the project root.
"""
import os

from PIL import Image

SRC = 'store-assets/icon-candidates/logo-G-fold-mark.png'
TARGETS = ['store-assets/icon.png', 'logo/logo128.png']
SIZE = 128
MARGIN = 0.06          # share of the canvas kept empty around the artwork


def main():
    art = Image.open(SRC).convert('RGBA')
    box = art.getbbox()
    assert box, 'source artwork is fully transparent'
    art = art.crop(box)

    side = int(round(max(art.size) / (1 - 2 * MARGIN)))
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    canvas.paste(art, ((side - art.width) // 2, (side - art.height) // 2), art)
    icon = canvas.resize((SIZE, SIZE), Image.LANCZOS)

    for target in TARGETS:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        icon.save(target)
        with Image.open(target) as check:
            assert check.size == (SIZE, SIZE), f'{target}: {check.size}'
        print(f'wrote {target} {SIZE}x{SIZE} {os.path.getsize(target)} bytes')


if __name__ == '__main__':
    main()
