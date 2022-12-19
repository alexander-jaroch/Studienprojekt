import bpy
from mathutils import Euler, Matrix, Vector
from math import degrees
import bmesh

col_seg = bpy.data.collections['Segments']

# representing hand and calculates its parameters
class Hand:
    # customizable properties
    prefix = 'Hand_' 
    fingers = { 'a': 3, 'b': 4, 'c': 4, 'd': 4, 'e': 4}
    
    # calculated transformaton matrices
    transform = Matrix()
    reverse_transform = Matrix()
    
    # calculated points, rotations and translations
    points = {}
    rotations = {}
    translations = {}
    
    # get a point
    def point(self, key, i, value = None):
        if value is not None:
            self.points[key + str(i)] = value
        else:
            value = self.points[key + str(i)]
        return value
    
    # get a rotation
    def rotation(self, key, i, value = None):
        if value is not None:
            self.rotations[key + str(i)] = value
        else:
            value = self.rotations[key + str(i)]
        return value
    
    # constructor
    def __init__(self, objects):   
        # get points     
        for obj in objects:
            if obj.name.startswith(self.prefix):
                key = obj.name.replace(self.prefix, '')
                self.points[key] = obj.location
                print (obj.location.copy())
            
        # calculate transformation matrices
        self.calc_transform(self.points['f2'], self.points['f1'], self.points['f3'])
        
        # iterate finger segments 
        for key in self.fingers:
            for i in range(1, self.fingers[key] - 1):
                p = self.point(key, i + 1)
                q = self.point(key, i)
                r = self.point(key, i + 2)
                s = self.point(key, i + 1)
    
                self.rotation(key, i + 1, (p - q).angle(r - s)) 
    
    # calculate o vector and axes x, y, z
    def calc_axes(self, o, x, y):
        x = x - o
        y = y - o
        z = x.cross(y)
        y = z.cross(x)
        return o, x.normalized(), y.normalized(), z.normalized()
            
    # calculate transformation matrix for hand (f1, f2, f3)  
    def calc_transform(self, o, x, y):
        o, x, y, z = self.calc_axes(o, x, y) 
        
        rotate = Matrix([x, y, z]).transposed()
        translate = Matrix.Translation(o)
        
        self.transform = translate @ rotate.to_4x4()
        self.reverse_transform = self.transform.inverted()

        # !!! IMPORTANT !!! transform @ v
        
    # dict to string
    def dict_str(self, name, dict, ident, hide, map = lambda x: x):
        r = ident + name + ': {'
        if hide:
            r += ' <' + str(len(dict)) + ' hidden> '
        else:
            r += '\n'
            for key in dict:
                r += ident + '  ' + key + ': ' + str(map(dict[key])) + '\n'
            r += ident
        return r + '}\n'
        
    # object to string
    def __str__(self):
        r = 'hand: {\n'
        r += '  transform:\n' + str(self.transform) + '\n'
        r += self.dict_str('points', self.points, '  ', True)
        r += self.dict_str('rotations', self.rotations, '  ', False, lambda x: degrees(x))
        r += self.dict_str('translations', self.translations, '  ', False)
        return '\n' + r + '}'
    
    # copy points for testing
    def copy_points(self): 
        copy = {}
        for key in self.points:
            copy[key] = self.points[key].copy()
        return copy
                
hand = Hand(bpy.data.objects)
print(hand)

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
    #c = (1/3) * (points['f1'] + points['f2'] + points['f3'])
    #print("c =", c)

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

# create hand from parameters
def create_hand(parameters):
    return

hand2points = hand.copy_points()
hand2points['f2'] = Vector((100, 200, 300))

# validate quality of parameters
def validate_quality(a, b, verbose = False):
    sum = 0
    len = 0
    for key in a:
        distance = (b[key] - a[key]).magnitude 
        if verbose:
            print(key, distance)
        sum += distance
        len += 1
    return sum / len

print(validate_quality(hand.points, hand2points, True))