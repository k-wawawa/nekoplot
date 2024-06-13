
import time
import skia
import numpy as np

if not "status" in dir():
    from . import status
if not "color" in dir():
    from . import color
if not "item" in dir():
    from . import item
if not "utility" in dir():
    from . import utility

class DetectorImage():
    def __init__(self):
        self._update = status.ImageStatus.NONE
        self._update_image = False
        self._update_mask = False
        self._update_mask_draw = False
        self.data = None
        self.data_mask = None
        self.data_mask_draw = None
        self._histogram = None
        self.vmin = 0
        self.vmax = 1
        self.auto_left = 25
        self.auto_right = 75
        self.colormap = "parula"
        self.img = None
        self.mask_img = None
        self.mask_draw_img = None
        self._mask_alpha = 0.5
        self._mask_color = color.ColorList["red"]
        self._colorbar = None

    @property
    def mask_color(self):
        return self._mask_color
    @mask_color.setter
    def mask_color(self,value):
        self._update_mask = True
        self._update_mask_draw = True
        self._mask_color = color.Color.fromU8(*value)

    @property
    def mask_alpha(self):
        return self._mask_alpha
    @mask_alpha.setter
    def mask_alpha(self,value):
        self._update_mask = True
        self._update_mask_draw = True
        self._mask_alpha = value

    def clear(self):
        self._update &= status.ImageStatus.NONE
        self._update_image = False
        self.data = None
        self.img = None

    def set(self,**dargs):
        if "data" in dargs:
            if dargs["data"] is None:
                self.clear()
            else:
                self._update |= status.ImageStatus.DATA
                self._update_image = True
                self.data = np.array(dargs["data"])
        if "mask" in dargs:
            if dargs["mask"] is None:
                self.data_mask = None
                self.mask_img = None
                self._update |= status.ImageStatus.DATA
                self._update_mask = False
            else:
                self._update |= status.ImageStatus.DATA
                self._update_mask = True
                self.data_mask = np.array(dargs["mask"],dtype=bool)
        if "mask_draw" in dargs:
            if dargs["mask_draw"] is None:
                self.data_mask_draw = None
                self.mask_draw_img = None
                self._update |= status.ImageStatus.DATA
                self._update_mask_draw = False
            else:
                self._update |= status.ImageStatus.DATA
                self._update_mask_draw = True
                self.data_mask_draw = np.array(dargs["mask"],dtype=bool)
        if "mask_color" in dargs:
            self.mask_color = dargs.get("mask_color",self.mask_color)
        if "mask_alpha" in dargs:
            self.mask_alpha = dargs.get("mask_alpha",self.mask_alpha)
        if {"vmin","vmax","colormap"} & set(dargs.keys()):
            self._update |= status.ImageStatus.VALUE
            self._update_image = True
        if "vmin" in dargs:
            self.vmin = dargs.get("vmin",self.vmin)
        if "vmax" in dargs:
            self.vmax = dargs.get("vmax",self.vmax)
        if self.vmin >= self.vmax:
            self.vmax = self.vmin
        if "colormap" in dargs:
            self.colormap = dargs.get("colormap")
            if self.colorbar is not None:
                self.colorbar._update |= status.GraphStatus.UPDATE
        if len(dargs)>0:
            if self.colorbar is not None:
                self.colorbar.image.set(**dargs)

    def make_histogram(self,bins=None):
        if self.data is None:
            self._histogram = None
        if self.data_mask is None:
            imgmax = int(np.max(self.data))
            bins = imgmax + 1 if bins is None else bins
            self._histogram = np.histogram(self.data,bins=bins,range=(0,bins))[0]
            if self.colorbar is not None:
                self.colorbar._update |= status.GraphStatus.FROM_DATA
        else:
            if not np.all(self.data_mask):
                imgmax = int(np.max(self.data[~self.data_mask]))
                bins = imgmax + 1 if bins is None else bins
                self._histogram = np.histogram(self.data,bins=bins,range=(0,bins),weights=(~self.data_mask).astype(int))[0]
                if self.colorbar is not None:
                    self.colorbar._update |= status.GraphStatus.FROM_DATA
            else:
                self._histogram = None
                if self.colorbar is not None:
                    self.colorbar._update |= status.GraphStatus.FROM_DATA
        return self._histogram

    def auto_colorrange(self,left=None,right=None):
        if self.data is None:
            self.set(vmin=0,vmax=1)
            return
        if self.data_mask is None:
            self.auto_left = left if left is not None else self.auto_left
            self.auto_right = right if right is not None else self.auto_right
            qleft,qright = np.percentile(self.data,[self.auto_left,self.auto_right])
            self.set(vmin=qleft,vmax=qright)
        else:
            if not np.all(self.data_mask):
                self.auto_left = left if left is not None else self.auto_left
                self.auto_right = right if right is not None else self.auto_right
                qleft,qright = np.percentile(self.data[~self.data_mask],[self.auto_left,self.auto_right])
                self.set(vmin=qleft,vmax=qright)
            else:
                self.set(vmin=0,vmax=1)

    def draw_image(self):
        if (not self._update_image) or (self.data is None):
            return
        # Apply color map
        tmp = self.data.astype(np.float32)
        if self.vmax == self.vmin:
            tmp[np.isnan(tmp)] = self.vmin
            small = tmp<=self.vmin
            large = tmp>self.vmax
            tmp[small] = 0
            tmp[large] = 255
        else:
            if True:
                d = 255./(self.vmax-self.vmin)
                tmp[np.isnan(tmp)] = self.vmin
                small = tmp<self.vmin
                large = tmp>self.vmax
                tmp[small] = self.vmin
                tmp[large] = self.vmax
                tmp -= self.vmin
                tmp *= d
            else:
                tmp = np.interp(tmp,[self.vmin,self.vmax],[0,255])
        tmp = self.colormap.apply(tmp).copy()
        self.img = skia.Image.fromarray(tmp,skia.ColorType.kRGBA_8888_ColorType)
        self._update &= status.ImageStatus.NONE
        self._update_image = False

    def draw_mask(self):
        if (not self._update_mask) or (self.data_mask is None):
            return
        col = self.mask_color.i32
        base = self.data_mask*col
        self.mask_img = skia.Image.fromarray(base,skia.ColorType.kRGBA_8888_ColorType)
        self._update &= status.ImageStatus.NONE
        self._update_mask = False

    def draw_mask_draw(self):
        if (not self._update_mask_draw) or (self.data_mask_draw is None):
            return
        col = self.mask_color.i32
        base = self.data_mask_draw *col
        self.mask_draw_img = skia.Image.fromarray(base,skia.ColorType.kRGBA_8888_ColorType)
        self._update &= status.ImageStatus.NONE
        self._update_mask_draw = False

    def process_mask(self,mask=True):
        if self.data_mask_draw is None:
            raise RuntimeWarning("data_mask_draw is None")
        if self.data_mask is None:
            tmp = np.zeros_like(self.data_mask_draw)
        else:
            tmp = self.data_mask.copy()
        if mask:
            tmp[self.data_mask_draw] = True
        else:
            tmp[self.data_mask_draw] = False
        self.data_mask_draw = None
        self._update_mask_draw = False
        self.mask_draw_img = None
        return tmp

    def draw(self):
        self.draw_image()
        self.draw_mask()
        self.draw_mask_draw()

    def flush(self,canvas):
        canvas.drawImage(self.img,0,0)
        canvas.drawImage(self.mask_img,0,0,skia.Paint(Alphaf=self.mask_alpha))
        canvas.drawImage(self.mask_draw_img,0,0,skia.Paint(Alphaf=self.mask_alpha))

    @property
    def colorbar(self):
        return self._colorbar
    @colorbar.setter
    def colorbar(self,value):
        self._colorbar = value

    @property
    def colormap(self):
        return self._colormap
    @colormap.setter
    def colormap(self,value):
        self._colormap = color.ColorMap(value)
