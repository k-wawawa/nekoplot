
import time

import skia
import numpy as np

import cv2 as cv

TEST_PAINT = skia.Paint(StrokeWidth=0,Color=skia.Color(0,0,0,255),AntiAlias=False,Style=skia.Paint.kStroke_Style)

if not "status" in dir():
    from . import status
if not "item" in dir():
    from . import item
if not "panel" in dir():
    from . import panel
if not "event" in dir():
    from . import event

class AbstractGraph(panel.Panel):
    def __init__(self,parent,rotate=status.RotateStatus.NONE):
        super().__init__(parent)
        self._update = status.GraphStatus.UPDATE
        self._devicerotate = rotate
        self._xlim = (0.,1.)
        self._ylim = (0.,1.)
        self.lines = list()
        self.images = list()
        self.flines = list()
        self._flipx = False
        self._flipy = False
        self._xtick = None
        self._ytick = None
        self._rubber_rect = None
        self.mat9 = (1,0,0,0,1,0,0,0,1)
        self.annotation = item.Annotation()
        self._border = status.BorderStatus.ALL
        self._capture_mouse = status.MouseStatus.NONE

    def _draw(self,recorder,xlim,ylim):
        raise NotImplementedError

    @property
    def flipx(self):
        return status.Direction.RtoL if self._flipx else status.Direction.LtoR
    @flipx.setter
    def flipx(self,value):
        if isinstance(value,status.Direction):
            if value == status.Direction.LtoR:
                self._flipx = False
            elif value == status.Direction.RtoL:
                self._flipx = True
            else:
                raise ValueError("choose LtoR or RtoL")
        else:
            raise ValueError("only status.Direction")

    @property
    def flipy(self):
        return status.Direction.DtoU if self._flipy else status.Direction.UtoD
    @flipy.setter
    def flipy(self,value):
        if isinstance(value,status.Direction):
            if value == status.Direction.UtoD:
                self._flipy = False
            elif value == status.Direction.DtoU:
                self._flipy = True
            else:
                raise ValueError("choose UtoD or DtoU")
        else:
            raise ValueError("only status.Direction")

    def toData(self,x,y):
        l,t = self._deviceXY
        w = self.width-1
        h = self.height-1
        if self._devicerotate == status.RotateStatus.FLIP:
            dy = -(x-l)
            dx = y-t
        else:
            dy = y-t
            dx = x-l
        l = w-dx if self._flipx else dx
        t = h-dy if self._flipy else dy
        dx = l/w
        dy = t/h
        vl,vr = self.xlim
        vb,vt = self.ylim
        vx = dx*(vr-vl)+vl
        vy = dy*(vt-vb)+vb
        return vx,vy

    def toDisp(self,x,y):
        l,t = self._deviceXY
        w = self.width-1
        h = self.height-1
        vl,vr = self.xlim
        vb,vt = self.ylim
        dx = (x-vl)/(vr-vl)*w
        dy = (y-vb)/(vt-vb)*h
        dx = w - dx if self._flipx else dx
        dy = h - dy if self._flipy else dy
        if self._devicerotate == status.RotateStatus.FLIP:
            xx = l+dy
            yy = t+dx
        else:
            xx = l+dx
            yy = t+dy
        # return int(xx),int(yy)
        return xx+0.5,yy+0.5

    def contains(self,x,y):
        xl,yt = self._deviceXY
        xr = xl+(self.width if (self._devicerotate == status.RotateStatus.NONE) else self.height)
        yd = yt+(self.height if (self._devicerotate == status.RotateStatus.NONE) else self.width)
        if xl<=x<xr and yt<=y<yd:
            return True
        return False

    def make_mat9(self,xlim=None,ylim=None):
        _xlim = xlim if xlim is not None else self.xlim
        _ylim = ylim if ylim is not None else self.ylim
        l,t,r,b = self.deviceRect
        if self._flipx:
            l,r = r,l
        if self._flipy:
            t,b = b,t
        xl,xr = _xlim
        yb,yt = _ylim
        xc, yc = 1/(xr-xl), 1/(yt-yb)
        xs, ys = (r-l)*xc, (b-t)*yc
        xtr, ytr = (l*xr-r*xl)*xc, (t*yt-b*yb)*yc
        self.mat9 = (xs,0.,xtr,0.,ys,ytr,0.,0.,1.)
        return self.mat9

    def deco_update(self):
        if self.parent is not None:
            self.parent.update()

    def draw(self,canvas,xlim=None,ylim=None):
        self.make_mat9(xlim,ylim)
        if self._update:
            recorder = skia.PictureRecorder()
            rec = recorder.beginRecording(self.deviceRect)
            rec.save()
            rec.clipRect(self.deviceRect,skia.ClipOp.kIntersect)
            rec.clear(self._background.skia4f)
            self._draw(rec)
            rec.restore()
            # rec.flush()
            self.picture = recorder.finishRecordingAsPicture()
            self.picture = skia.Image.MakeFromPicture(self.picture,skia.ISize.Make(int(self._width),int(self._height)),None,None,skia.Image.BitDepth.kU8,skia.ColorSpace.MakeSRGB())
            self._update &= status.GraphStatus.NONE
        canvas.save()
        canvas.translate(*self._deviceXY)
        if self._devicerotate == status.RotateStatus.FLIP:
            canvas.translate(self.height,0)
        rotate = 0 if (self._devicerotate == status.RotateStatus.NONE) else 90
        canvas.rotate(rotate)
        # canvas.drawPicture(self.picture)
        canvas.drawImage(self.picture,0,0)
        # rec.clipRect(self.clipRect,skia.ClipOp.kIntersect)
        self.grapharea(canvas)
        canvas.restore()
        if self.rubber_rect is not None:
            canvas.drawRect(self.rubber_rect,skia.Paint(Style=skia.Paint.kStroke_Style))

    def _draw_lines(self,canvas,matrix,rect):
        for line in self.lines:
            line.draw(matrix,rect)
            line.flush(canvas)

    def draw_lines(self,canvas):
        canvas.save()
        matrix = skia.Matrix.MakeAll(*self.mat9)
        canvas.clipRect(self.deviceRect)
        self._draw_lines(canvas,matrix,self.deviceRect)
        canvas.restore()

    def _draw_flines(self,canvas):
        for line in self.flines:
            line.draw()
            line.flush(canvas)

    def draw_flines(self,canvas):
        canvas.save()
        matrix = skia.Matrix.MakeAll(*self.mat9)
        canvas.clipRect(self.deviceRect)
        canvas.setMatrix(matrix)
        self._draw_flines(canvas)
        canvas.restore()

    def _draw_images(self,canvas):
        for image in self.images:
            image.draw()
            image.flush(canvas)

    def draw_images(self,canvas):
        canvas.save()
        matrix = skia.Matrix.MakeAll(*self.mat9)
        canvas.clipRect(self.deviceRect)
        canvas.setMatrix(matrix)
        self._draw_images(canvas)
        canvas.restore()

    def _draw_annotation(self,canvas,matrix,rect):
        if self.annotation is not None:
            self.annotation.draw(matrix,rect)
            self.annotation.flush(canvas)

    def draw_annotation(self,canvas):
        canvas.save()
        matrix = skia.Matrix.MakeAll(*self.mat9)
        self._draw_annotation(canvas,matrix,self.deviceRect)

    def flush(self,canvas):
        if self._update != status.GraphStatus.NONE:
            self.draw()
        canvas.drawPicture(self.picture)

    def grapharea(self,canvas):
        paint = skia.Paint(StrokeWidth=0,Color=skia.Color(0,0,0,255),AntiAlias=False,Style=skia.Paint.kStroke_Style)
        # なんで+0.5と-0.5の補正が必要なのかよくわかってない
        # 現状、アンチエイリアスをちゃんと無効にするため
        l,t,r,b = 0.5,0.5,self.width,self.height
        if status.BorderStatus.TOP in self.border:
            canvas.drawLine(l,t,r+0.5,t,paint)
        if status.BorderStatus.RIGHT in self.border:
            canvas.drawLine(r,t,r,b+0.5,paint)
        if status.BorderStatus.BOTTOM in self.border:
            canvas.drawLine(r,b,l-0.5,b,paint)
        if status.BorderStatus.LEFT in self.border:
            canvas.drawLine(l,b,l,t-0.5,paint)

    def line_bounds(self):
        minx,maxx = np.inf,-np.inf
        miny,maxy = np.inf,-np.inf
        xrs = np.array([itm.xrange for itm in self.lines+self.flines]).T
        yrs = np.array([itm.yrange for itm in self.lines+self.flines]).T
        minx,maxx = np.min([minx,*xrs[0]]),np.max([maxx,*xrs[1]])
        miny,maxy = np.min([miny,*yrs[0]]),np.max([maxy,*yrs[1]])
        return ((minx,maxx),(miny,maxy))

    def autorange(self):
        xr,yr = self.line_bounds()
        dx = (xr[1]-xr[0])*0.05
        dy = (yr[1]-yr[0])*0.05
        if dx<=0:
            self.xlim = (0,1)
        else:
            self.xlim = (xr[0]-dx,xr[1]+dx)
        if dy<=0:
            self.ylim = (0,1)
        else:
            self.ylim = (yr[0]-dy,yr[1]+dy)

    @property
    def LTRB(self):
        return (self.left,self.top,self.left+self.width,self.top+self.height)
    @LTRB.setter
    def LTRB(self,value):
        pl,pt,pr,pb = self.LTRB
        if (pl==value[0]) and (pt==value[1]) and (pr==value[2]) and (pb==value[3]):
            return
        self._left = value[0]
        self._top = value[1]
        pw = value[2]-value[0]+1
        ph = value[3]-value[1]+1
        self._width,self._height = (pw,ph) if self._devicerotate != status.RotateStatus.FLIP else (ph,pw)
        se = event.SizeEvent()
        se.LTRB = value
        self._OnSize(se)

    @property
    def LTWH(self):
        return (self.left,self.top,self.width,self.height)
    @LTWH.setter
    def LTWH(self,value):
        pl,pt,pw,ph = self.LTWH
        if (pl==value[0]) and (pt==value[1]) and (pw==value[2]) and (ph==value[3]):
            return
        self._left = value[0]
        self._top = value[1]
        self._width,self._height = (value[2],value[3]) if self._devicerotate != status.RotateStatus.FLIP else (value[3],value[2])
        se = event.SizeEvent()
        se.LTWH = value
        self._OnSize(se)

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self,value):
        self._update |= status.GraphStatus.UPDATE
        if self.parent is not None:
            self.parent.update()
        if self._devicerotate == status.RotateStatus.FLIP:
            self._height = value
        else:
            self._width = value
    @property
    def height(self):
        return self._height
    @height.setter
    def height(self,value):
        self._update |= status.GraphStatus.UPDATE
        if self.parent is not None:
            self.parent.update()
        if self._devicerotate == status.RotateStatus.FLIP:
            self._width = value
        else:
            self._height = value

    @property
    def xlim(self):
        return self._xlim
    @xlim.setter
    def xlim(self,value):
        self._update |= status.GraphStatus.UPDATE
        if self.parent is not None:
            self.parent.update()
        if value[0] == value[1]:
            value = (value[0]-0.5,value[0]+0.5)
        self._xlim = value
        if self.xtick is not None:
            self.xtick.lim = value

    @property
    def ylim(self):
        return self._ylim
    @ylim.setter
    def ylim(self,value):
        self._update |= status.GraphStatus.UPDATE
        if self.parent is not None:
            self.parent.update()
        if value[0] == value[1]:
            value = (value[0]-0.5,value[0]+0.5)
        self._ylim = value
        if self.ytick is not None:
            self.ytick.lim = value

    @property
    def xtick(self):
        return self._xtick
    @xtick.setter
    def xtick(self,value):
        self._xtick = value
        value.ref = self
        value.lim = self.xlim

    @property
    def ytick(self):
        return self._ytick
    @ytick.setter
    def ytick(self,value):
        self._ytick = value
        value.ref = self
        value.lim = self.ylim

    @property
    def border(self):
        return self._border
    @border.setter
    def border(self,value):
        self._border = value

    @property
    def rubber_rect(self):
        return self._rubber_rect
    @rubber_rect.setter
    def rubber_rect(self,value):
        self.deco_update()
        if value is None:
            self._rubber_rect = None
        elif isinstance(value,skia.Rect):
            self._rubber_rect = value
        else:
            self._rubber_rect = skia.Rect(*value)

class Graph(AbstractGraph):

    def _draw(self,recorder):
        self.draw_images(recorder)
        self.draw_lines(recorder)
        self.draw_flines(recorder)
        self.draw_annotation(recorder)

    def append(self,itm):
        if isinstance(itm,item.Line):
            self.lines.append(itm)
        elif isinstance(itm,item.Image):
            self.images.append(itm)
        elif isinstance(itm,item.FLine):
            self.flines.append(itm)
        else:
            raise AttributeError("Line, FLine or Image item only")

class Graph1Image(AbstractGraph):
    def __init__(self,parent,rotate=status.RotateStatus.NONE):
        super().__init__(parent,rotate)
        del self.images
        del self.lines
        self.image = item.Image()
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
        if self.image.data is not None:
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
        self.image.auto_colorrange()

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

class Graph1Line(AbstractGraph):
    def __init__(self,parent,rotate=status.RotateStatus.NONE):
        super().__init__(parent,rotate)
        del self.images
        del self.lines
        self.line = item.Line()

    def _draw(self,recorder):
        self.draw_lines(recorder)

    def _draw_lines(self,canvas,matrix,rect):
        if self.line.data is not None:
            self.line.draw(matrix,rect)
            self.line.flush(canvas)

    @property
    def data(self):
        if self.line.data is not None:
            return self.line.data.T[:,:2]
        return None
    @data.setter
    def data(self,value):
        self.update()
        self.line.set(data=value)

class GraphColorBar(AbstractGraph):
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
                self.ref.set(vmin=self.ref.image.vmin+(x-xx))
            elif self._grab_limit == 2:
                self.ref.set(vmax=self.ref.image.vmax+(x-xx))
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
        # SetCursor(yubi)
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
                    self.ref.set(vmin=self.ref.image.vmin+dx)
                    self.limit_px = pos
                elif self._grab_limit == 2:
                    self.ref.set(vmax=self.ref.image.vmax+dx)
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
                self.ref.set(vmin=x)
            elif self._grab_limit == 2:
                self.ref.set(vmax=x)
            self.update()
            self.ref.update()
        self._capture_mouse = status.MouseStatus.NONE

    def OnMouseDClick(self,evt):
        if self.ref.image.data is not None:
            self.ref.auto_colorrange()
            hist = self.ref.histogram
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

class GraphTick(AbstractGraph):
    def __init__(self,parent,Direction=status.Direction.LtoR):
        #rot = status.RotateStatus.NONE if Direction in [status.Direction.LtoR,status.Direction.RtoL] else status.RotateStatus.FLIP
        super().__init__(parent,status.RotateStatus.NONE)
        del self.images
        del self.lines
        self.tick = item.Ticks()
        self.direction = Direction
        self.font = item.Font(size=12)
        self.paint = skia.Paint(Color=skia.Color(0,0,0),AntiAlias=False,StrokeWidth=1,)
        self.tick_length = 5

    @property
    def dip(self):
        return self._dip
    @dip.setter
    def dip(self,value):
        self._dip = value
        self.font = self.font*self.dip

    @property
    def lim(self):
        return self.tick.minV,self.tick.maxV
    @lim.setter
    def lim(self,value):
        self._update |= status.GraphStatus.UPDATE
        self.tick.set_lim(*value)
        self.xlim = value
        self.ylim = value

    def _draw(self,recorder):
        self.draw_ticks(recorder)

    def draw(self,canvas,xlim=None,ylim=None):
        self.make_mat9(xlim,ylim)
        if self._update:
            recorder = skia.PictureRecorder()
            # w,h = max(100,self.deviceRect.width()),max(100,self.deviceRect.height())
            w,h = self.deviceRect.width(),self.deviceRect.height()
            rec = recorder.beginRecording(w,h)
            rec.save()
            # rec.clipRect(self.clipRect,skia.ClipOp.kIntersect)
            self._draw(rec)
            rec.restore()
            # rec.flush()
            self.picture = recorder.finishRecordingAsPicture()
            self._update &= status.GraphStatus.NONE
        # yflip
        canvas.save()
        canvas.translate(*self._deviceXY)
        if self._devicerotate == status.RotateStatus.FLIP:
            canvas.translate(self.height,0)
        rotate = 0 if (self._devicerotate == status.RotateStatus.NONE) else 90
        canvas.rotate(rotate)
        canvas.drawPicture(self.picture)
        # canvas.drawRect(self.deviceRect,skia.Paint(StrokeWidth=1,Color=skia.Color(0,0,0,255),AntiAlias=False,Style=skia.Paint.kStroke_Style))
        canvas.restore()

    def draw_ticks(self,canvas):
        rot = 0 if self.direction in [status.Direction.LtoR,status.Direction.RtoL] else 1
        l = (self.width,self.height)[rot]
        value,text = self.tick.value_text
        if rot == 0:
            longlongtext = "".join(text)
            tw = self.font.measureText(longlongtext,paint=self.paint)
            skip = 1 if tw < self.width else 2
        else:
            skip = 1 if self.font.getHeight()*len(text)<self.height else 2
        for v,t in zip(value[::skip],text[::skip]):
            pos = self.toDisp(v,v)[rot]-self._deviceXY[rot]
            # pos += 0.5
            s,e = ((pos,0),(pos,self.tick_length)) if (1-rot) else ((self.width-self.tick_length,pos),(self.width,pos))
            canvas.drawLine(*s,*e,self.paint)
            blob = skia.TextBlob.MakeFromString(t,self.font())
            tw = self.font.measureText(t,paint=self.paint)
            tpos = (-0.5*tw+pos,self.tick_length+self.font.getHeight()) if (1-rot) else (self.width-self.tick_length-tw-2,pos+0.5*self.font.getHeight())
            canvas.drawTextBlob(blob,*tpos,self.paint)
        offset = self.tick.offset
        if len(offset):
            blob = skia.TextBlob.MakeFromString(offset,self.font())
            tw = self.font.measureText(offset,paint=self.paint)
            tpos = (-tw+self.width,self.tick_length+2.1*self.font.getHeight()) if (1-rot) else (self.width-tw,-0.2*self.font.getHeight())
            canvas.drawTextBlob(blob,*tpos,self.paint)
