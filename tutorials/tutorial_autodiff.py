import godot.core.tempo as tempo
import godot.core.autodif as ad
import numpy as np


# usare epoche extended con autodiff scalari
xepoch = tempo.XEpoch("2012-12-23T18:23:23.00 TDB")
delta = ad.Scalar(30.0,"a")
xepoch += delta
print(xepoch)

xepochTAI = tempo.convert(tempo.TimeScale.TAI,xepoch)
print(xepochTAI)

# calcolare il gradiente di una epoca extended, in pratica gradient estre solo i leaf della variabile autodiff
g = tempo.gradient(xepochTAI)
print(g)
print(g[delta.leaf()])


# esempio con vettori autodiff
y = ad.Vector( [ 1, 2, 3 ], "y" )
print( y.value() )
print( y )

x = ad.Vector( [ 4, 5, 6 ], "x" )
z = ad.cross( x, y ) + y /3
print(z)

# esempio con matrici autodiff
#It is possible to create matrix parameters, each element is then tracked separately as a separate parameter.

Z = ad.Matrix( [[ 1, 2, 3 ],[4,5,6],[7,8,9] ], "Z" )

print( Z*y )


#Suppose we have small rotations dx, dy and dzabout the x, y and z axes

dx = ad.Scalar(0.0,"dx")
dy = ad.Scalar(0.0,"dy")
dz = ad.Scalar(0.0,"dz")
#We define the rotation matrices assuming the small angle approximation

Rx = ad.Matrix(np.identity(3))
Rx[1,2] = -dx
Rx[2,1] = +dx

Ry = ad.Matrix(np.identity(3))
Ry[0,2] = +dy
Ry[2,0] = -dy

Rz = ad.Matrix(np.identity(3))
Rz[0,1] = +dz
Rz[1,0] = -dz

print('Rx', Rx)
print('Ry', Ry)
print('Rz', Rz)
  
#and we can combine them to get a rotation matrix, tracking partials with respect to the small rotation angles.

R = Rz * Ry * Rx
print('R', R)


# Esempio con funzioni matematiche di autodiff      
a = ad.Scalar(1.0, "a")
b = ad.Scalar(2.0, "b")
def g(x, y):
    return ad.sin(x) / (x + y)

c = g(a, b)

print(c)