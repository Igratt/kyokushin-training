"""Draws the new pictures of the karate power program (public/assets/P_<day><n>.webp) and the kettlebell
front rack carry that replaced the farmer carry (public/assets/C_7r.webp). Two panels each, same mannequin style.

Usage:  py tools/draw_power.py [name ...]     (no names = all)
"""
import sys

from draw_exercises import ACCENT, Pic, bezier, go, side_figure
from draw_variants import (CX, EQUIP, EQUIP_HI, GREY, band, ball, front, joint, kettlebell, post, pulley, rect,
                           shadow, side, standing_view)

ACC = ACCENT


def pa1():
    """Pogo hops: stiff ankles, quick bounces on the balls of the feet."""
    pic, acc = Pic(), ACC["A"]
    for i, lift in enumerate((0, 18)):
        standing_view(pic, i)
        y = -lift
        j = side((124, 206 + y), (126, 290 + y), (120, 290 + y), (140, 236 + y), (134, 238 + y), knee=(6, 0),
                 n_toe=-30 if lift else 0, f_toe=-30 if lift else 0, elbow=(-12, 4))
        side_figure(pic, j)
        if lift:
            shadow(pic, 124)
            pic.arrow((176, 292), (184, 262), (176, 236), acc)
        pic.caption("1 · Pirštai, keliai beveik tiesūs" if not lift else "2 · Greitai atšok, trumpai ant žemės")
    pic.badge(1)
    pic.save("P_A1.webp")


def pa3():
    """Lateral bound (skater jump), front view: push off one leg, land on the other."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            # standing on the left leg (viewer's right), right foot off the floor behind, leaning into the push
            dx = -26
            front(pic, (CX - 12 + dx, 212), (CX + 12 + dx, 212), (CX - 26 + dx + 8, 160), (CX + 30 + dx + 8, 160),
                  (CX + dx + 10, 140), (CX - 40 + dx, 264), (CX + 22 + dx, 292), (CX - 50 + dx, 214), (CX + 56 + dx, 196),
                  l_knee=(14, -6), r_knee=(-16, 0), l_elbow=(-10, 6), r_elbow=(12, 0))
            pic.arrow((CX + 4, 236), (CX + 50, 210), (CX + 92, 236), acc)
            pic.caption("1 · Atsispirk kaire koja į šoną")
        else:
            dx = 36
            front(pic, (CX - 12 + dx, 214), (CX + 12 + dx, 214), (CX - 32 + dx, 162), (CX + 24 + dx, 162),
                  (CX + dx - 6, 142), (CX - 20 + dx, 292), (CX + 38 + dx, 266), (CX - 60 + dx, 198), (CX + 46 + dx, 214),
                  l_knee=(14, 0), r_knee=(-14, -6), l_elbow=(-12, 0), r_elbow=(10, 6))
            shadow(pic, CX + dx - 18, 24)
            pic.caption("2 · Nusileisk ant kitos, sustok 1 s")
    pic.badge(3)
    pic.save("P_A3.webp")


def trap_bar(pic, hands_y, cx, col):
    pic.capsule((cx - 46, hands_y), (cx + 46, hands_y), 4.5, GREY)
    for s in (-1, 1):
        pic.capsule((cx + s * 48, hands_y - 16), (cx + s * 48, hands_y + 16), 10, col)
        pic.capsule((cx + s * 58, hands_y - 13), (cx + s * 58, hands_y + 13), 8, col)


def pa4():
    """Trap-bar jump, front view: light trap bar, quarter squat, jump."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            front(pic, (CX - 13, 226), (CX + 13, 226), (CX - 28, 176), (CX + 28, 176), (CX, 156), (CX - 18, 292),
                  (CX + 18, 292), (CX - 36, 234), (CX + 36, 234), l_knee=(-16, 0), r_knee=(16, 0), l_elbow=(-4, 0),
                  r_elbow=(4, 0))
            trap_bar(pic, 238, CX, acc)
            pic.caption("1 · Lengva štanga, pusiau pritūpk")
        else:
            up = 26
            front(pic, (CX - 12, 206 - up), (CX + 12, 206 - up), (CX - 28, 152 - up), (CX + 28, 152 - up),
                  (CX, 132 - up), (CX - 14, 290 - up), (CX + 14, 290 - up), (CX - 36, 212 - up), (CX + 36, 212 - up),
                  l_elbow=(-4, 0), r_elbow=(4, 0))
            trap_bar(pic, 216 - up, CX, acc)
            shadow(pic, CX)
            pic.arrow((CX + 78, 286), (CX + 86, 246), (CX + 78, 206), acc)
            pic.caption("2 · Šok kuo aukščiau")
    pic.badge(4)
    pic.save("P_A4.webp")


def pa5():
    """Banded roundhouse kick: band from a low post to the kicking ankle."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i)
        post(pic, 14, 220)
        anchor = (14, 262)
        pulley(pic, anchor)
        if i == 0:
            j = side((128, 206), (156, 290), (98, 290), (148, 150), (136, 156), torso_ang=86, head_ang=84,
                     knee=(18, 0), elbow=(4, 18), f_elbow=(4, 18))
            band(pic, [anchor, (60, 276), j["f_ankle"]])
            side_figure(pic, j)
            pic.caption("1 · Guma ant kulkšnies")
        else:
            hip = (120, 208)
            j = side(hip, (126, 290), go(hip, 8, 86), (110, 150), (98, 160), torso_ang=104, head_ang=96,
                     knee=(4, 0), f_knee=(0, -18), f_toe=0, elbow=(4, 18), f_elbow=(4, 18))
            band(pic, [anchor, (110, 252), j["f_ankle"]])
            side_figure(pic, j)
            pic.arrow((150, 262), (196, 248), (226, 202), acc)
            pic.caption("2 · Greitas mawashi geri ir atgal")
    pic.badge(5)
    pic.save("P_A5.webp")


def pb1():
    """Shadow speed punches: fighting stance, straight punches as fast as possible."""
    pic, acc = Pic(), ACC["B"]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            j = side((118, 206), (148, 290), (90, 290), (198, 146), (150, 150), torso_ang=84, head_ang=82,
                     knee=(18, 0), elbow=(0, 16), f_elbow=(0, 18))
            pic.caption("1 · Kovinė stovėsena")
        else:
            j = side((120, 206), (150, 290), (92, 290), (150, 150), (200, 144), torso_ang=82, head_ang=80,
                     knee=(18, 0), elbow=(0, 18), f_elbow=(0, 6))
            pic.caption("2 · Kuo greičiau: kairė, dešinė")
        side_figure(pic, j)
        pic.arrow((168, 122), (196, 116), (226, 130), acc)
    pic.badge(1)
    pic.save("P_B1.webp")


def pb3():
    """Single-arm med ball shot put from the fighting stance."""
    pic, acc = Pic(), ACC["B"]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            j = side((114, 212), (150, 290), (82, 290), (130, 152), (150, 160), torso_ang=96, head_ang=86,
                     knee=(18, 0), elbow=(-6, 18), f_elbow=(6, 18))
            side_figure(pic, j)
            ball(pic, (j["n_hand"][0] + 2, j["n_hand"][1] - 8), 13)
            pic.caption("1 · Kamuolys prie peties")
        else:
            j = side((126, 208), (156, 290), (100, 282), (198, 136), (150, 166), torso_ang=74, head_ang=74,
                     knee=(18, 0), f_toe=-40, elbow=(0, 10), f_elbow=(-6, 18))
            side_figure(pic, j)
            ball(pic, (222, 120), 13)
            pic.arrow((140, 112), (172, 96), (204, 104), acc)
            pic.caption("2 · Stumk sprogstamai, kaip smūgį")
    pic.badge(3)
    pic.save("P_B3.webp")


def pc1():
    """Reaction start: fighting stance, sprint 5 m on a signal."""
    pic, acc = Pic(), ACC["C"]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            j = side((110, 210), (140, 290), (82, 290), (152, 150), (136, 156), torso_ang=86, head_ang=84,
                     knee=(18, 0), elbow=(4, 18), f_elbow=(4, 18))
            side_figure(pic, j)
            for k, r in enumerate((10, 17, 24)):
                pic.path(bezier(go((70, 118), 150, r), go((70, 118), 180, r * 1.15), go((70, 118), 210, r)), acc, 2.4)
            pic.caption("1 · Lauk signalo stovėsenoje")
        else:
            hip = (124, 214)
            j = side(hip, (90, 288), (172, 246), (92, 196), (168, 156), torso_ang=58, head_ang=52, knee=(-8, 10),
                     f_knee=(24, -14), n_toe=-20, f_toe=0, elbow=(-16, 4), f_elbow=(10, 16))
            side_figure(pic, j)
            pic.arrow((150, 296), (196, 284), (234, 290), acc)
            pic.caption("2 · Sprogstamas startas 5 m")
    pic.badge(1)
    pic.save("P_C1.webp")


def pc3():
    """Kettlebell swing: hinge, then snap the hips forward."""
    pic, acc = Pic(), ACC["C"]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            hip = (104, 214)
            j = side(hip, (126, 290), (120, 290), (128, 262), (124, 262), torso_ang=36, head_ang=28,
                     knee=(22, 0), elbow=(0, 0))
            side_figure(pic, j)
            kettlebell(pic, j["n_hand"], acc, off=(-4, 12))
            pic.caption("1 · Klubai atgal, gira tarp kojų")
        else:
            j = side((128, 206), (130, 290), (124, 290), (188, 152), (184, 154), torso_ang=92, head_ang=90,
                     knee=(6, 0), elbow=(4, 0))
            side_figure(pic, j)
            kettlebell(pic, j["n_hand"], acc, off=(14, -2))
            pic.arrow((96, 236), (110, 214), (132, 206), acc)
            pic.caption("2 · Klubų smūgis, gira iki krūtinės")
    pic.badge(3)
    pic.save("P_C3.webp")


def pc6():
    """Banded knee strike (hiza geri): band from a low post behind to the knee."""
    pic, acc = Pic(), ACC["C"]
    for i in range(2):
        standing_view(pic, i)
        post(pic, 14, 220)
        anchor = (14, 252)
        pulley(pic, anchor)
        if i == 0:
            j = side((128, 206), (156, 290), (98, 290), (152, 150), (140, 154), torso_ang=86, head_ang=84,
                     knee=(18, 0), elbow=(4, 18), f_elbow=(4, 18))
            band(pic, [anchor, (60, 246), j["f_knee"]])
            side_figure(pic, j)
            pic.caption("1 · Guma ant kelio, galinė koja")
        else:
            hip = (128, 204)
            fk, fa = joint(hip, (176, 214), 44, 44, (0, -30))
            j = side(hip, (126, 290), (176, 214), (168, 146), (160, 150), torso_ang=96, head_ang=90,
                     knee=(4, 0), f_knee=(0, -30), f_toe=-80, elbow=(-6, 18), f_elbow=(-6, 18))
            band(pic, [anchor, (100, 230), j["f_knee"]])
            side_figure(pic, j)
            pic.arrow((150, 236), (182, 218), (198, 184), acc)
            pic.caption("2 · Kelį sprogstamai aukštyn")
    pic.badge(6)
    pic.save("P_C6.webp")


def c7r():
    """Kettlebell front rack carry, front view: bells at the chest, shoulders DOWN (not shrugged)."""
    pic, acc = Pic(), ACC["C"]
    for i, shrug in enumerate((False, True)):
        standing_view(pic, i)
        sy = 152 if not shrug else 140
        head = (CX, 132 if not shrug else 128)
        l_sh, r_sh = (CX - 28, sy), (CX + 28, sy)
        hands = ((CX - 14, 170), (CX + 14, 170))
        front(pic, (CX - 12, 206), (CX + 12, 206), l_sh, r_sh, head, (CX - 14, 292), (CX + 14, 292), hands[0],
              hands[1], l_elbow=(-6, 22), r_elbow=(6, 22))
        for s, h in zip((-1, 1), hands):
            kettlebell(pic, h, acc, off=(s * 14, 2))
        if not shrug:
            for s in (-1, 1):
                pic.arrow((CX + s * 56, 128), (CX + s * 60, 140), (CX + s * 52, 154), acc)
        pic.mark(not shrug)
        pic.caption("Teisingai: pečiai žemyn" if not shrug else "Neteisingai: pečiai prie ausų")
    pic.badge(7)
    pic.save("C_7r.webp")


ALL = dict(pa1=pa1, pa3=pa3, pa4=pa4, pa5=pa5, pb1=pb1, pb3=pb3, pc1=pc1, pc3=pc3, pc6=pc6, c7r=c7r)

if __name__ == "__main__":
    for key in sys.argv[1:] or list(ALL):
        ALL[key]()
