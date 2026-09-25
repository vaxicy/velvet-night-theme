# Assets

Four English deliverables, all rendered from one headless-Chromium source
(`scripts/generate-store-assets.py`):

| File | Size | Content |
|------|------|---------|
| `screenshots/en/screenshot-1-browser.png` | 1280x800 | Full-window mockup of the themed browser |
| `screenshots/en/screenshot-2-introduction.png` | 1280x800 | Theme intro with the 2x2 colour cards |
| `promo/440x280.png` | 440x280 | Brand tile |
| `promo/1400x560.png` | 1400x560 | Marquee with the scaled window preview |

`icon.png` (128x128) is the logo the store listing and README use; it is built by
`scripts/make-logo.py` from the chosen candidate
`icon-candidates/logo-G-fold-mark.png` (folded velvet swatch, transparent).

## Colours

Theme-controlled colours are read from `manifest.json` (single source of truth):

| Token | Hex | Where |
|-------|-----|-------|
| frame | `#69363C` | Window frame, tab strip |
| background_tab | `#503F42` | Inactive tabs |
| toolbar | `#726373` | Toolbar, bookmark bar, active tab |
| ntp_background | `#1B1122` | New-tab page |
| tab_text / tab_background_text | `#F2EBEC` / `#C7A7AB` | Tab labels |
| bookmark_text | `#DFCBCF` | Bookmarks, secondary labels |

Chrome paints parts of its own UI and those colours were **sampled from a real
installed-Chrome capture** (`scripts/sample-reference-colors.py`, capture kept
locally at `references/real-browser-capture.png`, 1080x646):

| Element | Sampled | Note |
|---------|---------|------|
| Google mark on the new-tab page | `#FFFFFF` | `ntp_logo_alternate: 1`; Chrome computes it, it is not `ntp_text` |
| Omnibox pill | `#5E5360` | Chrome ignores `omnibox_background` (`#3D3433`) and derives this instead |
| Omnibox placeholder / glyphs | `#E8E1E2` | |
| Round "G" chip inside the omnibox | `#726373` | matches the toolbar colour, not the pill |
| Shortcut tiles (round) | `#201429` | Chrome tints them from the new-tab background |
| Shortcut labels, "Images" link | `#C4C1C6` | |
| NTP search box / its placeholder | `#FFFFFF` / `#5F6368` | |
| Customize Chrome pill | `#202124` with `#A8C7FA` label | |
| Caption strip behind the window buttons | `#71556D`, glyphs `#6D4757` | Chrome lightens the frame in that corner |
| Toolbar icons | `#EEE3E5` | = `toolbar_button_icon` |

## Layout

The window is authored in the real capture's pixel space (1080 wide, 675 tall)
and rasterised once per output with a matching device scale factor
(`1280/1080`), so the store screenshot is never upscaled:

- frame band 5px, tab strip 27px, toolbar 31px, bookmark bar 32px, new-tab rest
- omnibox at x 128-800 (h 26), nav icons x 16-115
- NTP: "Images" + apps grid top-right, Google mark y 190, search box
  x 278-803 y 282-316 (h 34), shortcut circles r 16 at y 344, labels y 392,
  Customize pill bottom-right
- promo 440x280 puts the logo on a white plate so the wine mark does not merge
  into the wine tile; the marquee reuses the same window HTML at scale .740741

Content that belongs to the browser user (their tabs, bookmarks and extensions)
is redrawn as generic English art of the same size — nothing personal ships.

## Regenerate

```bash
python3 scripts/make-logo.py             # icon.png + logo/logo128.png
python3 scripts/generate-store-assets.py # all four store images
```

Changing layout means editing `scripts/generate-store-assets.py` and re-running
the whole batch — never patching a finished PNG.
