
import time

import skia
import numpy as np

import cv2 as cv

TEST_PAINT = skia.Paint(StrokeWidth=0,Color=skia.Color(0,0,0,255),AntiAlias=False,Style=skia.Paint.kStroke_Style)

from .. import status
from .. import item
from .. import graph
from .. import scale
from . import ex_item

class GraphDetector(graph.Graph):
    def __init__(self,parent,rotate=status.RotateStatus.NONE):
        super().__init__(parent,rotate)
        del self.images
        del self.lines
        self.image = ex_item.DetectorImage()
        self._roix = None
        self._roiy = None
        self._colorbar = None
        self.font = item.Font(size=12)
        self.paint = skia.Paint(Color=skia.Color(0,0,0),AntiAlias=True)
        self._vlogscale = False

    def has_image(self):
        return True

    def set(self,**dargs):
        self._update |= status.GraphStatus.UPDATE
        self.image.set(**dargs)

    def _draw(self,recorder):
        self.draw_images(recorder)

    def _draw_images(self,canvas):
        self.image.draw()
        self.image.flush(canvas)

    def draw(self,canvas,xlim=None,ylim=None):
        super().draw(canvas,xlim,ylim)
        canvas.save()
        rotate = 0 if (self._devicerotate == status.RotateStatus.NONE) else 90
        canvas.rotate(rotate)
        x,y = self._deviceXY
        canvas.clipRect(skia.Rect.MakeXYWH(x,y,self.width,self.height))
        self.draw_roi(canvas)
        self.draw_value(canvas)
        canvas.restore()

    def draw_roi(self,canvas):
        if self.image.data is not None:
            x,y = self._deviceXY
            xx,yy = self.width+x-1,self.height+y-1
            if self.roix is not None and self.roiy is not None:
                x1,y1 = self.toDisp(self.roix[0],self.roiy[0])
                x2,y2 = self.toDisp(self.roix[1],self.roiy[1])
                canvas.drawLine(x1,y,x1,yy,skia.Paint())
                canvas.drawLine(x2,y,x2,yy,skia.Paint())
                canvas.drawLine(x,y1,xx,y1,skia.Paint())
                canvas.drawLine(x,y2,xx,y2,skia.Paint())

    def draw_value(self,canvas):
        if self.image.data is not None:
            xl = max(0,int(self.xlim[0]))
            xr = min(self.data.shape[1]-1,int(self.xlim[1]))
            yd = max(0,int(self.ylim[0]))
            yu = min(self.data.shape[0]-1,int(self.ylim[1]))
            d1,d2 = self.toDisp(1,1)
            d3,d4 = self.toDisp(2,2)
            if abs(d3-d1)>20 and abs(d4-d2)>20:
                for x in range(int(xl),int(xr)+1):
                    for y in range(int(yd),int(yu)+1):
                        ps = self.toDisp(x+0.5,y+0.5)
                        v = self.data[y][x]
                        t = str(v)
                        blob = skia.TextBlob.MakeFromString(t,self.font())
                        tw = self.font.measureText(t,paint=self.paint)
                        tpos = (-0.5*tw+ps[0],ps[1]+0.5*self.font.getSize())
                        canvas.drawTextBlob(blob,*tpos,self.paint)

    def modifydata(self,**dargs):
        self.update()
        self.image.set(**dargs)

    def data_withmask(self,data,mask):
        self._update = status.GraphStatus.UPDATE
        self.image.set(data=data,mask=mask)
        self.image.make_histogram()

    @property
    def colorbar(self):
        return self._colorbar
    @colorbar.setter
    def colorbar(self,value):
        self._colorbar = value
        self.image.colorbar = value
        value.ref = self

    @property
    def data(self):
        return self.image.data
    @data.setter
    def data(self,value):
        self._update = status.GraphStatus.UPDATE
        self.image.set(data=value)
        self.image.make_histogram()

    @property
    def mask(self):
        return self.image.data_mask
    @mask.setter
    def mask(self,value):
        self._update = status.GraphStatus.UPDATE
        self.image.set(mask=value)
        self.image.make_histogram()

    @property
    def im_mask(self):
        return (self.image.data,self.image.data_mask)
    @im_mask.setter
    def im_mask(self,value):
        self._update = status.GraphStatus.UPDATE
        self.image.set(data=value[0],mask=[1])
        self.image.make_histogram()

    @property
    def roix(self):
        return self._roix
    @roix.setter
    def roix(self,value):
        self.update()
        self._roix = value

    @property
    def roiy(self):
        return self._roiy
    @roiy.setter
    def roiy(self,value):
        self.update()
        self._roiy = value

    @property
    def colormap(self):
        return self.image.colormap
    @colormap.setter
    def colormap(self,value):
        self.update()
        self.image.set(colormap=value)

    @property
    def histogram(self):
        return self.image._histogram

    @property
    def vlogscale(self):
        return self._vlogscale
    @vlogscale.setter
    def vlogscale(self,value):
        self.update()
        self._vlogscale = value
        self.image.set(vscale=scale.Log10Scale() if value else scale.LinearScale())
        if self.colorbar is not None:
            self.colorbar.vlogscale = value

    @property
    def vscale(self):
        return self.image.vscale
    @vscale.setter
    def vscale(self,value):
        if isinstance(value,scale.AbstructScale):
            self.update()
            self.image.set(vscale=value)
            if self.colorbar is not None:
                self.colorbar.vscale = value

    @property
    def xscale(self):
        return self._xscale
    @xscale.setter
    def xscale(self,value):
        pass

    @property
    def yscale(self):
        return self._yscale
    @yscale.setter
    def yscale(self,value):
        pass

    @property
    def xyscale(self):
        return self._xscale
    @xyscale.setter
    def xyscale(self,value):
        pass