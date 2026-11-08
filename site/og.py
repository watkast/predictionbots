"""Share cards (1200x630 PNG) for pages without a chart: Learn pages, the simulator, Reality Check, the home page.
Called by build.py; needs Pillow (falls back to no card if it is missing). Text only, brand colours, no stock imagery."""
from __future__ import annotations

from pathlib import Path

W, H = 1200, 630
PAPER, INK, MUTED, BRAND, LOSS = (238, 241, 245), (20, 24, 31), (75, 85, 99), (36, 72, 201), (184, 55, 31)
FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def _font(size: int, bold: bool = True):
    from PIL import ImageFont
    for f in (FONTS if bold else FONTS[1:]):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def _wrap(draw, text: str, font, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(title: str, kicker: str, out: Path, brand: str = "PredictionBots") -> bool:
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return False
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=BRAND)
    d.text((72, 64), kicker.upper(), font=_font(26), fill=LOSS)
    size = 64
    while size > 36:
        f = _font(size)
        lines = _wrap(d, title, f, W - 144)
        if len(lines) * size * 1.18 <= 360:
            break
        size -= 4
    y = 120
    for ln in lines[:6]:
        d.text((72, y), ln, font=f, fill=INK)
        y += int(size * 1.18)
    d.text((72, H - 92), brand, font=_font(34), fill=INK)
    d.text((72, H - 50), "We don't predict. We measure.", font=_font(24, bold=False), fill=MUTED)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return True


if __name__ == "__main__":
    card("How long until your balance is $0 in this market?", "Simulator", Path("/tmp/og-test.png"))
    print("ok")
