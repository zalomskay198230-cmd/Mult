"""Blender: Владивосток для гибридного стиля «Глубины» — Золотой мост, бухта, сопки с домами, вечер.
blender -b -P vl3d.py -- <out.png> [samples]"""
import bpy, sys, math, random
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
SAMPLES = int(argv[1]) if len(argv) > 1 else 32
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene


def srgb(r, g, b):
    f = lambda c: (c / 255) ** 2.2
    return (f(r), f(g), f(b))


def mat(name, col, rough=.6, emit=None, strength=1.0, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


M = dict(
    water=mat("water", srgb(20, 40, 70), .08, metal=.2),
    hill=mat("hill", srgb(70, 80, 96), .9),
    hill2=mat("hill2", srgb(56, 60, 84), .9),
    bld=mat("bld", srgb(150, 150, 160), .7),
    bld2=mat("bld2", srgb(110, 112, 124), .7),
    win=mat("win", srgb(255, 200, 120), .4, emit=srgb(255, 190, 110), strength=8),
    bridge=mat("bridge", srgb(236, 232, 224), .35),
    lamp=mat("lamp", srgb(255, 220, 160), .3, emit=srgb(255, 210, 140), strength=30),
    walk=mat("walk", srgb(70, 68, 74), .8),
    rail=mat("rail", srgb(30, 30, 34), .5, metal=.6),
)


def box(loc, size, m, rot=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=(0, 0, rot))
    o = bpy.context.object
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(M[m])
    return o


def cyl(a, b, r, m):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=r, depth=d.length, location=(a + b) / 2)
    o = bpy.context.object
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    o.data.materials.append(M[m])
    return o


# вода
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0))
bpy.context.object.data.materials.append(M["water"])
# набережная (передний план)
box((0, -32, .6), (80, 8, 1.2), "walk")
for x in range(-40, 41, 2):
    box((x, -28.2, 1.7), (.08, .08, 1.0), "rail")
box((0, -28.2, 2.2), (60, .08, .08), "rail")

# сопки с домами
rnd = random.Random(4)
for row, (y, hmax, m) in enumerate(((140, 55, "hill2"), (95, 38, "hill"))):
    for i in range(18):
        x = -170 + i * 20 + rnd.uniform(-6, 6)
        h = rnd.uniform(.5, 1) * hmax
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, y, 0))
        o = bpy.context.object
        o.scale = (rnd.uniform(22, 34), 26, h)
        o.data.materials.append(M[m])
        for _ in range(9):   # дома на склоне
            bx = x + rnd.uniform(-16, 16)
            bz_top = h * math.sqrt(max(0, 1 - ((bx - x) / 26) ** 2))
            bh = rnd.uniform(5, 14)
            by = y - 20 - row * 2 + rnd.uniform(-3, 3)
            box((bx, by, bz_top * .55 + bh / 2), (rnd.uniform(3, 6), 3, bh), "bld" if rnd.random() < .5 else "bld2", rnd.uniform(-.2, .2))
            for wz in range(int(bh // 2.2)):
                if rnd.random() < .6:
                    box((bx + rnd.uniform(-1.2, 1.2), by - 1.55, bz_top * .55 + 1.2 + wz * 2.2), (.7, .05, .8), "win")

# прибрежные дома у воды (нижняя часть сопок)
for i in range(46):
    bx = -120 + i * 5.3 + rnd.uniform(-1, 1)
    bh = rnd.uniform(6, 20)
    by = 68 + rnd.uniform(-2, 2)
    box((bx, by, bh / 2), (rnd.uniform(3.5, 5), 3, bh), "bld" if i % 2 else "bld2", rnd.uniform(-.1, .1))
    for wz in range(int(bh // 2.2)):
        for wx in (-1.1, 0, 1.1):
            if rnd.random() < .45:
                box((bx + wx, by - 1.55, 1.2 + wz * 2.2), (.6, .05, .8), "win")

# Золотой мост: пролёт, V-пилоны, ванты, фонари
Y, DZ = 45, 16
box((0, Y, DZ), (240, 4, 1.2), "bridge")
for px in (-30, 30):
    for sg in (-1, 1):
        cyl((px + sg * 1.5, Y, 0), (px + sg * 9, Y, 62), 1.1, "bridge")
    box((px, Y, 58), (20, 2, 1.4), "bridge")
    box((px, Y, DZ / 2), (5, 5, DZ), "bridge")
    for k in range(12):
        z = 56 - k * 3.4
        for sg in (-1, 1):
            cyl((px, Y, z), (px + sg * (8 + k * 6.5), Y - 1.5, DZ + .6), .09, "bridge")
            cyl((px, Y, z), (px + sg * (8 + k * 6.5), Y + 1.5, DZ + .6), .09, "bridge")
for x in range(-118, 119, 8):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.35, location=(x, Y - 2.2, DZ + 1.2))
    bpy.context.object.data.materials.append(M["lamp"])
    bpy.ops.object.light_add(type="POINT", location=(x, Y - 3, DZ + 1.4))
    bpy.context.object.data.energy, bpy.context.object.data.color = 600, (1, .78, .5)

# небо: закатный градиент
S.world = bpy.data.worlds.new("w"); S.world.use_nodes = True
nt = S.world.node_tree
bg = nt.nodes["Background"]
tex = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
ramp = nt.nodes.new("ShaderNodeValToRGB")
nt.links.new(tex.outputs["Generated"], sep.inputs[0])
nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = .5, (*srgb(250, 140, 90), 1)
ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = .78, (*srgb(26, 28, 66), 1)
e = ramp.color_ramp.elements.new(.58); e.color = (*srgb(190, 90, 110), 1)
nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = .8

bpy.ops.object.light_add(type="SUN", location=(0, 200, 30), rotation=(math.radians(80), 0, math.radians(180)))
sun = bpy.context.object
sun.data.energy, sun.data.color, sun.data.angle = 1.2, (1, .55, .35), math.radians(5)
bpy.ops.object.light_add(type="AREA", location=(0, -20, 10), rotation=(math.radians(70), 0, 0))
fill = bpy.context.object
fill.data.energy, fill.data.size, fill.data.color = 3000, 30, (.5, .6, 1)

bpy.ops.object.camera_add(location=(6, -40, 6))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, Y, 30)) - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 22
S.camera = cam

r = S.render
r.engine = "BLENDER_EEVEE"
S.eevee.taa_render_samples = SAMPLES
S.eevee.use_bloom, S.eevee.bloom_intensity = True, .025
S.eevee.use_gtao = True
S.eevee.use_ssr = True
S.view_settings.view_transform = "AgX"
r.resolution_x, r.resolution_y, r.resolution_percentage = 720, 1280, 100
r.filepath = OUT
bpy.ops.render.render(write_still=True)
