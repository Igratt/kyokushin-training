"""Draws the new exercise pictures of the Hard Gym program (public/assets/G_<day><n>.webp): two panels each.

Usage:  py tools/draw_gym.py [name ...]     (no names = all)
Pictures reused from the Kyokushin program are copied with the right number by tools/make_hard_gym.py.
"""
import sys

from draw_exercises import Pic, dumbbell_side, go, side_figure
from draw_variants import CX, EQUIP, EQUIP_HI, GREY, arc_pts, cable, db_end, limb, lying_view, pulley, rect, side, stand_front, standing_view

ACC = {"A": (59, 130, 246), "B": (249, 115, 22), "C": (34, 197, 94), "D": (168, 85, 247)}


def flat_bench(pic, x0, x1, top, floor=292):
    rect(pic, x0, top, x1, top + 9, EQUIP_HI)
    rect(pic, x0 + 12, top + 9, x0 + 20, floor, EQUIP)
    rect(pic, x1 - 20, top + 9, x1 - 12, floor, EQUIP)


def ga4():
    """Single-arm dumbbell bench press, lying on a flat bench."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        lying_view(pic, i, 1.25)
        flat_bench(pic, 36, 160, 250)
        hip, sh = (136, 238), (82, 238)
        f_sh = (79, 240)
        n_knee, n_ankle = limb(hip, (194, 290), 44, 44, (184, 226))
        f_knee, f_ankle = limb(hip, (188, 291), 44, 44, (178, 228))
        if i == 0:
            n_elbow, n_hand = limb(sh, (92, 226), 30, 27, (100, 268))
        else:
            n_elbow, n_hand = limb(sh, (84, 184), 30, 27, (100, 210))
        f_elbow, f_hand = limb(f_sh, (118, 244), 30, 27, (96, 262))
        j = dict(hip=hip, sh=sh, head=(62, 237), n_knee=n_knee, n_ankle=n_ankle, n_toe=go(n_ankle, 0, 18),
                 f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, 0, 18), f_sh=f_sh, n_elbow=n_elbow, n_hand=n_hand,
                 f_elbow=f_elbow, f_hand=f_hand)
        side_figure(pic, j)
        db_end(pic, n_hand, acc)
        if i:
            pic.arrow((114, 232), (120, 206), (108, 186), acc)
        pic.caption("1 · Hantelis prie krūtinės" if not i else "2 · Spausk aukštyn")
    pic.badge(4)
    pic.save("G_A4.webp")


def ga5():
    """Single-arm dumbbell row: knee and hand on a bench, flat back."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i, 1.1)
        top = 254
        rect(pic, 52, top, 212, top + 9, EQUIP_HI)
        rect(pic, 64, top + 9, 72, 300, EQUIP)
        rect(pic, 192, top + 9, 200, 300, EQUIP)
        hip, sh = (150, 206), (96, 208)
        f_sh = (93, 210)
        f_knee, f_ankle = (150, 249), (194, 249)
        n_knee, n_ankle = limb(hip, (158, 292), 44, 44, (136, 250))
        f_elbow, f_hand = limb(f_sh, (92, 250), 30, 27, (80, 230))
        if i == 0:
            n_elbow, n_hand = limb(sh, (98, 264), 30, 27, (104, 236))
        else:
            n_elbow, n_hand = limb(sh, (126, 216), 30, 27, (112, 176))
        j = dict(hip=hip, sh=sh, head=go(sh, 176, 20), n_knee=n_knee, n_ankle=n_ankle, n_toe=go(n_ankle, 180, 18),
                 f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, -20, 14), f_sh=f_sh, n_elbow=n_elbow, n_hand=n_hand,
                 f_elbow=f_elbow, f_hand=f_hand)
        side_figure(pic, j)
        dumbbell_side(pic, n_hand, acc)
        if i:
            pic.arrow((146, 266), (154, 244), (142, 226), acc)
        pic.caption("1 · Ranka ištiesta žemyn" if not i else "2 · Trauk alkūnę aukštyn")
    pic.badge(5)
    pic.save("G_A5.webp")


def ga6():
    """Lateral raise, front view."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i, 1.1)
        if i == 0:
            h = stand_front(pic, (CX - 34, 212), (CX + 34, 212), l_elbow=(-6, 0), r_elbow=(6, 0))
        else:
            h = stand_front(pic, (CX - 80, 162), (CX + 80, 162), l_elbow=(-2, -8), r_elbow=(2, -8))
        for hand in (h["lh"], h["rh"]):
            db_end(pic, hand, acc)
        if i:
            for s in (-1, 1):
                pic.arrow((CX + s * 44, 226), (CX + s * 80, 220), (CX + s * 84, 186), acc)
        pic.caption("1 · Hanteliai prie šonų" if not i else "2 · Kelk iki pečių aukščio")
    pic.badge(6)
    pic.save("G_A6.webp")


def ga7():
    """Dumbbell curl, one arm at a time, side view."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i, 1.1)
        j = side((124, 204), (128, 292), (122, 292), (128, 258), (122, 260), elbow=(-4, 0), f_elbow=(-4, 0))
        sh = j["sh"]
        elbow = (sh[0] + 2, sh[1] + 30)
        hand = (sh[0] + 4, sh[1] + 57) if i == 0 else go(elbow, 64, 27)
        j.update(n_elbow=elbow, n_hand=hand)
        side_figure(pic, j)
        dumbbell_side(pic, hand, acc)
        if i:
            pic.arrow((elbow[0] + 36, elbow[1] + 24), (elbow[0] + 44, elbow[1] - 4), (elbow[0] + 26, elbow[1] - 24), acc)
        pic.caption("1 · Ranka žemyn" if not i else "2 · Lenk, alkūnė prie šono")
    pic.badge(7)
    pic.save("G_A7.webp")


def gc2():
    """Incline dumbbell press."""
    pic, acc = Pic(), ACC["C"]
    for i in range(2):
        standing_view(pic, i, 1.1)
        seat = 246
        back0 = (176, seat + 2)
        pic.capsule(back0, go(back0, 145, 116), 11, EQUIP_HI)
        rect(pic, 168, seat, 226, seat + 9, EQUIP_HI)
        rect(pic, 190, seat + 9, 200, 300, EQUIP)
        hip = (180, 236)
        sh = go(hip, 145, 54)
        f_sh = (sh[0] - 3, sh[1] + 2)
        n_knee, n_ankle = limb(hip, (236, 292), 44, 44, (232, 230))
        f_knee, f_ankle = limb(hip, (230, 292), 44, 44, (226, 232))
        if i == 0:
            n_elbow = go(sh, -122, 29)
            n_hand = go(n_elbow, 58, 27)
        else:
            n_elbow = go(sh, 64, 29)
            n_hand = go(n_elbow, 70, 27)
        f_elbow, f_hand = (n_elbow[0] - 3, n_elbow[1] + 2), (n_hand[0] - 3, n_hand[1] + 2)
        j = dict(hip=hip, sh=sh, head=go(sh, 145, 20), n_knee=n_knee, n_ankle=n_ankle, n_toe=go(n_ankle, 0, 18),
                 f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, 0, 18), f_sh=f_sh, n_elbow=n_elbow, n_hand=n_hand,
                 f_elbow=f_elbow, f_hand=f_hand)
        side_figure(pic, j)
        db_end(pic, n_hand, acc)
        if i:
            pic.arrow((196, 206), (204, 180), (190, 158), acc)
        pic.caption("1 · Hanteliai prie krūtinės" if not i else "2 · Spausk aukštyn")
    pic.badge(2)
    pic.save("G_C2.webp")


def gc7():
    """Cable triceps pushdown, elbows fixed at the sides."""
    pic, acc = Pic(), ACC["C"]
    for i in range(2):
        standing_view(pic, i, 1.1)
        pic.capsule((210, 30), (210, 300), 8, EQUIP)
        pulley(pic, (198, 58))
        j = side((112, 206), (118, 292), (110, 292), (150, 190), (146, 192), torso_ang=84, head_ang=84, elbow=(-6, 6))
        sh = j["sh"]
        elbow = (sh[0] + 6, sh[1] + 30)
        hand = go(elbow, 22, 27) if i == 0 else go(elbow, -76, 27)
        j.update(n_elbow=elbow, n_hand=hand, f_elbow=(elbow[0] - 3, elbow[1] + 1), f_hand=(hand[0] - 3, hand[1] + 1))
        cable(pic, (198, 58), hand)
        side_figure(pic, j)
        pic.dot(hand, 4.5, GREY)
        if i:
            pic.arrow((hand[0] + 24, hand[1] - 44), (hand[0] + 30, hand[1] - 20), (hand[0] + 16, hand[1] - 4), acc)
        pic.caption("1 · Alkūnės prie šonų" if not i else "2 · Spausk žemyn iki galo")
    pic.badge(7)
    pic.save("G_C7.webp")


def gd3():
    """Barbell hip thrust: upper back on a bench, feet on the floor."""
    pic, acc = Pic(), ACC["D"]
    for i in range(2):
        standing_view(pic, i, 1.15)
        top = 240
        rect(pic, 18, top, 96, top + 9, EQUIP_HI)
        rect(pic, 28, top + 9, 36, 300, EQUIP)
        rect(pic, 78, top + 9, 86, 300, EQUIP)
        sh = (90, 232)
        hip = (122, 276) if i == 0 else (142, 240)
        ankle = (184, 292)
        n_knee, n_ankle = limb(hip, ankle, 44, 44, (hip[0] + 44, hip[1] - 44))
        f_knee, f_ankle = (n_knee[0] - 5, n_knee[1] + 2), (n_ankle[0] - 7, n_ankle[1])
        bar = (hip[0] + 2, hip[1] - 12)
        n_elbow, n_hand = limb(sh, bar, 30, 27, (sh[0] + 22, sh[1] + 22))
        f_sh = (sh[0] - 3, sh[1] + 2)
        f_elbow, f_hand = limb(f_sh, (bar[0] - 2, bar[1] + 1), 30, 27, (sh[0] + 18, sh[1] + 24))
        j = dict(hip=hip, sh=sh, head=go(sh, 150 if i == 0 else 160, 20), n_knee=n_knee, n_ankle=n_ankle,
                 n_toe=go(n_ankle, 0, 20), f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, 0, 20), f_sh=f_sh,
                 n_elbow=n_elbow, n_hand=n_hand, f_elbow=f_elbow, f_hand=f_hand)
        side_figure(pic, j)
        pic.path(arc_pts(bar, 25, 0, 360, 40), acc, 4.5)
        pic.dot(bar, 5, GREY)
        if i:
            pic.arrow((hip[0] - 6, 292), (hip[0] - 12, 276), (hip[0] - 4, 262), acc)
        pic.caption("1 · Nugara ant suolo, klubai žemai" if not i else "2 · Kelk klubus, spausk sėdmenis")
    pic.badge(3)
    pic.save("G_D3.webp")


ALL = dict(ga4=ga4, ga5=ga5, ga6=ga6, ga7=ga7, gc2=gc2, gc7=gc7, gd3=gd3)

if __name__ == "__main__":
    for key in sys.argv[1:] or list(ALL):
        ALL[key]()
