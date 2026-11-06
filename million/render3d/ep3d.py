"""Blender: 3D-сцены серии 1 «Вернуть миллион» (пластилиновый стиль, 12 к/с).
Запуск: blender -b -P ep3d.py -- <timeline.json> <outdir> <сцена1,сцена2|all> [samples] [scale]
Для каждой сцены рендерит кадры <outdir>/<scene>_<NNNN>.png. Экран телефона, субтитры, плашки
накладываются потом в Python (seriya01_3d.py)."""
import bpy, sys, math, json, os, random
from mathutils import Vector, Euler, Quaternion

argv = sys.argv[sys.argv.index("--") + 1:]
TL = json.load(open(argv[0]))
OUTDIR = argv[1]
WANT = None if argv[2] == "all" else set(argv[2].split(","))
SAMPLES = int(argv[3]) if len(argv) > 3 else 16
SCALE = float(argv[4]) if len(argv) > 4 else .75
BG_ONLY = len(argv) > 5 and argv[5] == "bg"   # только фон: без Дениса, широкий план
FPS3D = 12
os.makedirs(OUTDIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene


def srgb(r, g, b):
    f = lambda c: (c / 255) ** 2.2
    return (f(r), f(g), f(b))


def mat(name, col, rough=.6, sss=0.0, emit=None, strength=1.0, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (1.0, .4, .25)
        b.inputs["Subsurface Scale"].default_value = .02
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


SKIN = mat("skin", srgb(214, 170, 140), .45, sss=.2)
HAIR = mat("hair", srgb(52, 40, 34), .55)
HOOD = mat("hoodie", srgb(84, 88, 96), .85)
JEANS = mat("jeans", srgb(62, 86, 120), .8)
SHOE = mat("shoe", srgb(236, 236, 232), .5)
EYE_W = mat("eye_w", srgb(240, 236, 230), .2)
IRIS = mat("iris", srgb(96, 84, 64), .3)
PUPIL = mat("pupil", (0.004, 0.004, 0.004), .1)
LACE = mat("lace", srgb(230, 230, 226), .6)
PHONE_M = mat("phone", (0.01, 0.01, 0.012), .25, metal=.4)
SCREEN = mat("screen", (0, 0, 0), .2, emit=srgb(120, 170, 230), strength=6)
MOUTH = mat("mouth", srgb(110, 50, 50), .5)


# ---------- примитивы ----------
def link(o, coll):
    for c in o.users_collection:
        c.objects.unlink(o)
    coll.objects.link(o)


def new_coll(name):
    c = bpy.data.collections.new(name)
    S.collection.children.link(c)
    return c


def sphere(name, loc, scale, material, parent=None, coll=None, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, location=loc)
    o = bpy.context.object
    o.name, o.scale = name, scale
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.materials.append(material)
    if parent:
        o.parent = parent
    if coll:
        link(o, coll)
    return o


def box(name, loc, size, material, bevel=.3, rot=(0, 0, 0), parent=None, coll=None):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new("bevel", "BEVEL")
        bv.width = min(size) * bevel
        bv.segments = 3
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.materials.append(material)
    if parent:
        o.parent = parent
    if coll:
        link(o, coll)
    return o


def meta(name, material, parent, coll, threshold=.22, res=.016):
    mb = bpy.data.metaballs.new(name)
    mb.render_resolution, mb.resolution, mb.threshold = res, .04, threshold
    o = bpy.data.objects.new(name, mb)
    coll.objects.link(o)
    o.data.materials.append(material)
    o.parent = parent
    return mb


def set_caps(e, a, b, r):
    a, b = Vector(a), Vector(b)
    d = b - a
    e.co = (a + b) / 2
    e.radius = r
    e.size_x = max(.001, d.length / 2)
    e.rotation = Vector((1, 0, 0)).rotation_difference(d.normalized() if d.length > 1e-6 else Vector((1, 0, 0)))


def new_caps(mb, r):
    e = mb.elements.new(type="CAPSULE")
    e.radius, e.stiffness = r, 2.0
    return e


def new_ell(mb, c, size, r, stiff=2.0):
    e = mb.elements.new(type="ELLIPSOID")
    e.co, e.radius, e.stiffness = c, r, stiff
    e.size_x, e.size_y, e.size_z = size
    return e


# ---------- Денис ----------
CH = new_coll("denis")
bpy.ops.object.empty_add(location=(0, 0, 0))
ROOT = bpy.context.object; ROOT.name = "root"; link(ROOT, CH)
bpy.ops.object.empty_add(location=(0, 0, 1.64))
HEAD = bpy.context.object; HEAD.name = "head"; HEAD.parent = ROOT; link(HEAD, CH)

# голова — отдельное мягкое тело, привязано к HEAD (координаты локальные)
hb = meta("head_mb", SKIN, HEAD, CH)
new_ell(hb, (0, 0, 0), (1.18, 1.1, 1.22), .15)
new_ell(hb, (0, -.02, -.09), (.85, .8, .6), .1, 1.5)
for sx in (-1, 1):
    new_ell(hb, (sx * .118, .01, -.01), (.5, .7, .9), .055)
new_ell(hb, (0, -.135, -.02), (.6, .9, 1.0), .032, 3)
hair = meta("hair_mb", HAIR, HEAD, CH, res=.014)
new_ell(hair, (0, .025, .075), (1.2, 1.15, .78), .16)
rnd = random.Random(3)
for k in range(16):
    a = -1.3 + k * .17
    new_ell(hair, (math.sin(a) * .143, -math.cos(a) * .13 + .02, .12 + rnd.uniform(-.01, .015)), (.7, .7, .7), .05)
for k in range(6):
    x = -.075 + k * .03
    new_ell(hair, (x, -.13, .09 - abs(x) * .25), (.5, .4, .9), .03, 3)
EYES, BROWS = [], []
for sx in (-1, 1):
    e = sphere("eye", (sx * .05, -.118, .02), (.03, .014, .026), EYE_W, HEAD, CH)
    e.location = (sx * .05, -.118, .02)
    i = sphere("iris", (sx * .05, -.13, .02), (.016, .006, .016), IRIS, HEAD, CH); i.location = (sx * .05, -.13, .02)
    pp = sphere("pupil", (sx * .05, -.135, .02), (.007, .003, .007), PUPIL, HEAD, CH); pp.location = (sx * .05, -.135, .02)
    EYES.append((e, i, pp))
    br = box("brow", (0, 0, 0), (.06, .012, .014), HAIR, .4, parent=HEAD, coll=CH)
    br.location = (sx * .052, -.128, .068)
    BROWS.append((br, sx))
MOUTH_O = sphere("mouth", (0, 0, 0), (.03, .006, .005), MOUTH, HEAD, CH)
MOUTH_O.location = (0, -.124, -.1)

# тело: толстовка (торс+руки), кожа рук/шеи, джинсы
body = meta("hood_mb", HOOD, ROOT, CH)
new_ell(body, (0, 0, 1.16), (1.05, .66, 1.25), .25)
new_ell(body, (0, .03, 1.4), (1.25, .7, .45), .2, 1.6)
new_ell(body, (0, .1, 1.47), (1.0, .5, .4), .11)
ARM_E = {s: (new_caps(body, .075), new_caps(body, .065)) for s in (-1, 1)}
skin = meta("skin_mb", SKIN, ROOT, CH)
NECK = new_caps(skin, .05)
HAND_E = {s: new_ell(skin, (0, 0, 0), (.8, .7, 1.1), .07) for s in (-1, 1)}
jeans = meta("jeans_mb", JEANS, ROOT, CH)
new_ell(jeans, (0, 0, .9), (1.05, .65, .55), .21, 1.5)
LEG_E = {s: (new_caps(jeans, .1), new_caps(jeans, .085)) for s in (-1, 1)}
SHOES = {s: box("shoe", (0, 0, 0), (.13, .29, .11), SHOE, .4, parent=ROOT, coll=CH) for s in (-1, 1)}
for sx in (-1, 1):
    l = box("lace", (sx * .053, -.152, 1.33), (.01, .01, .11), LACE, .3, parent=ROOT, coll=CH)
PHONE = box("phone", (0, 0, 0), (.075, .012, .15), PHONE_M, .2, parent=ROOT, coll=CH)
SCR = box("screen", (0, -.008, 0), (.066, .004, .136), SCREEN, .1, parent=PHONE, coll=CH)
SCR.location = (0, -.008, 0)

SH = {s: Vector((s * .24, 0, 1.38)) for s in (-1, 1)}
HIP = {s: Vector((s * .11, 0, .86)) for s in (-1, 1)}
UPPER, FORE, THIGH, SHIN = .27, .27, .38, .36

ARM_POSE = {
    "down": ((.29, .01, 1.12), (.28, -.02, .86)),
    "phone": ((.29, .02, 1.12), (.14, -.21, 1.2)),
    "ear": ((.31, -.06, 1.32), (.15, -.02, 1.6)),
    "fist_up": ((.34, -.02, 1.62), (.28, -.02, 1.92)),
    "head": ((.36, -.08, 1.68), (.11, -.02, 1.8)),
    "out": ((.42, 0, 1.2), (.54, -.02, 1.0)),
    "wind": ((.36, .12, 1.62), (.42, .16, 1.86)),
    "release": ((.36, -.22, 1.32), (.5, -.44, 1.22)),
}


def mirror(p, s):
    return Vector((p[0] * s, p[1], p[2]))


def apply_pose(arms=("down", "down"), legs=None, look=(0, 0), expr="neutral", blink=False, phone=None, head_tilt=0.0, jump=0.0):
    """arms: позы (левая, правая) или ((el),(wr)) в координатах правой руки; legs: dict s->(knee, ankle) или None"""
    for s, pose in zip((-1, 1), arms):
        el, wr = ARM_POSE[pose] if isinstance(pose, str) else pose
        el, wr = mirror(el, s), mirror(wr, s)
        set_caps(ARM_E[s][0], SH[s], el, .075)
        set_caps(ARM_E[s][1], el, wr, .065)
        HAND_E[s].co = wr + (wr - el).normalized() * .05
    set_caps(NECK, (0, 0, 1.43), (0, 0, 1.53), .05)
    for s in (-1, 1):
        if legs and s in legs:
            kn, an = legs[s]
        else:
            kn, an = Vector((s * .11, -.01, .48)), Vector((s * .11, 0, .12))
        set_caps(LEG_E[s][0], HIP[s], kn, .1)
        set_caps(LEG_E[s][1], kn, an, .085)
        sh_ = SHOES[s]
        sh_.location = (an[0], an[1] - .05, an[2] - .06)
        sh_.rotation_euler = (0, 0, 0)
    # телефон
    if phone:
        s = 1 if phone == "r" else -1
        el, wr = ARM_POSE[arms[1 if s > 0 else 0]] if isinstance(arms[1 if s > 0 else 0], str) else arms[1 if s > 0 else 0]
        wr = mirror(wr, s)
        PHONE.hide_render = SCR.hide_render = False
        PHONE.location = wr + Vector((0, -.05, .06))
        PHONE.rotation_euler = (math.radians(-25), 0, math.radians(15 * s))
        if arms[1] == "ear" and s > 0:
            PHONE.location = wr + Vector((-.02, .0, .02))
            PHONE.rotation_euler = (0, 0, math.radians(90))
    else:
        PHONE.hide_render = SCR.hide_render = True
    HEAD.location = (head_tilt * .03, 0, 1.64)
    HEAD.rotation_euler = (0, math.radians(-8 * head_tilt), 0)
    # лицо
    eh = {"neutral": 1, "tense": .8, "smile": .8, "shock": 1.35, "worried": 1.1, "sad": .75}[expr]
    if blink:
        eh = .12
    for e, i, pp in EYES:
        e.scale = (.03, .014, .026 * eh)
        for o, base in ((i, (.016, .006, .016)), (pp, (.007, .003, .007))):
            o.scale = (base[0], base[1], base[2] * min(1, eh * 1.1))
        ex = e.location[0]
        i.location = (ex + look[0] * .008, -.13, .02 + look[1] * .006)
        pp.location = (ex + look[0] * .008, -.135, .02 + look[1] * .006)
    tilt = {"neutral": 0, "tense": 14, "smile": -6, "shock": -10, "worried": -16, "sad": -18}[expr]
    for br, sx in BROWS:
        br.rotation_euler = (0, math.radians(tilt * sx), 0)
        br.location = (sx * .052, -.128, .068 + (.012 if expr == "shock" else 0))
    if expr == "shock":
        MOUTH_O.scale = (.016, .008, .022)
    elif expr == "smile":
        MOUTH_O.scale = (.034, .006, .008)
    else:
        MOUTH_O.scale = (.028, .006, .005)


def cycle(mode, ph):
    if mode == "run":
        th = 42 * math.sin(ph); kn = 12 + 95 * max(0, math.cos(ph)) ** 1.3; arm = -50 * math.sin(ph); el = 85
    else:
        th = 24 * math.sin(ph); kn = 4 + 38 * max(0, math.cos(ph)) ** 1.6; arm = -22 * math.sin(ph); el = 18
    return th, kn, arm, el


def side_pose(t, mode="run", expr="tense"):
    """шаг/бег на месте: ноги и руки качаются вперёд (-Y). Корень поворачиваем в сцене."""
    f = 1.0 if mode == "walk" else 1.6
    ph = 2 * math.pi * f * t
    legs, arms = {}, []
    low = 0
    for s, off in ((-1, 0), (1, math.pi)):
        th, kn, arm, el = cycle(mode, ph + off)
        hip = HIP[s]
        knee = hip + Vector((0, -THIGH * math.sin(math.radians(th)), -THIGH * math.cos(math.radians(th))))
        ank = knee + Vector((0, -SHIN * math.sin(math.radians(th - kn)), -SHIN * math.cos(math.radians(th - kn))))
        legs[s] = (knee, ank)
        sh = Vector((.24, 0, 1.38))
        elb = sh + Vector((.03, -UPPER * math.sin(math.radians(arm)), -UPPER * math.cos(math.radians(arm))))
        wr = elb + Vector((.0, -FORE * math.sin(math.radians(arm + el)), -FORE * math.cos(math.radians(arm + el))))
        arms.append(((elb[0], elb[1], elb[2]), (wr[0], wr[1], wr[2])))
    apply_pose(arms=(arms[1], arms[0]), legs=legs, expr=expr, blink=(t % 3.1) < .1)
    low_ank = min(legs[-1][1][2], legs[1][1][2])
    bounce = (.05 * abs(math.sin(ph))) if mode == "run" else .0
    return .12 - low_ank + bounce


# ---------- декорации ----------
SETS = {}


def set_room():
    c = new_coll("room")
    WALL = mat("wall", srgb(70, 74, 92), .9)
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0)); link(bpy.context.object, c)
    bpy.context.object.data.materials.append(mat("floor", srgb(70, 56, 48), .45))
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 1.2, 3), rotation=(math.radians(90), 0, 0)); link(bpy.context.object, c)
    bpy.context.object.data.materials.append(WALL)
    box("window", (-1.0, 1.18, 1.7), (.8, .02, 1.0), mat("win", (0, 0, 0), .2, emit=srgb(40, 60, 110), strength=1.5), .02, coll=c)
    SOFA = mat("sofa", srgb(80, 66, 96), .9)
    box("sofa", (1.05, .75, .25), (1.2, .5, .5), SOFA, .25, coll=c)
    box("sofa_back", (1.05, 1.0, .55), (1.2, .15, .6), SOFA, .3, coll=c)
    return c


def set_office():
    c = new_coll("office")
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0)); link(bpy.context.object, c)
    bpy.context.object.data.materials.append(mat("ofloor", srgb(120, 110, 100), .5))
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 1.4, 3), rotation=(math.radians(90), 0, 0)); link(bpy.context.object, c)
    bpy.context.object.data.materials.append(mat("owall", srgb(196, 204, 214), .9))
    for k in range(-3, 4):
        box("owin", (k * .7, 1.38, 1.7), (.5, .02, 1.1), mat("owinm", (0, 0, 0), .2, emit=srgb(200, 220, 240), strength=2.0), 0, coll=c)
    DESK = mat("desk", srgb(140, 110, 80), .5)
    box("desk", (.95, -.05, .72), (1.0, .6, .05), DESK, .2, coll=c)
    box("monitor", (1.0, .1, 1.0), (.5, .04, .32), mat("mon", (.01, .01, .01), .3), .1, coll=c)
    return c


def set_street():
    c = new_coll("street")
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); link(bpy.context.object, c)
    bpy.context.object.data.materials.append(mat("asphalt", srgb(30, 32, 40), .15))   # мокрый асфальт
    rnd = random.Random(5)
    WINM = mat("swin", (0, 0, 0), .2, emit=srgb(255, 200, 120), strength=3)
    for k in range(-14, 15):
        h = rnd.uniform(4, 10)
        b = box("bld", (k * 2.2, 6, h / 2), (1.9, 2, h), mat(f"b{k}", srgb(36 + k % 3 * 6, 40, 56), .8), 0, coll=c)
        for wy in range(int(h * 2)):
            for wx in range(3):
                if rnd.random() < .22:
                    box("w", (k * 2.2 - .6 + wx * .6, 4.98, .8 + wy * .5), (.25, .02, .3), WINM, 0, coll=c)
    LAMP = mat("lamp", (0, 0, 0), .2, emit=srgb(255, 220, 150), strength=12)
    for k in range(-8, 9):
        box("post", (k * 3.5, 2.5, 1.5), (.06, .06, 3), mat("pole", srgb(50, 52, 60), .5), 0, coll=c)
        sphere("bulb", (k * 3.5, 2.5, 3.05), (.12, .12, .12), LAMP, coll=c)
    return c


def set_stairs():
    c = new_coll("stairs")
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); link(bpy.context.object, c)
    bpy.context.object.data.materials.append(mat("sfloor", srgb(96, 92, 86), .6))
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 1.2, 3), rotation=(math.radians(90), 0, 0)); link(bpy.context.object, c)
    bpy.context.object.data.materials.append(mat("swall", srgb(120, 124, 118), .9))
    DOOR = mat("door", srgb(70, 90, 110), .6)
    for k in range(-12, 13):
        box("door", (k * 1.8, 1.17, 1.0), (.8, .04, 2.0), DOOR, .05, coll=c)
    LAMPM = mat("slamp", (0, 0, 0), .2, emit=srgb(255, 236, 190), strength=8)
    for k in range(-12, 13):
        box("lamp", (k * 1.8 + .9, .9, 2.7), (.3, .1, .06), LAMPM, .1, coll=c)
    return c


def set_newbuild():
    c = new_coll("newbuild")
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); link(bpy.context.object, c)
    bpy.context.object.data.materials.append(mat("nb_ground", srgb(28, 30, 38), .12))
    box("tower", (.6, 8, 10), (5, 3, 20), mat("tower", srgb(56, 60, 74), .8), 0, coll=c)
    DARK = mat("dwin", srgb(30, 34, 46), .3)
    LIT = mat("lwin", (0, 0, 0), .2, emit=srgb(255, 210, 130), strength=8)
    for row in range(20):
        for col in range(5):
            lit = (row, col) == (7, 3)
            box("nw", (-1.3 + col * .95, 6.48, 1.5 + row * .95), (.55, .02, .5), LIT if lit else DARK, 0, coll=c)
    box("entrance", (.1, 6.45, .8), (1.2, .1, 1.6), mat("ent", (0, 0, 0), .3, emit=srgb(220, 214, 196), strength=1.5), 0, coll=c)
    return c


for name, fn in (("room", set_room), ("office", set_office), ("street", set_street), ("stairs", set_stairs), ("newbuild", set_newbuild)):
    SETS[name] = fn()


def show_set(name):
    for n, c in SETS.items():
        c.hide_render = n != name


# ---------- свет ----------
def light(kind, loc, energy, col, size=1.0, rot=(0, 0, 0)):
    bpy.ops.object.light_add(type=kind, location=loc, rotation=rot)
    o = bpy.context.object
    o.data.energy, o.data.color = energy, col
    if kind == "AREA":
        o.data.size = size
    return o


FILL = light("AREA", (-1.2, -1.6, 2.6), 160, (.55, .65, 1.0), 2.0, (math.radians(50), 0, math.radians(-35)))
RIMl = light("AREA", (1.4, .6, 2.0), 260, (1.0, .62, .32), .8, (math.radians(70), 0, math.radians(120)))
PHL = light("POINT", (.05, -.4, 1.34), 10, (.55, .72, 1.0))
PHL.parent = ROOT
S.world = bpy.data.worlds.new("w"); S.world.use_nodes = True
BG = S.world.node_tree.nodes["Background"]

bpy.ops.object.camera_add()
CAM = bpy.context.object
S.camera = CAM


def cam(loc, look_at, lens=40):
    CAM.location = loc
    d = Vector(look_at) - Vector(loc)
    CAM.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    CAM.data.lens = lens


def lighting(day=False, phone_light=True, rim=260, fill=160, bg=(.01, .012, .02)):
    FILL.data.energy = fill * (3 if day else 1)
    FILL.data.color = (1, .98, .95) if day else (.55, .65, 1.0)
    RIMl.data.energy = rim
    PHL.data.energy = 10 if phone_light else 0
    BG.inputs["Color"].default_value = (*bg, 1)


# ---------- сцены ----------
def place(x=0.0, y=0.0, z=0.0, face=0.0):
    ROOT.location = (x, y, z)
    ROOT.rotation_euler = (0, 0, math.radians(face))


def sc_s01(t, L):   # бег по ночной улице, камера едет рядом
    show_set("street"); lighting(rim=420, fill=220)
    x = t * 4.2
    z = side_pose(t, "run", "shock")
    place(x, 0, z, 90)
    FILL.location = (x - 1.5, -2, 3); RIMl.location = (x + 1.6, 1.2, 2.2)
    cam((x - .2, -3.0, 1.15), (x + .2, 0, 1.0), 36)


def sc_s02(t, L):
    show_set("room"); lighting()
    place(-.15, 0, 0, 0)
    apply_pose(("head", "head"), expr="sad", blink=(t % 3.4) < .1)
    cam((.25, -2.05, 1.3), (.1, 0, 1.22), 38)


def sc_s03(t, L):
    show_set("office"); lighting(day=True, phone_light=t > .9, rim=120)
    place(-.2, 0, 0, 0)
    if t > .9:
        apply_pose(("down", "phone"), look=(.5, -.8), phone="r", blink=(t % 3.4) < .1)
    else:
        apply_pose(("down", "down"), blink=(t % 3.4) < .1)
    cam((.25, -2.05, 1.3), (.1, 0, 1.22), 38)


def sc_s04(t, L):
    show_set("office"); lighting(day=True, rim=120)
    place(-.2, 0, 0, 0)
    apply_pose(("down", "phone"), look=(.5, -.8), phone="r", blink=(t % 3.4) < .1)
    cam((.2 + .05 * t / L, -2.6 + .2 * t / L, 1.25), (0, 0, 1.25), 40)


def sc_s05(t, L, p):
    show_set("office"); lighting(day=True, rim=120)
    jump = 0.0
    if .15 < p < .5:
        jump = .25 * math.sin((p - .15) / .35 * math.pi)
    up = .1 < p < .6
    legs = None
    if jump > .02:
        legs = {s: (Vector((s * .17, -.12, .56)), Vector((s * .13, .02, .28))) for s in (-1, 1)}
    place(-.2, 0, jump, 0)
    apply_pose(("out", "fist_up") if up else ("down", "phone"), legs=legs, expr="smile" if p < .6 else "worried",
               phone=None if up else "r", look=(0, 0) if up else (.5, -.8))
    cam((.25, -2.05, 1.3), (.1, 0, 1.22), 38)


def sc_s06(t, L, p):
    show_set("room"); lighting()
    place(-.15, 0, 0, 0)
    apply_pose(("down", "phone"), expr="tense", look=(.5, -.8), phone="r", blink=(t % 3.4) < .1)
    k = min(1, p / .55)
    cam((.2 - .1 * k, -2.8 + 1.4 * k, 1.25 + .05 * k), (.0, 0, 1.3), 40 + 10 * k)


def sc_s07(t, L):
    show_set("room"); lighting()
    place(-.15, 0, 0, 0)
    apply_pose(("down", "phone"), expr="worried", look=(.5, -.8), phone="r", head_tilt=math.sin(t * 5) * .8, blink=(t % 3.4) < .1)
    cam((.25, -2.05, 1.3), (.05, 0, 1.22), 38)


def sc_s08(t, L, p):
    show_set("room"); lighting()
    place(-.1, 0, 0, 0)
    if p < .45:
        apply_pose(("down", "phone"), expr="shock", look=(.5, -.8), phone="r")
    elif p < .6:
        apply_pose(("down", "wind"), expr="tense", phone="r")
    elif p < .7:
        apply_pose(("down", "release"), expr="tense")
    else:
        apply_pose(("head", "head"), expr="shock")
    if p >= .6:   # телефон летит на диван
        q = min(1, (p - .6) / .2)
        PHONE.hide_render = SCR.hide_render = False
        PHONE.parent = None
        PHONE.location = (.5 + .7 * q, -.4 + 1.0 * q, 1.3 - .9 * q + .6 * math.sin(q * math.pi))
        PHONE.rotation_euler = (q * 12, q * 6, 0)
    cam((.3, -2.3, 1.25), (.2, 0, 1.2), 38)


def sc_s09(t, L):
    show_set("room"); lighting()
    x = -.1 + .55 * math.sin(t * 1.6)
    ph = 2 * math.pi * 1.6 * t
    legs = {}
    for s, off in ((-1, 0), (1, math.pi)):
        L_ = max(0, math.sin(ph + off))
        legs[s] = (Vector((s * .11, -.12 * L_, .48 + .1 * L_)), Vector((s * .11, 0, .12 + .1 * L_)))
    place(x, 0, .02 * abs(math.cos(ph)), 0)
    apply_pose(("down", "ear"), legs=legs, expr="worried", phone="r", blink=(t % 3.4) < .1)
    cam((.25, -2.6, 1.25), (.1, 0, 1.15), 36)


def sc_s10(t, L):
    show_set("room"); lighting()
    place(-.3, 0, 0, 0)
    apply_pose(("down", "phone"), expr="shock" if t > 1.2 else "tense", look=(.5, -.8), phone="r", blink=(t % 3.4) < .1)
    cam((.1, -2.05, 1.3), (-.1, 0, 1.22), 38)


def sc_s11(t, L):
    show_set("stairs"); lighting(rim=200, fill=120)
    x = t * 4.0
    z = side_pose(t, "run", "tense")
    place(x, 0, z, 90)
    FILL.location = (x - 1.5, -2, 3); RIMl.location = (x + 1.6, 1.0, 2.2)
    cam((x - .2, -3.0, 1.2), (x + .2, 0, 1.0), 36)


def sc_s12(t, L):
    show_set("newbuild"); lighting(rim=200, fill=70)
    place(-.6, 0, 0, 0)
    apply_pose(("down", "phone"), expr="tense", look=(0, 1), phone="r", blink=(t % 3.4) < .1)
    FILL.location = (-1.2, -1.6, 2.6); RIMl.location = (1.4, .6, 2.0)
    cam((-.4, -2.6, .9), (-.3, 2, 1.9), 30)


def sc_s13(t, L, p):
    show_set("newbuild"); lighting(rim=200, fill=70)
    k = min(1, p)
    z = side_pose(t, "walk", "tense")
    place(-.9 + 1.2 * k, .4 * k, z, 90 - 40 * k)
    FILL.location = (-1.2, -1.6, 2.6); RIMl.location = (1.4, .6, 2.0)
    cam((-.6, -3.0, 1.0), (-.4, 2, 1.7), 30)


SC = {n: globals()["sc_" + n] for n in ["s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10", "s11", "s12", "s13"]}

r = S.render
r.engine = "CYCLES"
S.cycles.device = "CPU"
S.cycles.samples = SAMPLES
S.cycles.use_denoising = False
S.cycles.max_bounces = 3
S.cycles.sample_clamp_indirect = 2
r.resolution_x, r.resolution_y = 720, 1280
r.resolution_percentage = int(SCALE * 100)
S.view_settings.view_transform = "AgX"

if BG_ONLY:
    CH.hide_render = True
    _cam = cam

    def cam(loc, look_at, lens=40):   # широкий план, чтобы был виден пол под 2D-героем
        if abs(loc[1]) < 3.6 and lens >= 34 and loc[2] > .95 and look_at[1] == 0:
            _cam((loc[0] + .15, -3.6, 1.15), (look_at[0] + .15, 0, .95), 34)
        else:
            _cam(loc, look_at, lens)
    for k in list(SC):
        SC[k].__globals__["cam"] = cam
MOVING = {"s01", "s11"}   # сцены, где камера едет за героем

for sc in TL["scenes"]:
    name, L = sc["name"], sc["length"]
    if WANT and name not in WANT:
        continue
    n = int(math.ceil(L * FPS3D))
    if BG_ONLY and name not in MOVING:
        n = 1
    for f in range(n):
        out = os.path.join(OUTDIR, f"{name}_{f:04d}.png")
        if os.path.exists(out):
            continue
        t = f / FPS3D
        # прогресс реплики (для сцен, где действие привязано к словам)
        p = (t - sc["cue_start"]) / sc["cue_dur"] if sc["cue_dur"] else t / L
        PHONE.parent = ROOT
        if BG_ONLY:
            PHL.data.energy = 0
        fn = SC[name]
        if fn.__code__.co_argcount == 3:
            fn(t, L, p)
        else:
            fn(t, L)
        r.filepath = out
        bpy.ops.render.render(write_still=True)
    print("SCENE DONE", name, n)
