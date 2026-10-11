"""Tiles exercise pictures 2×2 into review sheets: py tools/contact_sheet.py OUT.png A_1v A_3v ..."""
import sys

from PIL import Image

out, names = sys.argv[1], sys.argv[2:]
ims = [Image.open(f"D:/Kyokushin/public/assets/{n}.webp").convert("RGB") for n in names]
cols = 2
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (518 * cols + 10 * (cols - 1), 346 * rows + 10 * (rows - 1)), (0, 0, 0))
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * 528, (i // cols) * 356))
sheet.save(out)
print("sheet", out, sheet.size)
