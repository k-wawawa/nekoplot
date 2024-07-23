
import numpy as np

class AbstructScale:
    def __init__(self):
        pass

    def __call__(self,value):
        raise NotImplementedError()

    def inv(self,value):
        raise NotImplementedError()

class LinearScale(AbstructScale):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Linear"

    def __call__(self,value):
        return value

    def inv(self,value):
        return value

class Log10Scale(AbstructScale):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Log10"

    def __call__(self,value):
        with np.errstate(all="ignore"):
            return np.log10(value)

    def inv(self,value):
        with np.errstate(all="ignore"):
            return np.power(10,value)

class LnScale(AbstructScale):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Ln"

    def __call__(self,value):
        with np.errstate(all="ignore"):
            return np.log(value)

    def inv(self,value):
        with np.errstate(all="ignore"):
            return np.exp(value)

class ASinhScale(AbstructScale):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "ArcSinh"

    def __call__(self,value):
        with np.errstate(all="ignore"):
            return np.arcsinh(value)

    def inv(self,value):
        with np.errstate(all="ignore"):
            return np.sinh(value)

class ASinh10Scale(AbstructScale):
    L10 = np.array(np.log(10))
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "ArcSinh_Base10"

    def __call__(self,value):
        with np.errstate(all="ignore"):
            return np.arcsinh(value)/self.L10

    def inv(self,value):
        with np.errstate(all="ignore"):
            return np.sinh(self.L10*value)