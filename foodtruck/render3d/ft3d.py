"""Blender: «Фудтрак с нуля» в игрушечном 3D (как в референсе): крупный персонаж, уютный интерьер, мягкий свет.
Пробный кадр: blender -b -P ft3d.py -- test <out.png> [samples]
Кадры сцены: blender -b -P ft3d.py -- scene <name> <outdir> <длина_с> [samples]   (12 к/с)"""
import bpy, sys, math, os, random
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
MODE = argv[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
FPS3D = 12


def srgb(r, g, b):
    f = lambda c: (c / 255) ** 2.2
    return (f(r), f(g), f(b))


def mat(name, col, rough=.55, emit=None, strength=1.0, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


M = {
    "skin": mat("skin", srgb(226, 178, 142), .5),
    "hair": mat("hair", srgb(34, 28, 26), .6),
    "beard": mat("beard", srgb(46, 36, 32), .7),
    "hood": mat("hood", srgb(46, 122, 96), .7),
    "apron": mat("apron", srgb(244, 242, 236), .6),
    "pants": mat("pants", srgb(44, 48, 60), .75),
    "shoe": mat("shoe", srgb(36, 36, 40), .5),
    "eye": mat("eye", (0.003, 0.003, 0.003), .15, coat=1),
    "eyehl": mat("eyehl", (1, 1, 1), .2, emit=(1, 1, 1), strength=2),
    "mouth": mat("mouth", srgb(110, 50, 50), .5),
    "tile": mat("tile", srgb(244, 240, 228), .25, coat=.4),
    "grout": mat("grout", srgb(200, 196, 186), .8),
    "steel": mat("steel", srgb(176, 182, 190), .25, metal=.8),
    "dark": mat("dark", srgb(40, 42, 48), .5),
    "wood": mat("wood", srgb(168, 120, 78), .55),
    "red": mat("red", srgb(212, 62, 48), .45, coat=.3),
    "floor": mat("floor", srgb(96, 82, 70), .7),
    "glass": mat("glass", srgb(170, 210, 236), .1, emit=srgb(170, 210, 236), strength=.6),
    "street": mat("street", srgb(160, 176, 196), .9, emit=srgb(150, 170, 196), strength=.8),
    "bulb": mat("bulb", (1, .9, .7), .3, emit=(1, .85, .6), strength=12),
}


def shade_smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


def sphere(name, loc, scale, m, parent=None, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, location=loc)
    o = bpy.context.object
    o.name, o.scale = name, scale
    o.data.materials.append(M[m])
    shade_smooth(o)
    if parent:
        o.parent = parent
    return o


def cube(name, loc, size, m, bevel=.02, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(M[m])
    if bevel:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bv = o.modifiers.new("b", "BEVEL"); bv.width, bv.segments = bevel, 3
        shade_smooth(o)
    o.location = loc
    if parent:
        o.parent = parent
        o.location = loc
    return o


def capsule(name, a, b, r, m, parent=None):
    """цилиндр со сферами на концах между точками a и b"""
    a, b = Vector(a), Vector(b)
    mid, d = (a + b) / 2, (b - a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=r, depth=d.length, location=mid)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    o.data.materials.append(M[m])
    shade_smooth(o)
    for p_ in (a, b):
        s = sphere(name + "_e", p_, (r, r, r), m)
        s.parent = o
        s.matrix_parent_inverse = o.matrix_world.inverted()
    if parent:
        o.parent = parent
    return o


def empty(name, loc, parent=None):
    bpy.ops.object.empty_add(location=loc)
    o = bpy.context.object
    o.name = name
    if parent:
        o.parent = parent
        o.location = loc
    return o


# ---------- Тимур ----------
def build_timur():
    root = empty("timur", (0, 0, 0))
    # ноги
    for sx in (-1, 1):
        capsule(f"leg{sx}", (sx * .13, 0, .12), (sx * .13, 0, .55), .1, "pants", root)
        cube(f"shoe{sx}", (sx * .13, -.05, .06), (.2, .3, .12), "shoe", .04, root)
    # тело
    body = sphere("body", (0, 0, .95), (.36, .3, .46), "hood", root)
    apron = cube("apron", (0, -.29, .82), (.42, .04, .5), "apron", .05, root)      # фартук
    cube("strap", (0, -.27, 1.17), (.08, .03, .3), "apron", .01, root)
    cube("pocket", (0, -.315, .76), (.2, .02, .12), "apron", .02, root)
    # руки на шарнирах (плечо)
    arms = {}
    for sx in (-1, 1):
        sh = empty(f"shoulder{sx}", (sx * .36, 0, 1.22), root)
        up = capsule(f"arm{sx}", (0, 0, 0), (0, 0, -.42), .085, "hood", sh)
        hand = sphere(f"hand{sx}", (0, 0, -.5), (.1, .1, .1), "skin", sh)
        arms[sx] = sh
    # голова
    neck = empty("neck", (0, 0, 1.42), root)
    head = sphere("head", (0, 0, .36), (.36, .34, .38), "skin", neck)
    hair = sphere("hair", (0, .02, .5), (.37, .35, .3), "hair", neck)
    beard = sphere("beard", (0, -.06, .17), (.32, .29, .2), "beard", neck)
    nose = sphere("nose", (0, -.34, .36), (.06, .05, .06), "skin", neck)
    eyes = []
    for sx in (-1, 1):
        e = sphere(f"eye{sx}", (sx * .13, -.31, .44), (.045, .03, .055), "eye", neck)
        h = sphere(f"eyehl{sx}", (sx * .13 - .012, -.335, .465), (.012, .01, .012), "eyehl", neck)
        brow = cube(f"brow{sx}", (sx * .13, -.32, .53), (.12, .03, .025), "hair", .01, neck)
        eyes.append((e, h, brow))
    mouth = cube("mouth", (0, -.355, .25), (.13, .03, .025), "mouth", .01, neck)
    return dict(root=root, arms=arms, neck=neck, eyes=eyes, mouth=mouth)


def pose(T, t, arms=("down", "down"), smile=False, look=0.0, talk=False):
    A = {"down": (0, 8), "up": (0, 160), "wave": (0, 135 + 22 * math.sin(t * 9)), "front": (-75, 12), "hip": (0, 35)}
    for sx, key in zip((-1, 1), arms):
        rx, ry = A[key]
        T["arms"][sx].rotation_euler = (math.radians(rx), -math.radians(ry) * sx, 0)
    T["neck"].rotation_euler = (0, math.radians(4 * math.sin(t * 1.3)), math.radians(look))
    T["root"].location.z = .01 * math.sin(t * 2.4)   # дыхание
    m = 2.6 if smile else 1.0
    if talk:
        m = 1.0 + 2.2 * abs(math.sin(t * 13)) * (.6 + .4 * abs(math.sin(t * 3.1)))
    T["mouth"].scale = (1.0, 1.0, m)


# ---------- фургон-кухня ----------
def build_truck():
    W_, D_, H_ = 3.6, 2.4, 2.5
    cube("floor", (0, 0, -.02), (W_, D_, .04), "floor", 0)
    back = cube("back", (0, 1.2, H_ / 2), (W_, .06, H_), "tile", 0)
    for i in range(-8, 9):   # швы кафеля
        cube(f"gv{i}", (i * .22, 1.165, H_ / 2), (.012, .01, H_), "grout", 0)
    for j in range(12):
        cube(f"gh{j}", (0, 1.165, .2 + j * .22), (W_, .01, .012), "grout", 0)
    for sx in (-1, 1):
        cube(f"side{sx}", (sx * W_ / 2, 0, H_ / 2), (.06, D_, H_), "tile", 0)
    cube("ceil", (0, 0, H_), (W_, D_, .06), "apron", 0)
    # окно выдачи на задней стене
    cube("win", (.55, 1.14, 1.55), (1.3, .02, .8), "glass", 0)
    cube("street", (.55, 1.5, 1.55), (2.4, .02, 1.6), "street", 0)
    for k in range(5):   # дома за окном
        cube(f"house{k}", (-.2 + k * .38, 1.45, 1.3 + (k % 3) * .12), (.3, .02, .6 + (k % 3) * .25), "dark", 0)
    cube("sill", (.55, 1.05, 1.13), (1.45, .2, .05), "wood", .01)
    # прилавок, плита, полка
    cube("counter", (.55, .85, .55), (1.5, .5, 1.1), "red", .03)
    cube("ctop", (.55, .85, 1.11), (1.56, .56, .05), "steel", .01)
    cube("stove", (-1.15, .85, .5), (.9, .55, 1.0), "steel", .02)
    for bx in (-1.38, -.92):
        bpy.ops.mesh.primitive_cylinder_add(radius=.14, depth=.03, location=(bx, .85, 1.02))
        bpy.context.object.data.materials.append(M["dark"])
    cube("shelf", (-1.0, 1.1, 1.85), (1.2, .2, .04), "wood", .01)
    for k, c in enumerate(("red", "glass", "apron", "hood")):
        cube(f"jar{k}", (-1.45 + k * .3, 1.1, 1.97), (.14, .14, .2), c, .03)
    # лампа
    cube("lampwire", (0, .2, 2.35), (.01, .01, .3), "dark", 0)
    sphere("bulb", (0, .2, 2.18), (.07, .07, .07), "bulb")


def light(kind, loc, energy, col, size=1.0, rot=(0, 0, 0)):
    bpy.ops.object.light_add(type=kind, location=loc, rotation=rot)
    o = bpy.context.object
    o.data.energy, o.data.color = energy, col
    if kind == "AREA":
        o.data.size = size
    return o


def setup_render(samples):
    r = S.render
    r.engine = "BLENDER_EEVEE"
    e = S.eevee
    e.taa_render_samples = samples
    e.use_gtao, e.gtao_distance = True, .6
    e.use_soft_shadows = True
    e.use_bloom, e.bloom_intensity = True, .03
    e.shadow_cube_size, e.shadow_cascade_size = "1024", "2048"
    r.resolution_x, r.resolution_y = 720, 1280
    r.resolution_percentage = 100
    S.view_settings.view_transform = "AgX"
    S.view_settings.look = "AgX - Medium High Contrast"
    S.world = bpy.data.worlds.new("w"); S.world.use_nodes = True
    S.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.25, .28, .34, 1)
    S.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .6


def build_street(X=30.0):
    """улица и фургон снаружи (отдельная площадка, x≈30)"""
    cube("asph", (X, 2, -.03), (30, 30, .06), "dark", 0)
    cube("walk", (X, -1.6, .03), (30, 2.2, .1), "grout", 0)
    rnd = random.Random(3)
    for k in range(9):   # дома
        hx, hh = X - 9 + k * 2.3, rnd.uniform(4, 8)
        cube(f"bld{k}", (hx, 7.5, hh / 2), (2.1, 2, hh), ("street", "tile", "apron")[k % 3], 0)
        for r in range(int(hh / 1.1)):
            for c in range(3):
                cube(f"w{k}_{r}_{c}", (hx - .6 + c * .6, 6.48, .9 + r * 1.1), (.34, .02, .5), "glass", 0)
    # фургон
    vx, vy = X + .6, 1.8
    cube("vbody", (vx, vy, 1.25), (3.0, 1.7, 2.0), "apron", .08)
    cube("vstripe", (vx + .4, vy - .86, .7), (3.8, .02, .16), "red", 0)
    cube("vcab", (vx + 1.95, vy, .95), (1.0, 1.65, 1.4), "apron", .1)
    cube("vwind", (vx + 2.42, vy, 1.25), (.04, 1.4, .55), "glass", 0)
    cube("vside", (vx + 1.95, vy - .83, 1.25), (.7, .02, .5), "glass", 0)
    cube("hatch", (vx - .2, vy - .86, 1.5), (1.6, .02, .7), "glass", 0)
    cube("awning", (vx - .2, vy - 1.1, 1.95), (1.8, .5, .06), "red", .02, rot=(math.radians(-15), 0, 0))
    cube("vcounter", (vx - .2, vy - .95, 1.13), (1.7, .22, .06), "steel", .01)
    sphere("lamp_ok", (vx + 2.46, vy - .55, .62), (.03, .13, .13), "bulb")
    sphere("lamp_none", (vx + 2.46, vy + .55, .62), (.03, .13, .13), "dark")   # фары нет
    for wx in (vx - .9, vx + 1.9):
        for wy in (vy - .86, vy + .86):
            bpy.ops.mesh.primitive_cylinder_add(radius=.36, depth=.26, location=(wx, wy, .36), rotation=(math.radians(90), 0, 0))
            bpy.context.object.data.materials.append(M["dark"])
            shade_smooth(bpy.context.object)
    for k in range(5):   # ржавчина
        sphere(f"rust{k}", (vx - 1.2 + k * .6, vy - .86, .4 + (k % 2) * .1), (.12, .01, .06), "wood")
    light("SUN", (X, -5, 10), 3.0, (1, .96, .9), rot=(math.radians(50), 0, math.radians(-30)))


def build_box():
    root = empty("box", (0, 0, 0))
    cube("box_b", (0, 0, .17), (.6, .4, .34), "steel", .03, root)
    cube("box_lid", (0, 0, .36), (.64, .44, .06), "dark", .02, root)
    cube("box_lock", (0, -.21, .24), (.1, .03, .12), "wood", .01, root)
    return root


build_truck()
build_street()
BOX = build_box()
BOX.location = (.55, .38, 0)
T = build_timur()
light("AREA", (0, -2.6, 2.4), 420, (1, .95, .88), 3.0, (math.radians(60), 0, 0))       # мягкий фронтальный
light("POINT", (0, .2, 2.1), 120, (1, .82, .55))                                        # лампа
light("AREA", (1.6, .4, 2.2), 160, (.75, .85, 1.0), 1.0, (math.radians(70), 0, math.radians(110)))   # контровой
bpy.ops.object.camera_add()
CAM = bpy.context.object
S.camera = CAM


def cam(loc, look_at, lens=35):
    CAM.location = loc
    CAM.rotation_euler = (Vector(look_at) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    CAM.data.lens = lens


def show(o, on):
    o.hide_render = not on
    for c in o.children_recursive:
        c.hide_render = not on


def talking(sc, t):
    return any(a <= t <= b for a, b in sc["talk"])


def sky(outdoor):
    bgn = S.world.node_tree.nodes["Background"]
    bgn.inputs["Color"].default_value = (.42, .62, .9, 1) if outdoor else (.25, .28, .34, 1)
    bgn.inputs["Strength"].default_value = 1.2 if outdoor else .6


def sc_s01(t, L, sc):   # улица: Тимур идёт к фургону
    sky(True)
    k = min(1, t / (L * .7))
    T["root"].location = (27.6 + 1.4 * k, -.9, 0)
    T["root"].rotation_euler = (0, 0, math.radians(30 if k < 1 else 0))
    pose(T, t, ("wave", "down") if k >= 1 else ("down", "down"), smile=k >= 1, talk=talking(sc, t))
    T["root"].location.z += .05 * abs(math.sin(t * 9)) if k < 1 else 0
    cam((29.3, -6.2, 1.9), (30.0, .6, 1.1), 30)


def sc_s02(t, L, sc):   # фургон крупнее, «вах»
    sky(True)
    p = t / L
    T["root"].location = (32.2, -.95, 0)
    T["root"].rotation_euler = (0, 0, math.radians(-25))
    pose(T, t, ("up", "up") if p > .72 else ("down", "hip"), smile=p > .72, talk=talking(sc, t))
    cam((34.6, -4.2, 1.6), (31.8, .9, 1.1), 30)


def sc_s03(t, L, sc):   # внутри: «решаете вы» — показывает на зрителя
    T["root"].location = (0, -.3, 0); T["root"].rotation_euler = (0, 0, 0)
    pose(T, t, ("down", "front"), smile=True, talk=talking(sc, t))
    cam((0, -2.3, 1.62), (0, .2, 1.5), 34)


def sc_s04(t, L, sc):   # «лайк = 10 ₽» — машет
    T["root"].location = (0, -.1, 0); T["root"].rotation_euler = (0, 0, 0)
    pose(T, t, ("wave", "up") if t > L * .5 else ("down", "wave"), smile=True, talk=talking(sc, t))
    cam((0, -3.0, 1.45), (0, .3, 1.3), 32)


def sc_s05(t, L, sc):   # лезет под прилавок, находит ящик
    p = t / L
    crouch = min(1, p / .3)
    T["root"].location = (-.2, .0, -.55 * crouch); T["root"].rotation_euler = (0, 0, math.radians(-20 * crouch))
    pose(T, t, ("front", "front") if p > .3 else ("down", "down"), smile=False, talk=talking(sc, t))
    show(BOX, p > .3)
    cam((-.9, -3.0, 1.15), (.15, .3, .7), 30)


def sc_s06(t, L, sc):   # крупно ящик
    show(BOX, True)
    T["root"].location = (-1.6, -.4, -3)   # героя убираем из кадра
    cam((.55, -.55, 1.15 - .1 * min(1, t / L)), (.55, .38, .25), 34)


def sc_s07(t, L, sc):
    show(BOX, True)
    T["root"].location = (0, -.1, 0); T["root"].rotation_euler = (0, 0, 0)
    pose(T, t, ("down", "hip"), smile=False, talk=talking(sc, t), look=10 * math.sin(t))
    cam((0, -3.3, 1.4), (0, .3, 1.25), 30)


def sc_s08(t, L, sc):
    show(BOX, True)
    T["root"].location = (0, -.1, 0); T["root"].rotation_euler = (0, 0, 0)
    pose(T, t, ("wave", "wave"), smile=True, talk=talking(sc, t))
    cam((0, -3.3, 1.4), (0, .3, 1.25), 30)


if MODE == "scenes":
    import json
    TL = json.load(open(argv[1]))
    outdir = argv[2]
    setup_render(int(argv[3]) if len(argv) > 3 else 24)
    S.render.resolution_percentage = int(float(argv[4]) * 100) if len(argv) > 4 else 75
    os.makedirs(outdir, exist_ok=True)
    only = set(argv[5].split(",")) if len(argv) > 5 else None
    for sc in TL["scenes"]:
        name, L = sc["name"], sc["length"]
        if only and name not in only:
            continue
        fn = globals()["sc_" + name]
        for f in range(int(math.ceil(L * FPS3D))):
            out = os.path.join(outdir, f"{name}_{f:04d}.png")
            if os.path.exists(out):
                continue
            show(BOX, False)
            sky(False)
            fn(f / FPS3D, L, sc)
            S.render.filepath = out
            bpy.ops.render.render(write_still=True)
        print("SCENE DONE", name)

if MODE == "test":
    out = argv[1]
    setup_render(int(argv[2]) if len(argv) > 2 else 24)
    T["root"].location = (-.1, .1, 0)
    pose(T, .3, ("down", "wave"), smile=True)
    cam((0, -3.4, 1.35), (0, .3, 1.2), 32)
    S.render.filepath = out
    bpy.ops.render.render(write_still=True)

if MODE == "peek":   # по одному кадру из каждой сцены (60% длины) — проверить ракурсы
    import json
    TL = json.load(open(argv[1]))
    outdir = argv[2]
    setup_render(16)
    S.render.resolution_percentage = 50
    os.makedirs(outdir, exist_ok=True)
    for sc in TL["scenes"]:
        show(BOX, False)
        sky(False)
        globals()["sc_" + sc["name"]](sc["length"] * .6, sc["length"], sc)
        S.render.filepath = os.path.join(outdir, sc["name"] + ".png")
        bpy.ops.render.render(write_still=True)
