"""Copies an exercise picture with a different number in its corner badge.

The PDF photos carry the exercise number of the original program in a white or black square in the top-left
corner (size and position differ per photo); the drawn pictures have a white rounded badge at (8, 8)-(35, 35).
find_badge() locates that square, rebadge() paints it over in the same colour and writes the new number.

Usage:  py tools/rebadge.py SRC.webp DST.webp N
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "assets")
FONT_B = r"C:\Windows\Fonts\arialbd.ttf"


# Photos whose black badge touches black gym equipment, so the search can't separate it: boxes measured by eye.
OVERRIDES = {
    "B_1.webp": ((9, 4, 55, 49), "black"),
    "B_2.webp": ((8, 4, 56, 48), "black"),
    "B_3.webp": ((8, 4, 55, 49), "black"),
    "B_6.webp": ((8, 30, 54, 76), "black"),
}


def _white(p):
    return min(p) >= 226 and max(p) - min(p) <= 22


def _black(p):
    return max(p) <= 55


def find_badge(im, area=112):
    """Returns ((x0, y0, x1, y1), 'white' | 'black') of the number square in the top-left corner, or None."""
    region = im.crop((0, 0, min(area, im.width), min(area, im.height))).convert("RGB")
    w, h = region.size
    px = region.load()
    best = None
    for name, test in (("white", _white), ("black", _black)):
        mask = [[test(px[x, y]) for x in range(w)] for y in range(h)]
        seen = [[False] * w for _ in range(h)]
        for y in range(h):
            for x in range(w):
                if not mask[y][x] or seen[y][x]:
                    continue
                stack, pts = [(x, y)], []
                seen[y][x] = True
                while stack:
                    cx, cy = stack.pop()
                    pts.append((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and mask[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((nx, ny))
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
                bw, bh = x1 - x0 + 1, y1 - y0 + 1
                if not (22 <= bw <= 80 and 22 <= bh <= 84 and 0.6 <= bw / bh <= 1.6):
                    continue
                fill = len(pts) / (bw * bh)
                # a badge is a solid square with a digit-shaped hole in it
                if not 0.5 <= fill <= 0.96:
                    continue
                if best is None or len(pts) > best[0]:
                    best = (len(pts), (x0, y0, x1, y1), name)
    return (best[1], best[2]) if best else None


def rebadge(src, dst, n):
    im = Image.open(src).convert("RGB")
    found = OVERRIDES.get(os.path.basename(src)) or find_badge(im)
    if not found:
        raise SystemExit(f"no badge found in {src}")
    (x0, y0, x1, y1), colour = found
    bg, fg = ((255, 255, 255), (12, 12, 12)) if colour == "white" else ((12, 12, 12), (255, 255, 255))
    s = 4  # draw the new badge 4x larger and scale it down for smooth edges
    bw, bh = x1 - x0 + 3, y1 - y0 + 3
    tile = Image.new("RGB", (bw * s, bh * s), bg)
    d = ImageDraw.Draw(tile)
    drawn = (x0, y0) == (8, 8)  # the drawn pictures use a rounded badge on the navy background
    if drawn:
        tile.paste(im.crop((x0 - 1, y0 - 1, x0 - 1 + bw, y0 - 1 + bh)).resize((bw * s, bh * s)))
        d.rounded_rectangle([1 * s, 1 * s, (bw - 1) * s - 1, (bh - 1) * s - 1], radius=5 * s, fill=bg)
    font = ImageFont.truetype(FONT_B, int(min(bw, bh) * 0.68 * s))
    d.text((bw * s / 2, bh * s / 2 + s), str(n), font=font, fill=fg, anchor="mm")
    im.paste(tile.resize((bw, bh), Image.LANCZOS), (x0 - 1, y0 - 1))
    im.save(dst, "WEBP", quality=88, method=6)
    return (x0, y0, x1, y1), colour


if __name__ == "__main__":
    src, dst, n = sys.argv[1:4]
    print(rebadge(os.path.join(ASSETS, src), os.path.join(ASSETS, dst), n))
