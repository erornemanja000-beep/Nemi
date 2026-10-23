"""Zajedničke funkcije za Blender scene (pokreće se preko blender -b -P, vidi .claude/agents/blender-umetnik.md).

Iz skripte scene:
    import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    import common as C
"""
import math
import sys

import bpy
from mathutils import Vector


def args():
    """Argumenti posle `--` u komandnoj liniji Blendera, kao lista."""
    return sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def reset():
    """Prazna scena bez podrazumevane kocke, svetla i kamere."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def render_settings(scene, width=1600, height=1600, samples=64, transparent=True, fps=30):
    """Cycles na CPU-u sa OpenImageDenoise; PNG RGBA sa providnom pozadinom za web sekvence."""
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.max_bounces = 8
    scene.cycles.transparent_max_bounces = 16
    scene.cycles.transmission_bounces = 8
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.render.film_transparent = transparent
    # staklo propušta alfa kanal: kroz levak, bokal i V60 vidi se boja sajta, a ne crna
    scene.cycles.film_transparent_glass = transparent
    scene.cycles.film_transparent_roughness = 0.1
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA' if transparent else 'RGB'
    scene.render.image_settings.compression = 15
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'None'


def world(scene, color=(0.92, 0.89, 0.84), strength=0.6):
    """Mekana topla okolina (boja krem pozadine sajta), da odsjaji na inoxu i staklu ne budu crni."""
    w = bpy.data.worlds.new('World')
    scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (*color, 1)
    bg.inputs['Strength'].default_value = strength
    return w


def studio_lights(key=900, fill=250, rim=600):
    """Studijsko svetlo kao u referenci: veliki meki prozor levo gore, popuna desno, kontra iza."""
    def area(name, loc, rot, size, power, color=(1.0, 0.96, 0.9)):
        d = bpy.data.lights.new(name, 'AREA')
        d.energy, d.size, d.color = power, size, color
        o = bpy.data.objects.new(name, d)
        o.location, o.rotation_euler = loc, [math.radians(a) for a in rot]
        bpy.context.collection.objects.link(o)
        return o
    return [
        area('Key', (-2.2, -2.0, 2.6), (55, 0, -45), 2.5, key),
        area('Fill', (2.4, -1.6, 1.2), (70, 0, 55), 3.0, fill, (0.95, 0.97, 1.0)),
        area('Rim', (0.6, 2.4, 2.2), (-60, 0, 170), 1.5, rim),
    ]


def camera(loc, target, lens=85, name='Camera'):
    """Kamera sa dugim objektivom (malo izobličenje, kao product shot) okrenuta ka tački target."""
    d = bpy.data.cameras.new(name)
    d.lens = lens
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = o
    return o


def shadow_catcher(size=6, z=0.0):
    """Ravan koja hvata samo senku, da predmet „stoji" na pozadini sajta."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    p = bpy.context.active_object
    p.name = 'ShadowCatcher'
    p.is_shadow_catcher = True
    return p


def _principled(name, **inputs):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    for key, value in inputs.items():
        bsdf.inputs[key].default_value = value
    return m, bsdf


def mat_steel(name='Steel', roughness=0.22):
    """Brušeni inox (mlin, kuvalo)."""
    m, _ = _principled(name, **{'Base Color': (0.78, 0.77, 0.75, 1), 'Metallic': 1.0, 'Roughness': roughness,
                                'Anisotropic': 0.6})
    return m


def mat_glass(name='Glass', tint=(0.98, 0.98, 0.97), roughness=0.02):
    """Bistro staklo (levak mlina, bokal, V60)."""
    m, _ = _principled(name, **{'Base Color': (*tint, 1), 'Roughness': roughness, 'IOR': 1.47,
                                'Transmission Weight': 1.0})
    return m


def mat_plastic(name='Plastic', color=(0.03, 0.03, 0.03), roughness=0.35):
    m, _ = _principled(name, **{'Base Color': (*color, 1), 'Roughness': roughness})
    return m


def mat_paper(name='Paper', color=(0.93, 0.91, 0.86)):
    """Papirni filter: mat, malo propušta svetlo."""
    m, _ = _principled(name, **{'Base Color': (*color, 1), 'Roughness': 0.85,
                                'Subsurface Weight': 0.25, 'Subsurface Radius': (0.2, 0.2, 0.2)})
    return m


def mat_coffee_liquid(name='Coffee', color=(0.08, 0.035, 0.015)):
    """Tečna kafa: tamna, providna na ivicama, sjajna površina."""
    m, _ = _principled(name, **{'Base Color': (*color, 1), 'Roughness': 0.05, 'IOR': 1.34,
                                'Transmission Weight': 0.85})
    return m


def mat_water(name='Water'):
    m, _ = _principled(name, **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.0, 'IOR': 1.333,
                                'Transmission Weight': 1.0})
    return m


def mat_bean(name='Bean', color=(0.13, 0.065, 0.03)):
    """Prženo zrno: tamnobraon, blag sjaj od ulja, sitna neravnina."""
    m, bsdf = _principled(name, **{'Base Color': (*color, 1), 'Roughness': 0.38,
                                   'Coat Weight': 0.25, 'Coat Roughness': 0.3})
    nt = m.node_tree
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 60
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def mat_ceramic(name='Ceramic', color=(0.32, 0.22, 0.16), roughness=0.45):
    m, _ = _principled(name, **{'Base Color': (*color, 1), 'Roughness': roughness, 'Coat Weight': 0.5,
                                'Coat Roughness': 0.15})
    return m


def assign(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    return obj


def smooth(obj, subdiv=0):
    """Glatko senčenje i po želji subdivision modifier."""
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if subdiv:
        mod = obj.modifiers.new('Subsurf', 'SUBSURF')
        mod.levels = mod.render_levels = subdiv
    return obj


def lathe(name, profile, segments=96):
    """Telo okretanja: profile je lista (r, z) tačaka od dna nagore; vraća mesh objekat oko Z ose."""
    import bmesh
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
    for i in range(segments):
        a, b = rings[i], rings[(i + 1) % segments]
        for j in range(len(profile) - 1):
            bm.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return smooth(obj)


def render_frames(scene, out_dir, frames):
    """Renderuje samo zadate kadrove (npr. [1, 45, 90] za probu) u out_dir/kadar_0001.png."""
    for f in frames:
        scene.frame_set(f)
        scene.render.filepath = f'{out_dir}/kadar_{f:04d}.png'
        bpy.ops.render.render(write_still=True)
