import bpy
from numpy import cross
from mathutils import Euler, Matrix, Vector
from math import degrees

prefix = 'Hand_'
points = {}

def calculate_parameters(scene):
    for obj in bpy.data.objects:
        if obj.name.startswith(prefix):
            points[obj.name.replace(prefix, '')] = obj.location
            
    # Ausgabe Vektoren
    for key in points:
        print(key, points[key])
        
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
            angles[key + str(i + 1)] = (points[key + str(i + 1)] - points[key + str(i)])\
            .angle(points[key + str(i + 2)] - points[key + str(i + 1)])
        
    # Winkel der Knöchel (b1, c1, ...)
    # Spreizwinkel # Check!!! 
    for key in fingers:
        v = points[key + "1"]
        w = points[key + "2"]
        p = (w - v).normalized()
        q = p.copy()
        p.rotate(reuler)
        q.rotate(reuler)
        p = Vector((p.x, p.y))
        q = Vector((q.y, q.z))
        hvp = Vector((hand_vec_1.x, hand_vec_1.y))
        hvq = Vector((hand_vec_1.y, hand_vec_1.z))
        angles[key + "1z"] = hvp.angle_signed(p)
        angles[key + "1x"] = hvq.angle_signed(q)
        
    # Thumb!!!
    
    # Validate -> Reconstruct?
        
    # Ausgabe Winkel
    #for key in angles:
    #    print(key, degrees(angles[key]))    

bpy.app.handlers.frame_change_post.append(calculate_parameters)
