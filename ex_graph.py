
import time

import skia
import numpy as np

import cv2 as cv

TEST_PAINT = skia.Paint(StrokeWidth=0,Color=skia.Color(0,0,0,255),AntiAlias=False,Style=skia.Paint.kStroke_Style)

if not "status" in dir():
    from . import status
if not "item" in dir():
    from . import item
if not "ex_item" in dir():
    from . import ex_item
if not "graph" in dir():
    from . import graph

class GraphDetector(graph.AbstractGraph):
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

class GraphColorBar(graph.AbstractGraph):
    # self.ref.data is updated, then make_histogram,autocolor_range (is processed in self.ref.set)
    def __init__(self,parent,rotate=status.RotateStatus.NONE):
        super().__init__(parent,rotate)
        del self.images
        del self.lines
        self.line = item.Line()
        self.image = item.Image()
        self.vminbutton = None
        self.vmaxbutton = None
        self._ref = None
        self._capture_mouse = status.MouseStatus.NONE
        self._grab_limit = 0
        self.px = None
        self.cx = None
        self.limit_px = None
        self.triangle = skia.Path()
        self.triangle.lineTo(np.sqrt(3),1)
        self.triangle.lineTo(np.sqrt(3),-1)
        self.triangle.close()

    def _draw(self,recorder):
        self.draw_images(recorder)
        self.draw_lines(recorder)
        self.draw_ranges(recorder)

    def _draw_lines(self,canvas,matrix,rect):
        if self.line.data is not None:
            self.line.draw(matrix,rect)
            self.line.flush(canvas)

    def _draw_images(self,canvas):
        if self.image.data is not None:
            canvas.save()
            self.image.draw()
            if self._flipx:
                canvas.translate(self.width,0)
                canvas.scale(-1,1)
            if self._flipy:
                canvas.translate(0,self.height)
                canvas.scale(1,-1)
            self.image.img = self.image.img.resize(int(self.width),int(self.height/2))
            self.image.flush(canvas)
            canvas.restore()

    def draw_images(self,canvas):
        self._draw_images(canvas)

    def draw_ranges(self,canvas):
        rot = 0 if self._devicerotate == status.RotateStatus.NONE else 1
        left = self.toDisp(self.ref.image.vmin,self.ref.image.vmin)[rot]-self._deviceXY[rot]+0.5
        right = self.toDisp(self.ref.image.vmax,self.ref.image.vmax)[rot]-self._deviceXY[rot]+0.5
        ylim_d = 0
        ylim_u = self.height
        triangle_l = self.height*0.05
        fy = 0.25 if self._flipy else 0.75
        pl = skia.Path()
        pr = skia.Path()
        self.triangle.transform(skia.Matrix.Scale(triangle_l,triangle_l),pl)
        pl.offset(left,ylim_u*fy)
        self.triangle.transform(skia.Matrix.Scale(-triangle_l,triangle_l),pr)
        pr.offset(right,ylim_u*fy)
        canvas.drawPath(pl,skia.Paint(StrokeWidth=0,Color=skia.Color(0,255,0)))
        canvas.drawLine(left,ylim_d,left,ylim_u,skia.Paint(StrokeWidth=3,Color=skia.Color(0,255,0)))
        canvas.drawPath(pr,skia.Paint(StrokeWidth=0,Color=skia.Color(0,0,255)))
        canvas.drawLine(right,ylim_d,right,ylim_u,skia.Paint(StrokeWidth=3,Color=skia.Color(0,0,255)))

    def draw_roi(self,canvas):
        if self.px is not None and self.cx is not None:
            rot = 0 if self._devicerotate == status.RotateStatus.NONE else 1
            px = self.toDisp(self.px,self.px)[rot] - self._deviceXY[rot]+0.5
            cx = self.toDisp(self.cx,self.cx)[rot] - self._deviceXY[rot]+0.5
            ylim_d = 0
            ylim_u = self.height
            canvas.drawLine(cx,ylim_d-0.5,cx,ylim_u+0.5,skia.Paint())
            canvas.drawLine(px,ylim_d-0.5,px,ylim_u+0.5,skia.Paint())

    def make_gradation(self):
        vmin = self.ref.image.vmin
        vmax = self.ref.image.vmax
        cb = np.linspace(self.xlim[0],self.xlim[1],int(self.width)).reshape(1,int(self.width))
        self.image.set(data=cb,vmin=vmin,vmax=vmax,histogram=False)

    def histogram_proc(self,hist):
        # ヒストグラムの変化のない中間値をトリムする
        h = hist>0
        hm = np.append(h[1:],True)
        hp = np.append(True,h[:-1])
        dil = np.any(np.array([h,hm,hp]),axis=0)
        idxs = np.arange(len(hist))[dil]
        vals = hist[dil]
        return np.array([idxs,vals]).T

    def draw(self,canvas,xlim=None,ylim=None):
        if status.GraphStatus.FROM_DATA in self._update:
            if self.ref.image._histogram is not None:
                hist = self.ref.image._histogram
                self.line.set(data=self.histogram_proc(hist))
                self._update &= ~status.GraphStatus.FROM_DATA
        if status.GraphStatus.UPDATE in self._update:
            if self.ref.image.data is not None:
                self.make_gradation()
        super().draw(canvas,xlim,ylim)
        canvas.save()
        canvas.translate(*self._deviceXY)
        if self._devicerotate == status.RotateStatus.FLIP:
            canvas.translate(self.height,0)
        rotate = 0 if (self._devicerotate == status.RotateStatus.NONE) else 90
        canvas.rotate(rotate)
        canvas.clipRect(self.deviceRect)
        self.draw_roi(canvas)
        canvas.restore()

    @property
    def ref(self):
        return self._ref
    @ref.setter
    def ref(self,value):
        self._ref = value

    def OnMouseLDown(self,evt):
        self._capture_mouse |= status.MouseStatus.LEFT
        rot = 0 if self._devicerotate==status.RotateStatus.NONE else 1
        x = evt.GetPosition()[rot]
        left = self.toDisp(self.ref.image.vmin,self.ref.image.vmin)[rot]
        right = self.toDisp(self.ref.image.vmax,self.ref.image.vmax)[rot]
        # if abs(left-x) < 5:
        fliped = [self._flipx,self._flipy][rot]
        bleft = (-3-self.height*0.05 <= (x-left) <= 0) if not fliped else (0 <= (x-left) <= 3+self.height*0.05)
        bright = (0 <= (x-right) <= 3+self.height*0.05) if not fliped else (-3-self.height*0.05 <= (x-right) <= 0)
        if bleft:
            self._grab_limit = 1
            self.limit_px = x
        # elif abs(right-x) < 5:
        elif bright:
            self._grab_limit = 2
            self.limit_px = x
        else:
            self._grab_limit = 0

    def OnMouseLUp(self,evt):
        if status.MouseStatus.LEFT in self._capture_mouse:
            rot = 0 if self._devicerotate==status.RotateStatus.NONE else 1
            if not self.contains(*evt.GetPosition()):
                return
            if self.limit_px is None:
                return
            pos = evt.GetPosition()[rot]
            x,y = self.toData(pos,pos)
            xx,yy = self.toData(self.limit_px,self.limit_px)
            if self._grab_limit == 1:
                self.ref.image.set(vmin=self.ref.image.vmin+(x-xx))
            elif self._grab_limit == 2:
                self.ref.image.set(vmax=self.ref.image.vmax+(x-xx))
            self.limit_px = None
            self.update()
            self.ref.update()
            self._capture_mouse ^= status.MouseStatus.LEFT
            self.wx.draw()
            self.wx.Refresh()

    def OnMouseRDown(self,evt):
        self._capture_mouse |= status.MouseStatus.RIGHT
        rot = 0 if self._devicerotate==status.RotateStatus.NONE else 1
        x = evt.GetPosition()[rot]
        x = self.toData(x,x)[0]
        self.px = x

    def OnMouseRUp(self,evt):
        if status.MouseStatus.RIGHT in self._capture_mouse:
            if self.cx is None:
                self.px = None
                self.cx = None
                return
            rot = 0 if self._devicerotate==status.RotateStatus.NONE else 1
            s,l = min(self.px,self.cx),max(self.px,self.cx)
            if s == l:
                l += 1
            self.xlim = (s,l)
            self.px = None
            self.cx = None
            self.update()
            self.ref.update()
            self._capture_mouse ^= status.MouseStatus.RIGHT
            self.wx.draw()
            self.wx.Refresh()

    def OnMouseMotion(self,evt):
        if status.MouseStatus.LEFT in self._capture_mouse:
            rot = 0 if self._devicerotate==status.RotateStatus.NONE else 1
            if self.limit_px is None:
                return
            dev = self._deviceXY[rot]
            pos = evt.GetPosition()[rot]
            if dev <= pos <= dev+self.width:
                x,y = self.toData(pos,pos)
                xx,yy = self.toData(self.limit_px,self.limit_px)
                dx = x-xx
                if self._grab_limit == 1:
                    self.ref.image.set(vmin=self.ref.image.vmin+dx)
                    self.limit_px = pos
                elif self._grab_limit == 2:
                    self.ref.image.set(vmax=self.ref.image.vmax+dx)
                    self.limit_px = pos
                self.update()
                self.ref.update()
        if status.MouseStatus.RIGHT in self._capture_mouse:
            rot = 0 if self._devicerotate==status.RotateStatus.NONE else 1
            x = evt.GetPosition()[rot]
            x = self.toData(x,x)[0]
            self.cx = x
            self.deco_update()

    def OnMouseLeave(self,evt):
        if status.MouseStatus.LEFT in self._capture_mouse:
            x,y = self.toData(*evt.GetPosition())
            if self._grab_limit == 1:
                self.ref.image.set(vmin=x)
            elif self._grab_limit == 2:
                self.ref.image.set(vmax=x)
            self.update()
            self.ref.update()
        self._capture_mouse = status.MouseStatus.NONE

    def OnMouseDClick(self,evt):
        if self.ref.image.data is not None:
            self.ref.image.auto_colorrange()
            hist = self.ref.image._histogram
            l = len(hist)
            self.xlim = (-0.15*l,1.15*l)
            self.update()
            self.ref.update()
            self.wx.draw()
            self.wx.Refresh()
        self._capture_mouse = status.MouseStatus.NONE

    def OnMouseLDClick(self,evt):
        self.OnMouseDClick(evt)
    def OnMouseRDClick(self,evt):
        self.OnMouseDClick(evt)

    def OnMouseWheel(self, evt):
        bairitsu = 0.15
        if evt.GetWheelRotation() > 0:
            scale = 1-bairitsu
        else:
            scale = 1+bairitsu
        vl,vr = self.xlim
        vx,vy = self.toData(*evt.GetPosition())
        if (vx-scale*(vx-vl) >= vx+scale*(vr-vx)):
            return
        self.xlim = (vx-scale*(vx-vl) , vx+scale*(vr-vx))
        self.update()
        self.ref.update()
        self.wx.draw()
        self.wx.Refresh()