from godot.core import tempo
import godot.core.autodif as ad
import godot.model.common as common

# optionally avoid verbose logging messages
import godot.core.util as util
util.suppressLogger()

# Creiamo la prima classe che implementa le variabili ScalarTimeEvaluable
class Square ( common.ScalarTimeEvaluable ):
    def __init__(self, x : common.ScalarTimeEvaluable ):
        super().__init__()
        self.__x = x
    def eval(self, e ):
        x = self.__x.eval(e)
        return x * x

# creare una costante time-evaluable, quindi non dipendente dal tempo, ma posso comunque valutarla in funzione di una epoca   
x = common.ConstantScalarTimeEvaluable(2.0)
z = x.eval(tempo.Epoch())
print(z)

# creare una time-evaluable che dipende dal tempo
f = Square(x)
print(f.eval(tempo.Epoch()))

# Suppose I pass Square an autodif type, then I can evaluate it with or without partials by using Epoch or XEpoch respectively.
x = common.ConstantScalarTimeEvaluable(ad.Scalar( 2.0, "X" ))
f = Square(x)
z = f.eval(tempo.Epoch())
print(z)
z = f.eval(tempo.XEpoch())
print(z)

# Now, let's create another class that implements the same functionality as Square 
class OtherSquare ( common.ScalarTimeEvaluable ):
    def __init__(self, x : common.ScalarTimeEvaluable ):
        super().__init__()
        self.setx(x)
    def setx(self,x : common.ScalarTimeEvaluable):
        self.__x = x
    def eval(self, e ):
        x = self.__x.eval(e)
        return x * x
    
# Using OtherSquare with autodif ScalarTimeEvaluable     
x = common.ConstantScalarTimeEvaluable(ad.Scalar( 2.0, "X" ))
f = OtherSquare(x)
g = f + x * f
z =  g.eval(tempo.Epoch())
print(z)
z =  g.eval(tempo.XEpoch())
print(z)

# Now, we set the value of x inside f to be 3.0, and evaluate g. Because of the lazy evaluation, The result of g is now updated. In addition, there is a another gradient element.
f.setx(common.ConstantScalarTimeEvaluable(ad.Scalar( 3.0, "newX" )))
z =  g.eval(tempo.XEpoch())
print(z)