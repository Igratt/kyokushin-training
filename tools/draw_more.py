"""Pictures of the variants added 2026-11-10 so that every exercise except the base lifts alternates:
Hard Gym G_<day><n>v.webp and karate power P_<day><n>v.webp. Two panels each, same mannequin style.

Usage:  py tools/draw_more.py [name ...]     (no names = all)
"""
import math
import sys

import draw_stretches as ds
from draw_exercises import ACCENT, W, Pic, centered, go, side_figure
from draw_variants import (CX, EQUIP, EQUIP_HI, GREY, along, ball, band, cable, db_end, front, kettlebell, limb,
                           lying_view, post, pulley, pushup, rect, shadow, side, stand_front, standing_view)

ACC = dict(ACCENT, D=(168, 85, 247))


def db_line(pic, hand, ang, col):
    """Dumbbell seen along its length: handle at `ang` (degrees), plates at both ends."""
    a, b = go(hand, ang, 13), go(hand, ang + 180, 13)
    pic.capsule(a, b, 3, GREY)
    for p in (a, b):
        pic.capsule(go(p, ang + 90, 7), go(p, ang - 90, 7), 5, col)


# ------------------------------------------------------------------ Hard Gym
def ga4v():
    """Dumbbell floor press: lying on the floor, knees bent, elbows touch the floor at the bottom."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        lying_view(pic, i, 1.25)
        hip, sh = (136, 280), (82, 280)
        n_knee, n_ankle = limb(hip, (192, 290), 44, 44, (170, 236))
        f_knee, f_ankle = limb(hip, (186, 291), 44, 44, (164, 238))
        if i == 0:
            n_elbow, n_hand = (104, 288), (106, 262)
        else:
            n_elbow, n_hand = (88, 254), (90, 228)
        f_elbow, f_hand = (n_elbow[0] - 3, n_elbow[1] + 1), (n_hand[0] - 3, n_hand[1] + 1)
        db_end(pic, f_hand, acc)
        j = dict(hip=hip, sh=sh, head=(62, 279), n_knee=n_knee, n_ankle=n_ankle, n_toe=go(n_ankle, 0, 18),
                 f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, 0, 18), f_sh=(79, 282), n_elbow=n_elbow,
                 n_hand=n_hand, f_elbow=f_elbow, f_hand=f_hand)
        side_figure(pic, j)
        db_end(pic, n_hand, acc)
        if i:
            pic.arrow((114, 266), (122, 244), (110, 224), acc)
        pic.caption("1 · Alkūnės liečia grindis" if not i else "2 · Spausk abu aukštyn")
    pic.badge(4)
    pic.save("G_A4v.webp")


def ga5v():
    """Inverted row: under a bar at hip height, heels on the floor, body straight, chest to the bar."""
    pic, acc = Pic(), ACC["A"]
    bar, ankle = (96, 196), (226, 290)
    for i in range(2):
        standing_view(pic, i, 1.1)
        rect(pic, 102, 196, 110, 300, EQUIP)
        sh = (90, 252) if i == 0 else (100, 212)
        hip = along(sh, ankle, 54)
        knee = along(hip, ankle, 44)
        ang = math.degrees(math.atan2(-(sh[1] - ankle[1]), sh[0] - ankle[0]))
        if i == 0:
            n_elbow, n_hand = along(sh, bar, 30), bar
        else:
            n_elbow, n_hand = limb(sh, bar, 30, 27, (sh[0] + 34, sh[1] + 14))
        f_ankle = (ankle[0] + 2, ankle[1] + 2)
        j = dict(hip=hip, sh=sh, head=go(sh, ang, 20), n_knee=knee, n_ankle=ankle, n_toe=go(ankle, 90, 14),
                 f_knee=(knee[0], knee[1] + 3), f_ankle=f_ankle, f_toe=go(f_ankle, 90, 14), f_sh=(sh[0] - 2, sh[1] + 3),
                 n_elbow=n_elbow, n_hand=n_hand, f_elbow=(n_elbow[0] - 2, n_elbow[1] + 3),
                 f_hand=(n_hand[0] - 1, n_hand[1] + 2))
        side_figure(pic, j)
        pic.dot(bar, 6, GREY)
        if i:
            pic.arrow((sh[0] + 26, sh[1] + 40), (sh[0] + 34, sh[1] + 20), (sh[0] + 22, sh[1] + 4), acc)
        pic.caption("1 · Kūnas tiesus, rankos tiesios" if not i else "2 · Krūtinę prie skersinio")
    pic.badge(5)
    pic.save("G_A5v.webp")


def ga6v():
    """Cable lateral raise, front view: low pulley on the right, the left hand crosses in front and rises."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i, 1.1)
        pic.capsule((CX + 92, 30), (CX + 92, 300), 8, EQUIP)
        p = (CX + 80, 284)
        pulley(pic, p)
        if i == 0:
            h = stand_front(pic, (CX + 14, 218), (CX + 34, 212), l_elbow=(4, 4), r_elbow=(6, 0))
        else:
            h = stand_front(pic, (CX - 80, 166), (CX + 34, 212), l_elbow=(-2, -8), r_elbow=(6, 0))
        cable(pic, p, h["lh"])
        pic.dot(h["lh"], 4.5, GREY)
        if i:
            pic.arrow((CX - 14, 226), (CX - 62, 222), (CX - 78, 186), acc)
        pic.caption("1 · Rankena prie kito klubo" if not i else "2 · Kelk į šoną iki peties")
    pic.badge(6)
    pic.save("G_A6v.webp")


def ga7v():
    """Hammer curl: neutral grip (thumb up), elbow at the side."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i, 1.1)
        j = side((124, 204), (128, 292), (122, 292), (128, 258), (122, 260), elbow=(-4, 0), f_elbow=(-4, 0))
        sh = j["sh"]
        elbow = (sh[0] + 2, sh[1] + 30)
        hand = (sh[0] + 4, sh[1] + 57) if i == 0 else go(elbow, 64, 27)
        j.update(n_elbow=elbow, n_hand=hand)
        side_figure(pic, j)
        db_line(pic, hand, 0 if i == 0 else -26, acc)
        if i:
            pic.arrow((elbow[0] + 36, elbow[1] + 24), (elbow[0] + 44, elbow[1] - 4), (elbow[0] + 26, elbow[1] - 24), acc)
        pic.caption("1 · Delnas į šoną" if not i else "2 · Lenk, nykštys į viršų")
    pic.badge(7)
    pic.save("G_A7v.webp")


def gc2v():
    """Weighted push-up: a plate on the upper back, chest to the floor."""
    pic, acc = Pic(), ACC["C"]
    for i in range(2):
        standing_view(pic, i, 1.2)
        j = pushup((78, 236), 292) if i == 0 else pushup((84, 266), 292)
        side_figure(pic, j)
        sh, hip = j["sh"], j["hip"]
        a, b = along(sh, hip, 6), along(sh, hip, 34)
        ang = math.degrees(math.atan2(-(hip[1] - sh[1]), hip[0] - sh[0]))
        up = (math.cos(math.radians(ang + 90)) * 11, -math.sin(math.radians(ang + 90)) * 11)
        pic.capsule((a[0] + up[0], a[1] + up[1]), (b[0] + up[0], b[1] + up[1]), 5, acc)
        if i:
            pic.arrow((sh[0] - 14, sh[1] - 44), (sh[0] - 20, sh[1] - 24), (sh[0] - 12, sh[1] - 8), acc)
        pic.caption("1 · Svoris ant nugaros" if not i else "2 · Krūtinė prie grindų")
    pic.badge(2)
    pic.save("G_C2v.webp")


def gc7v():
    """Overhead dumbbell triceps extension: both hands on one dumbbell, elbows up and still."""
    pic, acc = Pic(), ACC["C"]
    for i in range(2):
        standing_view(pic, i, 1.1)
        j = side((124, 206), (128, 292), (122, 292), (128, 258), (122, 260), elbow=(-4, 0), f_elbow=(-4, 0))
        sh = j["sh"]
        elbow = (sh[0] + 6, sh[1] - 30)
        hand = (elbow[0] - 18, elbow[1] + 20) if i == 0 else (elbow[0] + 1, elbow[1] - 27)
        j.update(n_elbow=elbow, n_hand=hand, f_elbow=(elbow[0] - 3, elbow[1] + 1), f_hand=(hand[0] - 2, hand[1] + 1))
        side_figure(pic, j)
        db_line(pic, (hand[0], hand[1] + (8 if i == 0 else -6)), 90, acc)
        if i:
            pic.arrow((elbow[0] + 22, elbow[1] + 2), (elbow[0] + 28, elbow[1] - 18), (elbow[0] + 12, elbow[1] - 34), acc)
        pic.caption("1 · Hantelis už galvos" if not i else "2 · Tiesk rankas aukštyn")
    pic.badge(7)
    pic.save("G_C7v.webp")


# ------------------------------------------------------------------ karate power
def pa1v():
    """Lateral pogo hops, front view: quick small hops side to side on the balls of the feet."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i)
        cx, up = (CX - 24, 0) if i == 0 else (CX + 24, 16)
        front(pic, (cx - 11, 206 - up), (cx + 11, 206 - up), (cx - 28, 152 - up), (cx + 28, 152 - up), (cx, 132 - up),
              (cx - 9, 290 - up), (cx + 9, 290 - up), (cx - 34, 204 - up), (cx + 34, 204 - up),
              l_knee=(-3, 0), r_knee=(3, 0), l_elbow=(-8, 4), r_elbow=(8, 4))
        if i == 0:
            pic.arrow((cx + 18, 284), (cx + 38, 262), (cx + 58, 284), acc)
            pic.caption("1 · Ant pirštų, kojos kartu")
        else:
            shadow(pic, cx)
            pic.arrow((cx - 18, 268), (cx - 38, 246), (cx - 58, 268), acc)
            pic.caption("2 · Greiti šuoliukai į šonus")
    pic.badge(1)
    pic.save("P_A1v.webp")


def pa3v():
    """Lateral hurdle hops, front view: two-foot jumps sideways over a low hurdle and back."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i)
        rect(pic, CX - 4, 256, CX + 4, 292, EQUIP_HI)
        if i == 0:
            cx = CX - 50
            front(pic, (cx - 13, 226), (cx + 13, 226), (cx - 28, 176), (cx + 28, 176), (cx, 156), (cx - 18, 292),
                  (cx + 18, 292), (cx - 36, 234), (cx + 36, 234), l_knee=(-16, 0), r_knee=(16, 0), l_elbow=(-4, 0),
                  r_elbow=(4, 0))
            pic.arrow((cx + 26, 240), (CX, 196), (CX + 44, 240), acc)
            pic.caption("1 · Pusiau pritūpk šalia kliūties")
        else:
            up = 26
            front(pic, (CX - 12, 206 - up), (CX + 12, 206 - up), (CX - 28, 152 - up), (CX + 28, 152 - up),
                  (CX, 132 - up), (CX - 14, 270 - up), (CX + 14, 270 - up), (CX - 36, 196 - up), (CX + 36, 196 - up),
                  l_knee=(-14, 0), r_knee=(14, 0), l_elbow=(-6, 4), r_elbow=(6, 4))
            shadow(pic, CX)
            pic.caption("2 · Peršok į šoną ir atgal")
    pic.badge(3)
    pic.save("P_A3v.webp")


def pa5v():
    """Banded front kick (mae geri): band from a low post behind to the kicking ankle."""
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
            j = side(hip, (118, 290), go(hip, 14, 86), (142, 148), (130, 156), torso_ang=100, head_ang=94,
                     knee=(6, 0), f_knee=(0, -16), f_toe=70, elbow=(4, 18), f_elbow=(4, 18))
            band(pic, [anchor, (100, 250), j["f_ankle"]])
            side_figure(pic, j)
            pic.arrow((156, 236), (194, 226), (230, 214), acc)
            pic.caption("2 · Greitas mae geri ir atgal")
    pic.badge(5)
    pic.save("P_A5v.webp")


def pb1v():
    """Banded speed punches: band from a post behind at chest height to the punching hand."""
    pic, acc = Pic(), ACC["B"]
    for i in range(2):
        standing_view(pic, i)
        post(pic, 14, 120)
        anchor = (14, 150)
        pulley(pic, anchor)
        if i == 0:
            j = side((118, 206), (148, 290), (90, 290), (198, 146), (150, 150), torso_ang=84, head_ang=82,
                     knee=(18, 0), elbow=(0, 16), f_elbow=(0, 18))
            band(pic, [anchor, (80, 152), j["f_hand"]])
            pic.caption("1 · Guma už nugaros, rankoje")
        else:
            j = side((120, 206), (150, 290), (92, 290), (150, 150), (200, 144), torso_ang=82, head_ang=80,
                     knee=(18, 0), elbow=(0, 18), f_elbow=(0, 6))
            band(pic, [anchor, (100, 148), j["f_hand"]])
            pic.caption("2 · Tiesūs smūgiai prieš gumą")
        side_figure(pic, j)
        pic.arrow((168, 122), (196, 116), (226, 130), acc)
    pic.badge(1)
    pic.save("P_B1v.webp")


def pb3v():
    """Med ball chest pass: two hands at the chest, explosive push into the wall."""
    pic, acc = Pic(), ACC["B"]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            j = side((116, 210), (146, 290), (90, 290), (150, 166), (146, 168), torso_ang=94, head_ang=88,
                     knee=(14, 0), elbow=(-8, 18), f_elbow=(-8, 18))
            side_figure(pic, j)
            ball(pic, (j["n_hand"][0] + 12, j["n_hand"][1] - 4), 14)
            pic.caption("1 · Kamuolys prie krūtinės")
        else:
            j = side((124, 208), (154, 290), (98, 286), (196, 154), (192, 156), torso_ang=80, head_ang=78,
                     knee=(16, 0), f_toe=-30, elbow=(0, 8), f_elbow=(0, 8))
            side_figure(pic, j)
            ball(pic, (228, 150), 14)
            pic.arrow((150, 120), (186, 106), (214, 120), acc)
            pic.caption("2 · Stumk abiem rankom")
    pic.badge(3)
    pic.save("P_B3v.webp")


def pc1v():
    """Falling start: stand tall, lean forward until you fall, then sprint 5 m."""
    pic, acc = Pic(), ACC["C"]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            j = side((132, 208), (118, 290), (112, 290), (138, 254), (132, 256), torso_ang=74, head_ang=72,
                     knee=(4, 0), elbow=(-4, 0), f_elbow=(-4, 0))
            side_figure(pic, j)
            pic.arrow((176, 132), (200, 150), (210, 182), acc)
            pic.caption("1 · Tiesiai, krisk į priekį")
        else:
            hip = (124, 214)
            j = side(hip, (90, 288), (172, 246), (92, 196), (168, 156), torso_ang=58, head_ang=52, knee=(-8, 10),
                     f_knee=(24, -14), n_toe=-20, f_toe=0, elbow=(-16, 4), f_elbow=(10, 16))
            side_figure(pic, j)
            pic.arrow((150, 296), (196, 284), (234, 290), acc)
            pic.caption("2 · Pagauk kritimą sprintu 5 m")
    pic.badge(1)
    pic.save("P_C1v.webp")


def pc3v():
    """Single-arm kettlebell swing: one hand on the bell, the free arm follows at the side."""
    pic, acc = Pic(), ACC["C"]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            j = side((104, 214), (126, 290), (120, 290), (128, 262), (96, 248), torso_ang=36, head_ang=28,
                     knee=(22, 0), elbow=(0, 0), f_elbow=(-6, 6))
            side_figure(pic, j)
            kettlebell(pic, j["n_hand"], acc, off=(-4, 12))
            pic.caption("1 · Viena ranka, klubai atgal")
        else:
            j = side((128, 206), (130, 290), (124, 290), (188, 152), (140, 236), torso_ang=92, head_ang=90,
                     knee=(6, 0), elbow=(4, 0), f_elbow=(-4, 8))
            side_figure(pic, j)
            kettlebell(pic, j["n_hand"], acc, off=(14, -2))
            pic.arrow((96, 236), (110, 214), (132, 206), acc)
            pic.caption("2 · Klubų smūgis, kita ranka laisva")
    pic.badge(3)
    pic.save("P_C3v.webp")



def hip_release():
    """Left hip (psoas) release: lying face down, a soft block under the left hip bone and the lower belly.
    One pose, no number badge: the app adds it as the last exercise of every day (R_hip_release.webp)."""
    pic = Pic()
    ds.low(pic, 1.75)
    j = dict(hip=(140, 268), sh=(78, 280), head=(56, 272), n_knee=(186, 284), n_ankle=(230, 289),
             n_toe=go((230, 289), -20, 14), f_knee=(184, 286), f_ankle=(228, 290), f_toe=go((228, 290), -20, 14),
             f_sh=(80, 282), n_elbow=(86, 290), n_hand=(58, 286), f_elbow=(84, 291), f_hand=(60, 287))
    j = centered(j, W / 2)
    hip = j["hip"]
    rect(pic, hip[0] - 18, 276, hip[0] + 14, 292, (125, 211, 252))
    side_figure(pic, j)
    pic.arrow((hip[0] + 34, hip[1] - 54), (hip[0] + 30, hip[1] - 32), (hip[0] + 8, hip[1] - 14), ACC["A"])
    pic.caption("Blokelis po kairiu klubo kaulu · atsipalaiduok 1:30")
    pic.save("R_hip_release.webp")


ALL = dict(ga4v=ga4v, ga5v=ga5v, ga6v=ga6v, ga7v=ga7v, gc2v=gc2v, gc7v=gc7v, pa1v=pa1v, pa3v=pa3v, pa5v=pa5v,
           pb1v=pb1v, pb3v=pb3v, pc1v=pc1v, pc3v=pc3v, hip_release=hip_release)

if __name__ == "__main__":
    for name in (sys.argv[1:] or ALL):
        ALL[name]()
