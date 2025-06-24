
import time
import itertools
import skia
import numpy as np

from .. import status
from .. import color
from .. import item
from .. import utility
from .. import rect
from .. import const

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
        self._vscale = lambda x:x
        self._scaled_data = None
        self.auto_left = 25
        self.auto_right = 75
        self.colormap = "parula"
        self.nan_color = color.Color.fromU8(0,0,0,0)
        self.img = None
        self.mask_img = None
        self.mask_draw_img = None
        self._mask_alpha = 0.5
        self._mask_color = color.ColorList["red"]
        self._colorbar = None
        self.extent = None

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
        self._scaled_data = None
        self.img = None
        self.extent = None

    def set(self,**dargs):
        if "data" in dargs:
            if dargs["data"] is None:
                self.clear()
            else:
                self._update |= status.ImageStatus.DATA
                self._update_image = True
                self.data = np.array(dargs.pop("data"))
                self._scaled_data = self.vscale(self.data.astype(np.float32))
                self.extent = None
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
        if {"vmin","vmax","vscale","colormap"} & set(dargs.keys()):
            self._update |= status.ImageStatus.VALUE
            self._update_image = True
        if "vmin" in dargs:
            self.vmin = dargs.get("vmin",self.vmin)
        if "vmax" in dargs:
            self.vmax = dargs.get("vmax",self.vmax)
        if self.vmin >= self.vmax:
            self.vmax = self.vmin
        if "vscale" in dargs:
            self.vscale = dargs.get("vscale",self.vscale)
        if "extent" in dargs:
            self.extent = dargs.get("extent",self.extent)
            dargs.pop("extent")
        if "colormap" in dargs:
            self.colormap = dargs.get("colormap")
            if self.colorbar is not None:
                self.colorbar._update |= status.GraphStatus.UPDATE
        if len(dargs)>0:
            if self.colorbar is not None:
                self.colorbar.image.set(**dargs)

    def make_histogram(self):
        if self.data is None:
            self._histogram = None
            return self._histogram
        if self.data_mask is None:
            if np.issubdtype(self.data.dtype,np.integer):
                arr = self.data
                vmin,vmax = np.min(arr),np.max(arr)
                bins = min(int(vmax - vmin +1),const.MAX_HISTGRAM_BINS)
                r = (vmin-0.5,vmax+0.5)
            elif np.issubdtype(self.data.dtype,np.floating):
                arr = self.data[np.isfinite(self.data)]
                bins = "auto"
                r = (np.min(arr),np.max(arr))
            counts,edges = np.histogram(arr,bins=bins,range=r)
            self._histogram = np.array([(edges[:-1]+edges[1:])*0.5,counts])
            if self.colorbar is not None:
                self.colorbar.line.set(data=self._histogram)
        else:
            if not np.all(self.data_mask):
                if np.issubdtype(self.data.dtype,np.integer):
                    arr = self.data[~self.data_mask]
                    vmin,vmax = np.min(arr),np.max(arr)
                    bins = min(int(vmax - vmin +1),const.MAX_HISTGRAM_BINS)
                    r = (vmin-0.5,vmax+0.5)
                elif np.issubdtype(self.data.dtype,np.floating):
                    arr = self.data[np.logical_and(np.isfinite(self.data),~self.data_mask)]
                    bins = "auto"
                    r = (np.min(arr),np.max(arr))
                counts,edges = np.histogram(arr,bins=bins,range=r)
                self._histogram = np.array([(edges[:-1]+edges[1:])*0.5,counts])
                if self.colorbar is not None:
                    self.colorbar.line.set(data=self._histogram)
            else:
                self._histogram = None
                if self.colorbar is not None:
                    self.colorbar.line.set(data=None)
        return self._histogram

    def auto_colorrange(self,left=None,right=None):
        if self.data is None:
            self.set(vmin=1,vmax=1)
            return
        if self.data_mask is None:
            self.auto_left = left if left is not None else self.auto_left
            self.auto_right = right if right is not None else self.auto_right
            finite = np.isfinite(self._scaled_data)
            if np.any(finite):
                qleft,qright = np.percentile(self.data[finite],[self.auto_left,self.auto_right])
                self.set(vmin=qleft,vmax=qright)
            else:
                self.set(vmin=1,vmax=1)
        else:
            if not np.all(self.data_mask):
                self.auto_left = left if left is not None else self.auto_left
                self.auto_right = right if right is not None else self.auto_right
                mask = np.logical_and(np.isfinite(self._scaled_data),~self.data_mask)
                if np.any(mask):
                    qleft,qright = np.percentile(self.data[mask],[self.auto_left,self.auto_right])
                    self.set(vmin=qleft,vmax=qright)
                else:
                    self.set(vmin=1,vmax=1)
            else:
                self.set(vmin=1,vmax=1)

    def draw_image(self):
        if (self._update == status.ImageStatus.NONE) or (self.data is None):
            return
        # Apply color map
        tmp = self._scaled_data.copy()
        mask = np.isnan(tmp)
        vmin,vmax = self.vscale(self.vmin),self.vscale(self.vmax)
        if vmax == vmin:
            tmp = np.where(tmp>vmin,255,0)
            # tmp[np.isnan(tmp)] = vmin
            # small = tmp<=vmin
            # large = tmp>vmax
            # tmp[small] = 0
            # tmp[large] = 255
        else:
            d = 255./(vmax-vmin)
            tmp[np.isnan(tmp)] = vmin
            tmp = d*(np.clip(tmp,vmin,vmax)-vmin)
            # tmp[np.isnan(tmp)] = vmin
            # small = tmp<vmin
            # large = tmp>vmax
            # tmp[small] = vmin
            # tmp[large] = vmax
            # tmp -= vmin
            # tmp *= d
        tmp = self.colormap.apply(tmp).copy()
        tmp[mask] = self.nan_color.i32
        self.img = skia.Image.fromarray(tmp,skia.ColorType.kRGBA_8888_ColorType)
        self._update &= status.ImageStatus.NONE

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
        if (self.img is not None):
            irct = skia.Rect.MakeWH(self.img.width(),self.img.height())
            canvas.drawImageRect(self.img,irct,self.extent.skiaRect)
            if self.mask_img is not None:
                canvas.drawImageRect(self.mask_img,irct,self.extent.skiaRect,paint=skia.Paint(Alphaf=self.mask_alpha))
            if self.mask_draw_img is not None:
                canvas.drawImageRect(self.mask_draw_img,irct,self.extent.skiaRect,paint=skia.Paint(Alphaf=self.mask_alpha))

    def draw_value(self,canvas,graph):
        if self.data is not None:
            font = graph.font*graph.sizescale
            xl = max(self.extent.x0,graph.xlim[0])
            xr = min(self.extent.x1,graph.xlim[1])
            yd = max(self.extent.y0,graph.ylim[0])
            yu = min(self.extent.y1,graph.ylim[1])
            imrect = self.rect
            toextent = imrect.to(self.extent)
            ds = toextent(np.array([[0,0],[1,1]]))
            d1,d2 = graph.toDisp(*ds[0])
            d3,d4 = graph.toDisp(*ds[1])
            mbox = font.getHeight()*1.1*3
            if abs(d3-d1)>mbox and abs(d4-d2)>mbox:
                torect = self.extent.to(imrect)
                iis = torect(np.array([[xl,yd],[xr,yu]]))
                i1,i2 = iis[0]
                i3,i4 = iis[1]
                xs = np.arange(int(i1),min(int(i3)+1,self.data.shape[1]))
                ys = np.arange(int(i2),min(int(i4)+1,self.data.shape[0]))
                ijs = np.array(list(itertools.product(xs,ys)))
                xys = toextent(ijs+0.5)
                for ij,xy in zip(ijs,xys):
                    i,j = ij
                    ps = graph.toDisp(*xy)
                    v = self.data[j][i]
                    t = str(v)
                    blob = font.makeText(t)
                    tw = font.measureText(t,paint=graph.paint)
                    tpos = (ps[0]-0.5*tw, ps[1]+0.5*font.getSize())
                    canvas.drawTextBlob(blob,*tpos,graph.paint)

    def draw_roi(self,canvas,graph):
        if self.data is not None:
            x,y = graph._deviceXY
            xx,yy = graph.width+x-1, graph.height+y-1
            if graph.roix is not None and graph.roiy is not None:
                x1,y1 = graph.toDisp(graph.roix[0],graph.roiy[0])
                x2,y2 = graph.toDisp(graph.roix[1],graph.roiy[1])
                canvas.drawLine(x1,y,x1,yy,skia.Paint())
                canvas.drawLine(x2,y,x2,yy,skia.Paint())
                canvas.drawLine(x,y1,xx,y1,skia.Paint())
                canvas.drawLine(x,y2,xx,y2,skia.Paint())

    @property
    def width(self):
        if self.data is not None:
            return self.data.shape[1]
        return 1
    @property
    def height(self):
        if self.data is not None:
            return self.data.shape[0]
        return 1

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

    @property
    def vscale(self):
        return self._vscale
    @vscale.setter
    def vscale(self,value):
        if callable(value):
            self._vscale = value
            if self.data is not None:
                self._scaled_data = self.vscale(self.data.astype(np.float32))
            self._update |= status.ImageStatus.VALUE
        else:
            raise RuntimeWarning("numpy array callable only")

    @property
    def extent(self):
        return self._extent
    @extent.setter
    def extent(self,value):
        if value is not None:
            self._extent = rect.Rect(coodinate=value)
        else:
            self._extent = rect.Rect(coodinate=(0.,0.,self.width+.0,self.height+.0))

    @property
    def rect(self):
        return rect.Rect(coodinate=(0.,0.,self.width+.0,self.height+.0))