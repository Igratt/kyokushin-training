"""Draws the two-panel pictures for the exercise variants (public/assets/<day>_<n>v.webp).

Usage:  py tools/draw_variants.py [name ...]     (no names = all)

Reuses the mannequin style of draw_exercises.py. Knees and elbows are placed with a small two-bone solver:
each pose only gives hips, shoulders, feet and hands, plus a hint point telling which way a joint bends.
"""
import math
import sys

from draw_exercises import (ACCENT, FAR, GREEN, NEAR, PANEL_W, R_HAND, RED, TORSO, W_FORE, W_FOOT, W_NECK,
                            W_SHIN, W_THIGH, W_UPPER, Pic, bezier, dumbbell_side, go, side_figure)

BAND = (168, 85, 247)
GREY = (150, 160, 190)
EQUIP = (58, 70, 104)
EQUIP_HI = (80, 94, 132)
BALL = (122, 92, 62)
DARK = (30, 22, 14)
SHADOW = (18, 26, 50)
CX = PANEL_W / 2


# ------------------------------------------------------------------ geometry helpers
def limb(a, target, l1, l2, hint):
    """Two-bone solver: returns (middle joint, end). The end is pulled in if the target is out of reach."""
    dx, dy = target[0] - a[0], target[1] - a[1]
    d = math.hypot(dx, dy) or 1e-6
    reach = l1 + l2 - 0.5
    if d > reach:
        target = (a[0] + dx / d * reach, a[1] + dy / d * reach)
        d = reach
    base = math.atan2(target[1] - a[1], target[0] - a[0])
    ang = math.acos(max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    cands = [(a[0] + math.cos(base + s * ang) * l1, a[1] + math.sin(base + s * ang) * l1) for s in (1, -1)]
    return min(cands, key=lambda m: math.dist(m, hint)), target


def joint(a, b, l1, l2, off):
    return limb(a, b, l1, l2, ((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1]))


def along(a, b, length):
    d = math.dist(a, b) or 1e-6
    return (a[0] + (b[0] - a[0]) / d * length, a[1] + (b[1] - a[1]) / d * length)


def side(hip, n_ankle, f_ankle, n_hand, f_hand, torso_ang=90, head_ang=90, knee=(30, 0), f_knee=None,
         elbow=(-20, 10), f_elbow=None, n_toe=0, f_toe=None, f_sh_off=(-3, 2), sh=None, head=None):
    """Side-view joints for side_figure(). knee/elbow are offsets from the limb middle showing the bend side."""
    sh = sh or go(hip, torso_ang, 54)
    head = head or go(sh, head_ang, 20)
    nk, na = joint(hip, n_ankle, 44, 44, knee)
    fk, fa = joint(hip, f_ankle, 44, 44, f_knee or knee)
    fsh = (sh[0] + f_sh_off[0], sh[1] + f_sh_off[1])
    ne, nh = joint(sh, n_hand, 30, 27, elbow)
    fe, fh = joint(fsh, f_hand, 30, 27, f_elbow or elbow)
    return dict(hip=hip, sh=sh, head=head, n_knee=nk, n_ankle=na, n_toe=go(na, n_toe, 20), f_knee=fk, f_ankle=fa,
                f_toe=go(fa, n_toe if f_toe is None else f_toe, 20), n_elbow=ne, n_hand=nh, f_sh=fsh, f_elbow=fe, f_hand=fh)


def shift(j, dx=0.0, dy=0.0):
    return {k: (v[0] + dx, v[1] + dy) for k, v in j.items()}


def front(pic, l_hip, r_hip, l_sh, r_sh, head, l_ankle, r_ankle, l_hand, r_hand,
          l_knee=(-10, 0), r_knee=(10, 0), l_elbow=(-14, 4), r_elbow=(14, 4), feet=True, arms_behind=False,
          l_knee_pt=None, r_knee_pt=None):
    """Front-view mannequin. Returns the solved hands and ankles.
    l_knee_pt/r_knee_pt place a knee directly (legs pointing at the viewer look short, which the solver can't do)."""
    lk, la = (l_knee_pt, l_ankle) if l_knee_pt else joint(l_hip, l_ankle, 44, 44, l_knee)
    rk, ra = (r_knee_pt, r_ankle) if r_knee_pt else joint(r_hip, r_ankle, 44, 44, r_knee)
    le, lh = joint(l_sh, l_hand, 30, 27, l_elbow)
    re, rh = joint(r_sh, r_hand, 30, 27, r_elbow)

    def arms():
        for s, e, h in ((l_sh, le, lh), (r_sh, re, rh)):
            pic.capsule(s, e, W_UPPER + 1, NEAR)
            pic.capsule(e, h, W_FORE + 1, NEAR)
            pic.dot(h, R_HAND + 0.5, NEAR)

    if arms_behind:
        arms()
    for hip, k, an, sd in ((l_hip, lk, la, -1), (r_hip, rk, ra, 1)):
        pic.capsule(hip, k, W_THIGH + 1, FAR)
        pic.capsule(k, an, W_SHIN + 1, FAR)
        if feet:
            pic.capsule((an[0] - sd * 2, an[1] + 4), (an[0] + sd * 11, an[1] + 4), W_FOOT + 1, FAR)
    pic.capsule(l_hip, r_hip, 20, FAR)
    pic.poly([(l_hip[0] - 4, l_hip[1] + 2), (r_hip[0] + 4, r_hip[1] + 2), (r_sh[0] + 2, r_sh[1]), (l_sh[0] - 2, l_sh[1])], TORSO)
    pic.dot(l_sh, 9.5, TORSO)
    pic.dot(r_sh, 9.5, TORSO)
    neck = ((l_sh[0] + r_sh[0]) / 2, (l_sh[1] + r_sh[1]) / 2 - 4)
    pic.capsule(neck, head, W_NECK, TORSO)
    pic.dot(head, 13, NEAR)
    if not arms_behind:
        arms()
    return dict(lh=lh, rh=rh, la=la, ra=ra)


# ------------------------------------------------------------------ equipment
def ellipse(pic, c, rx, ry, col):
    x, y = pic.P(c)
    k = pic.kk(False) * 3
    pic.d.ellipse([x - rx * k, y - ry * k, x + rx * k, y + ry * k], fill=col)


def arc_pts(c, r, a0, a1, n=14):
    return [go(c, a0 + (a1 - a0) * i / n, r) for i in range(n + 1)]


def rect(pic, x0, y0, x1, y1, col):
    pic.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col)


def kettlebell(pic, grip, col, off=(0, 14)):
    bell = (grip[0] + off[0], grip[1] + off[1])
    top = (bell[0], bell[1] - 7)
    pic.path(arc_pts(top, 6.5, 0, 180), col, 3)
    pic.dot(bell, 9.5, col)
    pic.dot((bell[0] - 3, bell[1] - 3), 2.2, (255, 255, 255))


def db_end(pic, hand, col):
    pic.dot(hand, 9, col)
    pic.dot(hand, 3.5, DARK)


def ball(pic, c, r=12):
    pic.dot(c, r, BALL)
    pic.path(arc_pts((c[0], c[1] - r * 1.6), r * 1.7, 245, 295), DARK, 1.6)


def cable(pic, a, b):
    pic.capsule(a, b, 1.8, GREY)


def pulley(pic, c):
    pic.dot(c, 5.5, EQUIP_HI)
    pic.dot(c, 2.2, GREY)


def post(pic, x, y0, y1=300):
    pic.capsule((x, y0), (x, y1), 8, EQUIP)


def band(pic, pts):
    pic.path(pts, BAND, 3.2)


def shadow(pic, x, w=30):
    ellipse(pic, (x, 300), w, 4, SHADOW)


def standing_view(pic, i, k=1.1):
    pic.panel(i, 300)
    pic.view(300, 300, k)


def lying_view(pic, i, k=1.35):
    pic.panel(i, 250)
    pic.view(292, 250, k)


# ------------------------------------------------------------------ A day
def a1v():
    pic, acc = Pic(), ACCENT["A"]
    standing_view(pic, 0)
    j = side((104, 228), (126, 292), (120, 292), (80, 224), (76, 220), torso_ang=46, head_ang=36, knee=(30, 0))
    side_figure(pic, j)
    pic.arrow((96, 172), (66, 186), (64, 214), acc)
    pic.caption("1 · Rankos atgal, pritūpk")
    standing_view(pic, 1)
    pic.path(bezier((20, 292), (118, 96), (236, 292))[::1], (70, 86, 128), 2.2, dashed=True)
    j = side((122, 196), (84, 242), (90, 236), (206, 138), (200, 144), torso_ang=50, head_ang=42,
             knee=(14, 16), n_toe=205, elbow=(0, 10))
    side_figure(pic, j)
    shadow(pic, 120)
    pic.arrow((178, 196), (214, 206), (226, 246), acc)
    pic.caption("2 · Šok kuo toliau")
    pic.badge(1)
    pic.save("A_1v.webp")


def a3v():
    pic, acc = Pic(), ACCENT["A"]
    standing_view(pic, 0)
    j = side((126, 204), (110, 278), (128, 292), (130, 206), (122, 208), knee=(30, 0), f_knee=(30, 0), n_toe=-20)
    side_figure(pic, j)
    kettlebell(pic, j["n_hand"], acc)
    pic.caption("1 · Stovėk ant vienos kojos")
    standing_view(pic, 1)
    hip = (128, 210)
    j = side(hip, go(hip, 176, 86), (138, 292), (186, 258), (182, 256), torso_ang=4, head_ang=2,
             knee=(0, -20), f_knee=(30, 0), n_toe=-95, f_toe=0, elbow=(-10, 0))
    side_figure(pic, j)
    kettlebell(pic, j["n_hand"], acc)
    n = (math.cos(math.radians(94)), -math.sin(math.radians(94)))
    a = (j["hip"][0] + n[0] * 20 - 30, j["hip"][1] + n[1] * 20)
    b = (j["sh"][0] + n[0] * 20, j["sh"][1] + n[1] * 20)
    pic.path([a, b], acc, 2.4, dashed=True)
    pic.caption("2 · Lenkis, koja atgal")
    pic.badge(3)
    pic.save("A_3v.webp")


def a4v():
    pic, acc = Pic(), ACCENT["A"]
    standing_view(pic, 0)
    j = side((124, 204), (128, 292), (122, 292), (142, 170), (139, 172), elbow=(4, 14))
    side_figure(pic, j)
    kettlebell(pic, (144, 168), acc)
    pic.caption("1 · Kettlebell prie krūtinės")
    standing_view(pic, 1)
    j = side((118, 240), (152, 292), (66, 284), (134, 206), (131, 208), knee=(30, -6), f_knee=(0, 24),
             f_toe=200, elbow=(4, 14))
    side_figure(pic, j)
    kettlebell(pic, (136, 204), acc)
    pic.arrow((96, 300 - 30), (76, 262), (62, 276), acc)
    pic.caption("2 · Ženk atgal ir leiskis")
    pic.badge(4)
    pic.save("A_4v.webp")


def a5v():
    pic, acc = Pic(), ACCENT["A"]
    standing_view(pic, 0)
    j = side((118, 238), (152, 292), (66, 286), (98, 236), (146, 198), torso_ang=92, knee=(30, -6),
             f_knee=(0, 24), f_toe=196, elbow=(-16, 10), f_elbow=(6, 16))
    side_figure(pic, j)
    pic.caption("1 · Įtūpstas")
    standing_view(pic, 1)
    j = side((126, 186), (100, 262), (156, 256), (150, 196), (102, 206), torso_ang=92, knee=(-10, 12),
             f_knee=(26, -4), n_toe=230, f_toe=-30, elbow=(6, 16), f_elbow=(-16, 10))
    side_figure(pic, j)
    shadow(pic, 128)
    pic.arrow((196, 286), (204, 236), (196, 196), acc)
    pic.caption("2 · Šok ir sukeisk kojas")
    pic.badge(5)
    pic.save("A_5v.webp")


def a6v():
    pic, acc = Pic(), ACCENT["A"]
    for i, up in enumerate((0, 14)):
        standing_view(pic, i)
        rect(pic, 116, 270, 206, 300, EQUIP)
        rect(pic, 116, 268, 206, 272, EQUIP_HI)
        post(pic, 186, 150)
        ankle = (120, 274 - up)
        toe_ang = 18 if not up else -42
        j = side((124, 186 - up), ankle, (104, 230 - up), (128, 240 - up), (186, 172), knee=(24, 0), f_knee=(26, 8),
                 n_toe=toe_ang, f_toe=-60, elbow=(-10, 0), f_elbow=(0, 16))
        side_figure(pic, j)
        dumbbell_side(pic, j["n_hand"], acc)
        if up:
            pic.arrow((96, 280), (90, 262), (100, 246), acc)
        pic.caption("1 · Kulnas žemai" if not up else "2 · Kilk ant pirštų")
    pic.badge(6)
    pic.save("A_6v.webp")


def bench(pic, x0, x1, top):
    rect(pic, x0, top, x1, top + 9, EQUIP_HI)
    rect(pic, x0 + 12, top + 9, x0 + 20, 292, EQUIP)
    rect(pic, x1 - 20, top + 9, x1 - 12, 292, EQUIP)


def a7v():
    pic, acc = Pic(), ACCENT["A"]
    for i in range(2):
        lying_view(pic, i, 1.25)
        bench(pic, 36, 216, 250)
        if i == 0:
            j = dict(hip=(136, 238), sh=(82, 238), head=(62, 237), n_knee=(146, 194), n_ankle=(190, 197), f_knee=(141, 196),
                     f_ankle=(184, 199), n_elbow=(60, 222), n_hand=(42, 246), f_sh=(79, 240), f_elbow=(57, 225), f_hand=(39, 244))
        else:
            j = dict(hip=(128, 222), mid=(108, 236), sh=(82, 238), head=(62, 237), n_knee=(110, 182), n_ankle=(152, 170),
                     f_knee=(106, 185), f_ankle=(147, 173), n_elbow=(60, 222), n_hand=(42, 246), f_sh=(79, 240),
                     f_elbow=(57, 225), f_hand=(39, 244))
        j["n_toe"] = go(j["n_ankle"], 15, 18)
        j["f_toe"] = go(j["f_ankle"], 15, 18)
        side_figure(pic, j)
        if i:
            pic.arrow((178, 214), (176, 172), (150, 152), acc)
        pic.caption("1 · Keliai sulenkti" if not i else "2 · Kelius link krūtinės")
    pic.badge(7)
    pic.save("A_7v.webp")


def a8v():
    pic, acc = Pic(), ACCENT["A"]
    for i in range(2):
        standing_view(pic, i)
        post(pic, 14, 160)
        anchor = (14, 214)
        pulley(pic, anchor)
        hip_y = 250
        hands = ((CX - 4, 214), (CX + 4, 214)) if i == 0 else ((CX - 3, 220), (CX + 3, 220))
        elb = ((-16, 8), (16, 8)) if i == 0 else ((-2, 0), (2, 0))
        band(pic, [anchor, (CX - 2, hands[0][1])])
        # half-kneeling, facing the viewer: front leg (image left) has its thigh pointing at us, so it looks
        # short; the back leg (image right) kneels with the knee on the floor right under the hip
        front(pic, (CX - 13, hip_y), (CX + 13, hip_y), (CX - 28, 196), (CX + 28, 196), (CX, 176),
              (CX - 17, 292), (CX + 14, 293), hands[0], hands[1], l_elbow=elb[0], r_elbow=elb[1], feet=False,
              l_knee_pt=(CX - 17, 258), r_knee_pt=(CX + 14, 292))
        pic.capsule((CX - 24, 296), (CX - 10, 296), W_FOOT + 1, FAR)
        pic.dot((CX + 14, 293), 7, FAR)
        if i:
            pic.dot((CX, 220), 7.5, NEAR)
        pic.caption("1 · Guma prie krūtinės" if not i else "2 · Spausk į priekį, nesisuk")
    pic.badge(8)
    pic.save("A_8v.webp")


def crunch_with_plate(curl):
    from draw_exercises import bent_legs, lying_base
    j = bent_legs(lying_base(curl))
    sh, hip = j["sh"], j["hip"]
    d = (hip[0] - sh[0], hip[1] - sh[1])
    ln = math.hypot(*d)
    u = (d[0] / ln, d[1] / ln)
    nrm = (u[1], -u[0])
    chest = (sh[0] + u[0] * 16 + nrm[0] * 13, sh[1] + u[1] * 16 + nrm[1] * 13)
    j["n_elbow"] = (sh[0] + u[0] * 6 + nrm[0] * 22, sh[1] + u[1] * 6 + nrm[1] * 22)
    j["n_hand"] = chest
    j["f_elbow"] = (j["n_elbow"][0] - 3, j["n_elbow"][1] + 2)
    j["f_hand"] = (chest[0] - 2, chest[1] + 1)
    plate = ((sh[0] + u[0] * 4 + nrm[0] * 15, sh[1] + u[1] * 4 + nrm[1] * 15),
             (sh[0] + u[0] * 30 + nrm[0] * 15, sh[1] + u[1] * 30 + nrm[1] * 15))
    return j, plate


def a9v():
    pic, acc = Pic(), ACCENT["A"]
    for i, curl in enumerate((0, 35)):
        lying_view(pic, i)
        j, plate = crunch_with_plate(curl)
        side_figure(pic, j)
        pic.capsule(plate[0], plate[1], 7, acc)
        pic.dot(j["n_hand"], R_HAND, NEAR)
        if curl:
            h = j["head"]
            pic.arrow((h[0] - 22, h[1] + 30), (h[0] - 34, h[1] + 4), (h[0] - 14, h[1] - 22), acc)
        pic.caption("1 · Diskas ant krūtinės" if not curl else "2 · Pakelk pečius")
    pic.badge(9)
    pic.save("A_9v.webp")


# ------------------------------------------------------------------ B day
def b1v():
    pic, acc = Pic(), ACCENT["B"]
    for i in range(2):
        standing_view(pic, i)
        post(pic, 12, 110)
        anchor = (12, 156)
        pulley(pic, anchor)
        if i == 0:
            j = side((124, 206), (156, 292), (92, 292), (150, 140), (140, 146), torso_ang=84, head_ang=80,
                     knee=(20, 0), elbow=(0, 18), f_elbow=(0, 18))
        else:
            j = side((128, 206), (158, 292), (100, 284), (142, 142), (214, 148), torso_ang=80, head_ang=78,
                     knee=(20, 0), f_toe=-40, elbow=(0, 18), f_elbow=(0, -6))
        band(pic, [anchor, (60, 150), j["f_hand"]])
        side_figure(pic, j)
        if i:
            pic.arrow((150, 118), (186, 112), (222, 126), acc)
        pic.caption("1 · Guma už nugaros" if not i else "2 · Sprogstamas smūgis")
    pic.badge(1)
    pic.save("B_1v.webp")


def b3v():
    """Band-assisted pull-ups: a loop band hangs from the bar, one foot in it, the other leg straight."""
    pic, acc = Pic(), ACCENT["B"]
    for i in range(2):
        standing_view(pic, i)
        pullup_frame(pic)
        dy = 0 if i == 0 else -40
        bx = CX - 38
        foot = (bx, 252 + dy)
        front(pic, (CX - 12, 184 + dy), (CX + 12, 184 + dy), (CX - 28, 130 + dy), (CX + 28, 130 + dy), (CX, 112 + dy),
              foot, (CX + 10, 270 + dy), (CX - 18, 72), (CX + 18, 72),
              l_elbow=(-4, 0) if i == 0 else (-14, 10), r_elbow=(4, 0) if i == 0 else (14, 10),
              l_knee_pt=(CX - 34, 230 + dy), feet=False)
        pic.capsule((CX + 8, 274 + dy), (CX + 21, 274 + dy), W_FOOT + 1, FAR)
        band(pic, [(bx, 54), (bx, foot[1] + 2)])
        pic.capsule((foot[0] - 8, foot[1] + 4), (foot[0] + 8, foot[1] + 4), W_FOOT + 1, FAR)
        band(pic, [(bx - 10, foot[1] + 8), (bx + 10, foot[1] + 8)])
        if i:
            pic.arrow((CX + 58, 210), (CX + 66, 170), (CX + 58, 130), acc)
        pic.caption("1 · Pėda gumoje, kabok" if not i else "2 · Smakras virš skersinio")
    pic.badge(3)
    pic.save("B_3v.webp")


def b4v():
    pic, acc = Pic(), ACCENT["B"]
    for i in range(2):
        standing_view(pic, i)
        hand = (132, 190) if i == 0 else (122, 132)
        j = side((118, 250), (156, 292), (70, 290), hand, (110, 244), torso_ang=90, knee=(26, -10),
                 f_knee=(0, 30), f_toe=180, elbow=(4, 18) if i == 0 else (6, 0), f_elbow=(-10, 0))
        side_figure(pic, j)
        kettlebell(pic, j["n_hand"], acc, off=(8, -6) if i == 0 else (4, -10))
        if i:
            pic.arrow((150, 196), (156, 160), (146, 128), acc)
        pic.caption("1 · Kettlebell prie peties" if not i else "2 · Spausk virš galvos")
    pic.badge(4)
    pic.save("B_4v.webp")


def b5v():
    """Landmine row: straddling the bar, hinged over, pulling the loaded end up to the chest."""
    pic, acc = Pic(), ACCENT["B"]
    for i in range(2):
        standing_view(pic, i)
        pivot = (238, 290)
        rect(pic, 226, 283, 250, 296, EQUIP_HI)
        hand = (134, 262) if i == 0 else (118, 232)
        elbow = (0, 10) if i == 0 else (-24, 4)
        j = side((84, 230), (90, 292), (98, 292), hand, (hand[0] - 4, hand[1] + 2), torso_ang=30, head_ang=24,
                 knee=(16, -8), f_knee=(16, -8), elbow=elbow, f_elbow=elbow, n_toe=-6, f_toe=-6)
        end = (hand[0] - 12, hand[1] + 5)
        pic.capsule(pivot, end, 4.5, GREY)
        pic.capsule((end[0] + 6, end[1] - 13), (end[0] + 6, end[1] + 13), 7, EQUIP_HI)
        pic.capsule((end[0], end[1] - 15), (end[0], end[1] + 15), 8, acc)
        side_figure(pic, j)
        if i:
            pic.arrow((150, 262), (154, 244), (136, 232), acc)
        pic.caption("1 · Apžergęs štangą, pasilenk" if not i else "2 · Trauk galą prie krūtinės")
    pic.badge(5)
    pic.save("B_5v.webp")


def pushup(sh, hand_y, ankle=(212, 290)):
    hip = along(sh, ankle, 54)
    ang = math.degrees(math.atan2(-(ankle[1] - sh[1]), ankle[0] - sh[0]))
    head = go(sh, 180 + ang, 20)
    j = side(hip, ankle, (ankle[0] + 4, ankle[1] + 2), (66, hand_y), (72, hand_y), sh=sh, head=head,
             knee=(0, -6), elbow=(14, -10), n_toe=-60, f_toe=-60)
    return j


def b6v():
    pic, acc = Pic(), ACCENT["B"]
    for i in range(2):
        standing_view(pic, i, 1.18)
        j = pushup((80, 272), 296) if i == 0 else pushup((78, 240), 286)
        # the band runs from the hands over the shoulders and across the upper back
        sh, hip = j["sh"], j["hip"]
        u = ((hip[0] - sh[0]) / 54, (hip[1] - sh[1]) / 54)
        b0 = along(sh, hip, 22)
        back = (b0[0] + u[1] * 14, b0[1] - u[0] * 14)
        over = (sh[0] - u[1] * -12 - 2, sh[1] - 14)
        band(pic, [j["f_hand"], (sh[0] - 4, sh[1] - 8), over, back])
        side_figure(pic, j)
        band(pic, [j["n_hand"], (sh[0] - 2, sh[1] - 10), over, back])
        if i:
            for x in (58, 66, 74):
                pic.capsule((x, 298), (x + 4, 292), 1.6, GREY)
            pic.arrow((128, 252), (124, 224), (136, 206), acc)
        pic.caption("1 · Guma per nugarą" if not i else "2 · Sprogstamai aukštyn")
    pic.badge(6)
    pic.save("B_6v.webp")


def stand_front(pic, l_hand, r_hand, l_elbow=(-14, 4), r_elbow=(14, 4), dy=0):
    return front(pic, (CX - 12, 206 + dy), (CX + 12, 206 + dy), (CX - 28, 152 + dy), (CX + 28, 152 + dy), (CX, 132 + dy),
                 (CX - 14, 292), (CX + 14, 292), l_hand, r_hand, l_elbow=l_elbow, r_elbow=r_elbow)


def b7v():
    pic, acc = Pic(), ACCENT["B"]
    standing_view(pic, 0)
    f = stand_front(pic, (CX - 20, 168), (CX + 20, 168), l_elbow=(0, 4), r_elbow=(0, 4))
    band(pic, [f["lh"], f["rh"]])
    pic.caption("1 · Guma priešais krūtinę")
    standing_view(pic, 1)
    f = stand_front(pic, (CX - 84, 158), (CX + 84, 158), l_elbow=(0, -3), r_elbow=(0, -3))
    band(pic, [f["lh"], (CX, 162), f["rh"]])
    for sd in (-1, 1):
        pic.arrow((CX + sd * 34, 192), (CX + sd * 58, 196), (CX + sd * 80, 180), acc)
    pic.caption("2 · Tempk į šonus")
    pic.badge(7)
    pic.save("B_7v.webp")


def b8v():
    """Low-to-high chop with a kettlebell: from outside the left knee up across to above the right shoulder."""
    pic, acc = Pic(), ACCENT["B"]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            f = front(pic, (CX - 12, 232), (CX + 12, 232), (CX - 36, 186), (CX + 6, 180), (CX - 14, 160),
                      (CX - 40, 292), (CX + 40, 292), (CX - 30, 226), (CX - 24, 228),
                      l_knee=(-14, 0), r_knee=(14, 0), l_elbow=(-14, 0), r_elbow=(4, 12))
        else:
            f = front(pic, (CX - 12, 212), (CX + 12, 212), (CX - 4, 160), (CX + 40, 166), (CX + 12, 138),
                      (CX - 36, 292), (CX + 36, 292), (CX + 40, 124), (CX + 46, 128),
                      l_knee=(-12, 0), r_knee=(12, 0), l_elbow=(0, -6), r_elbow=(12, 6))
        grip = ((f["lh"][0] + f["rh"][0]) / 2, (f["lh"][1] + f["rh"][1]) / 2)
        kettlebell(pic, grip, acc)
        if i:
            pic.arrow((CX - 34, 240), (CX - 14, 128), (CX + 36, 102), acc)
        pic.caption("1 · Kettlebell prie kairio kelio" if not i else "2 · Įstrižai virš dešinio peties")
    pic.badge(8)
    pic.save("B_8v.webp")


def side_plank(sag):
    sh, ankle = (70, 262), (214, 288)
    hip = along(sh, ankle, 54)
    knee = along(hip, ankle, 44)
    if sag:
        hip = (hip[0], hip[1] + 16)
        knee = (knee[0], knee[1] + 8)
    ang = math.degrees(math.atan2(-(ankle[1] - sh[1]), ankle[0] - sh[0]))
    head = go(sh, 180 + ang, 20)
    j = dict(hip=hip, sh=sh, head=head, n_knee=knee, n_ankle=ankle, n_toe=go(ankle, 0, 16),
             f_knee=(knee[0], knee[1] + 3), f_ankle=(ankle[0] + 2, ankle[1] + 4), f_toe=go((ankle[0] + 2, ankle[1] + 4), 0, 16),
             f_sh=(sh[0], sh[1] + 4), f_elbow=(68, 294), f_hand=(92, 296), n_elbow=go(sh, 90, 30), n_hand=go(sh, 90, 57))
    return j, ang


def b9v():
    pic = Pic()
    for i, sag in enumerate((False, True)):
        standing_view(pic, i, 1.2)
        j, ang = side_plank(sag)
        side_figure(pic, j)
        n = (math.cos(math.radians(ang + 90)), -math.sin(math.radians(ang + 90)))
        a = (j["head"][0] + n[0] * 24 - 4, j["head"][1] + n[1] * 24)
        b = (j["n_ankle"][0] + n[0] * 24 + 6, j["n_ankle"][1] + n[1] * 24)
        if not sag:
            pic.path([a, b], GREEN, 2.6, dashed=True)
            pic.mark(True)
            pic.caption("Teisingai: klubai aukštai", GREEN)
        else:
            mid = (j["hip"][0], j["hip"][1] - 24)
            ctrl = (2 * mid[0] - (a[0] + b[0]) / 2, 2 * mid[1] - (a[1] + b[1]) / 2)
            pic.path(bezier(a, ctrl, b), RED, 2.6, dashed=True)
            pic.mark(False)
            pic.caption("Neteisingai: klubai nukrito", RED)
    pic.badge(9)
    pic.save("B_9v.webp")


# ------------------------------------------------------------------ C day
def c1v():
    pic, acc = Pic(), ACCENT["C"]
    standing_view(pic, 0)
    j = side((106, 228), (126, 292), (120, 292), (132, 240), (128, 242), torso_ang=58, head_ang=58, elbow=(-6, 0))
    side_figure(pic, j)
    dumbbell_side(pic, j["n_hand"], acc)
    pic.caption("1 · Pritūpk su hanteliais")
    standing_view(pic, 1)
    j = side((128, 184), (124, 268), (130, 266), (132, 186), (128, 188), torso_ang=86, head_ang=86,
             knee=(8, 0), n_toe=-70, f_toe=-70, elbow=(-6, 0))
    side_figure(pic, j)
    dumbbell_side(pic, j["n_hand"], acc)
    shadow(pic, 128)
    pic.arrow((186, 286), (196, 236), (186, 196), acc)
    pic.caption("2 · Šok aukštyn")
    pic.badge(1)
    pic.save("C_1v.webp")


def c4v():
    pic, acc = Pic(), ACCENT["C"]
    standing_view(pic, 0)
    stand_front(pic, (CX - 6, 174), (CX + 6, 174), l_elbow=(-12, 10), r_elbow=(12, 10))
    kettlebell(pic, (CX, 170), acc)
    pic.caption("1 · Kettlebell prie krūtinės")
    standing_view(pic, 1)
    front(pic, (88, 246), (110, 246), (72, 194), (124, 192), (98, 174), (52, 292), (184, 292), (92, 214), (104, 214),
          l_knee=(-18, 0), r_knee=(0, -4), l_elbow=(-12, 10), r_elbow=(12, 10))
    kettlebell(pic, (98, 210), acc)
    pic.arrow((120, 278), (88, 266), (62, 276), acc)
    pic.caption("2 · Ženk į šoną ir leiskis")
    pic.badge(4)
    pic.save("C_4v.webp")


def pullup_frame(pic):
    pic.capsule((24, 52), (231, 52), 6, EQUIP)
    pic.capsule((24, 52), (24, 300), 6, EQUIP)
    pic.capsule((231, 52), (231, 300), 6, EQUIP)
    for sd in (-1, 1):
        pic.capsule((CX + sd * 18, 52), (CX + sd * 18, 72), 4, GREY)


def c5v():
    pic, acc = Pic(), ACCENT["C"]
    for i in range(2):
        standing_view(pic, i)
        pullup_frame(pic)
        dy = 0 if i == 0 else -40
        front(pic, (CX - 12, 184 + dy), (CX + 12, 184 + dy), (CX - 28, 130 + dy), (CX + 28, 130 + dy), (CX, 112 + dy),
              (CX - 10, 270 + dy), (CX + 10, 270 + dy), (CX - 18, 72), (CX + 18, 72),
              l_elbow=(-4, 0) if i == 0 else (-14, 10), r_elbow=(4, 0) if i == 0 else (14, 10), arms_behind=False)
        if i:
            pic.arrow((CX + 58, 210), (CX + 66, 170), (CX + 58, 130), acc)
        pic.caption("1 · Kabok ištiestomis rankomis" if not i else "2 · Smakras virš rankenų")
    pic.badge(5)
    pic.save("C_5v.webp")


def c6v():
    pic, acc = Pic(), ACCENT["C"]
    standing_view(pic, 0)
    f = front(pic, (CX - 12, 206), (CX + 12, 206), (CX - 28, 152), (CX + 28, 152), (CX, 132), (CX - 16, 292), (CX + 16, 292),
              (CX - 9, 98), (CX + 9, 98), l_elbow=(-6, 0), r_elbow=(6, 0))
    ball(pic, (CX, 86))
    pic.caption("1 · Kamuolys virš galvos")
    standing_view(pic, 1)
    front(pic, (CX - 12, 224), (CX + 12, 224), (CX - 6, 186), (CX + 42, 198), (CX + 20, 174), (CX - 22, 292), (CX + 24, 292),
          (CX + 52, 260), (CX + 60, 264), l_elbow=(0, 8), r_elbow=(8, 0))
    ball(pic, (CX + 62, 284))
    for k in (-1, 0, 1):
        pic.capsule((CX + 62 + k * 14, 296), (CX + 62 + k * 20, 290 - abs(k) * 2), 1.6, GREY)
    pic.arrow((CX - 36, 92), (CX + 40, 110), (CX + 66, 236), acc)
    pic.caption("2 · Trenk įstrižai į šoną")
    pic.badge(6)
    pic.save("C_6v.webp")


def c7v():
    pic, acc = Pic(), ACCENT["C"]
    for i, lean in enumerate((False, True)):
        standing_view(pic, i)
        if not lean:
            l_sh, r_sh, head, r_hand = (CX - 28, 152), (CX + 28, 152), (CX, 132), (CX + 32, 210)
        else:
            l_sh, r_sh, head, r_hand = (CX - 22, 148), (CX + 30, 166), (CX + 8, 130), (CX + 38, 222)
        front(pic, (CX - 12, 206), (CX + 12, 206), l_sh, r_sh, head, (CX - 14, 292), (CX + 14, 292),
              (CX - 32, 206), r_hand, l_elbow=(-6, 0), r_elbow=(6, 0))
        db_end(pic, (r_hand[0] + 1, r_hand[1] + 4), acc)
        a = (l_sh[0] - 26, l_sh[1] - 18)
        b = (r_sh[0] + 26, r_sh[1] - 18 + (r_sh[1] - l_sh[1]) * 0.9)
        pic.path([a, b], GREEN if not lean else RED, 2.6, dashed=True)
        pic.mark(not lean)
        pic.caption("Teisingai: pečiai lygūs" if not lean else "Neteisingai: pasvirai į šoną", GREEN if not lean else RED)
    pic.badge(7)
    pic.save("C_7v.webp")


def c8v():
    pic, acc = Pic(), ACCENT["C"]
    for i in range(2):
        lying_view(pic, i, 1.08)
        sh, hip = (95, 279), (150, 279)
        j = dict(hip=hip, mid=(125, 279), sh=sh, head=(75, 281), n_knee=(152, 236), n_ankle=(196, 238),
                 f_knee=(148, 238), f_ankle=(192, 240), f_sh=(92, 281), n_elbow=(95, 249), n_hand=(95, 222),
                 f_elbow=(93, 251), f_hand=(92, 225))
        if i:
            j["n_elbow"] = go(sh, 166, 30)
            j["n_hand"] = go(sh, 166, 57)
            j["f_knee"] = go(hip, -4, 44)
            j["f_ankle"] = go(hip, -4, 86)
        j["n_toe"] = go(j["n_ankle"], 12, 18)
        j["f_toe"] = go(j["f_ankle"], 12 if not i else 60, 18)
        j = shift(j, dx=-11 if not i else -17)
        side_figure(pic, j)
        if i:
            s, h, k, a = j["sh"], j["n_hand"], j["f_knee"], j["f_ankle"]
            pic.arrow((s[0] - 4, s[1] - 48), (s[0] - 40, s[1] - 46), (h[0] + 6, h[1] - 12), acc)
            pic.arrow((k[0] + 6, k[1] - 22), (a[0] - 12, a[1] - 26), (a[0] + 2, a[1] - 12), acc)
        pic.caption("1 · Rankos ir keliai aukštyn" if not i else "2 · Priešinga ranka ir koja")
    pic.badge(8)
    pic.save("C_8v.webp")


def c9v():
    pic, acc = Pic(), ACCENT["C"]
    for i, sd in enumerate((-1, 1)):
        standing_view(pic, i, 1.15)
        l_sh = (CX - 30, 216) if sd < 0 else (CX - 18, 212)
        r_sh = (CX + 18, 212) if sd < 0 else (CX + 30, 216)
        head = (CX + sd * 8, 194)
        hand = (CX + sd * 52, 270)
        # seated facing the viewer: knees come up towards us (short thighs), feet hover in front
        front(pic, (CX - 14, 286), (CX + 14, 286), l_sh, r_sh, head, (CX - 17, 270), (CX + 17, 270),
              (hand[0] - 4, hand[1]), (hand[0] + 4, hand[1]), l_elbow=(0, 10), r_elbow=(0, 10), feet=False,
              l_knee_pt=(CX - 22, 244), r_knee_pt=(CX + 22, 244))
        for s in (-1, 1):
            pic.capsule((CX + s * 17, 272), (CX + s * 26, 276), W_FOOT + 1, FAR)
        ball(pic, (CX + sd * 58, 282))
        pic.arrow((CX - sd * 40, 250), (CX, 228), (CX + sd * 40, 250), acc)
        pic.caption("1 · Kamuolys į kairę" if sd < 0 else "2 · Sukis į dešinę")
    pic.badge(9)
    pic.save("C_9v.webp")


ALL = [a1v, a3v, a4v, a5v, a6v, a7v, a8v, a9v, b1v, b3v, b4v, b5v, b6v, b7v, b8v, b9v,
       c1v, c4v, c5v, c6v, c7v, c8v, c9v]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for fn in ALL:
        if not wanted or fn.__name__ in wanted:
            fn()
