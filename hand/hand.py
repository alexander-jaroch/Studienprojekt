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
c = 1/3 * (points['f1'] + points['f2'] + points['f3'])    
print("c =", c)

# Ebenenvektoren berechnen
#cf1 = points['f1'] - c
#cf2 = points['f2'] - c

# Normale berechenn
#n = Vector(cross(cf1, cf2))
#print("n =", n)
#print("|n| =", n.length)

# Projektion berechnen
#p = n.copy()
#p.z = 0
#print("p =", p)

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

# v2 is center
#def make_matrix(v1, v2, v3):
#    a = v1-v2
#    b = v3-v2

#    c = a.cross(b)
#    if c.magnitude > 0:
#        c.normalize()
#    else:
#        return None
#    print(c)

#    b2 = c.cross(a).normalized()
#    a2 = a.normalized()
#    m = Matrix([a2, b2, c]).transposed()
#    s = a.magnitude
#    m = Matrix.Translation(v2) * Matrix.Scale(s,4) * m.to_4x4()

#    return m

#m = make_matrix(points['f1'], points['f2'], points['f3'])
#print("M =", m)

f2_f1 = points['f1'] - points['f2']
f2_f3 = points['f3'] - points['f2']

pan = calc_angle(f2_f1, 'z')

f2_f1.rotate(Euler((0, 0, -pan)))
f2_f3.rotate(Euler((0, 0, -pan)))
tilt = calc_angle(f2_f1, 'y')

f2_f1.rotate(Euler((0, -tilt, -pan)))
f2_f3.rotate(Euler((0, -tilt, -pan)))
roll = calc_angle(f2_f3, 'x')

f2_f1.rotate(Euler((-roll, -tilt, -pan)))
f2_f3.rotate(Euler((-roll, -tilt, -pan)))
print("f2_f1 =", f2_f1)
print("f2_f3 =", f2_f3)

hand_vec = Vector((1, 0, 0))
euler = Euler((roll, tilt, pan))
print("euler =", euler)

hand_vec.rotate(euler)
print("hand_vec =", hand_vec)

print("pan =", degrees(pan)) 
print("tilt =", degrees(tilt))   
print("roll =", degrees(roll))

# Platzhalter für a1, b1, c1, d1, e1

# Daumen ausblenden (a1, a2, a3)

# Winkel der Knöchel (b2, b3, ... c2, c3, ...)
fingers = {'b': 4, 'c': 4, 'd': 4, 'e': 4}
angles = {}

for key in fingers:
    for i in range(1, fingers[key] - 1):
        angles[key + str(i + 1)] = (points[key + str(i + 1)] - points[key + str(i)])\
        .angle(points[key + str(i + 2)] - points[key + str(i + 1)])
    
for key in angles:
    print(key, degrees(angles[key]))
    
