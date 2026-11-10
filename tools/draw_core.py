"""C7 core picture that replaced the carries (no load in the hands): side plank hip lift (public/assets/C_7s.webp).

Usage:  py tools/draw_core.py
"""
from draw_exercises import ACCENT, Pic, side_figure
from draw_variants import side_plank, standing_view


def c7s():
    """Side plank hip lift: hips lowered towards the floor, then lifted until the body is straight."""
    pic, acc = Pic(), ACCENT["C"]
    for i in range(2):
        standing_view(pic, i, 1.2)
        j, _ = side_plank(i == 0)
        side_figure(pic, j)
        h = j["hip"]
        if i:
            pic.arrow((h[0] + 16, h[1] + 22), (h[0] + 24, h[1] + 8), (h[0] + 16, h[1] - 8), acc)
        else:
            pic.arrow((h[0] + 16, h[1] - 26), (h[0] + 24, h[1] - 12), (h[0] + 16, h[1] + 2), acc)
        pic.caption("1 · Nuleisk klubus žemyn" if not i else "2 · Kelk aukštai, kūnas tiesus")
    pic.badge(7)
    pic.save("C_7s.webp")


if __name__ == "__main__":
    c7s()
