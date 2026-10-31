"""Draws the new exercise pictures of the karate power program (public/assets/P_<day><n>[v].webp): two panels each.

Usage:  py tools/draw_power.py [name ...]     (no names = all)
Pictures reused from the other programs are copied with the right number by tools/make_power.py.
"""
import math
import sys

from draw_exercises import ACCENT, FAR, NEAR, W_FOOT, Pic, bezier, go, side_figure
from draw_variants import CX, EQUIP, EQUIP_HI, GREY, along, ball, band, front, kettlebell, limb, post, rect, shadow, side, standing_view

ACC = ACCENT


# ------------------------------------------------------------------ helpers
def speed_lines(pic, p, ang, n=3, gap=7, length=14, back=12):
    """Short motion lines trailing behind point p (the fist, the foot), opposite to the direction `ang`."""
    nrm = (math.cos(math.radians(ang + 90)), -math.sin(math.radians(ang + 90)))
    start = go(p, ang + 180, back)
    for i in range(n):
        off = (i - (n - 1) / 2) * gap
        a = (start[0] + nrm[0] * off, start[1] + nrm[1] * off)
        pic.capsule(a, go(a, ang + 180, length), 1.8, GREY)


def box(pic, x0, x1, top, floor=300):
    rect(pic, x0, top, x1, floor, EQUIP)
    rect(pic, x0, top, x1, top + 5, EQUIP_HI)


def hurdle(pic, x, h=26, w=22):
    rect(pic, x, 300 - h, x + 3, 300, EQUIP)
    rect(pic, x + w - 3, 300 - h, x + w, 300, EQUIP)
    rect(pic, x - 2, 300 - h - 4, x + w + 2, 300 - h, EQUIP_HI)


def cone(pic, x, col=(249, 115, 22)):
    pic.poly([(x - 9, 300), (x + 9, 300), (x + 3, 276), (x - 3, 276)], col)
    rect(pic, x - 11, 297, x + 11, 300, EQUIP_HI)


def wall(pic, x=228):
    rect(pic, x, 16, x + 18, 300, EQUIP)
    rect(pic, x, 16, x + 3, 300, EQUIP_HI)


def guard(sh, f_sh):
    """Hands in front of the chin, elbows down (karate guard), side view facing right."""
    n_elbow, n_hand = limb(sh, (sh[0] + 22, sh[1] - 14), 30, 27, (sh[0] + 16, sh[1] + 22))
    f_elbow, f_hand = limb(f_sh, (sh[0] + 14, sh[1] - 6), 30, 27, (sh[0] + 8, sh[1] + 24))
    return dict(n_elbow=n_elbow, n_hand=n_hand, f_elbow=f_elbow, f_hand=f_hand)


def airborne(hip, n_ankle, f_ankle, n_hand, f_hand, **kw):
    """Side-view figure in the air: toes point down."""
    return side(hip, n_ankle, f_ankle, n_hand, f_hand, n_toe=-70, f_toe=-70, **kw)


# ------------------------------------------------------------------ A day: legs, jumps, kick speed
def pa1():
    """Depth jump: step off a box, land softly and rebound straight up as fast as possible."""
    pic, acc = Pic(), ACC["A"]
    standing_view(pic, 0)
    box(pic, 10, 72, 236)
    j = side((146, 232), (164, 292), (158, 292), (118, 226), (114, 228), torso_ang=50, head_ang=40, knee=(30, 0), elbow=(-6, 10))
    side_figure(pic, j)
    pic.arrow((78, 226), (108, 206), (134, 232), acc)
    pic.caption("1 · Nulipk, nusileisk minkštai")
    standing_view(pic, 1)
    box(pic, 10, 60, 236)
    j = airborne((128, 176), (122, 262), (130, 260), (142, 70), (138, 72), torso_ang=88, head_ang=88, knee=(8, 0), elbow=(8, 0))
    side_figure(pic, j)
    shadow(pic, 128)
    pic.arrow((196, 286), (206, 236), (196, 196), acc)
    pic.caption("2 · Iš karto atšok kuo aukščiau")
    pic.badge(1)
    pic.save("P_A1.webp")


def pa2():
    """Hurdle hops: a row of low hurdles, both feet, no pause between them."""
    pic, acc = Pic(), ACC["A"]
    standing_view(pic, 0)
    for x in (130, 170, 210):
        hurdle(pic, x)
    j = side((82, 222), (96, 292), (90, 292), (58, 230), (54, 232), torso_ang=62, head_ang=56, knee=(30, 0), elbow=(-6, 8))
    side_figure(pic, j)
    pic.caption("1 · Prieš kliūtis, lengvai pritūpk")
    standing_view(pic, 1)
    for x in (70, 112, 154):
        hurdle(pic, x)
    pic.path(bezier((56, 292), (123, 140), (190, 292)), (70, 86, 128), 2.2, dashed=True)
    j = side((124, 196), (160, 232), (154, 235), (166, 146), (162, 148), knee=(30, -10), elbow=(0, 14), n_toe=-60, f_toe=-60)
    side_figure(pic, j)
    pic.caption("2 · Šok per visas, kontaktas trumpas")
    pic.badge(2)
    pic.save("P_A2.webp")


def trap_bar(pic, hand_y, col, plate_y=None):
    """Front view of a trap bar held at the hands: axle with edge-on plates, raised handles joined by a frame."""
    plate_y = hand_y + 22 if plate_y is None else plate_y
    pic.capsule((CX - 72, plate_y), (CX + 72, plate_y), 4.5, GREY)
    pic.path([(CX - 72, plate_y), (CX - 36, hand_y), (CX + 36, hand_y), (CX + 72, plate_y)], GREY, 4)
    for s in (-1, 1):
        pic.capsule((CX + s * 72, plate_y - 22), (CX + s * 72, plate_y + 22), 8, col)
        pic.capsule((CX + s * 36, hand_y - 10), (CX + s * 36, hand_y + 10), 6, EQUIP_HI)


def pa3():
    """Trap-bar jump: deep crouch holding the handles, then a jump with the bar."""
    pic, acc = Pic(), ACC["A"]
    standing_view(pic, 0)
    trap_bar(pic, 256, acc, plate_y=278)
    front(pic, (CX - 12, 250), (CX + 12, 250), (CX - 28, 196), (CX + 28, 196), (CX, 176), (CX - 24, 292), (CX + 24, 292),
          (CX - 36, 256), (CX + 36, 256), l_elbow=(-4, 0), r_elbow=(4, 0), l_knee_pt=(CX - 34, 258), r_knee_pt=(CX + 34, 258))
    pic.caption("1 · Pritūpk, suimk rankenas")
    standing_view(pic, 1)
    shadow(pic, CX, 40)
    f = front(pic, (CX - 12, 186), (CX + 12, 186), (CX - 28, 132), (CX + 28, 132), (CX, 112), (CX - 14, 262), (CX + 14, 262),
              (CX - 36, 190), (CX + 36, 190), l_knee=(-6, 0), r_knee=(6, 0), l_elbow=(-4, 0), r_elbow=(4, 0))
    trap_bar(pic, f["lh"][1], acc)
    pic.arrow((CX + 96, 286), (CX + 104, 236), (CX + 96, 196), acc)
    pic.caption("2 · Sprogstamai šok su štanga")
    pic.badge(3)
    pic.save("P_A3.webp")


def pa4():
    """Banded knee drive: band at the ankle anchored low behind, knee thrown up like hiza geri."""
    pic, acc = Pic(), ACC["A"]
    for i in range(2):
        standing_view(pic, i)
        post(pic, 16, 150)
        anchor = (16, 270)
        pic.dot(anchor, 4, GREY)
        if i == 0:
            j = side((124, 204), (100, 292), (134, 292), (146, 136), (140, 142), knee=(10, 0), f_knee=(6, 0), elbow=(0, 18), f_elbow=(0, 18), n_toe=20)
            sh = j["sh"]
            j.update(guard(sh, j["f_sh"]))
            band(pic, [anchor, (j["n_ankle"][0] - 2, j["n_ankle"][1] - 2)])
        else:
            j = side((126, 204), (160, 232), (130, 292), (146, 136), (140, 142), knee=(30, -20), f_knee=(10, 0), elbow=(0, 18), n_toe=-80, f_toe=0)
            j.update(guard(j["sh"], j["f_sh"]))
            band(pic, [anchor, (j["n_ankle"][0] - 4, j["n_ankle"][1] + 2)])
        side_figure(pic, j)
        if i:
            pic.arrow((108, 274), (96, 226), (140, 186), acc)
        pic.caption("1 · Guma už čiurnos, stovėk tiesiai" if not i else "2 · Sprogstamai mesk kelį aukštyn")
    pic.badge(4)
    pic.save("P_A4.webp")


def pa5():
    """Lateral bound: push off one leg sideways, land on the other and stick the landing."""
    pic, acc = Pic(), ACC["A"]
    standing_view(pic, 0)
    front(pic, (CX - 30, 226), (CX - 6, 226), (CX - 46, 172), (CX - 2, 176), (CX - 22, 152), (CX - 34, 292), (CX + 18, 270),
          (CX - 70, 230), (CX - 20, 240), l_knee=(-16, 0), l_elbow=(-10, 6), r_elbow=(8, 10), r_knee_pt=(CX + 6, 256))
    pic.arrow((CX - 6, 150), (CX + 44, 112), (CX + 88, 150), acc)
    pic.caption("1 · Pritūpk ant kairės, atsispirk į šoną")
    standing_view(pic, 1)
    pic.path(bezier((CX - 76, 288), (CX - 30, 150), (CX + 6, 212)), (70, 86, 128), 2.2, dashed=True)
    front(pic, (CX + 10, 228), (CX + 34, 228), (CX + 6, 174), (CX + 50, 174), (CX + 28, 154), (CX - 10, 268), (CX + 42, 292),
          (CX - 10, 236), (CX + 72, 232), r_knee=(16, 0), l_elbow=(-8, 10), r_elbow=(10, 6), l_knee_pt=(CX + 2, 256))
    pic.caption("2 · Nusileisk ant dešinės ir sustok 1 s")
    pic.badge(5)
    pic.save("P_A5.webp")


def kick_figure(pic, hip, n_knee, n_ankle, toe_ang, torso=92):
    sh = go(hip, torso, 54)
    f_sh = (sh[0] - 3, sh[1] + 2)
    f_knee, f_ankle = limb(hip, (hip[0] + 4, 292), 44, 44, (hip[0] + 34, 248))
    j = dict(hip=hip, sh=sh, head=go(sh, torso - 4, 20), n_knee=n_knee, n_ankle=n_ankle, n_toe=go(n_ankle, toe_ang, 15),
             f_knee=f_knee, f_ankle=f_ankle, f_toe=go(f_ankle, 0, 20), f_sh=f_sh)
    j.update(guard(sh, f_sh))
    side_figure(pic, j)
    return j


def pa6():
    """Speed front kicks (mae geri): knee chambered high, snap out, snap back."""
    pic, acc = Pic(), ACC["A"]
    standing_view(pic, 0)
    kick_figure(pic, (112, 204), (152, 188), (136, 226), 20)
    pic.caption("1 · Kelis aukštai (chamber)")
    standing_view(pic, 1)
    hip = (104, 204)
    ankle = go(hip, 2, 87)
    j = kick_figure(pic, hip, along(hip, ankle, 44), ankle, 90)
    speed_lines(pic, (j["n_ankle"][0] + 4, j["n_ankle"][1] - 6), 0, back=28)
    pic.arrow((150, 236), (184, 232), (196, 212), acc)
    pic.caption("2 · Spirk greitai ir iš karto grąžink")
    pic.badge(6)
    pic.save("P_A6.webp")


def pa7():
    """Pogo jumps: straight legs, bouncing off the toes only, the shortest ground contact possible."""
    pic, acc = Pic(), ACC["A"]
    standing_view(pic, 0)
    j = side((124, 196), (128, 284), (122, 284), (142, 236), (108, 238), knee=(4, 0), elbow=(-4, 0), f_elbow=(4, 0), n_toe=-50, f_toe=-50)
    side_figure(pic, j)
    pic.caption("1 · Ant pirštų, kojos tiesios")
    standing_view(pic, 1)
    j = airborne((124, 170), (128, 258), (122, 258), (144, 208), (106, 210), knee=(4, 0), elbow=(-4, 0), f_elbow=(4, 0))
    side_figure(pic, j)
    shadow(pic, 126, 26)
    for x in (104, 118, 132):
        pic.capsule((x, 296), (x + 6, 286), 1.6, GREY)
    pic.arrow((190, 288), (196, 258), (190, 232), acc)
    pic.caption("2 · Trumpas kontaktas, kaip spyruoklė")
    pic.badge(7)
    pic.save("P_A7.webp")


# ------------------------------------------------------------------ B day: punch power, hand speed
def pb1():
    """Medicine ball chest pass into a wall from a split stance."""
    pic, acc = Pic(), ACC["B"]
    standing_view(pic, 0)
    wall(pic)
    j = side((104, 206), (134, 292), (78, 292), (134, 160), (130, 162), torso_ang=88, head_ang=86, knee=(20, 0), elbow=(-6, 14), f_elbow=(-6, 14))
    side_figure(pic, j)
    ball(pic, (146, 160))
    pic.caption("1 · Kamuolys prie krūtinės, stovėsena")
    standing_view(pic, 1)
    wall(pic)
    j = side((116, 206), (154, 292), (82, 292), (176, 150), (172, 152), torso_ang=80, head_ang=78, knee=(24, 0), f_toe=-30, elbow=(0, 6), f_elbow=(0, 6))
    side_figure(pic, j)
    ball(pic, (212, 146))
    speed_lines(pic, (212, 146), 0, back=20)
    pic.arrow((150, 126), (182, 116), (216, 124), acc)
    pic.caption("2 · Žingsnis ir mesk į sieną")
    pic.badge(1)
    pic.save("P_B1.webp")


def landmine_bar(pic, pivot, hand, col):
    end = along(pivot, hand, math.dist(pivot, hand) + 8)
    pic.capsule(pivot, end, 4.5, GREY)
    u = ((end[0] - pivot[0]) / math.dist(pivot, end), (end[1] - pivot[1]) / math.dist(pivot, end))
    p = along(pivot, hand, math.dist(pivot, hand) - 14)
    pic.capsule((p[0] - u[1] * 13, p[1] + u[0] * 13), (p[0] + u[1] * 13, p[1] - u[0] * 13), 8, col)


def pb3():
    """Landmine punch press: bar end at the shoulder, hips turn and the arm punches it forward and up."""
    pic, acc = Pic(), ACC["B"]
    pivot = (20, 290)
    standing_view(pic, 0)
    rect(pic, 8, 284, 32, 296, EQUIP_HI)
    j = side((118, 206), (150, 292), (84, 292), (136, 150), (112, 212), torso_ang=90, knee=(20, 0), elbow=(-4, 20), f_elbow=(-10, 6))
    landmine_bar(pic, pivot, j["n_hand"], acc)
    side_figure(pic, j)
    pic.caption("1 · Štangos galas prie peties")
    standing_view(pic, 1)
    rect(pic, 8, 284, 32, 296, EQUIP_HI)
    j = side((124, 206), (158, 292), (82, 286), (172, 122), (116, 214), torso_ang=82, head_ang=80, knee=(20, 0), f_toe=-40, elbow=(6, -6), f_elbow=(-10, 6))
    landmine_bar(pic, pivot, j["n_hand"], acc)
    side_figure(pic, j)
    pic.arrow((136, 136), (152, 112), (176, 96), acc)
    pic.caption("2 · Suk klubus, smūgiuok pirmyn")
    pic.badge(3)
    pic.save("P_B3.webp")


def pb4v():
    """Shadow speed punches: guard, then a full punch with the fist snapping back."""
    pic, acc = Pic(), ACC["B"]
    standing_view(pic, 0)
    j = side((124, 206), (156, 292), (92, 292), (150, 140), (140, 146), torso_ang=84, head_ang=80, knee=(20, 0), elbow=(0, 18), f_elbow=(0, 18))
    side_figure(pic, j)
    pic.caption("1 · Sargyba, kumščiai prie smakro")
    standing_view(pic, 1)
    j = side((128, 206), (158, 292), (100, 284), (142, 142), (214, 148), torso_ang=80, head_ang=78, knee=(20, 0), f_toe=-40, elbow=(0, 18), f_elbow=(0, -6))
    side_figure(pic, j)
    pic.dot(j["f_hand"], 7, FAR)
    speed_lines(pic, j["f_hand"], 0, back=14)
    pic.arrow((150, 118), (186, 112), (222, 126), acc)
    pic.caption("2 · Smūgis iki galo ir greitai atgal")
    pic.badge(4)
    pic.save("P_B4v.webp")


def pb6():
    """Landmine rotation: straight arms, the bar end swings from one hip to the other, hips do the turning."""
    pic, acc = Pic(), ACC["B"]
    for i, sd in enumerate((-1, 1)):
        standing_view(pic, i)
        rect(pic, CX - 10, 292, CX + 10, 300, EQUIP_HI)
        hand = (CX + sd * 60, 238)
        l_sh = (CX - 32, 156) if sd < 0 else (CX - 22, 148)
        r_sh = (CX + 22, 148) if sd < 0 else (CX + 32, 156)
        front(pic, (CX - 12, 206), (CX + 12, 206), l_sh, r_sh, (CX + sd * 6, 130), (CX - 40, 292), (CX + 40, 292),
              (hand[0] - 3, hand[1]), (hand[0] + 3, hand[1]), l_knee=(-10, 0), r_knee=(10, 0), l_elbow=(0, -2), r_elbow=(0, -2))
        pic.capsule((CX, 294), hand, 4.5, GREY)
        p = along((CX, 294), hand, math.dist((CX, 294), hand) - 16)
        u = ((hand[0] - CX) / math.dist((CX, 294), hand), (hand[1] - 294) / math.dist((CX, 294), hand))
        pic.capsule((p[0] - u[1] * 13, p[1] + u[0] * 13), (p[0] + u[1] * 13, p[1] - u[0] * 13), 8, acc)
        pic.dot(hand, 7, NEAR)
        if i:
            pic.arrow((CX - 56, 216), (CX, 160), (CX + 56, 216), acc)
        pic.caption("1 · Štangos galas prie kairio klubo" if not i else "2 · Greitai suk klubus į kitą pusę")
    pic.badge(6)
    pic.save("P_B6.webp")


# ------------------------------------------------------------------ C day: full body, reaction, footwork
def pc1():
    """Kettlebell swing: hinge with the bell behind, snap the hips to chest height."""
    pic, acc = Pic(), ACC["C"]
    standing_view(pic, 0)
    j = side((108, 222), (136, 292), (130, 292), (128, 246), (124, 248), torso_ang=25, head_ang=20, knee=(30, 0), elbow=(0, 0))
    side_figure(pic, j)
    kettlebell(pic, j["n_hand"], acc, off=(-6, 12))
    pic.caption("1 · Klubai atgal, svoris tarp kojų")
    standing_view(pic, 1)
    j = side((124, 204), (132, 292), (126, 292), (181, 150), (177, 152), knee=(8, 0), elbow=(0, 0))
    side_figure(pic, j)
    kettlebell(pic, (j["n_hand"][0] + 10, j["n_hand"][1]), acc, off=(12, 0))
    pic.arrow((136, 256), (200, 236), (192, 176), acc)
    pic.caption("2 · Sprogstamai ištiesk klubus iki krūtinės")
    pic.badge(1)
    pic.save("P_C1.webp")


def pc1v():
    """Medicine ball scoop toss: squat with the ball low, extend and throw it over the head backwards."""
    pic, acc = Pic(), ACC["C"]
    standing_view(pic, 0)
    j = side((120, 240), (138, 292), (132, 292), (146, 268), (142, 270), torso_ang=55, head_ang=48, knee=(30, 0), elbow=(0, 0))
    side_figure(pic, j)
    ball(pic, (152, 278))
    pic.caption("1 · Kamuolys žemai tarp kojų")
    standing_view(pic, 1)
    j = side((128, 200), (134, 286), (128, 288), (98, 106), (94, 108), torso_ang=96, head_ang=104, knee=(8, 0), elbow=(8, -8), n_toe=-50, f_toe=-50)
    side_figure(pic, j)
    pic.path(bezier((92, 100), (50, 24), (14, 70)), (70, 86, 128), 2.2, dashed=True)
    ball(pic, (46, 50))
    pic.arrow((176, 262), (186, 206), (168, 150), acc)
    pic.caption("2 · Ištiesk ir mesk per galvą atgal")
    pic.badge(1)
    pic.save("P_C1v.webp")


def pc2():
    """Shuttle sprint: explosive start, touch the line, sprint back."""
    pic, acc = Pic(), ACC["C"]
    standing_view(pic, 0)
    cone(pic, 20)
    cone(pic, 234)
    j = side((110, 206), (146, 244), (72, 290), (84, 212), (150, 150), torso_ang=70, head_ang=66, knee=(30, -16), f_knee=(-6, 10),
             elbow=(-10, 10), f_elbow=(6, 10), n_toe=-60, f_toe=-30)
    side_figure(pic, j)
    speed_lines(pic, (j["hip"][0] - 10, j["hip"][1] - 20), 0, n=3, gap=10, length=16, back=18)
    pic.arrow((150, 264), (180, 258), (212, 262), acc)
    pic.caption("1 · Startuok sprogstamai, 10 m")
    standing_view(pic, 1)
    cone(pic, 20)
    cone(pic, 234)
    j = side((160, 236), (178, 292), (150, 292), (216, 294), (194, 262), torso_ang=28, head_ang=20, knee=(30, 0), f_knee=(24, 0), elbow=(10, -6), f_elbow=(6, 6))
    side_figure(pic, j)
    pic.arrow((176, 178), (120, 156), (66, 184), acc)
    pic.caption("2 · Paliesk liniją ir sprintu atgal")
    pic.badge(2)
    pic.save("P_C2.webp")


def pc2v():
    """Fast feet: low athletic stance, tapping the feet on the spot as fast as possible."""
    pic, acc = Pic(), ACC["C"]
    for i in range(2):
        standing_view(pic, i)
        r_ankle = (CX + 30, 292) if i == 0 else (CX + 30, 278)
        front(pic, (CX - 12, 222), (CX + 12, 222), (CX - 28, 168), (CX + 28, 168), (CX, 148), (CX - 30, 292), r_ankle,
              (CX - 36, 236), (CX + 36, 236), l_knee=(-10, 0), r_knee=(10, 0), l_elbow=(-12, 4), r_elbow=(12, 4))
        for s in (-1, 1):
            for k in (-1, 0, 1):
                pic.capsule((CX + s * 30 + k * 9, 298), (CX + s * 30 + k * 9 + 4, 292), 1.5, GREY)
        if i:
            pic.arrow((CX + 56, 296), (CX + 64, 282), (CX + 56, 268), acc, 3)
            pic.arrow((CX - 56, 268), (CX - 64, 282), (CX - 56, 296), acc, 3)
        pic.caption("1 · Žema stovėsena, ant pirštų" if not i else "2 · Kuo greičiau tapsėk vietoje")
    pic.badge(2)
    pic.save("P_C2v.webp")


def pc3():
    """Tuck jump: quarter squat, jump and pull the knees to the chest."""
    pic, acc = Pic(), ACC["C"]
    standing_view(pic, 0)
    j = side((112, 226), (130, 292), (124, 292), (80, 230), (76, 232), torso_ang=56, head_ang=50, knee=(30, 0), elbow=(-6, 8))
    side_figure(pic, j)
    pic.caption("1 · Lengvai pritūpk, rankos atgal")
    standing_view(pic, 1)
    hip = (126, 176)
    sh = go(hip, 88, 54)
    f_sh = (sh[0] - 3, sh[1] + 2)
    n_elbow, n_hand = limb(sh, (162, 160), 30, 27, (150, 150))
    f_elbow, f_hand = limb(f_sh, (158, 162), 30, 27, (146, 152))
    j = dict(hip=hip, sh=sh, head=go(sh, 88, 20), n_knee=(156, 158), n_ankle=(152, 200), n_toe=go((152, 200), -70, 14),
             f_knee=(151, 161), f_ankle=(147, 203), f_toe=go((147, 203), -70, 14), f_sh=f_sh,
             n_elbow=n_elbow, n_hand=n_hand, f_elbow=f_elbow, f_hand=f_hand)
    side_figure(pic, j)
    shadow(pic, 132)
    pic.arrow((200, 286), (210, 236), (200, 196), acc)
    pic.caption("2 · Šok ir trauk kelius prie krūtinės")
    pic.badge(3)
    pic.save("P_C3.webp")


def pc5():
    """Speed roundhouse kicks (mawashi geri), front view: knee chambered to the side, leg whips out level."""
    pic, acc = Pic(), ACC["C"]
    standing_view(pic, 0)
    front(pic, (CX - 14, 206), (CX + 10, 206), (CX - 30, 154), (CX + 22, 152), (CX - 4, 132), (CX - 12, 292), (CX + 54, 222),
          (CX - 16, 162), (CX + 14, 160), l_knee=(-6, 0), l_elbow=(-14, 10), r_elbow=(12, 12), r_knee_pt=(CX + 46, 198), feet=False)
    pic.capsule((CX - 20, 296), (CX - 2, 296), W_FOOT + 1, FAR)
    pic.capsule((CX + 52, 226), (CX + 64, 218), W_FOOT + 1, FAR)
    pic.caption("1 · Kelis aukštai į šoną (chamber)")
    standing_view(pic, 1)
    front(pic, (CX - 20, 206), (CX + 4, 206), (CX - 42, 156), (CX + 12, 150), (CX - 18, 132), (CX - 18, 292), (CX + 92, 196),
          (CX - 24, 164), (CX + 8, 160), l_knee=(-6, 0), l_elbow=(-14, 10), r_elbow=(12, 12), r_knee_pt=(CX + 48, 200), feet=False)
    pic.capsule((CX - 30, 296), (CX - 12, 296), W_FOOT + 1, FAR)
    pic.capsule((CX + 92, 196), (CX + 106, 190), W_FOOT + 1, FAR)
    speed_lines(pic, (CX + 104, 198), 70, n=3, gap=8, length=12, back=10)
    pic.arrow((CX + 40, 252), (CX + 96, 246), (CX + 100, 210), acc)
    pic.caption("2 · Spirk ratu ir greitai grąžink")
    pic.badge(5)
    pic.save("P_C5.webp")


ALL = dict(pa1=pa1, pa2=pa2, pa3=pa3, pa4=pa4, pa5=pa5, pa6=pa6, pa7=pa7, pb1=pb1, pb3=pb3, pb4v=pb4v, pb6=pb6,
           pc1=pc1, pc1v=pc1v, pc2=pc2, pc2v=pc2v, pc3=pc3, pc5=pc5)

if __name__ == "__main__":
    for key in sys.argv[1:] or list(ALL):
        ALL[key]()
