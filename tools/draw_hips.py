"""Draws the hip pictures:
- warm-up drills (whole body + hips), one pose across the picture with an "APŠILIMAS" chip: public/assets/W_<key>.webp
- hip strength exercises added as exercise 10 of each day, two panels: A_10, B_10, C_10

Usage:  py tools/draw_hips.py [name ...]     (no names = all)
"""
import math
import sys

import draw_stretches as ds
from draw_exercises import ACCENT, FAR, GREEN, NEAR, RED, W, W_FOOT, W_SHIN, W_THIGH, Pic, bezier, centered, go, side_figure
from draw_variants import CX as PCX
from draw_variants import EQUIP, EQUIP_HI, along, front, kettlebell, limb, post, pushup, rect, side, standing_view

FCX = W / 2  # centre of a one-pose picture
TEAL = ds.TEAL


def chip(pic):
    pic.ox = 0
    pic.d.rounded_rectangle([8 * 3, 8 * 3, 104 * 3, 32 * 3], radius=5 * 3, fill=(255, 255, 255))
    pic.text((56, 20.5), "APŠILIMAS", 12, (12, 12, 12), anchor="mm")


def finish(pic, caption, key):
    pic.caption(caption)
    chip(pic)
    pic.save(f"W_{key}.webp")


def arc_arrow(pic, c, rx, ry, a0, a1, col, w=2.6):
    """Dashed elliptic arc from angle a0 to a1 (degrees, y up) with an arrow head at the end."""
    n = 28
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((c[0] + math.cos(a) * rx, c[1] - math.sin(a) * ry))
    pic.path(pts[:-2], col, w, dashed=True)
    (ax, ay), (bx, by) = pts[-3], pts[-1]
    ang = math.atan2(by - ay, bx - ax)
    length = 10
    pic.poly([(bx + 3 * math.cos(ang), by + 3 * math.sin(ang)),
              (bx - length * math.cos(ang - 0.5), by - length * math.sin(ang - 0.5)),
              (bx - length * math.cos(ang + 0.5), by - length * math.sin(ang + 0.5))], col)


# ------------------------------------------------------------------ warm-up drills
def hip_cars():
    pic = Pic()
    ds.standing(pic, 1.2)
    hip = (FCX + 6, 204)
    sh = go(hip, 90, 54)
    f_knee, f_ankle = limb(hip, (hip[0] + 2, 292), 44, 44, (hip[0] + 30, 248))
    n_knee = (hip[0] + 44, hip[1] - 4)
    n_ankle = (n_knee[0] + 4, n_knee[1] + 44)
    f_sh = (sh[0] - 3, sh[1] + 2)
    post(pic, hip[0] - 44, 150)
    f_elbow, f_hand = limb(f_sh, (hip[0] - 40, 194), 30, 27, (hip[0] - 22, 200))
    n_elbow, n_hand = limb(sh, (hip[0] + 8, 200), 30, 27, (hip[0] - 18, 182))
    j = dict(hip=hip, sh=sh, head=go(sh, 90, 20), n_knee=n_knee, n_ankle=n_ankle, n_toe=go(n_ankle, -60, 18),
             f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, 0, 20), n_elbow=n_elbow, n_hand=n_hand,
             f_sh=f_sh, f_elbow=f_elbow, f_hand=f_hand)
    side_figure(pic, j)
    arc_arrow(pic, (n_knee[0] + 4, n_knee[1] + 8), 36, 30, 205, -115, TEAL)
    finish(pic, "Kelį suk kuo didesniu ratu, liemuo nejuda", "hip_cars")


def leg_swings():
    pic = Pic()
    ds.standing(pic, 1.2)
    hip = (FCX - 20, 204)
    sh = go(hip, 92, 54)
    f_knee, f_ankle = limb(hip, (hip[0] + 2, 292), 44, 44, (hip[0] + 30, 248))
    n_ankle = go(hip, -12, 87)
    n_knee = along(hip, n_ankle, 44)
    f_sh = (sh[0] - 3, sh[1] + 2)
    post(pic, hip[0] - 42, 150)
    f_elbow, f_hand = limb(f_sh, (hip[0] - 38, 192), 30, 27, (hip[0] - 22, 198))
    n_elbow, n_hand = limb(sh, (hip[0] + 34, 178), 30, 27, (hip[0] + 6, 196))
    j = dict(hip=hip, sh=sh, head=go(sh, 90, 20), n_knee=n_knee, n_ankle=n_ankle, n_toe=go(n_ankle, 78, 16),
             f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, 0, 20), n_elbow=n_elbow, n_hand=n_hand,
             f_sh=f_sh, f_elbow=f_elbow, f_hand=f_hand)
    side_figure(pic, j)
    arc_arrow(pic, hip, 102, 92, -122, -14, TEAL)
    finish(pic, "Mosuok tiesia koja pirmyn ir atgal, po to į šonus", "leg_swings")


def ninety_ninety():
    pic = Pic()
    ds.low(pic, 1.45, 272)
    c = FCX
    l_hip, r_hip = (c - 12, 276), (c + 12, 276)
    l_sh, r_sh = (c - 24, 226), (c + 24, 226)
    l_knee, l_ankle = (c - 52, 291), (c - 8, 295)      # front leg: knee out left, shin across in front
    r_knee, r_ankle = (c + 56, 289), (c + 76, 281)     # back leg: thigh out right, shin pointing back
    # the back leg is drawn by front(); the front leg lies in front of the pelvis, so it is drawn afterwards
    front(pic, l_hip, r_hip, l_sh, r_sh, (c, 204), l_hip, r_ankle, (c - 32, 278), (c + 34, 278),
          l_elbow=(-12, 0), r_elbow=(12, 0), feet=False, arms_behind=True, l_knee_pt=l_hip, r_knee_pt=r_knee)
    pic.capsule((r_ankle[0], r_ankle[1] + 1), (r_ankle[0] + 12, r_ankle[1] - 3), W_FOOT + 1, FAR)
    pic.capsule(l_hip, l_knee, W_THIGH + 1, NEAR)
    pic.capsule(l_knee, l_ankle, W_SHIN + 1, NEAR)
    pic.capsule((l_ankle[0] - 2, l_ankle[1] + 1), (l_ankle[0] + 15, l_ankle[1] - 1), W_FOOT + 1, NEAR)
    pic.arrow((c - 60, 272), (c, 214), (c + 62, 268), TEAL)
    finish(pic, "Abu keliai 90°, lėtai versk juos į kitą pusę", "9090")


def cossack_bottom(pic, c, kb_col=None):
    """Front view: deep on the left leg (knee out), right leg straight out to the side, toes up."""
    l_hip, r_hip = (c - 30, 256), (c - 8, 258)
    l_sh, r_sh = (c - 40, 204), (c + 6, 206)
    l_ankle, r_ankle = (c - 60, 292), (c + 74, 290)
    hands = (c - 23, 224), (c - 11, 224)
    front(pic, l_hip, r_hip, l_sh, r_sh, (c - 18, 184), l_ankle, r_ankle, hands[0], hands[1],
          l_knee=(-30, -8), r_knee=(0, -3), l_elbow=(-12, 10), r_elbow=(12, 10), feet=False)
    pic.capsule((l_ankle[0] + 4, l_ankle[1] + 4), (l_ankle[0] - 13, l_ankle[1] + 4), W_FOOT + 1, FAR)
    pic.capsule((r_ankle[0] + 1, r_ankle[1] + 4), (r_ankle[0] + 5, r_ankle[1] - 12), W_FOOT + 1, FAR)
    if kb_col:
        kettlebell(pic, ((hands[0][0] + hands[1][0]) / 2, 222), kb_col)


def cossack():
    pic = Pic()
    ds.standing(pic, 1.25)
    cossack_bottom(pic, FCX)
    pic.arrow((FCX - 52, 168), (FCX + 6, 140), (FCX + 62, 172), TEAL)
    finish(pic, "Leiskis ant vienos kojos, kita tiesi, pirštai aukštyn", "cossack")


def deep_squat():
    pic = Pic()
    ds.standing(pic, 1.3, 296)
    hip = (FCX - 22, 262)
    j = side(hip, (FCX + 6, 292), (FCX + 2, 292), (FCX + 22, 214), (FCX + 20, 216), torso_ang=72, head_ang=80,
             knee=(34, -30), elbow=(2, 18), n_toe=0)
    side_figure(pic, j)
    finish(pic, "Kulnai prie žemės, alkūnėmis stumk kelius į šonus", "deep_squat")


def wgs():
    ds.finish = finish  # same pose as the cool-down picture, with the warm-up chip
    ds.wgs()


# ------------------------------------------------------------------ whole-body warm-up drills
def jacks():
    """Jumping jacks, front view: legs apart, arms overhead, arcs showing the arm swing."""
    pic = Pic()
    ds.standing(pic, 1.15)
    c = FCX
    front(pic, (c - 12, 206), (c + 12, 206), (c - 28, 152), (c + 28, 152), (c, 132), (c - 52, 292), (c + 52, 292),
          (c - 40, 100), (c + 40, 100), l_knee=(-6, 0), r_knee=(6, 0), l_elbow=(-10, -2), r_elbow=(10, -2))
    arc_arrow(pic, (c + 28, 152), 66, 66, 10, 75, TEAL)
    arc_arrow(pic, (c - 28, 152), 66, 66, 170, 105, TEAL)
    finish(pic, "Kojos į šonus, rankos virš galvos, ritmingai", "jacks")


def arm_circles():
    """Arms straight out to the sides, a circle arrow around each hand."""
    pic = Pic()
    ds.standing(pic, 1.15)
    c = FCX
    front(pic, (c - 12, 206), (c + 12, 206), (c - 28, 152), (c + 28, 152), (c, 132), (c - 16, 292), (c + 16, 292),
          (c - 84, 150), (c + 84, 150), l_elbow=(0, -3), r_elbow=(0, -3))
    arc_arrow(pic, (c + 84, 150), 26, 26, 200, -130, TEAL)
    arc_arrow(pic, (c - 84, 150), 26, 26, -20, 310, TEAL)
    finish(pic, "Dideli ratai tiesiomis rankomis: pirmyn, tada atgal", "arm_circles")


def cat_cow():
    """On all fours with the back rounded up; the arched (cow) position is dashed below."""
    pic = Pic()
    ds.low(pic, 1.45, 272)
    hip, sh, mid = (222, 247), (276, 247), (249, 233)
    f_sh = (sh[0] - 3, sh[1] + 2)
    j = ds.quadruped_legs(dict(hip=hip, mid=mid, sh=sh, head=go(sh, -64, 20), n_elbow=along(sh, (280, 292), 30),
                               n_hand=(280, 292), f_sh=f_sh, f_elbow=along(f_sh, (284, 292), 30), f_hand=(284, 292)))
    j = centered(j, FCX)
    side_figure(pic, j)
    h, m, s = j["hip"], j["mid"], j["sh"]
    pic.path(bezier((h[0] + 6, h[1] + 10), (m[0], m[1] + 66), (s[0] - 6, s[1] + 10)), TEAL, 2.4, dashed=True)
    pic.arrow((m[0], m[1] - 18), (m[0], m[1] - 30), (m[0], m[1] - 44), TEAL, 3)
    finish(pic, "Nugarą apvalink aukštyn, tada išlenk žemyn", "cat_cow")


def tspine():
    """Quadruped thoracic rotation: hand behind the head, elbow turning up to the ceiling."""
    pic = Pic()
    ds.low(pic, 1.4, 270)
    hip = (222, 247)
    sh = go(hip, 6, 54)
    f_sh = (sh[0] - 3, sh[1] + 2)
    j = ds.quadruped_legs(dict(hip=hip, sh=sh, head=(sh[0] + 16, sh[1] - 10), n_elbow=(sh[0] + 8, sh[1] - 30),
                               n_hand=(sh[0] + 4, sh[1] - 15), f_sh=f_sh, f_elbow=along(f_sh, (282, 292), 30), f_hand=(282, 292)))
    j = centered(j, FCX)
    side_figure(pic, j)
    s = j["sh"]
    arc_arrow(pic, (s[0], s[1] - 4), 44, 40, 236, 74, TEAL)
    finish(pic, "Ranka už galvos, alkūnę suk į lubas", "tspine")


def scap_pushup():
    """Scapular push-up: straight-arm plank, only the shoulder blades move (double arrow at the upper back)."""
    pic = Pic()
    ds.standing(pic, 1.2)
    j = centered(pushup((78, 236), 292), FCX)
    side_figure(pic, j)
    p = along(j["sh"], j["hip"], 16)
    b = (p[0] + 4, p[1] - 26)
    pic.arrow((b[0], b[1] - 4), (b[0], b[1] - 12), (b[0], b[1] - 22), TEAL, 3)
    pic.arrow((b[0], b[1] + 4), (b[0], b[1] + 8), (b[0], b[1] + 12), TEAL, 3)
    finish(pic, "Rankos tiesios, juda tik mentės: žemyn ir stumk", "scap_pushup")


def inchworm():
    """Inchworm: folded over, hands walking out towards a plank."""
    pic = Pic()
    ds.standing(pic, 1.2)
    j = side((168, 206), (134, 292), (128, 292), (236, 292), (232, 292), torso_ang=-44, head_ang=-50,
             knee=(-4, 0), elbow=(10, -6), n_toe=0, f_toe=0)
    j = centered(j, FCX)
    side_figure(pic, j)
    h = j["n_hand"]
    pic.arrow((h[0] + 12, h[1] - 8), (h[0] + 34, h[1] - 24), (h[0] + 56, h[1] - 6), TEAL, 3)
    finish(pic, "Rankomis eik į planką, pėdomis grįžk prie rankų", "inchworm")


# ------------------------------------------------------------------ hip strength (exercise 10)
def body_line(pic, j, ang, ok):
    n = (math.cos(math.radians(ang + 90)), -math.sin(math.radians(ang + 90)))
    a = (j["head"][0] + n[0] * 24 - 4, j["head"][1] + n[1] * 24)
    b = (j["n_ankle"][0] + n[0] * 24 + 6, j["n_ankle"][1] + n[1] * 24)
    if ok:
        pic.path([a, b], GREEN, 2.6, dashed=True)
    else:
        mid = (j["hip"][0], j["hip"][1] - 24)
        ctrl = (2 * mid[0] - (a[0] + b[0]) / 2, 2 * mid[1] - (a[1] + b[1]) / 2)
        pic.path(bezier(a, ctrl, b), RED, 2.6, dashed=True)


def a10():
    """Copenhagen plank: side plank on the forearm, top leg on a bench, bottom leg free."""
    pic = Pic()
    for i, sag in enumerate((False, True)):
        standing_view(pic, i, 1.2)
        top = 252
        rect(pic, 176, top + 7, 182, 300, EQUIP)
        rect(pic, 226, top + 7, 232, 300, EQUIP)
        rect(pic, 170, top, 240, top + 7, EQUIP_HI)
        sh, ankle = (64, 262), (212, top - 6)
        hip = along(sh, ankle, 54)
        knee = along(hip, ankle, 44)
        if sag:
            hip = (hip[0], hip[1] + 18)
            knee = (knee[0], knee[1] + 9)
        ang = math.degrees(math.atan2(-(ankle[1] - sh[1]), ankle[0] - sh[0]))
        f_knee, f_ankle = limb(hip, (hip[0] + 72, 296), 44, 44, (hip[0] + 40, hip[1] + 44))
        j = dict(hip=hip, sh=sh, head=go(sh, 180 + ang, 20), n_knee=knee, n_ankle=ankle, n_toe=go(ankle, 6, 16),
                 f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, -10, 16), f_sh=(sh[0], sh[1] + 4),
                 f_elbow=(62, 294), f_hand=(86, 296), n_elbow=go(sh, 90, 30), n_hand=go(sh, 90, 57))
        side_figure(pic, j)
        body_line(pic, j, ang, not sag)
        pic.mark(not sag)
        pic.caption("Teisingai: kūnas tiesus" if not sag else "Neteisingai: klubai nukarę", GREEN if not sag else RED)
    pic.badge(10)
    pic.save("A_10.webp")


def b10():
    """Standing kick hold: straight leg held up in front, standing tall in guard."""
    pic = Pic()
    for i, bad in enumerate((False, True)):
        standing_view(pic, i, 1.1)
        hip = (92, 204) if not bad else (98, 210)
        torso = 92 if not bad else 118
        kick = -4 if not bad else -34
        sh = go(hip, torso, 54)
        f_knee, f_ankle = limb(hip, (hip[0] + (2 if not bad else 12), 292), 44, 44, (hip[0] + 34, 248))
        n_ankle = go(hip, kick, 87)
        n_knee = along(hip, n_ankle, 44)
        f_sh = (sh[0] - 3, sh[1] + 2)
        n_elbow, n_hand = limb(sh, (sh[0] + 22, sh[1] - 14), 30, 27, (sh[0] + 16, sh[1] + 22))
        f_elbow, f_hand = limb(f_sh, (sh[0] + 14, sh[1] - 6), 30, 27, (sh[0] + 8, sh[1] + 24))
        j = dict(hip=hip, sh=sh, head=go(sh, torso - 4, 20), n_knee=n_knee, n_ankle=n_ankle, n_toe=go(n_ankle, kick + 90, 16),
                 f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, 0, 20), n_elbow=n_elbow, n_hand=n_hand,
                 f_sh=f_sh, f_elbow=f_elbow, f_hand=f_hand)
        side_figure(pic, j)
        if not bad:
            pic.path([(hip[0] - 6, 108), (hip[0] - 6, 300)], GREEN, 2.4, dashed=True)
            pic.mark(True)
            pic.caption("Teisingai: tiesiai, koja aukštai", GREEN)
        else:
            pic.path([along(hip, sh, -20), along(hip, sh, 92)], RED, 2.4, dashed=True)
            pic.mark(False)
            pic.caption("Neteisingai: atsilošta atgal", RED)
    pic.badge(10)
    pic.save("B_10.webp")


def c10():
    """Cossack squat with a kettlebell held at the chest."""
    pic, acc = Pic(), ACCENT["C"]
    standing_view(pic, 0)
    c = PCX
    front(pic, (c - 12, 206), (c + 12, 206), (c - 26, 152), (c + 26, 152), (c, 132), (c - 46, 292), (c + 46, 292),
          (c - 7, 176), (c + 7, 176), l_knee=(-8, 0), r_knee=(8, 0), l_elbow=(-12, 12), r_elbow=(12, 12))
    kettlebell(pic, (c, 172), acc)
    pic.caption("1 · Plačiai, kettlebell prie krūtinės")
    standing_view(pic, 1)
    cossack_bottom(pic, PCX + 8, acc)
    pic.arrow((PCX + 2, 166), (PCX - 44, 150), (PCX - 56, 192), acc)
    pic.caption("2 · Leiskis ant vienos kojos")
    pic.badge(10)
    pic.save("C_10.webp")


# ------------------------------------------------------------------ bodyweight mobility-strength variants (exercise 10v)
def seated_9090(pic, c, lift):
    """90/90 sit, front view; lift > 0 raises the pelvis off the floor while the knees stay down."""
    l_hip, r_hip = (c - 12, 276 - lift), (c + 12, 276 - lift)
    l_sh, r_sh = (c - 24, 226 - lift), (c + 24, 226 - lift)
    l_knee, l_ankle = (c - 52, 291), (c - 8, 295)
    r_knee, r_ankle = (c + 56, 289), (c + 76, 281)
    hands = ((c - 34, 278 - lift * 0.4), (c + 36, 278 - lift * 0.4))
    front(pic, l_hip, r_hip, l_sh, r_sh, (c, 204 - lift), l_hip, r_ankle, hands[0], hands[1],
          l_elbow=(-12, 0), r_elbow=(12, 0), feet=False, arms_behind=True, l_knee_pt=l_hip, r_knee_pt=r_knee)
    pic.capsule((r_ankle[0], r_ankle[1] + 1), (r_ankle[0] + 12, r_ankle[1] - 3), W_FOOT + 1, FAR)
    pic.capsule(l_hip, l_knee, W_THIGH + 1, NEAR)
    pic.capsule(l_knee, l_ankle, W_SHIN + 1, NEAR)
    pic.capsule((l_ankle[0] - 2, l_ankle[1] + 1), (l_ankle[0] + 15, l_ankle[1] - 1), W_FOOT + 1, NEAR)


def a10v():
    """90/90 hip lift: from the 90/90 sit, push the hips up off the floor."""
    pic, acc = Pic(), ACCENT["A"]
    for i, lift in enumerate((0, 26)):
        pic.panel(i, 300)
        pic.view(300, 300, 1.25)
        seated_9090(pic, PCX, lift)
        if lift:
            pic.arrow((PCX - 48, 290), (PCX - 54, 262), (PCX - 36, 240), acc)
        pic.caption("1 · Sėsk 90/90, keliai sulenkti" if not lift else "2 · Kelk užpakalį nuo žemės")
    pic.badge(10)
    pic.save("A_10v.webp")


def b10v():
    """Hip airplane: single-leg hinge, arms out, then rotate the pelvis open and back."""
    pic, acc = Pic(), ACCENT["B"]
    for i in range(2):
        standing_view(pic, i, 1.1)
        hip = (118, 206)
        ankle = (124, 292)
        f_ankle = go(hip, 172, 86) if i == 0 else go(hip, 160, 86)
        hands = ((176, 190), (66, 214)) if i == 0 else ((172, 170), (74, 234))
        j = side(hip, ankle, f_ankle, hands[0], hands[1], torso_ang=6, head_ang=2,
                 knee=(6, 0), f_knee=(0, 20), n_toe=-10, f_toe=0, elbow=(0, -14), f_elbow=(0, 14))
        side_figure(pic, j)
        if i:
            arc_arrow(pic, (hip[0], hip[1] + 2), 30, 24, 250, -40, acc)
        pic.caption("1 · Pasilenk, rankos į šonus" if not i else "2 · Suk klubą į išorę ir atgal")
    pic.badge(10)
    pic.save("B_10v.webp")


def c10v():
    """Kiba dachi hold: wide horse stance, thighs near parallel, knees out over the toes (vs. knees caving in)."""
    pic = Pic()
    for i, bad in enumerate((False, True)):
        standing_view(pic, i, 1.1)
        c = PCX
        spread = 78
        knee_x = 62 if not bad else 34
        l_knee, r_knee = (c - knee_x, 256), (c + knee_x, 256)
        front(pic, (c - 14, 236), (c + 14, 236), (c - 28, 182), (c + 28, 182), (c, 162), (c - spread, 292), (c + spread, 292),
              (c - 26, 238), (c + 26, 238), l_elbow=(-14, 6), r_elbow=(14, 6), l_knee_pt=l_knee, r_knee_pt=r_knee)
        for s in (-1, 1):
            pic.dot((c + s * 26, 238), 7.5, NEAR)
        if not bad:
            pic.path([(c - spread - 4, 300), (c - spread - 4, 236)], GREEN, 2.4, dashed=True)
            pic.path([(c + spread + 4, 300), (c + spread + 4, 236)], GREEN, 2.4, dashed=True)
            pic.mark(True)
            pic.caption("Teisingai: keliai virš pėdų, kumščiai prie klubų", GREEN)
        else:
            pic.arrow((c - 24, 230), (c - 14, 248), (c - 30, 262), RED, 3)
            pic.arrow((c + 24, 230), (c + 14, 248), (c + 30, 262), RED, 3)
            pic.mark(False)
            pic.caption("Neteisingai: keliai krenta į vidų", RED)
    pic.badge(10)
    pic.save("C_10v.webp")


ALL = dict(hip_cars=hip_cars, leg_swings=leg_swings, ninety_ninety=ninety_ninety, cossack=cossack, deep_squat=deep_squat,
           wgs=wgs, jacks=jacks, arm_circles=arm_circles, cat_cow=cat_cow, tspine=tspine, scap_pushup=scap_pushup,
           inchworm=inchworm, a10=a10, b10=b10, c10=c10, a10v=a10v, b10v=b10v, c10v=c10v)

if __name__ == "__main__":
    for key in sys.argv[1:] or list(ALL):
        ALL[key]()
