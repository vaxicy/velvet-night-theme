"""Compose every Velvet Night store asset from one HTML/CSS source.

Layering and geometry mirror the real installed-Chrome capture kept at
store-assets/references/real-browser-capture.png (1080x646 of a maximized
window). The window is authored in that capture's pixel space and scaled once
per output:

  screenshot-1     1280x800  dsf 1280/1080, window authored 1080x675 (16:10)
  screenshot-2     1280x800  intro + 2x2 colour cards
  promo 440x280    brand tile
  promo 1400x560   marquee with a scaled window (same HTML as screenshot-1)

Theme-controlled colors are read from manifest.json (single source of truth).
Chrome-painted UI colors are hardcoded from the real capture; every value below
was sampled with scripts/sample-reference-colors.py.
"""
from pathlib import Path
import base64
import hashlib
import json
import re

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'store-assets' / 'references'
OUT.mkdir(parents=True, exist_ok=True)

C = json.loads((ROOT / 'manifest.json').read_text('utf-8-sig'))['theme']['colors']


def color(key):
    return '#%02X%02X%02X' % tuple(C[key])


# ---------------------------------------------------------------------------
# Chrome-painted UI: sampled from the real install, NOT derived from the theme.
# ---------------------------------------------------------------------------
CAPTION_BG = '#71556D'      # lighter strip behind the window control buttons
CAPTION_GLYPH = '#6D4757'   # – ▢ ✕ glyphs
OMNI_BG = '#5E5360'         # omnibox pill (Chrome derives it, not omnibox_background)
OMNI_TEXT = '#E8E1E2'       # omnibox placeholder
OMNI_CHIP = '#726373'       # the round "G" chip at the omnibox' left end
LOGO = '#FFFFFF'            # NTP Google wordmark (ntp_logo_alternate: 1)
SEARCH_BG = '#FFFFFF'       # NTP search box
SEARCH_TEXT = '#5F6368'     # NTP placeholder / grey glyphs
TILE_BG = '#201429'         # Chrome-tinted shortcut circle
TILE_LABEL = '#C4C1C6'      # shortcut labels, NTP top-right links
GRID_ICON = '#FFFFFF'       # NTP top-right apps grid
PILL_BG = '#202124'         # Customize Chrome pill
PILL_FG = '#A8C7FA'         # its label + pencil
NAV_ICON = color('toolbar_button_icon')
G_RED, G_BLUE, G_YELLOW, G_GREEN = '#EA4335', '#4285F4', '#FBBC05', '#34A853'

VARS = f""":root{{
  --frame:{color('frame')};
  --frame-inactive:{color('frame_inactive')};
  --toolbar:{color('toolbar')};
  --bg-tab:{color('background_tab')};
  --tab-text:{color('tab_text')};
  --tab-bg-text:{color('tab_background_text')};
  --nav-icon:{NAV_ICON};
  --button:{color('button_background')};
  --bookmark-text:{color('bookmark_text')};
  --ntp:{color('ntp_background')};
  --ntp-text:{color('ntp_text')};
  --link:{color('ntp_link')};
  --caption:{CAPTION_BG};
  --caption-glyph:{CAPTION_GLYPH};
  --omni:{OMNI_BG};
  --omni-text:{OMNI_TEXT};
  --omni-chip:{OMNI_CHIP};
  --logo:{LOGO};
  --search:{SEARCH_BG};
  --search-text:{SEARCH_TEXT};
  --tile:{TILE_BG};
  --tile-label:{TILE_LABEL};
  --grid:{GRID_ICON};
  --pill:{PILL_BG};
  --pill-fg:{PILL_FG};
  --ui-text:#B9B4BB;
  /* neutral gallery backdrop for screenshot-2 only: deliberately NOT one of
     the theme colours, otherwise the swatch painted with that colour would
     dissolve into the page */
  --sheet:#2B262E;
}}"""

CSS = VARS + """
*{box-sizing:border-box}
body{margin:0;overflow:hidden;font-family:Arial,'Helvetica Neue',sans-serif}
svg{display:block}

/* ================= browser window (authored 1080 wide) ================= */
.window{width:1080px;background:var(--ntp);position:relative;overflow:hidden;display:flex;flex-direction:column}
.frameband{height:5px;background:var(--frame);flex:0 0 auto}
.tabstrip{height:27px;background:var(--frame);display:flex;align-items:flex-end;padding-left:33px;
          position:relative;flex:0 0 auto}
.tab{width:138px;height:26px;border-radius:9px 9px 0 0;margin-right:8px;padding:0 12px 0 30px;
     display:flex;align-items:center;font-size:11.5px;color:var(--tab-bg-text);position:relative;
     white-space:nowrap;overflow:hidden}
.tab.on{background:var(--toolbar);color:var(--tab-text)}
.tab i{position:absolute;left:10px;top:7px;width:12px;height:12px;border-radius:3px;background:rgba(242,235,236,.28)}
.tab.on i{background:rgba(27,17,34,.45)}
.tab .x{margin-left:auto;opacity:.85}
.caption{position:absolute;right:0;top:0;width:107px;height:32px;background:var(--caption);
         display:flex;align-items:center;justify-content:space-around;padding:0 14px}
.toolbar{height:31px;background:var(--toolbar);display:flex;align-items:center;position:relative;flex:0 0 auto}
.nav{display:flex;align-items:center;gap:16px;padding-left:15px}
.omni{position:absolute;left:128px;top:4px;width:672px;height:26px;border-radius:13px;background:var(--omni);
      display:flex;align-items:center;padding-right:12px;overflow:hidden}
.chip{width:22px;height:22px;border-radius:50%;background:var(--omni-chip);margin-left:2px;
      display:flex;align-items:center;justify-content:center;flex:0 0 auto}
.omni .ph{font-size:14px;color:var(--omni-text);margin-left:16px;flex:1;white-space:nowrap;overflow:hidden}
.omni .right{display:flex;align-items:center;gap:12px}
.tools{position:absolute;right:8px;top:0;height:31px;display:flex;align-items:center;gap:14px}
.ext{width:16px;height:16px;border-radius:4px}
.badge{position:relative}
.badge b{position:absolute;right:-4px;bottom:-5px;background:#1F1F1F;color:#E7E1E3;font-size:8px;
         font-weight:normal;border-radius:6px;padding:0 3px;line-height:11px}
.divider{width:1px;height:15px;background:rgba(242,235,236,.30)}
.avatar{width:18px;height:18px;border-radius:50%;background:conic-gradient(#EA4335,#FBBC05,#34A853,#4285F4,#EA4335)}
.bookmarks{height:32px;background:var(--toolbar);display:flex;align-items:center;gap:18px;
           padding:0 12px;font-size:11.5px;color:var(--bookmark-text);flex:0 0 auto}
.bookmarks .sep{width:1px;height:14px;background:rgba(242,235,236,.28)}
.bm{display:flex;align-items:center;gap:6px;white-space:nowrap}

/* ================= new tab page ================= */
.ntp{flex:1;position:relative;background:var(--ntp)}
.gtop{position:absolute;top:13px;right:9px;display:flex;align-items:center;gap:16px;font-size:12.5px;color:var(--tile-label)}
.glogo{position:absolute;top:92px;left:0;right:0;text-align:center;font-family:'Google Sans','Product Sans',Arial,sans-serif;
       font-size:64px;font-weight:500;letter-spacing:-2.6px;color:var(--logo);line-height:1}
.nsearch{position:absolute;top:187px;left:50%;margin-left:-262px;width:525px;height:34px;border-radius:17px;
         background:var(--search);display:flex;align-items:center;padding:0 13px 0 16px;gap:11px}
.nsearch .ph{flex:1;font-size:15px;color:var(--search-text);white-space:nowrap;overflow:hidden}
.shortcuts{position:absolute;top:249px;left:0;right:0;display:flex;justify-content:center;gap:48px}
.shortcut{width:76px;text-align:center;font-size:12px;color:var(--tile-label)}
.shortcut .circle{width:32px;height:32px;border-radius:50%;background:var(--tile);margin:0 auto 16px;
                  display:flex;align-items:center;justify-content:center}
.shortcut .lbl{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.customize{position:absolute;right:10px;bottom:12px;height:24px;border-radius:12px;background:var(--pill);
           color:var(--pill-fg);display:flex;align-items:center;gap:6px;padding:0 12px;font-size:11.5px}

/* ================= promo: 440x280 brand tile ================= */
.tile{width:440px;height:280px;background:var(--frame);position:relative;overflow:hidden;text-align:center;color:var(--tab-text)}
.tile .plate{width:92px;height:92px;border-radius:24px;background:#FFFFFF;margin:24px auto 0;display:flex;
             align-items:center;justify-content:center;box-shadow:0 6px 18px rgba(20,10,20,.22)}
.tile .plate img{width:68px;height:68px;display:block}
.tile h1{font-family:Georgia,serif;font-weight:normal;font-size:36px;margin:13px 0 0}
.tile .kicker{font-size:12px;letter-spacing:5px;margin-top:8px;color:var(--tab-bg-text)}
.tile p{font-size:13.5px;margin:15px 0 0;color:var(--bookmark-text)}
.tile:after{content:'';position:absolute;left:0;right:0;bottom:0;height:14px;background:var(--toolbar)}

/* ================= promo: 1400x560 marquee ================= */
.marquee{width:1400px;height:560px;background:var(--ntp);position:relative;overflow:hidden;text-align:center;
         border-top:8px solid var(--frame)}
.marquee h1{font-family:Georgia,serif;font-weight:normal;font-size:47px;margin:24px 0 0;color:var(--ntp-text)}
.marquee p{font-size:17px;margin:9px 0 0;color:var(--ui-text)}
.marquee .frame{position:absolute;top:139px;left:298px;width:804px;height:374px;overflow:hidden;
                border:2px solid var(--frame);border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.35)}
.marquee .frame .window{transform:scale(.740741);transform-origin:top left}

/* ================= screenshot 2: introduction + colour cards ================= */
.intro{width:1280px;height:800px;background:var(--sheet);padding:64px 74px;position:relative}
.intro .kicker{font-size:12px;letter-spacing:4px;color:var(--tile-label)}
.intro h1{font-family:Georgia,serif;font-weight:normal;font-size:54px;margin:15px 0 0;color:var(--ntp-text)}
.intro .lead{font-size:21px;margin:13px 0 0;color:var(--tab-bg-text)}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:40px}
.card{height:228px;border-radius:18px;padding:30px;display:flex;flex-direction:column;justify-content:flex-end;
      border:1px solid rgba(242,235,236,.16);box-shadow:inset 0 0 0 1px rgba(0,0,0,.05)}
.card strong{font-size:28px}
.card span{font-size:16px;margin-top:9px;opacity:.92}
.intro .chips{font-size:16px;margin-top:34px;color:var(--tile-label)}
"""


# ------------------------------------------------------------------ artwork --
def g_mark(size):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 48 48">'
            f'<path fill="{G_RED}" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>'
            f'<path fill="{G_BLUE}" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>'
            f'<path fill="{G_YELLOW}" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>'
            f'<path fill="{G_GREEN}" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>')


def google_g_white(size):
    """The white 'G' inside the omnibox chip (sampled #FFFFFF)."""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 48 48">'
            f'<path fill="{LOGO}" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>'
            f'<path fill="{LOGO}" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>'
            f'<path fill="{LOGO}" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>'
            f'<path fill="{LOGO}" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>')


def apps(size, fill):
    dots = ''.join(f'<circle cx="{3 + 9 * (i % 3)}" cy="{3 + 9 * (i // 3)}" r="2.6"/>' for i in range(9))
    return f'<svg width="{size}" height="{size}" viewBox="0 0 30 30" fill="{fill}">{dots}</svg>'


def mic(size, fill):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<rect x="9" y="2" width="6" height="11" rx="3" fill="{fill}"/>'
            f'<path d="M5 11v1a7 7 0 0 0 14 0v-1" fill="none" stroke="{fill}" stroke-width="2"/>'
            f'<path d="M12 19v3" stroke="{fill}" stroke-width="2"/></svg>')


def win_controls():
    g = f'stroke="{CAPTION_GLYPH}" stroke-width="1.4" stroke-linecap="round" fill="none"'
    return ('<div class="caption">'
            f'<svg width="10" height="10" viewBox="0 0 12 12"><path d="M1.4 6h9.2" {g}/></svg>'
            f'<svg width="9" height="9" viewBox="0 0 12 12"><rect x="1.6" y="1.6" width="8.8" height="8.8" rx="2" {g}/></svg>'
            f'<svg width="10" height="10" viewBox="0 0 12 12"><path d="M2.3 2.3l7.4 7.4M9.7 2.3L2.3 9.7" {g}/></svg>'
            '</div>')


def nav_icons():
    g = f'stroke="{NAV_ICON}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" fill="none"'
    return ('<div class="nav">'
            f'<svg width="16" height="16" viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7" {g}/></svg>'
            f'<svg width="16" height="16" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" {g}/></svg>'
            f'<svg width="16" height="16" viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-2.6-5.9" {g}/><path d="M20 3.6V7h-3.4" {g}/></svg>'
            f'<svg width="16" height="16" viewBox="0 0 24 24"><path d="M4 11l8-7 8 7v8.5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z" {g}/></svg>'
            '</div>')


def tab(title, active=False, title_width=None):
    cls = 'tab on' if active else 'tab'
    style = f' style="max-width:{title_width}px"' if title_width else ''
    ink = color('tab_text') if active else color('tab_background_text')
    return (f'<div class="{cls}"><i></i><span{style}>{title}</span>'
            f'<span class="x"><svg width="9" height="9" viewBox="0 0 12 12">'
            f'<path d="M2 2l8 8M10 2l-8 8" stroke="{ink}" stroke-width="1.6" stroke-linecap="round"/></svg></span></div>')


def bookmark_bar():
    g = f'stroke="{color("bookmark_text")}" stroke-width="1.4" stroke-linejoin="round" fill="none"'
    folder = (f'<svg width="13" height="13" viewBox="0 0 24 24">'
              f'<path d="M3 7.5h6l2 2.5h10v8.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z" {g}/></svg>')
    items = ''.join(f'<div class="bm">{folder}{name}</div>'
                    for name in ('Work', 'Reference', 'Design', 'Reading', 'Docs', 'Bookmarks'))
    return ('<div class="bookmarks">' + apps(14, color('bookmark_text'))
            + '<div class="sep"></div>' + items + '</div>')


def toolbar_row():
    # three neutral extension tiles; the capture's own extensions are the user's,
    # so they are redrawn as generic art of the same size
    chips = ('<div class="ext" style="background:#4C8DF6"></div>'
             '<div class="ext badge" style="background:#E2604A"><b>12</b></div>'
             '<div class="ext" style="background:#3FA46A"></div>')
    return ('<div class="toolbar">' + nav_icons()
            + f'<div class="omni"><div class="chip">{google_g_white(15)}</div>'
            + '<span class="ph">Search Google or type a URL</span>'
            + f'<div class="right">{mic(15, OMNI_TEXT)}{g_mark(15)}</div></div>'
            + f'<div class="tools">{chips}'
            + f'<svg width="16" height="16" viewBox="0 0 24 24"><path d="M9 3h6v3.2c0 .6.3 1.2.8 1.5l4.2 2.6v4.4l-4.2 2.6c-.5.3-.8.9-.8 1.5V21H9v-3.2c0-.6-.3-1.2-.8-1.5L4 13.7V9.3l4.2-2.6c.5-.3.8-.9.8-1.5z" fill="none" stroke="{color("toolbar_button_icon")}" stroke-width="1.5" stroke-linejoin="round"/></svg>'
            + '<div class="divider"></div>'
            + f'<svg width="15" height="15" viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4.6L6 21z" fill="none" stroke="{color("toolbar_button_icon")}" stroke-width="1.5" stroke-linejoin="round"/></svg>'
            + f'<div class="avatar"></div>'
            + f'<svg width="14" height="14" viewBox="0 0 24 24">'
            + ''.join(f'<circle cx="12" cy="{5 + 7 * i}" r="1.8" fill="{color("toolbar_button_icon")}"/>' for i in range(3))
            + '</svg></div></div>')


def ntp():
    yt = (f'<svg width="18" height="18" viewBox="0 0 24 24">'
          f'<rect x="1" y="5" width="22" height="14" rx="4.4" fill="{G_RED}"/>'
          f'<path d="M10 8.8l6 3.2-6 3.2z" fill="#FFFFFF"/></svg>')
    cws = (f'<svg width="18" height="18" viewBox="0 0 24 24">'
           f'<circle cx="12" cy="12" r="11" fill="#FFFFFF"/>'
           f'<path d="M12 1a11 11 0 0 1 9.53 5.5L12 12z" fill="{G_RED}"/>'
           f'<path d="M21.53 6.5A11 11 0 0 1 12 23L12 12z" fill="{G_GREEN}"/>'
           f'<path d="M12 23A11 11 0 0 1 2.47 17.5L12 12z" fill="{G_YELLOW}"/>'
           f'<circle cx="12" cy="12" r="5" fill="{G_BLUE}"/><circle cx="12" cy="12" r="2.1" fill="#FFFFFF"/></svg>')
    plus = (f'<svg width="15" height="15" viewBox="0 0 24 24">'
            f'<path d="M12 5v14M5 12h14" stroke="{GRID_ICON}" stroke-width="2.2" stroke-linecap="round"/></svg>')
    short = ('<div class="shortcuts">'
             f'<div class="shortcut"><div class="circle">{yt}</div><div class="lbl">YouTube</div></div>'
             f'<div class="shortcut"><div class="circle">{cws}</div><div class="lbl">Chrome Web Store</div></div>'
             f'<div class="shortcut"><div class="circle">{plus}</div><div class="lbl">Add shortcut</div></div>'
             '</div>')
    gtop = ('<div class="gtop"><span>Images</span>' + apps(15, GRID_ICON) + '</div>')
    nsearch = ('<div class="nsearch">'
               f'<svg width="17" height="17" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.6" fill="none" stroke="{SEARCH_TEXT}" stroke-width="2"/><path d="M15.6 15.6l5 5" stroke="{SEARCH_TEXT}" stroke-width="2" stroke-linecap="round"/></svg>'
               '<span class="ph">Search Google or type a URL</span>'
               + mic(16, SEARCH_TEXT) + g_mark(17) + '</div>')
    customize = ('<div class="customize">'
                 f'<svg width="12" height="12" viewBox="0 0 24 24"><path d="M4 20l4.2-1.1L20 7.1 16.9 4 5.1 15.8z" fill="none" stroke="{PILL_FG}" stroke-width="2" stroke-linejoin="round"/></svg>'
                 'Customize Chrome</div>')
    return ('<div class="ntp">' + gtop + '<div class="glogo">Google</div>'
            + nsearch + short + customize + '</div>')


def window(height=675):
    tabs = ('Project roadmap', '(1) Excel for Data A', 'ThemeBake \u2014 Cre', 'Chrome Web Store',
            'Extensions', 'New Tab')
    strip = ('<div class="frameband"></div><div class="tabstrip">'
             + ''.join(tab(t, i == len(tabs) - 1, 118 if i == 1 else None) for i, t in enumerate(tabs))
             + win_controls() + '</div>')
    return (f'<div class="window" style="height:{height}px">' + strip + toolbar_row()
            + bookmark_bar() + ntp() + '</div>')


# ------------------------------------------------------------------ content --
LOGO_PNG = ROOT / 'store-assets' / 'icon-candidates' / 'logo-G-fold-mark.png'
if not LOGO_PNG.exists():
    LOGO_PNG = ROOT / 'store-assets' / 'icon.png'
LOGO_URI = 'data:image/png;base64,' + base64.b64encode(LOGO_PNG.read_bytes()).decode()

TILE = ('<div class="tile">' + f'<div class="plate"><img src="{LOGO_URI}" alt="Velvet Night logo"></div>'
        '<h1>Velvet Night</h1><div class="kicker">CHROME THEME</div>'
        '<p>Deep wine, muted plum and dusty rose.</p></div>')
MARQUEE = ('<div class="marquee"><h1>Velvet Night Theme</h1>'
           '<p>Deep wine, muted plum and dusty rose.</p>'
           '<div class="frame">' + window(height=500) + '</div></div>')

PALETTE = [
    ('Velvet Wine', 'frame', 'Window frame'),
    ('Deep Plum', 'ntp_background', 'New tab background'),
    ('Soft Mauve', 'toolbar', 'Toolbar and active tab'),
    ('Powder Rose', 'bookmark_text', 'Bookmarks and labels'),
]


def luminance(hexstr):
    r, g, b = (int(hexstr[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def readable_on(hexstr):
    """Pick the light or dark card text with the better contrast ratio."""
    lum = luminance(hexstr)
    light, dark = 0.941, 0.031
    cr_light = (light + 0.05) / (lum + 0.05)
    cr_dark = (lum + 0.05) / (dark + 0.05)
    return color('tab_text') if cr_light >= cr_dark else '#241318'


CARDS = ''.join(
    f'<div class="card" style="background:{color(k)};color:{readable_on(color(k))}">'
    f'<strong>{name}</strong><span>{color(k).upper()} \u00b7 {role}</span></div>'
    for name, k, role in PALETTE)

INTRO = ('<div class="intro"><div class="kicker">DEEP WINE AND MUTED PLUM</div>'
         '<h1>Velvet Night Theme</h1>'
         '<p class="lead">Four colors. One low-lit, luxurious space.</p>'
         '<div class="cards">' + CARDS + '</div>'
         '<p class="chips">Solid colors \u00b7 No wallpaper \u00b7 Muted, low-glare palette</p></div>')


def page(body):
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><style>'
            + CSS + '</style><body>' + body + '</body></html>')


# name, output size, design size. The window is authored in the real capture's
# pixel space (1080 wide) and rasterised with a matching device scale factor so
# the 1280x800 shot is crisp instead of being upscaled.
JOBS = [
    ('screenshot-1-browser', 1280, 800, 1080, 675, window(675)),
    ('screenshot-2-introduction', 1280, 800, 1280, 800, INTRO),
    ('promo-440x280', 440, 280, 440, 280, TILE),
    ('promo-1400x560', 1400, 560, 1400, 560, MARQUEE),
]


README = ROOT / 'README.md'
README_ASSETS = [
    'logo/logo128.png',
    'store-assets/screenshots/en/screenshot-1-browser.png',
    'store-assets/screenshots/en/screenshot-2-introduction.png',
]


def sync_readme_revisions():
    """Stamp ?rev=<content hash> onto every raw image URL in the README.

    Re-rendering an image is not enough: GitHub's raw/camo CDN and the viewer's
    browser both cache hard, so the reference itself has to change before anyone
    sees a new render. Bumping the stamp per content hash keeps it honest.
    """
    text = README.read_text('utf-8')
    for rel in README_ASSETS:
        path = ROOT / rel
        if not path.exists():
            print(f'  skipped missing {rel}')
            continue
        rev = hashlib.md5(path.read_bytes()).hexdigest()[:8]
        pattern = re.compile(
            r'(https://raw\.githubusercontent\.com/[^\s")]*' + re.escape(path.name) + r')(\?rev=[0-9a-f]+)?')
        text, hits = pattern.subn(lambda m: f'{m.group(1)}?rev={rev}', text)
        assert hits == 1, f'{rel}: expected exactly one README reference, found {hits}'
        print(f'  README {path.name} -> rev={rev}')
    README.write_text(text, 'utf-8')


def main():
    with sync_playwright() as p:
        engine = p.chromium.launch(headless=True)
        for name, w, h, dw, dh, body in JOBS:
            dsf = w / dw
            html = page(body)
            (OUT / f'{name}.html').write_text(html, 'utf-8')
            sheet = engine.new_page(device_scale_factor=dsf, viewport={'width': dw, 'height': dh})
            sheet.set_content(html)
            sheet.screenshot(path=str(OUT / f'{name}.png'))
            sheet.close()
            destination = ROOT / 'store-assets' / (
                'promo' if name.startswith('promo-') else 'screenshots/en') / (
                name.removeprefix('promo-') + '.png')
            destination.parent.mkdir(parents=True, exist_ok=True)
            temp = destination.with_suffix('.new.png')
            with Image.open(OUT / f'{name}.png') as img:
                out = img.convert('RGB')
                if out.size != (w, h):
                    print(f'  resampling {name} {out.size} -> {(w, h)}')
                    out = out.resize((w, h), Image.LANCZOS)
                assert out.size == (w, h), f'{name}: got {out.size}, expected {(w, h)}'
                assert out.mode == 'RGB', f'{name}: expected RGB, got {out.mode}'
                out.save(temp)
            temp.replace(destination)
            print(f'Rendered {name} {w}x{h}')
        engine.close()
    sync_readme_revisions()


if __name__ == '__main__':
    main()
