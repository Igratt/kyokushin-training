"""Pictures of the endurance finishers (tools/add_endurance.py, 2026-11-18): punch-outs, guard hold with dumbbells,
dumbbell guard punches, fight simulation (shadow fighting: main time and extensions) and burpees. rope, bounce and
climber are spare drawings, checked but not used by any program now.
Two panels each, same mannequin style. Day colour, corner number and file name are parameters, because the same
picture sits at different positions in the three programs. Called by tools/add_endurance.py (no CLI of its own).
"""
from draw_exercises import ACCENT, Pic, bezier, go, side_figure
from draw_more import db_line
from draw_variants import CX, front, pushup, shadow, side, standing_view

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


def rope(day, n, name):
    """Jump rope, front view: the rope over the head, then under the feet in a low jump."""
    pic, acc = Pic(), ACC[day]
    for i in range(2):
        standing_view(pic, i)
        up = 14 * i
        hands = ((CX - 42, 204 - up), (CX + 42, 204 - up))
        if i:
            shadow(pic, CX, 26)
        front(pic, (CX - 12, 206 - up), (CX + 12, 206 - up), (CX - 28, 152 - up), (CX + 28, 152 - up),
              (CX, 132 - up), (CX - 13, 290 - up), (CX + 13, 290 - up), hands[0], hands[1], l_knee=(-6, 0),
              r_knee=(6, 0), l_elbow=(4, 0), r_elbow=(-4, 0))
        ends = []
        for s, h in zip((-1, 1), hands):
            ends.append((h[0] + s * 6, h[1] + 12))
            pic.capsule(h, ends[-1], 3.5, acc)
        if i == 0:
            pic.path(bezier(ends[0], (CX, -16), ends[1]), acc, 2.4)
            pic.caption("1 · Lengvai ant pirštų, suka riešai")
        else:
            pic.path(bezier(ends[0], (CX, 390), ends[1]), acc, 2.4)
            pic.arrow((CX + 78, 282), (CX + 86, 256), (CX + 78, 230), acc)
            pic.caption("2 · Žemas šuolis, virvė po kojomis")
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


POSES = dict(guard=guard, guard_punch=guard_punch, punch_out=punch_out, shadow=shadow_rounds, burpee=burpee,
             fight=lambda d, n, f: shadow_rounds(d, n, f, ("1 · 3 min kovos tempu, gynyba",
                                                          "2 · Kas 30 s – 10 s visu greičiu")),
             fight_ext=lambda d, n, f: shadow_rounds(d, n, f, ("1 · Po 30 s pauzės – vėl gynyba",
                                                              "2 · 2 min kovos tempu, krušos")),
             rope=rope, bounce=bounce, climber=climber)
