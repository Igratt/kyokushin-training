"""Draws the cool-down stretch pictures (public/assets/S_<key>.webp): one pose across the whole picture.

Usage:  py tools/draw_stretches.py [key ...]     (no keys = all)
"""
import sys

from draw_exercises import FAR, NEAR, R_HAND, TORSO, W, W_FOOT, W_FORE, W_UPPER, Pic, centered, go, side_figure
from draw_variants import EQUIP, along, front, limb, rect

CX = W / 2
TEAL = (45, 212, 191)


def chip(pic):
    pic.ox = 0
    pic.d.rounded_rectangle([8 * 3, 8 * 3, 92 * 3, 32 * 3], radius=5 * 3, fill=(255, 255, 255))
    pic.text((50, 20.5), "TEMPIMAS", 12, (12, 12, 12), anchor="mm")


def standing(pic, k=1.2, floor_dst=300):
    pic.full(floor_dst)
    pic.view(300, floor_dst, k)


def low(pic, k=1.4, floor_dst=266):
    pic.full(floor_dst)
    pic.view(300, floor_dst, k)


def finish(pic, caption, key):
    pic.caption(caption)
    chip(pic)
    pic.save(f"S_{key}.webp")


def hip_flexor():
    pic = Pic()
    standing(pic, 1.25)
    hip = (250, 248)
    sh = go(hip, 92, 54)
    f_knee, f_ankle = limb(hip, (306, 292), 44, 44, (300, 240))
    f_sh = (sh[0] - 3, sh[1] + 2)
    f_elbow, f_hand = limb(f_sh, (292, 248), 30, 27, (282, 214))
    j = dict(hip=hip, sh=sh, head=go(sh, 90, 20), n_knee=(234, 292), n_ankle=(190, 293), n_toe=go((190, 293), 180, 16),
             f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, 0, 20), n_elbow=go(sh, 95, 30), n_hand=go(sh, 95, 57),
             f_sh=f_sh, f_elbow=f_elbow, f_hand=f_hand)
    j = centered(j, CX)
    side_figure(pic, j)
    h = j["hip"]
    pic.arrow((h[0] - 46, h[1] + 2), (h[0] - 32, h[1] - 6), (h[0] - 16, h[1] + 2), TEAL)
    finish(pic, "Klubus stumk pirmyn, ranka aukštyn", "hip_flexor")


def pigeon():
    pic = Pic()
    low(pic, 1.4)
    hip = (240, 268)
    sh = go(hip, 60, 54)
    n_elbow, n_hand = limb(sh, (284, 276), 30, 27, (258, 256))
    f_sh = (sh[0] - 3, sh[1] + 2)
    f_elbow, f_hand = limb(f_sh, (280, 278), 30, 27, (254, 258))
    j = dict(hip=hip, sh=sh, head=go(sh, 72, 20), n_knee=(282, 288), n_ankle=(240, 293), n_toe=go((240, 293), 185, 14),
             f_knee=(196, 289), f_ankle=(152, 291), f_toe=go((152, 291), 180, 18), n_elbow=n_elbow, n_hand=n_hand,
             f_sh=f_sh, f_elbow=f_elbow, f_hand=f_hand)
    j = centered(j, CX)
    side_figure(pic, j)
    finish(pic, "Klubai lygiai, lėtai leiskis žemyn", "pigeon")


def hamstring():
    pic = Pic()
    low(pic, 1.5, 262)
    hip = (220, 286)
    sh = go(hip, 30, 54)
    n_elbow, n_hand = limb(sh, (310, 280), 30, 27, (292, 258))
    f_sh = (sh[0] - 3, sh[1] + 2)
    f_elbow, f_hand = limb(f_sh, (306, 282), 30, 27, (288, 260))
    j = dict(hip=hip, sh=sh, head=go(sh, 22, 20), n_knee=(264, 289), n_ankle=(308, 290), n_toe=go((308, 290), 85, 16),
             f_knee=(262, 290), f_ankle=(305, 291), f_toe=go((305, 291), 85, 16), n_elbow=n_elbow, n_hand=n_hand,
             f_sh=f_sh, f_elbow=f_elbow, f_hand=f_hand)
    j = centered(j, CX)
    side_figure(pic, j)
    s = j["sh"]
    pic.arrow((s[0] - 34, s[1] - 14), (s[0] - 6, s[1] - 30), (s[0] + 22, s[1] - 22), TEAL)
    finish(pic, "Nugara tiesi, lenkis per klubus", "hamstring")


def butterfly():
    pic = Pic()
    low(pic, 1.35, 270)
    front(pic, (CX - 16, 286), (CX + 16, 286), (CX - 28, 234), (CX + 28, 234), (CX, 214), (CX - 7, 290), (CX + 7, 290),
          (CX - 10, 286), (CX + 10, 286), l_elbow=(-22, 2), r_elbow=(22, 2), feet=False,
          l_knee_pt=(CX - 64, 276), r_knee_pt=(CX + 64, 276))
    for sd in (-1, 1):
        pic.capsule((CX + sd * 7, 290), (CX + sd * 3, 297), W_FOOT + 1, FAR)
        pic.arrow((CX + sd * 64, 238), (CX + sd * 67, 250), (CX + sd * 64, 262), TEAL, 3)
    finish(pic, "Pėdos kartu, kelius leisk žemyn", "butterfly")


def straddle():
    pic = Pic()
    low(pic, 1.3, 270)
    front(pic, (CX - 16, 288), (CX + 16, 288), (CX - 28, 252), (CX + 28, 252), (CX, 236), (CX - 118, 291), (CX + 118, 291),
          (CX - 24, 298), (CX + 24, 298), l_elbow=(-14, 0), r_elbow=(14, 0), feet=False,
          l_knee_pt=(CX - 66, 290), r_knee_pt=(CX + 66, 290))
    for sd in (-1, 1):
        pic.capsule((CX + sd * 118, 291), (CX + sd * 121, 279), W_FOOT + 1, FAR)
    pic.arrow((CX + 44, 232), (CX + 54, 250), (CX + 44, 266), TEAL, 3)
    finish(pic, "Kojos plačiai, lenkis pirmyn", "straddle")


def calf():
    pic = Pic()
    standing(pic, 1.2)
    rect(pic, 332, 40, 350, 300, EQUIP)
    n_ankle = (190, 292)
    hip = go(n_ankle, 58, 87)
    sh = go(hip, 58, 54)
    f_knee, f_ankle = limb(hip, (268, 292), 44, 44, (274, 250))
    n_elbow, n_hand = limb(sh, (330, 166), 30, 27, (300, 160))
    f_sh = (sh[0] - 3, sh[1] + 2)
    f_elbow, f_hand = limb(f_sh, (328, 170), 30, 27, (298, 164))
    j = dict(hip=hip, sh=sh, head=go(sh, 58, 20), n_knee=along(hip, n_ankle, 44), n_ankle=n_ankle, n_toe=go(n_ankle, 0, 20),
             f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, 0, 20), n_elbow=n_elbow, n_hand=n_hand, f_sh=f_sh,
             f_elbow=f_elbow, f_hand=f_hand)
    side_figure(pic, j)
    pic.arrow((196, 300 - 4), (190, 288), (184, 300 - 4), TEAL, 2.6)
    pic.arrow((hip[0] - 22, hip[1] - 4), (hip[0] - 6, hip[1] - 16), (hip[0] + 10, hip[1] - 10), TEAL, 3)
    finish(pic, "Galinis kulnas prie grindų", "calf")


def doorway():
    pic = Pic()
    standing(pic, 1.15)
    for sd in (-1, 1):
        pic.capsule((CX + sd * 64, 60), (CX + sd * 64, 300), 9, EQUIP)
    pic.capsule((CX - 64, 60), (CX + 64, 60), 9, EQUIP)
    front(pic, (CX - 12, 206), (CX + 12, 206), (CX - 28, 152), (CX + 28, 152), (CX, 132), (CX - 14, 292), (CX + 14, 292),
          (CX - 58, 126), (CX + 58, 126), l_elbow=(-15, 15), r_elbow=(15, 15))
    finish(pic, "Dilbiai ant staktos, žingsnis pirmyn", "doorway")


def cross_body():
    pic = Pic()
    standing(pic, 1.2)
    front(pic, (CX - 12, 206), (CX + 12, 206), (CX - 28, 152), (CX + 28, 152), (CX, 132), (CX - 14, 292), (CX + 14, 292),
          (CX + 44, 158), (CX + 4, 160), l_elbow=(0, 2), r_elbow=(14, 20))
    pic.arrow((CX + 46, 128), (CX + 26, 118), (CX + 4, 128), TEAL, 3)
    finish(pic, "Ranka per krūtinę, prispausk alkūnę", "cross_body")


def triceps():
    pic = Pic()
    standing(pic, 1.15)
    front(pic, (CX - 12, 206), (CX + 12, 206), (CX - 28, 152), (CX + 28, 152), (CX, 132), (CX - 14, 292), (CX + 14, 292),
          (CX + 10, 106), (CX + 2, 126), l_elbow=(-12, -14), r_elbow=(0, -30))
    pic.arrow((CX + 46, 86), (CX + 40, 100), (CX + 30, 110), TEAL, 3)
    finish(pic, "Alkūnė aukštyn, delnas už galvos", "triceps")


def child():
    pic = Pic()
    low(pic, 1.5, 262)
    hip = (214, 268)
    sh = go(hip, 6, 54)
    n_elbow, n_hand = limb(sh, (326, 287), 30, 27, (296, 268))
    f_sh = (sh[0] - 3, sh[1] + 2)
    f_elbow, f_hand = limb(f_sh, (322, 289), 30, 27, (292, 270))
    j = dict(hip=hip, sh=sh, head=go(sh, -25, 20), n_knee=(252, 291), n_ankle=(208, 293), n_toe=go((208, 293), 180, 14),
             f_knee=(249, 291), f_ankle=(205, 293), f_toe=go((205, 293), 180, 14), n_elbow=n_elbow, n_hand=n_hand,
             f_sh=f_sh, f_elbow=f_elbow, f_hand=f_hand)
    j = centered(j, CX)
    side_figure(pic, j)
    h = j["n_hand"]
    pic.arrow((h[0] - 40, h[1] - 26), (h[0] - 14, h[1] - 34), (h[0] + 6, h[1] - 18), TEAL, 3)
    finish(pic, "Sėsk ant kulnų, rankos toli pirmyn", "child")


def quadruped_legs(j):
    j.update(n_knee=(222, 291), n_ankle=(178, 292), n_toe=go((178, 292), 180, 14),
             f_knee=(226, 291), f_ankle=(182, 292), f_toe=go((182, 292), 180, 14))
    return j


def thread():
    pic = Pic()
    low(pic, 1.4, 270)
    hip = (222, 247)
    sh = along(hip, (276, 270), 54)
    f_sh = (sh[0] - 1, sh[1] + 4)
    f_elbow, f_hand = limb(f_sh, (220, 290), 30, 27, (246, 292))
    up = (sh[0], sh[1] - 8)
    j = quadruped_legs(dict(hip=hip, sh=sh, head=(sh[0] + 18, sh[1] + 12), n_elbow=go(up, 90, 30), n_hand=go(up, 90, 57),
                            f_sh=f_sh, f_elbow=f_elbow, f_hand=f_hand))
    side_figure(pic, j)
    h = j["n_hand"]
    pic.arrow((h[0] + 34, h[1] + 44), (h[0] + 36, h[1] + 14), (h[0] + 12, h[1] - 2), TEAL, 3)
    finish(pic, "Ranka po kūnu, kita į lubas", "thread")


def wrist():
    pic = Pic()
    low(pic, 1.45, 270)
    hip = (222, 245)
    sh = go(hip, 8.5, 54)
    j = quadruped_legs(dict(hip=hip, sh=sh, head=go(sh, -10, 20), n_elbow=along(sh, (278, 292), 30), n_hand=(278, 292),
                            f_sh=(sh[0] - 3, sh[1] + 2), f_elbow=along((sh[0] - 3, sh[1] + 2), (282, 292), 30), f_hand=(282, 292)))
    pic.capsule((282, 293), (268, 295), 5, FAR)
    side_figure(pic, j)
    pic.capsule((278, 293), (263, 295), 5, NEAR)
    pic.dot((278, 292), R_HAND, NEAR)
    pic.arrow((214, 228), (196, 222), (186, 236), TEAL, 3)
    finish(pic, "Pirštai atgal, lėtai sėskis atgal", "wrist")


def wgs():
    pic = Pic()
    standing(pic, 1.25, 296)
    hip = (250, 262)
    sh = go(hip, 38, 54)
    n_knee, n_ankle = limb(hip, (318, 292), 44, 44, (304, 250))
    f_sh = (sh[0] - 3, sh[1] + 2)
    f_elbow, f_hand = limb(f_sh, (306, 292), 30, 27, (310, 256))
    f_ankle = along(hip, (166, 286), 87)
    j = dict(hip=hip, sh=sh, head=go(sh, 70, 20), n_knee=n_knee, n_ankle=n_ankle, n_toe=go(n_ankle, 0, 20),
             f_knee=along(hip, f_ankle, 44), f_ankle=f_ankle, f_toe=go(f_ankle, -40, 14), n_elbow=go(sh, 95, 30),
             n_hand=go(sh, 95, 57), f_sh=f_sh, f_elbow=f_elbow, f_hand=f_hand)
    j = centered(j, CX)
    side_figure(pic, j)
    h = j["n_hand"]
    pic.arrow((h[0] + 34, h[1] + 44), (h[0] + 36, h[1] + 14), (h[0] + 14, h[1] - 2), TEAL, 3)
    finish(pic, "Įtūpstas, ranka į lubas", "wgs")


def cobra():
    pic = Pic()
    low(pic, 1.4, 270)
    hip = (238, 287)
    sh = go(hip, 36, 54)
    n_elbow, n_hand = limb(sh, (290, 292), 30, 27, (262, 280))
    f_sh = (sh[0] - 3, sh[1] + 2)
    f_elbow, f_hand = limb(f_sh, (286, 293), 30, 27, (258, 282))
    j = dict(hip=hip, sh=sh, head=go(sh, 62, 20), n_knee=(194, 292), n_ankle=(150, 292), n_toe=go((150, 292), 180, 16),
             f_knee=(196, 293), f_ankle=(152, 293), f_toe=go((152, 293), 180, 16), n_elbow=n_elbow, n_hand=n_hand,
             f_sh=f_sh, f_elbow=f_elbow, f_hand=f_hand)
    j = centered(j, CX)
    side_figure(pic, j)
    s = j["sh"]
    pic.arrow((s[0] + 30, s[1] + 4), (s[0] + 36, s[1] - 16), (s[0] + 22, s[1] - 32), TEAL, 3)
    finish(pic, "Klubai prie grindų, krūtinė aukštyn", "cobra")


ALL = dict(hip_flexor=hip_flexor, pigeon=pigeon, hamstring=hamstring, butterfly=butterfly, straddle=straddle, calf=calf,
           doorway=doorway, cross_body=cross_body, triceps=triceps, thread=thread, child=child, wrist=wrist, wgs=wgs, cobra=cobra)

if __name__ == "__main__":
    for key in sys.argv[1:] or list(ALL):
        ALL[key]()
