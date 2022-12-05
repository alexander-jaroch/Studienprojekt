import bpy
from numpy import cross
from mathutils import Euler, Matrix, Vector
from math import degrees

prefix = 'Hand_'
points = {}

for obj in bpy.data.objects:
    if obj.name.startswith(prefix):
        points[obj.name.replace(prefix, '')] = obj.location
        
# Ausgabe Vektoren
for key in points:
    print(key, points[key])
    
# Mittelpunkt berechnen        
c = (1/3) * (points['f1'] + points['f2'] + points['f3'])
print("c =", c)

# Winkel der Grundfläche (f1, f2, f3) berechnen
def calc_angle(vector, view):
    angle = 0
    match view:
        case 'x': 
            projection = Vector((vector.y, vector.z))
            angle = projection.angle_signed((1, 0))
        case 'y': 
            projection = Vector((vector.x, vector.z))
            angle = projection.angle_signed((1, 0))
        case 'z': 
            projection = Vector((vector.x, vector.y))
            angle = projection.angle_signed((1, 0))
    return angle

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
    
    # Skalierungsfaktor
    s = a.magnitude
    a.normalize()

    m = Matrix([a, b, c])
    m.transpose()
        
    m = Matrix.Translation(v1) @ Matrix.Scale(s, 4) @ m.to_4x4()
    return m

# Matrix für "Handflächen"-Transformation bestimmen
m = make_matrix(points['f2'], points['f1'], points['f3'])
print("M =", m)

euler = m.to_euler()
print("E =", euler)

# Überprüfung, ob Pan, Tilt, Roll passen
hand_vec_1 = Vector(points['f1'] - points['f2'])
hand_vec_2 = Vector(points['f3'] - points['f2'])

reuler = euler.copy()
reuler.x = -1 * reuler.x
reuler.y = -1 * reuler.y
reuler.z = -1 * reuler.z
reuler.order = "ZYX"

# Check durch inverse Rotation
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
    
for key in angles:
    print(key, degrees(angles[key]))
    
