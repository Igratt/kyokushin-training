"""Pictures of the endurance finishers (tools/add_endurance.py, 2026-11-18/25): punch-outs, guard hold with dumbbells,
dumbbell guard punches, the fight simulation (a minute of shadow fighting, then 10 s of burpees, or of knees in the
variant) and the heavy-bag rounds (2026-11-25; their variant, jump rope + shadow fighting, reuses the rope pose).
bounce and climber are spare drawings, checked but not used by any program now; burpee too (its plank pose is reused
by fight_burst).
Two panels each, same mannequin style. Day colour, corner number and file name are parameters, because the same
picture sits at different positions in the three programs. Called by tools/add_endurance.py (no CLI of its own).
"""
from draw_exercises import ACCENT, NEAR, R_HAND, W_FORE, Pic, bezier, go, side_figure
from draw_more import db_line
from draw_variants import CX, ellipse, front, pushup, shadow, side, standing_view

ACC = dict(ACCENT, D=(168, 85, 247))

# Fighting stance facing right, as in draw_power.pb1; fists at the cheekbones, elbows down.
STANCE = dict(torso_ang=84, head_ang=82, knee=(18, 0), elbow=(0, 16), f_elbow=(0, 16))
GUARD = ((152, 136), (143, 140))
DROPPED = ((150, 172), (142, 176))


def stance(hands=GUARD, dx=0, dy=0, **kw):
    (nx, ny), (fx, fy) = hands
    return side((118 + dx, 206 + dy), (148 + dx, 290 + dy), (90 + dx, 290 + dy), (nx + dx, ny + dy),
                (fx + dx, fy + dy), **dict(STANCE, **kw))


def with_dumbbells(pic, j, acc):
    """Neutral grip, the handle upright in the fist; the far one first so it sits behind the body."""
    db_line(pic, j["f_hand"], 90, acc)
    side_figure(pic, j)
    db_line(pic, j["n_hand"], 90, acc)


def guard(day, n, name):
    """Guard hold with light dumbbells: right (fists at the cheekbones) and wrong (guard dropped)."""
    pic, acc = Pic(), ACC[day]
    for i, ok in enumerate((True, False)):
        standing_view(pic, i)
        with_dumbbells(pic, stance(GUARD if ok else DROPPED), acc)
        pic.mark(ok)
        pic.caption("Teisingai: kumščiai prie skruostų" if ok else "Neteisingai: rankos nukrito")
    pic.badge(n)
    pic.save(name)


def guard_punch(day, n, name):
    """Slow straight punches with light dumbbells; the other fist stays at the face."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            with_dumbbells(pic, stance(), acc)
            pic.caption("1 · Gynyba su lengvais hanteliais")
        else:
            with_dumbbells(pic, stance(((178, 146), GUARD[1]), elbow=(0, 6)), acc)
            pic.arrow((168, 120), (196, 114), (222, 126), acc)
            pic.caption("2 · Lėtas smūgis ir atgal į gynybą")
    pic.badge(n)
    pic.save(name)


def punch_out(day, n, name):
    """Punch-outs: fast straight punches with light dumbbells, then the last 30 s holding the guard with them."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            with_dumbbells(pic, stance(((178, 146), GUARD[1]), elbow=(0, 6)), acc)
            pic.arrow((168, 120), (196, 114), (222, 126), acc)
            pic.caption("1 · 60 s greitų smūgių be pauzės")
        else:
            with_dumbbells(pic, stance(), acc)
            pic.caption("2 · Paskutinės 30 s – gynyba")
    pic.badge(n)
    pic.save(name)


def plate(pic, c, acc):
    """A weight plate held upright in both hands, seen from the side and turned a little toward the viewer."""
    ellipse(pic, c, 9, 26, acc)
    ellipse(pic, c, 6, 20, tuple(int(v * 0.7) for v in acc))
    ellipse(pic, c, 2.5, 5, (24, 30, 52))


def plate_press(day, n, name):
    """Plate press-outs (2026-11-24; replaced the banded punch-outs, whose band rubbed his thumb and shoulders): a plate
    in both hands pushed straight out and back fast, then held at the chin for the last 30 s."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            j, c = stance(((176, 152), (172, 154)), elbow=(0, 4), f_elbow=(0, 4)), (179, 153)
        else:
            j, c = stance(((148, 150), (144, 152))), (151, 150)
        side_figure(pic, j)
        plate(pic, c, acc)
        pic.capsule(j["n_elbow"], j["n_hand"], W_FORE, NEAR)  # the near hand grips the rim in front of the plate
        pic.dot(j["n_hand"], R_HAND, NEAR)
        if i == 0:
            pic.arrow((160, 112), (190, 104), (218, 118), acc)
        pic.caption("1 · 60 s greitų išstūmimų" if i == 0 else "2 · Paskutinės 30 s – prie smakro")
    pic.badge(n)
    pic.save(name)


def shadow_rounds(day, n, name, caps=("1 · Rankos gynyboje visą raundą", "2 · Kombinacijos be sustojimo")):
    """Shadow fighting: guard up all round, combinations without stopping."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            side_figure(pic, stance())
        else:
            side_figure(pic, stance((GUARD[0], (204, 140)), f_elbow=(0, 6)))
            pic.arrow((168, 120), (196, 114), (222, 126), acc)
        pic.caption(caps[i])
    pic.badge(n)
    pic.save(name)


def knee_strike():
    """Front-leg knee strike, side view: thigh up and forward, support leg under the hip, guard up."""
    return side((118, 206), (144, 232), (110, 290), (145, 136), (136, 140), torso_ang=92, head_ang=88,
                knee=(28, -28), f_knee=(10, 0), elbow=(0, 16), f_elbow=(0, 16), n_toe=280, f_toe=0)


def fight_burst(day, n, name, first, burst):
    """Fight simulation (his ask, 2026-11-20): a minute of fighting, then 10 s of burpees ("burpee") or knees ("knee")."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        if i == 0:
            standing_view(pic, i)
            side_figure(pic, stance((GUARD[0], (204, 140)), f_elbow=(0, 6)))
            pic.arrow((168, 120), (196, 114), (222, 126), acc)
            pic.caption(first)
        elif burst == "burpee":
            standing_view(pic, i, 1.18)
            side_figure(pic, pushup((78, 242), 296))
            pic.arrow((150, 248), (178, 238), (204, 252), acc)
            pic.caption("2 · Po minutės – 10 s burpių")
        else:
            standing_view(pic, i)
            side_figure(pic, knee_strike())
            pic.arrow((176, 232), (194, 214), (186, 184), acc)
            pic.caption("2 · Po minutės – 10 s kelių")
    pic.badge(n)
    pic.save(name)


def rope_pose(pic, acc, up=0):
    """Jump rope, front view: up=0 the rope over the head, up=14 a low jump with the rope under the feet."""
    hands = ((CX - 42, 204 - up), (CX + 42, 204 - up))
    if up:
        shadow(pic, CX, 26)
    front(pic, (CX - 12, 206 - up), (CX + 12, 206 - up), (CX - 28, 152 - up), (CX + 28, 152 - up),
          (CX, 132 - up), (CX - 13, 290 - up), (CX + 13, 290 - up), hands[0], hands[1], l_knee=(-6, 0),
          r_knee=(6, 0), l_elbow=(4, 0), r_elbow=(-4, 0))
    ends = []
    for s, h in zip((-1, 1), hands):
        ends.append((h[0] + s * 6, h[1] + 12))
        pic.capsule(h, ends[-1], 3.5, acc)
    if up:
        pic.path(bezier(ends[0], (CX, 390), ends[1]), acc, 2.4)
        pic.arrow((CX + 78, 282), (CX + 86, 256), (CX + 78, 230), acc)
    else:
        pic.path(bezier(ends[0], (CX, -16), ends[1]), acc, 2.4)


def rope(day, n, name):
    """Jump rope: the rope over the head, then under the feet in a low jump."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        standing_view(pic, i)
        rope_pose(pic, acc, 14 * i)
        pic.caption(("1 · Lengvai ant pirštų, suka riešai", "2 · Žemas šuolis, virvė po kojomis")[i])
    pic.badge(n)
    pic.save(name)


BAG, BAG_HI, BAG_TOP, CHAIN = (150, 58, 52), (184, 84, 74), (70, 32, 32), (150, 160, 186)


def heavy_bag(pic, x, acc, top=92, bottom=238):
    """A hanging heavy bag from the side: chains to a hook, leather body with a light strip, a band in the day colour."""
    hook = (x, 66)
    pic.capsule((x, 34), hook, 2.4, CHAIN)
    for s in (-1, 1):
        pic.capsule(hook, (x + s * 13, top + 3), 1.8, CHAIN)
    pic.dot(hook, 3, CHAIN)
    pic.capsule((x, top + 18), (x, bottom - 18), 36, BAG)
    pic.capsule((x - 8, top + 22), (x - 8, bottom - 24), 7, BAG_HI)
    pic.capsule((x - 15, top + 5), (x + 15, top + 5), 7, BAG_TOP)
    mid = (top + bottom) / 2
    pic.capsule((x - 17, mid), (x + 17, mid), 5, acc)


def bag_rounds(day, n, name):
    """Heavy-bag rounds (his ask, 2026-11-25: with karate only 1-2 times a week the arms burn and the stamina dropped):
    a strike with the other fist at the face and the hand straight back to the guard, then close-range combinations."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        standing_view(pic, i)
        heavy_bag(pic, 210, acc)
        if i == 0:
            side_figure(pic, stance((GUARD[0], (204, 140)), dx=10, f_elbow=(0, 6)))  # the arm stops at full reach
            pic.arrow((188, 114), (172, 106), (154, 114), acc)  # back to the guard
            pic.caption("1 · Po smūgio – ranka į gynybą")
        else:
            side_figure(pic, stance(((159, 170), GUARD[1]), dx=30))  # close: the near arm bent, a short shot
            pic.arrow((166, 204), (182, 208), (190, 192), acc)
            pic.caption("2 · Kombinacijos po 6–8 smūgius")
    pic.badge(n)
    pic.save(name)


def rope_shadow(day, n, name):
    """The rounds' variant without the bag: jump rope, then shadow fighting without stopping."""
    pic, acc = Pic(), ACC[day]
    standing_view(pic, 0)
    rope_pose(pic, acc)
    pic.caption("1 · Šokdynė: lengvai ant pirštų")
    standing_view(pic, 1)
    side_figure(pic, stance((GUARD[0], (204, 140)), f_elbow=(0, 6)))
    pic.arrow((168, 120), (196, 114), (222, 126), acc)
    pic.caption("2 · Šešėlio kova be sustojimo")
    pic.badge(n)
    pic.save(name)


def bounce(day, n, name):
    """Fighting-stance bounce: on the balls of the feet, short steps in every direction, guard up."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        standing_view(pic, i)
        if i == 0:
            side_figure(pic, stance(dy=-5, n_toe=-16, f_toe=-30))
            pic.arrow((198, 296), (206, 274), (198, 252), acc)
            pic.caption("1 · Ant pirštų, rankos gynyboje")
        else:
            shadow(pic, 140, 40)
            side_figure(pic, stance(dx=22, dy=-14, n_toe=-30, f_toe=-40))
            pic.arrow((196, 294), (218, 284), (240, 292), acc)
            pic.caption("2 · Žingsniai pirmyn, atgal, į šonus")
    pic.badge(n)
    pic.save(name)


def burpee(day, n, name):
    """Burpee: feet jump back to a straight-arm plank, then back to the hands and a jump with the arms overhead."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        if i == 0:
            standing_view(pic, i, 1.18)
            side_figure(pic, pushup((78, 242), 296))
            pic.arrow((150, 248), (178, 238), (204, 252), acc)
            pic.caption("1 · Šuoliu kojos atgal į atramą")
        else:
            standing_view(pic, i)
            shadow(pic, 128, 28)
            side_figure(pic, side((128, 190), (128, 272), (132, 274), (136, 82), (132, 84), torso_ang=90,
                                  head_ang=92, knee=(-6, 0), elbow=(-4, 0), n_toe=212, f_toe=212))
            pic.arrow((180, 262), (188, 232), (180, 204), acc)
            pic.caption("2 · Kojos prie rankų, šuolis aukštyn")
    pic.badge(n)
    pic.save(name)


def climber(day, n, name):
    """Mountain climbers: straight-arm plank, knees driven to the chest in turn."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        standing_view(pic, i, 1.18)
        j = pushup((78, 242), 296)
        knee = go(j["hip"], 200, 44)
        ankle = go(knee, -20, 44)
        if i == 0:
            j.update(n_knee=knee, n_ankle=ankle, n_toe=go(ankle, -45, 20))
        else:
            knee, ankle = (knee[0] + 3, knee[1] + 2), (ankle[0] + 3, ankle[1] + 2)
            j.update(f_knee=knee, f_ankle=ankle, f_toe=go(ankle, -45, 20))
        side_figure(pic, j)
        if i == 0:
            pic.arrow((180, 252), (152, 238), (124, 248), acc)
            pic.caption("1 · Kelis prie krūtinės, klubai žemai")
        else:
            pic.arrow((124, 248), (152, 238), (180, 252), acc)
            pic.caption("2 · Greitai keisk kojas")
    pic.badge(n)
    pic.save(name)


POSES = dict(guard=guard, guard_punch=guard_punch, punch_out=punch_out, plate_press=plate_press, shadow=shadow_rounds,
             fight=lambda d, n, f: fight_burst(d, n, f, "1 · Minutė kovos pagal eigą", "burpee"),
             fight_ext=lambda d, n, f: fight_burst(d, n, f, "1 · Po pauzės – minutė kovos", "burpee"),
             fight_kick=lambda d, n, f: fight_burst(d, n, f, "1 · Minutė kovos pagal eigą", "knee"),
             burpee=burpee, rope=rope, bounce=bounce, climber=climber, bag=bag_rounds, rope_shadow=rope_shadow)
