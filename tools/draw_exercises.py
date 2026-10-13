"""Draws two-panel exercise illustrations (start → end) for exercises that have no photo in the PDF.

Usage:  py tools/draw_exercises.py      (writes public/assets/A_9.webp, B_7.webp, B_9.webp, C_9.webp)

Style: dark navy panels like the app, a light "mannequin" figure (far-side limbs darker), day-colour arrows,
a white exercise-number badge in the corner like the PDF photos. Coordinates are in final pixels (518×346);
everything is drawn at 3× and downsampled for smooth edges.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

S = 3
W, H = 518, 346
PANEL_W, GAP = 255, 8
NAVY = (11, 16, 32)
PANEL_TOP, PANEL_BOT = (26, 37, 70), (14, 21, 44)
FLOOR, FLOOR_LINE = (29, 40, 72), (55, 70, 110)
NEAR, TORSO, FAR = (233, 238, 248), (204, 212, 232), (120, 133, 166)
TEXT, GREEN, RED = (205, 213, 236), (34, 197, 94), (239, 68, 68)
ACCENT = {"A": (59, 130, 246), "B": (249, 115, 22), "C": (34, 197, 94)}
FONT_B = r"C:\Windows\Fonts\arialbd.ttf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "assets")

W_TORSO, W_THIGH, W_SHIN, W_UPPER, W_FORE, W_FOOT, R_HAND, R_HEAD, W_NECK = 24, 15, 12, 11, 9.5, 7, 5.5, 11.5, 10


def go(p, ang, length):
    a = math.radians(ang)
    return (p[0] + math.cos(a) * length, p[1] - math.sin(a) * length)


def bezier(p0, p1, p2, n=28):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]


class Pic:
    def __init__(self):
        self.img = Image.new("RGB", (W * S, H * S), NAVY)
        self.d = ImageDraw.Draw(self.img)
        self.ox = 0
        self.pw = PANEL_W
        self.k, self.fs, self.fd = 1.0, None, None

    def full(self, floor_y):
        """One panel across the whole picture (used for single-pose stretches)."""
        self.ox, self.pw, self.fs = 0, W, None
        for y in range(H * S):
            t = y / (H * S)
            self.d.line([(0, y), (W * S - 1, y)], fill=tuple(int(PANEL_TOP[k] + (PANEL_BOT[k] - PANEL_TOP[k]) * t) for k in range(3)))
        self.d.rectangle([0, floor_y * S, W * S - 1, H * S], fill=FLOOR)
        self.d.line([(0, floor_y * S), (W * S - 1, floor_y * S)], fill=FLOOR_LINE, width=2 * S)

    def view(self, floor_src, floor_dst, k):
        """Figures are designed with the floor at y=floor_src; draw them k times larger with the floor at floor_dst."""
        self.fs, self.fd, self.k = floor_src, floor_dst, k

    def panel(self, i, floor_y):
        self.ox = 0 if i == 0 else PANEL_W + GAP
        self.pw = PANEL_W
        self.fs = None
        x0, x1 = self.ox * S, (self.ox + PANEL_W) * S - 1
        for y in range(H * S):
            t = y / (H * S)
            self.d.line([(x0, y), (x1, y)], fill=tuple(int(PANEL_TOP[k] + (PANEL_BOT[k] - PANEL_TOP[k]) * t) for k in range(3)))
        self.d.rectangle([x0, floor_y * S, x1, H * S], fill=FLOOR)
        self.d.line([(x0, floor_y * S), (x1, floor_y * S)], fill=FLOOR_LINE, width=2 * S)

    def P(self, p, raw=False):
        x, y = p
        if self.fs is not None and not raw:
            x = self.pw / 2 + (x - self.pw / 2) * self.k
            y = self.fd + (y - self.fs) * self.k
        return ((self.ox + x) * S, y * S)

    def kk(self, raw):
        return 1.0 if (raw or self.fs is None) else self.k

    def capsule(self, a, b, w, col, raw=False):
        A, B = self.P(a, raw), self.P(b, raw)
        w = w * self.kk(raw)
        self.d.line([A, B], fill=col, width=max(1, int(round(w * S))))
        r = w * S / 2
        for x, y in (A, B):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=col)

    def dot(self, c, r, col, raw=False):
        x, y = self.P(c, raw)
        r = r * self.kk(raw)
        self.d.ellipse([x - r * S, y - r * S, x + r * S, y + r * S], fill=col)

    def poly(self, pts, col, raw=False):
        self.d.polygon([self.P(p, raw) for p in pts], fill=col)

    def text(self, xy, s, size, col, anchor="la"):
        self.d.text(self.P(xy, True), s, font=ImageFont.truetype(FONT_B, int(size * S)), fill=col, anchor=anchor)

    def path(self, pts, col, w=3.2, dashed=False):
        if not dashed:
            for a, b in zip(pts, pts[1:]):
                self.capsule(a, b, w, col)
            return
        # dashes along the polyline: 7 px on, 5 px off
        on, off, pos, drawing = 7.0, 5.0, 0.0, True
        for a, b in zip(pts, pts[1:]):
            seg = math.dist(a, b)
            t = 0.0
            while t < seg:
                step = min((on if drawing else off) - pos, seg - t)
                if drawing:
                    p1 = (a[0] + (b[0] - a[0]) * t / seg, a[1] + (b[1] - a[1]) * t / seg)
                    p2 = (a[0] + (b[0] - a[0]) * (t + step) / seg, a[1] + (b[1] - a[1]) * (t + step) / seg)
                    self.capsule(p1, p2, w, col)
                t += step
                pos += step
                if pos >= (on if drawing else off) - 1e-6:
                    pos, drawing = 0.0, not drawing

    def arrow(self, p0, p1, p2, col, w=3.4):
        pts = bezier(p0, p1, p2)
        self.path(pts[:-1], col, w)
        (ax, ay), (bx, by) = pts[-4], pts[-1]
        ang = math.atan2(by - ay, bx - ax)
        length = 11 / self.kk(False)
        self.poly([(bx + 3 * math.cos(ang), by + 3 * math.sin(ang)),
                   (bx - length * math.cos(ang - 0.5), by - length * math.sin(ang - 0.5)),
                   (bx - length * math.cos(ang + 0.5), by - length * math.sin(ang + 0.5))], col)

    def mark(self, ok):
        c = (self.pw - 26, 30)
        white = (255, 255, 255)
        self.dot(c, 15, GREEN if ok else RED, raw=True)
        if ok:
            self.capsule((c[0] - 7, c[1] + 0.5), (c[0] - 2, c[1] + 6), 3.6, white, raw=True)
            self.capsule((c[0] - 2, c[1] + 6), (c[0] + 8, c[1] - 6), 3.6, white, raw=True)
        else:
            self.capsule((c[0] - 6, c[1] - 6), (c[0] + 6, c[1] + 6), 3.6, white, raw=True)
            self.capsule((c[0] - 6, c[1] + 6), (c[0] + 6, c[1] - 6), 3.6, white, raw=True)

    def label(self, s):
        self.text((self.pw - 14, 26), s, 11, (150, 162, 196), anchor="rs")

    def caption(self, s, col=TEXT):
        self.text((14, 328), s, 13.5, col, anchor="ls")

    def badge(self, n):
        self.ox = 0
        self.d.rounded_rectangle([8 * S, 8 * S, 36 * S, 36 * S], radius=5 * S, fill=(255, 255, 255))
        self.text((22, 23), str(n), 19, (12, 12, 12), anchor="mm")

    def save(self, name):
        path = os.path.join(OUT, name)
        self.img.resize((W, H), Image.LANCZOS).save(path, "WEBP", quality=86, method=6)
        print("wrote", os.path.normpath(path))


def centered(j, target=PANEL_W / 2):
    xs = [p[0] for p in j.values() if isinstance(p, tuple)]
    dx = target - (min(xs) + max(xs)) / 2
    return {k: (v[0] + dx, v[1]) if isinstance(v, tuple) else v for k, v in j.items()}


def side_figure(pic, j):
    """Side-view mannequin. Far-side limbs first, then torso, head and the near-side limbs."""
    pic.capsule(j["hip"], j["f_knee"], W_THIGH, FAR)
    pic.capsule(j["f_knee"], j["f_ankle"], W_SHIN, FAR)
    pic.capsule(j["f_ankle"], j["f_toe"], W_FOOT, FAR)
    pic.capsule(j.get("f_sh", j["sh"]), j["f_elbow"], W_UPPER, FAR)
    pic.capsule(j["f_elbow"], j["f_hand"], W_FORE, FAR)
    pic.dot(j["f_hand"], R_HAND, FAR)
    if "mid" in j:
        pic.capsule(j["hip"], j["mid"], W_TORSO, TORSO)
        pic.capsule(j["mid"], j["sh"], W_TORSO - 1, TORSO)
    else:
        pic.capsule(j["hip"], j["sh"], W_TORSO, TORSO)
    pic.capsule(j["sh"], j["head"], W_NECK, TORSO)
    pic.dot(j["head"], R_HEAD, NEAR)
    pic.capsule(j["hip"], j["n_knee"], W_THIGH, NEAR)
    pic.capsule(j["n_knee"], j["n_ankle"], W_SHIN, NEAR)
    pic.capsule(j["n_ankle"], j["n_toe"], W_FOOT, NEAR)
    pic.capsule(j["sh"], j["n_elbow"], W_UPPER, NEAR)
    pic.capsule(j["n_elbow"], j["n_hand"], W_FORE, NEAR)
    pic.dot(j["n_hand"], R_HAND, NEAR)


def lying_base(curl):
    """Lying on the back, head left. curl=0 flat, larger values lift the shoulders (lower back stays down)."""
    hip = (150, 279)
    mid = (125, 279)
    sh = go(mid, 180 - curl, 30)
    head = go(sh, 184 - curl * 1.15, 20)
    return {"hip": hip, "mid": mid, "sh": sh, "head": head}


def bent_legs(j):
    j["n_knee"] = go(j["hip"], 52, 44)
    j["n_ankle"] = (j["n_knee"][0] + 14.2, 287)
    j["n_toe"] = (j["n_ankle"][0] + 20, 288.5)
    j["f_knee"] = (j["n_knee"][0] - 5.5, j["n_knee"][1] + 1.5)
    j["f_ankle"] = (j["n_ankle"][0] - 7, 287)
    j["f_toe"] = (j["f_ankle"][0] + 20, 288.5)
    return j


def hands_at_head(j, near_ang, far_ang):
    j["n_elbow"] = go(j["sh"], near_ang, 30)
    j["n_hand"] = (j["head"][0] + 4, j["head"][1] - 9)
    j["f_elbow"] = go(j["sh"], far_ang, 28)
    j["f_hand"] = (j["head"][0] - 1, j["head"][1] - 6)
    return j


# ---------------------------------------------------------------- A9 Crunch
def crunch():
    pic, acc = Pic(), ACCENT["A"]
    start = centered(hands_at_head(bent_legs(lying_base(0)), 120, 132))
    end = hands_at_head(bent_legs(lying_base(35)), 92, 104)
    end = {k: (v[0] + (start["hip"][0] - 150), v[1]) for k, v in end.items()}
    pic.panel(0, 250)
    pic.view(292, 250, 1.45)
    side_figure(pic, start)
    pic.caption("1 · Pradžia")
    pic.panel(1, 250)
    pic.view(292, 250, 1.45)
    side_figure(pic, end)
    h = end["head"]
    pic.arrow((h[0] - 22, h[1] + 30), (h[0] - 34, h[1] + 4), (h[0] - 14, h[1] - 22), acc)
    pic.caption("2 · Pakelk pečius")
    pic.badge(9)
    pic.save("A_9.webp")


# ---------------------------------------------------------------- B9 Plank
def plank_joints(sag):
    elbow = (74, 294.5)
    sh = (74, 263.5)
    ang = -math.degrees(math.asin(23.5 / 142))
    hip = go(sh, ang, 54)
    knee = go(hip, ang, 44)
    ankle = go(knee, ang, 44)
    if sag:
        hip = (hip[0], hip[1] + 15)
        knee = (knee[0], knee[1] + 7)
    j = {
        "sh": sh, "hip": hip, "head": go(sh, 180 + ang, 20),
        "n_elbow": elbow, "n_hand": (47, 294.5), "f_sh": (78, 265), "f_elbow": (81, 294.5), "f_hand": (55, 294.5),
        "n_knee": knee, "n_ankle": ankle, "n_toe": go(ankle, -62, 12),
        "f_knee": (knee[0] + 2.5, knee[1] + 1.8), "f_ankle": (ankle[0] + 3.5, ankle[1] + 2), "f_toe": (ankle[0] + 9, 298.5),
    }
    return j, ang


def plank():
    pic = Pic()
    for i, sag in enumerate((False, True)):
        j, ang = plank_joints(sag)
        dx = PANEL_W / 2 - (j["n_hand"][0] - 6 + j["f_toe"][0] + 4) / 2
        j = {k: (v[0] + dx, v[1]) for k, v in j.items()}
        pic.panel(i, 262)
        pic.view(300, 262, 1.25)
        side_figure(pic, j)
        n = (math.cos(math.radians(ang + 90)), -math.sin(math.radians(ang + 90)))
        a = (j["head"][0] + n[0] * 24 - 4, j["head"][1] + n[1] * 24)
        b = (j["n_ankle"][0] + n[0] * 24 + 6, j["n_ankle"][1] + n[1] * 24)
        if not sag:
            pic.path([a, b], GREEN, 2.6, dashed=True)
            pic.mark(True)
            pic.caption("Teisingai: tiesi linija", GREEN)
        else:
            mid = (j["hip"][0], j["hip"][1] - 22)
            ctrl = (2 * mid[0] - (a[0] + b[0]) / 2, 2 * mid[1] - (a[1] + b[1]) / 2)
            pic.path(bezier(a, ctrl, b), RED, 2.6, dashed=True)
            pic.mark(False)
            pic.caption("Neteisingai: klubai nukarę", RED)
    pic.badge(9)
    pic.save("B_9.webp")


# ---------------------------------------------------------------- C9 Bicycle Crunch
def bicycle():
    pic, acc = Pic(), ACCENT["C"]
    base = lying_base(32)
    sh, head, hip = base["sh"], base["head"], base["hip"]
    tuck_knee = go(hip, 110, 42)
    tuck_ankle = go(tuck_knee, -5, 42)
    tuck_toe = go(tuck_ankle, 20, 18)
    long_knee = go(hip, 22, 44)
    long_ankle = go(long_knee, 22, 42)
    long_toe = go(long_ankle, 45, 16)
    back_elbow, back_hand = go(sh, 112, 29), (head[0] + 4, head[1] - 9)
    fwd_elbow, fwd_hand = (sh[0] + 10.5, sh[1] - 20), (head[0] + 1, head[1] - 5)
    panels = [
        # near knee in + far elbow forward
        dict(base, n_knee=tuck_knee, n_ankle=tuck_ankle, n_toe=tuck_toe, f_knee=long_knee, f_ankle=long_ankle, f_toe=long_toe,
             n_elbow=back_elbow, n_hand=back_hand, f_sh=(sh[0] + 3, sh[1] + 3), f_elbow=fwd_elbow, f_hand=fwd_hand),
        # mirrored: far knee in + near elbow forward
        dict(base, f_knee=tuck_knee, f_ankle=tuck_ankle, f_toe=tuck_toe, n_knee=long_knee, n_ankle=long_ankle, n_toe=long_toe,
             f_elbow=back_elbow, f_hand=back_hand, n_elbow=fwd_elbow, n_hand=fwd_hand),
    ]
    for i, j in enumerate(panels):
        j = centered(j)
        pic.panel(i, 250)
        pic.view(292, 250, 1.3)
        side_figure(pic, j)
        knee = j["n_knee"] if i == 0 else j["f_knee"]
        elbow = j["f_elbow"] if i == 0 else j["n_elbow"]
        pic.arrow((elbow[0] + 8, elbow[1] - 8), ((elbow[0] + knee[0]) / 2, min(elbow[1], knee[1]) - 26), (knee[0] - 6, knee[1] - 12), acc, 3)
        pic.caption("1 · Alkūnė prie priešingo kelio" if i == 0 else "2 · Keisk puses")
    pic.badge(9)
    pic.save("C_9.webp")


# ---------------------------------------------------------------- B7 Rear Delt Fly
def dumbbell_side(pic, hand, acc):
    pic.capsule((hand[0] - 13, hand[1]), (hand[0] + 13, hand[1]), 4, (150, 160, 190))
    for x in (hand[0] - 12, hand[0] + 12):
        pic.capsule((x, hand[1] - 8), (x, hand[1] + 8), 7, acc)


def rear_delt():
    pic, acc = Pic(), ACCENT["B"]
    # panel 1: side view - hips back, flat back about 18 degrees above horizontal, arms hanging
    pic.panel(0, 300)
    pic.view(300, 296, 1.22)
    ankle = (104, 292)
    knee = go(ankle, 78, 46)
    hip = go(knee, 106, 44)
    sh = go(hip, 18, 56)
    head = go(sh, 12, 20)
    j = {
        "hip": hip, "sh": sh, "head": head,
        "n_knee": knee, "n_ankle": ankle, "n_toe": (ankle[0] + 20, 295.5),
        "f_knee": (knee[0] - 6, knee[1] + 1), "f_ankle": (ankle[0] - 8, ankle[1]), "f_toe": (ankle[0] + 12, 295.5),
        "n_elbow": (sh[0] + 1, sh[1] + 29), "n_hand": (sh[0] + 2, sh[1] + 55),
        "f_sh": (sh[0] - 4, sh[1] + 2), "f_elbow": (sh[0] - 3, sh[1] + 31), "f_hand": (sh[0] - 2, sh[1] + 57),
    }
    j = centered(j)
    side_figure(pic, j)
    dumbbell_side(pic, j["n_hand"], acc)
    n = (math.cos(math.radians(108)), -math.sin(math.radians(108)))
    a = (j["hip"][0] + n[0] * 22, j["hip"][1] + n[1] * 22)
    b = (j["sh"][0] + n[0] * 22, j["sh"][1] + n[1] * 22)
    pic.path([a, b], acc, 2.4, dashed=True)
    pic.label("IŠ ŠONO")
    pic.caption("1 · Pasilenk, nugara tiesi")

    # panel 2: the same bent-over position from the front, arms raised out to the sides
    pic.panel(1, 300)
    pic.view(300, 296, 1.18)
    cx = PANEL_W / 2
    for side in (-1, 1):
        h, k2, an = (cx + 14 * side, 230), (cx + 21 * side, 262), (cx + 19 * side, 292)
        pic.capsule(h, k2, W_THIGH + 1, FAR)
        pic.capsule(k2, an, W_SHIN + 1, FAR)
        pic.capsule((cx + 13 * side, 296), (cx + 26 * side, 296), W_FOOT + 1, FAR)
    pic.capsule((cx - 16, 228), (cx + 16, 228), 20, FAR)
    pic.capsule((cx - 30, 214), (cx + 30, 214), 22, TORSO)
    for side in (-1, 1):
        sh2 = (cx + 30 * side, 214)
        elbow = (cx + 60 * side, 217)
        hand = (cx + 88 * side, 225)
        pic.capsule(sh2, elbow, W_UPPER + 1, NEAR)
        pic.capsule(elbow, hand, W_FORE + 1, NEAR)
        pic.dot(hand, 10, acc)
        pic.dot(hand, 4, (40, 24, 12))
        pic.arrow((cx + 34 * side, 266), (cx + 76 * side, 268), (cx + 88 * side, 242), acc, 3)
    pic.dot((cx, 222), 13, NEAR)
    pic.label("IŠ PRIEKIO")
    pic.caption("2 · Kelk rankas į šonus")
    pic.badge(7)
    pic.save("B_7.webp")


if __name__ == "__main__":
    crunch()
    plank()
    bicycle()
    rear_delt()
