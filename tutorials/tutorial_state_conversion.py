import numpy as np
import godot.core.astro as astro    
import godot.core.autodif as ad 

# Definizione parametri orbitali classici
d2r = np.pi/180
a = 6371.0 + 425.0  # km
e = 0.01
I = 32*d2r
RAAN = 10*d2r
argP = 170*d2r
ta = 23*d2r
coe = np.array([a, e, I, RAAN, argP, ta])
print(coe)

# Conversione in stato cartesiano
GM = 398600.4418
xyz = astro.cartFromKep(coe, GM)
print('xyz: ', xyz)

# Conversione in stato cartesiano usando astro.convert
From = 'Kep'
To = 'Cart'
gm = astro.StateConversionProperty(GM)
xyz_new = astro.convert(From, To, coe, gm)

# Verifica che le due conversioni diano lo stesso risultato
print('xyz: ', xyz_new)
print('error check: ', xyz_new - xyz)

# Conversione inversa in elementi orbitali equinoctial 
equi = astro.equiFromCart(xyz, GM)
print('equi: ', equi)

# Conversione inversa in parametri orbitali classici (per verifica  )
coe_check = astro.kepFromEqui(equi, GM)
print('coe_check: ', coe_check)

err = coe - coe_check
print('Norm of absolute error: ', np.linalg.norm(err))

# One advantage available in godot is that seemingly straightforward
# conversions can be implemented also when calculating partial derivatives. For instance:
coe_x = ad.Vector(coe, 'coe') # defining the classical orbital elements as autodiff parameters
GM_x = ad.Scalar(GM, 'GM')
xyz_x = astro.cartFromKep(coe_x, GM_x)
print(xyz_x)