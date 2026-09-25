<div align="center">
  <img src="https://raw.githubusercontent.com/vaxicy/velvet-night-theme/main/logo/logo128.png" alt="Velvet Night Theme icon" width="88">
  <h1>Velvet Night Theme</h1>
  <p>A deep, low-lit Chrome theme in wine, muted plum and dusty rose.</p>
  <p>
    <img src="https://img.shields.io/badge/license-Non--Commercial-lightgrey" alt="Non-Commercial License">
    <img src="https://img.shields.io/badge/Chrome%20Web%20Store-theme-726373?logo=googlechrome" alt="Chrome Web Store">
  </p>
</div>

---

## About

Velvet Night Theme gives the browser a velvet-dark surface. A wine frame carries the window and tab strip, a muted plum toolbar and bookmark bar sit just below it, and a dark plum new-tab page keeps the reading area quiet. Dusty rose and powder-pink text colours run through the tabs, bookmarks and secondary labels.

Every layer is painted as a single flat solid colour, so the window stays uncluttered, and the text colours are tuned so tabs, toolbar, bookmarks and the address bar stay readable on each surface. The palette avoids bright whites, which makes it comfortable for evening use.

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Velvet Wine | `#69363C` | Window frame, tab strip, window buttons |
| Deep Plum | `#1B1122` | New-tab page background |
| Soft Mauve | `#726373` | Toolbar, bookmark bar, active tab |
| Shaded Wine | `#503F42` | Inactive tabs |
| Dusky Rose | `#C7A7AB` | Inactive tab labels |
| Powder Rose | `#DFCBCF` | Bookmarks and secondary labels |

## Chrome UI Notes

Some parts of the browser are painted by Chrome itself rather than by the theme manifest. The store screenshots follow what Chrome actually renders after installing this theme:

- **Google mark on the new-tab page:** Chrome draws it as one flat colour, which with this palette renders as white `#FFFFFF`.
- **Omnibox:** Chrome derives its own pill colour from the toolbar and renders it as a deeper `#5E5360`, with a round "G" chip that keeps the toolbar tone.
- **Shortcut tiles:** Chrome tints the round shortcut buttons from the new-tab background, rendering them as near-black plum `#201429`.
- **Caption corner:** Chrome lightens the frame behind the window buttons `#71556D`, so the minimize / maximize / close glyphs stay visible.

## Features

| Feature | Detail |
|---------|--------|
| 🍷 Wine and plum palette | Deep wine frame above a muted plum toolbar |
| 🌙 Low-glare dark new tab | Dark plum reading surface, no bright whites |
| 🪞 Flat color layers | Each surface is one solid colour |
| 👓 Tuned contrast | Tab, toolbar, bookmark and address-bar text stays readable |
| 🕯️ Incognito styling | A deeper wine frame keeps private windows distinct |
| 🪶 Pure theme package | A manifest and an icon |

## Install

### From source (unpacked)

1. Download or clone this repository.
2. Open Chrome and navigate to `chrome://extensions`.
3. Enable **Developer mode** in the top-right corner.
4. Click **Load unpacked** and select this folder.

### From Chrome Web Store

Search for **Velvet Night Theme** in the Chrome Web Store and install it.

## Preview

![Velvet Night Theme browser preview](https://raw.githubusercontent.com/vaxicy/velvet-night-theme/main/store-assets/screenshots/en/screenshot-1-browser.png)

![Velvet Night Theme color palette](https://raw.githubusercontent.com/vaxicy/velvet-night-theme/main/store-assets/screenshots/en/screenshot-2-introduction.png)

## Files

| File | Description |
|------|-------------|
| `manifest.json` | Chrome theme manifest (MV3) with inline `theme` config |
| `logo/logo128.png` | Theme icon (128x128, transparent background) |
| `store-assets/icon.png` | Store listing icon (128x128) |
| `store-assets/screenshots/en/` | Store listing screenshots (1280x800) |
| `store-assets/promo/` | Promo tiles (440x280 and 1400x560) |
| `store-assets/store-description.txt` | Store listing text |
| `store-assets/ASSET-NOTES.md` | How the store artwork is composed and calibrated |
| `store-assets/icon-candidates/` | Logo candidates the icon was chosen from |
| `scripts/generate-store-assets.py` | Renders every store asset from one HTML/CSS source |
| `scripts/make-logo.py` | Builds `icon.png` and `logo/logo128.png` from the chosen logo |
| `scripts/sample-reference-colors.py` | Samples Chrome-painted UI colours from a real capture |
| `scripts/crop-asset.py` | Zoom helper used while checking the rendered assets |
| `scripts/package.py` | Builds the release ZIP into the default output folder |

## Packaging

```bash
python3 scripts/package.py
```

The archive is written as `velvet-night-theme-<version>.zip` into the default output folder (two levels above the project, derived from the script location).

Packaged: `manifest.json`, `README.md`, `logo/`. Left out, because Chrome Web Store takes them as separate uploads: `store-assets/` (screenshots, promo tiles, listing text), `scripts/`, `.gitignore`, `Cached Theme.pak`. The script re-reads `manifest.json` from inside the finished archive and fails if the archive root or the referenced files are wrong.

## License

Non-Commercial License — personal use permitted.

- ✅ Personal use, modification for personal use, sharing with attribution.
- ❌ Commercial use without permission.

Commercial licensing: contact the author.
