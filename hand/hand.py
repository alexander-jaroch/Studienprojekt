import bpy
import numpy as np
import mathutils as mu
import math

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
cf1 = points['f1'] - c
cf2 = points['f2'] - c

# Normale berechenn
n = mu.Vector(np.cross(cf1, cf2))
print("n =", n)
print("|n| =", n.length)

# Projektion berechnen
p = n.copy()
p.z = 0
print("p =", p)

# Winkel der Grundfläche (f1, f2, f3) berechnen
def calc_angle(vector, view):
    angle = 0
    match view:
        case 'x': 
            projection = mu.Vector((vector.y, vector.z))
            angle = projection.angle_signed((1, 0))
        case 'y': 
            projection = mu.Vector((vector.x, vector.z))
            angle = projection.angle_signed((1, 0))
        case 'z': 
            projection = mu.Vector((vector.x, vector.y))
            angle = projection.angle_signed((0, 1))
    return angle

pan = calc_angle(points['f1'] - points['f2'], 'z')
tilt = calc_angle(points['f1'] - points['f2'], 'x')
roll = calc_angle(points['f3'] - points['f2'], 'y')

print("pan =", math.degrees(pan)) 
print("tilt =", math.degrees(tilt))   
print("roll =", math.degrees(roll))

# Platzhalter für a1, b1, c1, d1, e1

# Daumen ausblenden (a1, a2, a3)

# Winkel der Knöchel (b2, b3, ...)
fingers = {'b': 4, 'c': 4, 'd': 4, 'e': 4}
angles = {}


for key in fingers:
    for i in range(1, fingers[key] - 1):
        angles[key + str(i + 1)] = (points[key + str(i + 1)] - points[key + str(i)])\
        .angle(points[key + str(i + 2)] - points[key + str(i + 1)])
    
for key in angles:
    print(key, math.degrees(angles[key]))