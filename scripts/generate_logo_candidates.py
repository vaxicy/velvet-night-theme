"""Velvet Night Theme — logo candidates (code-first, PIL + NumPy).

Generates 8 logo directions at 512px so the user can pick one.
Palette is read from manifest.json at runtime, so the logo can never drift
from the theme colors.

Run from the project root (relative paths only, see Windows/Pillow note):
    python3 scripts/generate_logo_candidates.py

Outputs into store-assets/icon-candidates/:
    logo-A-velvet-drape.png ... logo-H-moon-disc.png   (512x512 RGBA)
    preview-sheet-light.png / preview-sheet-dark.png
    preview-small-sizes.png
"""

import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 512          # final size
SS = 2           # supersample factor -> smoother curves after downscale
W = S * SS

OUT_DIR = "store-assets/icon-candidates"

_g = np.mgrid[0:W, 0:W].astype(np.float32)
YS, XS = _g[0], _g[1]
U = XS / (W - 1.0)
V = YS / (W - 1.0)
CENT = 0.5 * W


# ---------------------------------------------------------------- palette ---
def load_palette():
    with open("manifest.json", encoding="utf-8") as fh:
        c = json.load(fh)["theme"]["colors"]

    def rgb(key):
        return np.array(c[key], dtype=np.float32)

    p = {
        "wine": rgb("frame"),
        "wine_hi": rgb("frame_inactive"),
        "mauve": rgb("toolbar"),
        "plum": rgb("button_background"),
        "ink": rgb("ntp_background"),
        "ink2": rgb("omnibox_background"),
        "cream": rgb("tab_text"),
        "pink": rgb("bookmark_text"),
        "peri": rgb("ntp_link"),
    }
    p["wine_lo"] = p["wine"] * 0.60
    p["plum_lo"] = p["plum"] * 0.52
    p["plum_hi"] = np.clip(p["plum"] * 1.22, 0, 255)
    return p


# ---------------------------------------------------------------- helpers ---
def mix(a, b, t):
    a = np.asarray(a, np.float32)
    b = np.asarray(b, np.float32)
    t = np.asarray(t, np.float32)
    if t.ndim == 2:
        t = t[..., None]
    return a + (b - a) * t


def vgrad(top, bot):
    return top + (bot - top) * V[..., None]


def pleats(n, phase=0.0, sharp=1.5):
    pl = 0.5 + 0.5 * np.cos(2 * np.pi * n * U + phase)
    return np.power(pl, sharp)


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def glow(d, r, sigma):
    return np.exp(-((d - r) / sigma) ** 2)


def crescent(cx, cy, r, cut_dx, cut_dy, cut_scale=0.95):
    """Disc minus an offset disc -> one clean crescent. Returns (mask, dist)."""
    d = np.hypot(XS - cx, YS - cy)
    disc = d <= r
    cut = np.hypot(XS - (cx + cut_dx), YS - (cy + cut_dy)) <= r * cut_scale
    return disc & ~cut, d


def mask_from(draw_fn):
    m = Image.new("L", (W, W), 0)
    draw_fn(ImageDraw.Draw(m))
    return np.asarray(m, np.float32) / 255.0


def blur_arr(m, radius):
    im = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), "L")
    return np.asarray(im.filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255.0


def squircle(radius_ratio=0.235, inset=0):
    return mask_from(lambda d: d.rounded_rectangle(
        [inset, inset, W - 1 - inset, W - 1 - inset],
        radius=int(radius_ratio * W), fill=255))


def vignette(col, strength=0.30):
    d = np.hypot(XS - CENT, YS - CENT) / (W * 0.72)
    f = 1.0 - strength * np.clip((d - 0.52) / 0.48, 0, 1) ** 1.7
    return col * f[..., None]


def stars(col, spec, color):
    for sx, sy, sr, sa in spec:
        dd = np.hypot(XS - sx * W, YS - sy * W)
        g = np.exp(-(dd / (sr * W)) ** 2)
        col = mix(col, color, (sa * g)[..., None])
    return col


def finish(col, alpha):
    col = np.clip(col, 0, 255)
    arr = np.dstack([col, np.clip(alpha, 0, 1) * 255]).astype(np.uint8)
    return Image.fromarray(arr, "RGBA").resize((S, S), Image.LANCZOS)


# --------------------------------------------------------------- variants ---
def v_a_velvet_drape(P):
    """Full-bleed velvet curtain: soft vertical pleats, satin sheen."""
    pl = pleats(4.2, -0.6, 2.2)
    col = mix(P["wine_lo"] * 0.85, P["wine_hi"] * 1.12, 0.10 + 0.90 * pl)
    col = col * (1.0 - 0.34 * V)[..., None]
    col = mix(col, P["plum"], (0.20 * np.clip((U - 0.48) / 0.52, 0, 1))[..., None])
    sheen = np.exp(-((V - 0.20) / 0.15) ** 2) * (0.35 + 0.65 * pl)
    col = mix(col, P["pink"], (0.26 * sheen)[..., None])
    drop = np.exp(-((V - 0.97) / 0.07) ** 2)
    col = mix(col, P["ink"], (0.35 * drop)[..., None])
    return finish(vignette(col, 0.26), squircle())


def v_b_curtain_moon(P):
    """Dark plum night framed by two wine velvet drapes, cream crescent center."""
    col = vgrad(P["ink2"], P["ink"])
    col = mix(col, P["plum"], (0.10 * (1 - V))[..., None])
    pl = pleats(3.2, -0.9, 1.9)
    dcol = mix(P["wine_lo"] * 0.78, P["wine_hi"] * 1.10, 0.10 + 0.90 * pl)
    dcol = dcol * (0.70 + 0.45 * (1 - V))[..., None]
    dl = np.clip(1 - (U - 0.020) / 0.29, 0, 1)
    dr = np.clip(1 - (0.980 - U) / 0.29, 0, 1)
    da = smoothstep(np.maximum(dl, dr))
    col = mix(col, dcol, da[..., None])
    hem = np.clip(np.exp(-((U - 0.310) / 0.022) ** 2) + np.exp(-((U - 0.690) / 0.022) ** 2), 0, 1)
    col = mix(col, P["ink"], (0.60 * hem)[..., None])

    cx, cy, r = 0.545 * W, 0.430 * W, 0.170 * W
    cres, d = crescent(cx, cy, r, -0.086 * W, -0.048 * W, 0.96)
    halo = blur_arr(cres.astype(np.float32), 0.024 * W)
    col = mix(col, mix(P["peri"], P["cream"], 0.50), (0.70 * halo)[..., None])
    col = np.where(cres[..., None], P["cream"], col)
    col = stars(col, [(0.44, 0.185, 0.0085, 0.80), (0.68, 0.250, 0.0065, 0.65),
                      (0.38, 0.720, 0.0070, 0.60), (0.70, 0.740, 0.0085, 0.70)],
                P["cream"])
    return finish(vignette(col, 0.30), squircle())


def v_c_folded_velvet(P):
    """One velvet swatch with a crisp fold crease along the diagonal."""
    base = vgrad(mix(P["ink2"], P["plum"], 0.34), P["ink"])
    r = 0.375 * W
    pts = [(CENT, CENT - r), (CENT + r, CENT), (CENT, CENT + r), (CENT - r, CENT)]
    m = blur_arr(mask_from(lambda d: d.polygon(pts, fill=255)), 0.0045 * W)

    f = ((XS - CENT) + (YS - CENT)) / (2 * r)      # signed distance to the fold
    side = smoothstep((f + 0.010) / 0.022)
    facet = mix(P["wine_hi"] * 1.10, P["wine_lo"] * 0.92, side)
    facet = facet * (1 - 0.34 * np.exp(-(f / 0.020) ** 2))[..., None]      # crease line
    sheen = np.exp(-(((XS - CENT) + (YS - CENT)) / (0.26 * W)) ** 2)        # satin band
    facet = mix(facet, P["pink"], (0.26 * sheen * (1 - side))[..., None])
    umbra = np.clip(((XS - CENT) + (YS - CENT)) / (0.95 * W), 0, 1)
    facet = facet * (1 - 0.22 * umbra)[..., None]

    sh = np.roll(blur_arr(m, 0.055 * W), (int(0.030 * W), int(0.034 * W)), axis=(0, 1))
    col = mix(base, P["ink"], (0.55 * sh)[..., None])
    col = mix(col, facet, m[..., None])
    return finish(vignette(col, 0.28), squircle())


def v_d_tufted_velvet(P):
    """Capitonne / quilted upholstery: soft puffs + buttons at intersections."""
    col = vgrad(P["wine_hi"], mix(P["wine_lo"], P["ink"], 0.40))
    step, n = 0.300 * W, 3
    centers = np.array([CENT + (i - (n - 1) / 2.0) * step for i in range(n)], np.float32)
    dx = np.min(np.abs(XS[..., None] - centers), axis=2)
    dy = np.min(np.abs(YS[..., None] - centers), axis=2)

    crease = np.exp(-(dx / (0.070 * W)) ** 2) + np.exp(-(dy / (0.070 * W)) ** 2)
    col = col * (1 - 0.26 * np.clip(crease, 0, 1))[..., None]
    puff = np.exp(-(dx ** 2 + dy ** 2) / (2 * (0.085 * W) ** 2))
    col = mix(col, P["wine_hi"] * 1.30, (0.75 * puff)[..., None])

    btn = (dx ** 2 + dy ** 2) <= (0.034 * W) ** 2
    col = np.where(btn[..., None], P["plum_lo"] * 0.85, col)
    spec = np.exp(-(((dx - 0.011 * W) ** 2 + (dy - 0.011 * W) ** 2) / (0.011 * W) ** 2))
    col = mix(col, P["pink"], (0.70 * spec * np.clip(puff * 4, 0, 1))[..., None])
    return finish(vignette(col, 0.30), squircle())


def v_e_valance_moon(P):
    """Pleated velvet valance at the top, moonlit night below."""
    col = vgrad(P["ink2"], P["ink"])
    pl = pleats(5.0, 0.0, 1.4)
    edge = 0.255 + 0.050 * np.cos(2 * np.pi * 5.0 * U)
    vcol = mix(P["wine_lo"], P["wine_hi"], 0.20 + 0.80 * pl)
    vcol = vcol * (1.0 - 1.05 * V)[..., None]
    col = np.where((V <= edge)[..., None], vcol, col)
    rod = np.exp(-((V - 0.058) / 0.013) ** 2)
    col = mix(col, P["plum_hi"], (0.85 * rod)[..., None])
    hem = np.exp(-((V - edge) / 0.012) ** 2)
    col = mix(col, P["plum"], (0.55 * hem)[..., None])

    cx, cy, r = 0.500 * W, 0.660 * W, 0.135 * W
    d = np.hypot(XS - cx, YS - cy)
    cres = (d <= r) & ~(np.hypot(XS - (cx - 0.048 * W), YS - (cy - 0.024 * W)) <= r * 0.94)
    col = mix(col, mix(P["peri"], P["cream"], 0.75), (0.70 * glow(d, r, 0.070 * W))[..., None])
    col = np.where(cres[..., None], P["cream"], col)
    col = stars(col, [(0.235, 0.555, 0.0080, 0.75), (0.765, 0.520, 0.0065, 0.65),
                      (0.300, 0.815, 0.0060, 0.55), (0.725, 0.800, 0.0075, 0.65)],
                P["cream"])
    return finish(vignette(col, 0.30), squircle())


def v_f_velvet_pillow(P):
    """A single wine velvet pillow with center tuft on a mauve backdrop."""
    col = vgrad(mix(P["plum"], P["pink"], 0.22), mix(P["plum_lo"], P["ink"], 0.45))
    inset = 0.125 * W
    m = blur_arr(mask_from(lambda d: d.rounded_rectangle(
        [inset, inset, W - 1 - inset, W - 1 - inset],
        radius=int(0.205 * W), fill=255)), 0.006 * W)

    puff = np.exp(-(((XS - CENT) / (0.40 * W)) ** 2 + ((YS - CENT) / (0.46 * W)) ** 2))
    pcol = mix(P["wine_lo"], P["wine_hi"], 0.15 + 0.85 * puff)
    band = np.exp(-((((XS - CENT) * 0.74 - (YS - CENT) * 0.67) / (0.17 * W)) ** 2))
    pcol = mix(pcol, P["pink"], (0.24 * band)[..., None])
    sh = np.roll(blur_arr(m, 0.055 * W), (int(0.028 * W), int(0.032 * W)), axis=(0, 1))
    col = mix(col, P["ink"], (0.50 * sh)[..., None])
    col = mix(col, pcol, m[..., None])

    dd = np.hypot(XS - CENT, YS - (CENT + 0.012 * W))
    col = np.where((dd <= 0.042 * W)[..., None], mix(P["plum_lo"], P["ink"], 0.45), col)
    col = mix(col, P["wine_hi"], (0.55 * glow(dd, 0.042 * W, 0.011 * W))[..., None])
    spec = np.exp(-(np.hypot(XS - (CENT - 0.013 * W), YS - (CENT - 0.003 * W))
                    / (0.013 * W)) ** 2)
    col = mix(col, P["cream"], (0.80 * spec)[..., None])
    return finish(vignette(col, 0.26), squircle())


def v_g_fold_mark(P):
    """Transparent-background flat mark: velvet swatch with a turned-down corner."""
    col = np.zeros((W, W, 3), np.float32)
    x0, x1 = 0.130 * W, 0.870 * W
    y0, y1 = 0.150 * W, 0.890 * W
    f = 0.300 * W                                     # fold size

    def draw_body(d):
        d.rounded_rectangle([x0, y0, x1, y1], radius=int(0.085 * W), fill=255)
        d.polygon([(x0 - 2, y1 - f), (x0 + f + 2, y1 + 2), (x0 - 2, y1 + 2)], fill=0)

    def draw_flap(d):
        d.polygon([(x0, y1 - f), (x0 + f, y1), (x0 + f, y1 - f)], fill=255)

    m = blur_arr(mask_from(draw_body), 0.0035 * W)
    fl = blur_arr(mask_from(draw_flap), 0.0035 * W)

    body = vgrad(P["wine_hi"] * 1.06, P["wine_lo"] * 0.94)
    band = np.exp(-(((XS - CENT) * 0.72 - (YS - CENT) * 0.69) / (0.21 * W)) ** 2)
    body = mix(body, P["pink"], (0.20 * band)[..., None])
    edge = np.clip(m - blur_arr(m, 0.020 * W), 0, 1)
    body = mix(body, P["ink"], (0.35 * edge)[..., None])
    col = mix(col, body, m[..., None])

    flap = mix(P["pink"], P["wine_hi"], 0.28)
    flap = mix(flap, P["pink"], (0.45 * np.clip(((XS - x0) + (y1 - YS)) / f, 0, 1))[..., None])
    col = mix(col, flap, fl[..., None])
    crease = np.exp(-(np.clip((XS - x0) + (y1 - YS) - f, 0, None) / (0.030 * W)) ** 2)
    col = mix(col, P["ink"], (0.40 * crease * m)[..., None])
    return finish(col, m)


def v_h_moon_disc(P):
    """Circular badge: wine velvet band under a glowing crescent."""
    disc = mask_from(lambda d: d.ellipse([0.030 * W, 0.030 * W,
                                          W - 1 - 0.030 * W, W - 1 - 0.030 * W], fill=255))
    col = vgrad(P["ink2"], P["ink"])
    pl = pleats(4.0, -1.2, 1.5)
    band = (V >= 0.500) & (V <= 0.880)
    bcol = mix(P["wine_lo"], P["wine_hi"], 0.18 + 0.82 * pl)
    bcol = bcol * (0.70 + 0.50 * np.clip(1 - (V - 0.50) / 0.38, 0, 1))[..., None]
    col = np.where(band[..., None], bcol, col)

    cx, cy, r = 0.485 * W, 0.345 * W, 0.150 * W
    d = np.hypot(XS - cx, YS - cy)
    cres = (d <= r) & ~(np.hypot(XS - (cx - 0.054 * W), YS - (cy - 0.028 * W)) <= r * 0.94)
    col = mix(col, mix(P["peri"], P["cream"], 0.70), (0.75 * glow(d, r, 0.075 * W))[..., None])
    col = np.where(cres[..., None], P["cream"], col)
    col = stars(col, [(0.660, 0.185, 0.0080, 0.70), (0.315, 0.245, 0.0060, 0.55)],
                P["cream"])

    d0 = np.hypot(XS - CENT, YS - CENT)
    col = mix(col, P["plum_hi"], (0.80 * glow(d0, 0.468 * W, 0.013 * W))[..., None])
    return finish(vignette(col, 0.28), disc)


VARIANTS = [
    ("logo-A-velvet-drape.png", "A", "VELVET DRAPE", v_a_velvet_drape),
    ("logo-B-curtain-moon.png", "B", "CURTAIN + MOON", v_b_curtain_moon),
    ("logo-C-folded-velvet.png", "C", "FOLDED VELVET", v_c_folded_velvet),
    ("logo-D-tufted-velvet.png", "D", "TUFTED VELVET", v_d_tufted_velvet),
    ("logo-E-valance-moon.png", "E", "VALANCE + MOON", v_e_valance_moon),
    ("logo-F-velvet-pillow.png", "F", "VELVET PILLOW", v_f_velvet_pillow),
    ("logo-G-fold-mark.png", "G", "FOLD MARK (flat)", v_g_fold_mark),
    ("logo-H-moon-disc.png", "H", "MOON DISC", v_h_moon_disc),
]


# ------------------------------------------------------------------ sheets ---
def font(size):
    for path in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def sheet(images, bg, ink, name):
    pad, gap, cols = 28, 30, 3
    tile, label_h = S, 44
    rows = (len(images) + cols - 1) // cols
    cw, ch = tile + gap, tile + label_h + gap
    SW, SH = pad * 2 + cols * cw - gap, pad * 2 + rows * ch - gap
    sh = Image.new("RGB", (SW, SH), bg)
    d = ImageDraw.Draw(sh)
    f = font(30)
    for i, (key, title, img) in enumerate(images):
        r, c = divmod(i, cols)
        x = pad + c * cw
        y = pad + r * ch
        assert x + tile <= SW - pad, "tile overflows right edge"
        assert y + tile + label_h <= SH - pad, "tile overflows bottom edge"
        sh.paste(img, (x, y), img)
        d.text((x + 2, y + tile + 8), "%s  %s" % (key, title), fill=ink, font=f)
    sh.save(os.path.join(OUT_DIR, name), "PNG", optimize=True)
    print("wrote", os.path.join(OUT_DIR, name))


def small_strip(images, bg, ink, name):
    pad, gap, small_h, label_h = 28, 26, 48, 34
    SW = pad * 2 + len(images) * (128 + gap) - gap
    SH = pad * 2 + 128 + 12 + small_h + label_h
    sh = Image.new("RGB", (SW, SH), bg)
    d = ImageDraw.Draw(sh)
    f = font(26)
    for i, (key, _title, img) in enumerate(images):
        x = pad + i * (128 + gap)
        assert x + 128 <= SW - pad, "small tile overflows right edge"
        assert pad + 128 + 12 + small_h + label_h <= SH - pad, "strip overflows bottom edge"
        big = img.resize((128, 128), Image.LANCZOS)
        sh.paste(big, (x, pad), big)
        for j, sz in enumerate((48, 24)):
            t = img.resize((sz, sz), Image.LANCZOS)
            sh.paste(t, (x + j * (small_h + 8), pad + 128 + 12 + small_h - sz), t)
        d.text((x + 2, pad + 128 + 12 + small_h + 2), key, fill=ink, font=f)
    sh.save(os.path.join(OUT_DIR, name), "PNG", optimize=True)
    print("wrote", os.path.join(OUT_DIR, name))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    P = load_palette()
    made = []
    for fname, key, title, fn in VARIANTS:
        img = fn(P)
        img.save(os.path.join(OUT_DIR, fname), "PNG", optimize=True)
        made.append((key, title, img))
        print("wrote", os.path.join(OUT_DIR, fname))

    sheet(made, (245, 240, 243), (58, 42, 50), "preview-sheet-light.png")
    sheet(made, (24, 16, 28), (238, 228, 232), "preview-sheet-dark.png")
    small_strip(made, (245, 240, 243), (58, 42, 50), "preview-small-sizes.png")
    print("done ->", os.path.abspath(OUT_DIR))


if __name__ == "__main__":
    main()
