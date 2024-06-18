
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

    def __call__(self,value):
        return value

    def inv(self,value):
        return value

class Log10Scale(AbstructScale):
    def __init__(self):
        super().__init__()

    def __call__(self,value):
        return np.log10(value)

    def inv(self,value):
        return 10.**value

class LnScale(AbstructScale):
    def __init__(self):
        super().__init__()

    def __call__(self,value):
        return np.log(value)

    def inv(self,value):
        return np.exp(value)

class SinhScale(AbstructScale):
    def __init__(self):
        super().__init__()

    def __call__(self,value):
        return np.sinh(value)

    def inv(self,value):
        return np.arcsinh(value)