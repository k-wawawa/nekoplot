import numpy as np
import skia

class Rect(tuple):
    def __new__(cls,*,coodinate=None,affine=None):
        """
        coodinate = (x0,y0,x1,y1)
        affine = (sx,tx,sy,ty)
        """
        if not ((coodinate is not None) ^ (affine is not None)):
            raise ValueError("only one of coodinate or affine can be provided,not both")
        if coodinate:
            if not isinstance(coodinate,(list,tuple)):
                raise TypeError("Should be a list or tuple")
            if len(coodinate) != 4:
                raise ValueError("Should contain exactly 4 elements")
            obj = super().__new__(cls,[x+.0 for x in coodinate])
            obj.sx = obj.x1-obj.x0
            obj.sy = obj.y1-obj.y0
            obj.tx = obj.x0
            obj.ty = obj.y0
            obj.sxi = 1./obj.sx
            obj.syi = 1./obj.sy
            obj.txi = - obj.tx*obj.sxi
            obj.tyi = - obj.ty*obj.syi
        if affine:
            if not isinstance(affine,(list,tuple)):
                raise TypeError("Should be a list or tuple")
            if len(affine) != 4:
                raise ValueError("Should contain exactly 4 elements")
            tpl = (affine[1],affine[3],affine[0]+affine[1],affine[2]+affine[3])
            obj = super().__new__(cls,tpl)
            obj.sx = affine[0]
            obj.sy = affine[2]
            obj.tx = affine[1]
            obj.ty = affine[3]
            obj.sxi = 1./obj.sx
            obj.syi = 1./obj.sy
            obj.txi = - obj.tx*obj.sxi
            obj.tyi = - obj.ty*obj.syi
        obj.skiaRect = skia.Rect.MakeLTRB(obj[0]+.0,obj[1]+.0,obj[2]+.0,obj[3]+.0)
        return obj

    @property
    def x0(self):
        return self[0]
    @property
    def y0(self):
        return self[1]
    @property
    def x1(self):
        return self[2]
    @property
    def y1(self):
        return self[3]

    def to(self,rect):
        if not isinstance(rect,Rect):
            raise TypeError("Should be Rect!!")
        sx = self.sxi*rect.sx
        tx = self.txi*rect.sx + rect.tx
        sy = self.syi*rect.sy
        ty = self.tyi*rect.sy + rect.ty
        return Rect(affine=(sx,tx,sy,ty))

    def __call__(self,xys):
        if not xys.shape[1] == 2:
            raise TypeError("Should be N*2 numpy array")
        xs,ys = xys.T
        xxs = self.sx*xs + self.tx
        yys = self.sy*ys + self.ty
        return np.row_stack([xxs,yys]).T
