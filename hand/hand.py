import bpy
from mathutils import Euler, Matrix, Vector
from math import degrees
import bmesh

col_seg = bpy.data.collections['Segments']

# representing hand and calculates its parameters
class Hand:
    prefix = 'Hand_'
    points = {}
    
    def __init__(self, objects):        
        for obj in objects:
            if obj.name.startswith(self.prefix):
                key = obj.name.replace(self.prefix, '')
                self.points[key] = obj.location
                
hand = Hand(bpy.data.objects)
#print(hand.points)

        

# draw a line between two vectors
def draw_segment(name, v, w):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(mesh.name, mesh)
    b = bmesh.new()
    
    col_seg.objects.link(obj)
    
    edge = []
    edge.append(b.verts.new(v))
    edge.append(b.verts.new(w))
    b.edges.new(edge)
    
    b.to_mesh(mesh)
    
# clear segment collection
def clear_segments():
    for obj in col_seg.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    print('Segments cleared.')

# hand calculations
prefix = 'Hand_'
points = {}

def calculate_parameters(draw=False):
    print(draw)
    if draw: 
        clear_segments()
    
    for obj in bpy.data.objects:
        if obj.name.startswith(prefix):
            points[obj.name.replace(prefix, '')] = obj.location
            
    # Ausgabe Vektoren
    #for key in points:
    #    print(key, points[key])
        
    # Mittelpunkt berechnen        
    c = (1/3) * (points['f1'] + points['f2'] + points['f3'])
    print("c =", c)

    # Matrix für Koordinatentransformation bestimmen
    def make_matrix(v1, v2, v3):
        a = v2 - v1
        b = v3 - v1

        c = a.cross(b)
        if c.magnitude > 0:
            c.normalize()
        else:
            return None

        # Orthogonalisieren
        b = c.cross(a).normalized()

        a.normalize()

        m = Matrix([a, b, c])
        m.transpose()
            
        m = Matrix.Translation(v1) @ m.to_4x4()
        return m

    # Matrix für "Handflächen"-Transformation bestimmen
    m = make_matrix(points['f2'], points['f1'], points['f3'])
    print("M =", m)

    euler = m.to_euler()
    print("E =", euler)

    # Überprüfung, ob Euler-Winkel passen
    hand_vec_1 = Vector(points['f1'] - points['f2'])
    hand_vec_2 = Vector(points['f3'] - points['f2'])

    reuler = euler.copy()
    reuler.x = -1 * reuler.x
    reuler.y = -1 * reuler.y
    reuler.z = -1 * reuler.z
    reuler.order = "ZYX"

    hand_vec_1.rotate(reuler)
    hand_vec_2.rotate(reuler)

    print("hand_vec_1 =", hand_vec_1)
    print("hand_vec_2 =", hand_vec_2)

    # Winkel der Knöchel (b2, b3, ... c2, c3, ...)
    fingers = {'b': 4, 'c': 4, 'd': 4, 'e': 4}
    angles = {}

    for key in fingers:
        for i in range(1, fingers[key] - 1):
            p = points[key + str(i + 1)]
            q = points[key + str(i)]
            r = points[key + str(i + 2)]
            s = points[key + str(i + 1)]
            if draw: 
                draw_segment(key, p, q)
            if draw: 
                draw_segment(key, r, s)
            angles[key + str(i + 1)] = (p - q).angle(r - s)
        
    # Winkel der Knöchel (b1, c1, ...)
    # Spreizwinkel # Check!!! 
    for key in fingers:
        v = points[key + "1"]
        w = points[key + "2"]      
        p = (w - v)
        q = p.copy()               
        p.rotate(reuler)
        q.rotate(reuler)
        #if draw:
        #    draw_segment('z__' + key, (0,0,0), (p.x, p.y, p.z))
        p = Vector((p.x, p.y))
        q = Vector((q.x, q.z))
        #if draw:
        #    draw_segment('z_' + key + 'XY', (0,0,0), (p.x, p.y, 0))
        #    draw_segment('z_' + key + 'XZ', (0,0,0), (q.x, 0, q.y))
        hvp = Vector((hand_vec_1.x, hand_vec_1.y))
        hvq = Vector((hand_vec_1.x, hand_vec_1.z))
        #if draw:
        #    draw_segment('z_' + key + 'XY_hvp', (0,0,0), (hvp.x, hvp.y, 0))
        #    draw_segment('z_' + key + 'XZ_hvq', (0,0,0), (hvq.x, 0, hvq.y))
        angles[key + "1z"] = p.angle_signed(hvp)
        angles[key + "1x"] = q.angle_signed(hvq)
        
    # Thumb!!!
    
    # Validate -> Reconstruct?
        
    # Ausgabe Winkel
    for key in angles:
        print(key, degrees(angles[key]))    
    
# handler for frame_change_post event
def handle_frame_change_post(scene):
    calculate_parameters(False)    

# clear and set event handlers
bpy.app.handlers.frame_change_post.clear()
bpy.app.handlers.frame_change_post.append(handle_frame_change_post)

# calculate parameters
calculate_parameters(True)
