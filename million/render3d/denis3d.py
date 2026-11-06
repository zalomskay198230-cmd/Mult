"""3D-Денис в Blender (стилизованный «мультяшный 3D», как в анимационных фильмах).
Запуск: blender -b -P denis3d.py -- <out.png> [samples]
Строит персонажа из примитивов со сглаживанием, комнату ночью и рендерит Cycles на CPU."""
import bpy, sys, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "/tmp/denis3d.png"
SAMPLES = int(argv[1]) if len(argv) > 1 else 48

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ---------- материалы ----------
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


def srgb(r, g, b):
    f = lambda c: (c / 255) ** 2.2
    return (f(r), f(g), f(b))


SKIN = mat("skin", srgb(214, 170, 140), .45, sss=.25)
HAIR = mat("hair", srgb(52, 40, 34), .55)
HOOD = mat("hoodie", srgb(84, 88, 96), .85)
HOOD_D = mat("hoodie_d", srgb(62, 66, 72), .85)
JEANS = mat("jeans", srgb(62, 86, 120), .8)
SHOE = mat("shoe", srgb(236, 236, 232), .5)
SOLE = mat("sole", srgb(180, 180, 176), .6)
EYE_W = mat("eye_w", srgb(240, 236, 230), .2)
IRIS = mat("iris", srgb(96, 84, 64), .3)
PUPIL = mat("pupil", (0.005, 0.005, 0.005), .1)
LACE = mat("lace", srgb(230, 230, 226), .6)
PHONE = mat("phone", (0.01, 0.01, 0.012), .25, metal=.4)
SCREEN = mat("screen", (0, 0, 0), .2, emit=srgb(120, 170, 230), strength=6)
WALL = mat("wall", srgb(70, 74, 92), .9)
FLOOR = mat("floor", srgb(70, 56, 48), .5)
SOFA = mat("sofa", srgb(80, 66, 96), .9)
WINDOW = mat("window", (0, 0, 0), .2, emit=srgb(40, 60, 110), strength=1.5)


def smooth(obj, levels=2):
    for p in obj.data.polygons:
        p.use_smooth = True
    m = obj.modifiers.new("sub", "SUBSURF")
    m.levels = m.render_levels = levels
    return obj


def sphere(name, loc, scale, material, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.materials.append(material)
    return o


def capsule(name, a, b, r, material, r2=None):
    """цилиндр со скруглёнными концами между точками a и b"""
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=r, depth=d.length, location=(a + b) / 2)
    o = bpy.context.object
    o.name = name
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    if r2:   # сужение к концу
        for v in o.data.vertices:
            if v.co.z > 0:
                v.co.x *= r2 / r
                v.co.y *= r2 / r
    smooth(o, 2)
    o.data.materials.append(material)
    for end, rr in ((a, r), (b, r2 or r)):
        sphere(name + "_j", end, (rr, rr, rr), material, 24)
    return o


def box(name, loc, size, material, bevel=.3, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    bv = o.modifiers.new("bevel", "BEVEL")
    bv.width = min(size) * bevel
    bv.segments = 4
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.materials.append(material)
    return o


# ---------- Денис (рост ~1.8, лицом к -Y) ----------
def meta(name, material, resolution=.012):
    mb = bpy.data.metaballs.new(name)
    mb.render_resolution = resolution
    mb.resolution = .03
    mb.threshold = .22
    o = bpy.data.objects.new(name, mb)
    scene.collection.objects.link(o)
    o.data.materials.append(material)
    return mb


def m_caps(mb, a, b, r, stiff=2.0):
    a, b = Vector(a), Vector(b)
    d = b - a
    e = mb.elements.new(type="CAPSULE")
    e.co = (a + b) / 2
    e.radius = r
    e.size_x = d.length / 2
    e.rotation = Vector((1, 0, 0)).rotation_difference(d.normalized())
    e.stiffness = stiff
    return e


def m_ell(mb, c, size, r=.1, stiff=2.0):
    e = mb.elements.new(type="ELLIPSOID")
    e.co = c
    e.radius = r
    e.size_x, e.size_y, e.size_z = size
    e.stiffness = stiff
    return e


def denis():
    HZ = 1.64   # центр головы
    # кожа: голова, шея, кисти — одно мягкое тело
    skin = meta("skin_mb", SKIN)
    m_ell(skin, (0, 0, HZ), (1.18, 1.1, 1.22), .15)
    m_ell(skin, (0, -.02, HZ - .09), (.85, .8, .6), .1, 1.5)     # щёки/подбородок
    m_caps(skin, (0, 0, 1.43), (0, 0, 1.52), .05)
    for sx in (-1, 1):
        m_ell(skin, (sx * .118, .01, HZ - .01), (.5, .7, .9), .055)         # уши
    m_ell(skin, (0, -.135, HZ - .02), (.6, .9, 1.0), .032, 3)       # нос
    m_ell(skin, (-.28, -.03, .8), (.8, .7, 1.1), .07)               # левая кисть
    m_ell(skin, (.13, -.22, 1.2), (.9, .8, 1.0), .07)               # правая кисть с телефоном
    # толстовка: торс, капюшон, руки
    hood = meta("hoodie_mb", HOOD)
    m_ell(hood, (0, 0, 1.2), (1.0, .62, 1.15), .24)
    m_ell(hood, (0, .03, 1.4), (1.25, .7, .45), .2, 1.6)            # плечи
    m_ell(hood, (0, .1, 1.47), (1.0, .5, .4), .11)                  # капюшон на спине
    m_caps(hood, (-.24, 0, 1.38), (-.29, .01, 1.12), .065)
    m_caps(hood, (-.29, .01, 1.12), (-.28, -.02, .86), .056)
    m_caps(hood, (.24, 0, 1.38), (.29, .02, 1.12), .065)
    m_caps(hood, (.29, .02, 1.12), (.15, -.2, 1.19), .056)
    # джинсы
    jeans = meta("jeans_mb", JEANS)
    m_ell(jeans, (0, 0, .96), (1.0, .6, .5), .2, 1.5)
    for sx in (-1, 1):
        m_caps(jeans, (sx * .1, 0, .94), (sx * .1, -.01, .52), .085)
        m_caps(jeans, (sx * .1, -.01, .52), (sx * .1, 0, .12), .07)
        box("shoe", (sx * .1, -.05, .06), (.13, .29, .11), SHOE, .4)
        box("sole", (sx * .1, -.05, .014), (.135, .3, .028), SOLE, .3)
    # лицо: крупные глаза, брови, рот
    for sx in (-1, 1):
        sphere("eye", (sx * .05, -.118, HZ + .02), (.03, .014, .026), EYE_W)
        sphere("iris", (sx * .05, -.13, HZ + .02), (.016, .006, .016), IRIS)
        sphere("pupil", (sx * .05, -.135, HZ + .02), (.007, .003, .007), PUPIL)
        sphere("glint", (sx * .05 + .006, -.138, HZ + .028), (.003, .002, .003), mat("glint", (1, 1, 1), .1, emit=(1, 1, 1), strength=2))
        capsule("brow", (sx * .022, -.13, HZ + .068), (sx * .082, -.118, HZ + .062), .008, HAIR)
    capsule("mouth", (-.03, -.122, HZ - .1), (.03, -.122, HZ - .098), .005, mat("lip", srgb(150, 90, 80), .5))
    # волосы
    import random
    rnd = random.Random(3)
    hair = meta("hair_mb", HAIR, .01)
    m_ell(hair, (0, .025, HZ + .075), (1.2, 1.15, .78), .16)
    for k in range(16):
        a = -1.3 + k * .17
        x, y = math.sin(a) * .13, -math.cos(a) * .13
        m_ell(hair, (x * 1.1, y + .02, HZ + .12 + rnd.uniform(-.01, .015)), (.7, .7, .7), .05, 2)
    for k in range(6):   # чёлка
        x = -.075 + k * .03
        m_ell(hair, (x, -.13, HZ + .09 - abs(x) * .25), (.5, .4, .9), .03, 3)
    # шнурки, карман, телефон
    for sx in (-1, 1):
        capsule("lace", (sx * .05, -.152, 1.38), (sx * .056, -.158, 1.27), .006, LACE)
    box("phone", (.11, -.26, 1.25), (.075, .012, .15), PHONE, .2, rot=(math.radians(-25), 0, math.radians(15)))
    box("screen", (.11, -.267, 1.253), (.066, .004, .136), SCREEN, .1, rot=(math.radians(-25), 0, math.radians(15)))


denis()

# ---------- комната ----------
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
bpy.context.object.data.materials.append(FLOOR)
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 1.2, 3), rotation=(math.radians(90), 0, 0))
bpy.context.object.data.materials.append(WALL)
box("window", (-.9, 1.18, 1.7), (.8, .02, 1.0), WINDOW, .02)
box("sofa", (.95, .75, .25), (1.2, .5, .5), SOFA, .25)
box("sofa_back", (.95, 1.0, .55), (1.2, .15, .6), SOFA, .3)

# ---------- свет ----------
def light(kind, loc, energy, col, size=1.0, rot=(0, 0, 0)):
    bpy.ops.object.light_add(type=kind, location=loc, rotation=rot)
    l = bpy.context.object.data
    l.energy = energy
    l.color = col
    if kind == "AREA":
        l.size = size
    return l


light("AREA", (-1.2, -1.6, 2.6), 160, (.55, .65, 1.0), 2.0, (math.radians(50), 0, math.radians(-35)))   # холодный заполняющий
light("AREA", (1.4, .6, 2.0), 260, (1.0, .62, .32), .8, (math.radians(70), 0, math.radians(120)))        # тёплый контровой
light("POINT", (.05, -.36, 1.34), 12, (.55, .72, 1.0))                                                   # свет телефона на лицо
scene.world = bpy.data.worlds.new("w")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.01, .012, .02, 1)

# ---------- камера ----------
bpy.ops.object.camera_add(location=(.2, -2.7, 1.2), rotation=(math.radians(88), 0, math.radians(4)))
cam = bpy.context.object
cam.data.lens = 40
scene.camera = cam

r = scene.render
r.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = False   # в сборке из apt нет OpenImageDenoise
scene.cycles.sample_clamp_indirect = 3
r.resolution_x, r.resolution_y = 720, 1280
r.filepath = OUT
scene.view_settings.view_transform = "AgX" if "AgX" in [v.identifier for v in scene.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
bpy.ops.render.render(write_still=True)
print("RENDERED", OUT)
