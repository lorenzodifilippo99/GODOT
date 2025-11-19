import godot.core.tempo as tempo
import godot.core.autodif as ad

# convertire epoca in strainga e viceversa
epoch = tempo.Epoch("2012-12-23T18:23:23.00 TDB")
#print(epoch.calStr("TDB", 6))


# MJD in days
e1 = tempo.Epoch("1020.0 TDB")
# Specify the Julian day type in the string
e2 = tempo.Epoch("1020.0 MJD1950 TDB")
# Integer and float days to be added together
e3 = tempo.Epoch(1,123.234544444,tempo.TimeScale.TDB)
# Integer and float days to be added together with Julian day type
e4 = tempo.Epoch(1,123.342598888,tempo.TimeScale.TDB,tempo.JulianDay.MJD1950)
e5 = tempo.Epoch(2,123.342598888,tempo.TimeScale.TDB,tempo.JulianDay.MJD1950)

print(e1)
print(e2)
print(e3)
print(e4)
print(e5)

# convert epoch to different time scales    
epochTAI = epoch.convertTo(tempo.TimeScale.TAI)
print(epoch)
print(epochTAI)

# creare un intervallo di epoche e generare una griglia di epoche
rng = tempo.EpochRange(epoch,epoch+360)
for t in rng.createGrid(20.123):
    print(t)

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

