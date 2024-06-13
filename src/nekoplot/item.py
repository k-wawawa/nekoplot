import time
from enum import Flag, auto,Enum
import skia
# from matplotlib.ticker import AutoLocator,ScalarFormatter
import numpy as np

if not "status" in dir():
    from . import status
if not "color" in dir():
    from . import color
if not "utility" in dir():
    from . import utility

BASE_LINE_PAINT = skia.Paint(AntiAlias=True,
                             Style=skia.Paint.Style.kStroke_Style,
                             StrokeJoin=skia.Paint.kRound_Join)#,
                            #  FilterQuality=skia.kMedium_FilterQuality,
                            #  MaskFilter=skia.MaskFilter.MakeBlur(skia.kInner_BlurStyle, 1))
                            #  MaskFilter=skia.MaskFilter.MakeBlur(skia.kSolid_BlurStyle, 0.5))

class LineType(Enum):
    NONE = None
    SOLID = 0
    DASH = skia.DashPathEffect.Make([10.,10.],0.)
    DOT_DASH = skia.DashPathEffect.Make([10.,2.5,2.5,2.5],0.)
    DDOT_DASH = skia.DashPathEffect.Make([10.,2.5,2.5,2.5,2.5,2.5],0.)
    DOT = skia.DashPathEffect.Make([5.,5.],0.)

class MarkerType(Enum):
    NONE = skia.Paint.kButt_Cap
    CIRCLE = skia.Paint.kRound_Cap
    RECT = skia.Paint.kSquare_Cap

class Line:
    def __init__(self):
        self._update = status.LineStatus.NONE
        self._data = None
        self._label = "Line"
        self._linePaint = skia.Paint(BASE_LINE_PAINT)
        self._markerPaint = skia.Paint(Style=skia.Paint.Style.kFill_Style)
        self.linecolor = color.Color(1,0,0,1.0)
        self._linetype = None
        self.linetype = LineType.SOLID.name
        self.linewidth = 2
        self.markercolor = color.Color(0,1.0,0,1)
        self._markertype = None
        self.markertype = MarkerType.NONE.name
        self.markersize = 5.
        self._lpath = skia.Path()
        self.xrange = (np.inf,-np.inf)
        self.yrange = (np.inf,-np.inf)
        self.matrix = skia.Matrix.I()

    def clear(self):
        self._update &= status.LineStatus.NONE
        self._data = None
        self._lpath = skia.Path()
        self.xrange = (np.inf,-np.inf)
        self.yrange = (np.inf,-np.inf)

    @property
    def data(self):
        if self._data is not None:
            return self._data
        return None
    @data.setter
    def data(self,value):
        # input N*2
        if value is None:
            self.xrange = (np.inf,-np.inf)
            self.yrange = (np.inf,-np.inf)
            self._data = None
            self._lpath = skia.Path()
        d = np.array(value,dtype=np.float64).T
        self.xrange = (np.min(d[0]),np.max(d[0]))
        self.yrange = (np.min(d[1]),np.max(d[1]))
        self._data = d
        self._lpath = skia.Path()
        self._lpath.moveTo(*d.T[0])
        for x,y in d.T[1:]:
            self._lpath.lineTo(x,y)
        # self._lpath.close()
        # _dta 3*N

    @property
    def label(self):
        return str(self._label)
    @label.setter
    def label(self,value):
        self._label = value

    def set(self,**dargs):
        if "data" in dargs:
            if dargs["data"] is None:
                self.clear()
            else:
                self._update = status.LineStatus.DATA
                self.data = dargs["data"]
        if "linecolor" in dargs:
            self.linecolor = dargs.get("linecolor",self.linecolor)
        if "linetype" in dargs:
            self.linetype = dargs.get("linetype",self.linetype)
        if "linewidth" in dargs:
            self.linewidth = dargs.get("linewidth",self.linewidth)
        if "markercolor" in dargs:
            self.markercolor = dargs.get("markercolor",self.markercolor)
        if "markertype" in dargs:
            self.markertype = dargs.get("markertype",self.markertype)
        if "markersize" in dargs:
            self.markersize = dargs.get("markersize",self.markersize)

    @property
    def markertype(self):
        return self._markertype
    @markertype.setter
    def markertype(self,value):
        if value in MarkerType._member_names_:
            self._markertype = MarkerType[value]
            self._markerPaint.setStrokeCap(MarkerType[value].value)
        elif value in MarkerType:
            self._markertype = value
            self._markerPaint.setStrokeCap(value.value)
        else:
            raise RuntimeWarning("marker type warning")

    @property
    def markercolor(self):
        return color.Color(*self._markerPaint.getColor4f())
    @markercolor.setter
    def markercolor(self,value):
        if isinstance(value,int):
            self._markerPaint.setColor(value)
        elif isinstance(value,skia.Color4f):
            self._markerPaint.setColor4f(value)
        elif isinstance(value,color.Color):
            self._markerPaint.setColor4f(value.skia4f)
        else:
            raise RuntimeWarning("marker color warning")

    @property
    def markersize(self):
        return self._markerPaint.getStrokeWidth()
    @markersize.setter
    def markersize(self,value):
        if isinstance(value,float):
            self._markerPaint.setStrokeWidth(value)
        else:
            raise RuntimeWarning("marker size warning")

    @property
    def linetype(self):
        return self._linetype
    @linetype.setter
    def linetype(self,value):
        if value in LineType._member_names_:
            if value == "SOLID":
                self._linetype = LineType[value]
                p = skia.Paint(BASE_LINE_PAINT)
                p.setColor4f(self.linecolor.skia4f)
                p.setStrokeWidth(self.linewidth)
                self._linePaint = p
            elif value == "NONE":
                self._linetype = LineType[value]
                p = skia.Paint(BASE_LINE_PAINT)
                p.setColor4f(self.linecolor.skia4f)
                p.setStrokeWidth(self.linewidth)
                self._linePaint = p
            else:
                self._linetype = value
                self._linePaint.setPathEffect(LineType[value].value)
        elif value in LineType:
            if value == LineType.SOLID:
                self._linetype = value
                p = skia.Paint(BASE_LINE_PAINT)
                p.setColor4f(self.linecolor.skia4f)
                p.setStrokeWidth(self.linewidth)
                self._linePaint = p
            elif value == LineType.NONE:
                self._linetype = value
                p = skia.Paint(BASE_LINE_PAINT)
                p.setColor4f(self.linecolor.skia4f)
                p.setStrokeWidth(self.linewidth)
                self._linePaint = p
            else:
                self._linetype = value
                self._linePaint.setPathEffect(value.value)
        else:
            raise RuntimeWarning("line type warning")

    @property
    def linecolor(self):
        return color.Color(*self._linePaint.getColor4f())
    @linecolor.setter
    def linecolor(self,value):
        if isinstance(value,int):
            self._linePaint.setColor(value)
        elif isinstance(value,skia.Color4f):
            self._linePaint.setColor4f(value)
        elif isinstance(value,color.Color):
            self._linePaint.setColor4f(value.skia4f)
        else:
            raise RuntimeWarning("line color warning")

    @property
    def linewidth(self):
        return self._linePaint.getStrokeWidth()
    @linewidth.setter
    def linewidth(self,value):
        if isinstance(value,(float,int)):
            self._linePaint.setStrokeWidth(value)
        else:
            raise RuntimeWarning("line size warning")

    def draw(self,matrix,rect=None):
        # lineとかmarkerとか書くやつ
        if self._update == status.LineStatus.NONE and matrix == self.matrix:
            return
        if self._data is None:
            self._lpath = skia.Path()
            self._aff_data = skia.Path()
        self._aff_data = skia.Path()
        self._lpath.transform(matrix,self._aff_data)
        self.matrix = matrix
        self._update &= status.LineStatus.NONE

    def flush(self,canvas):
        # canvas にぶち込む
        if self.linetype != LineType.NONE:
            canvas.drawPath(self._aff_data,self._linePaint)
        if self.markertype != MarkerType.NONE:
            canvas.drawPoints(skia.Canvas.kPoints_PointMode,self._aff_data.getPoints(),self._markerPaint)

class FLine():
    def __init__(self):
        self._update = status.LineStatus.NONE
        self._data = None
        self._label = "Line"
        self._linePaint = skia.Paint(Style=skia.Paint.Style.kStroke_Style,StrokeWidth=0)
        self.linecolor = skia.Color4f(1,0,0,1.0)
        self._linetype = LineType.NONE
        self.linetype = LineType.SOLID.name
        self._lpath = skia.Path()
        self.xrange = (np.inf,-np.inf)
        self.yrange = (np.inf,-np.inf)

    def clear(self):
        self._update &= status.LineStatus.NONE
        self._data = None
        self._lpath = skia.Path()
        self.xrange = (np.inf,-np.inf)
        self.yrange = (np.inf,-np.inf)

    @property
    def data(self):
        if self._data is not None:
            return self._data
        return None
    @data.setter
    def data(self,value):
        # input N*2
        if value is None:
            self.xrange = (np.inf,-np.inf)
            self.yrange = (np.inf,-np.inf)
            self._data = None
            self._lpath = skia.Path()
        d = np.array(value,dtype=np.float64).T
        self.xrange = (np.min(d[0]),np.max(d[0]))
        self.yrange = (np.min(d[1]),np.max(d[1]))
        self._data = d
        self._lpath = skia.Path()
        self._lpath.moveTo(*value[0])
        for x,y in value[1:]:
            self._lpath.lineTo(x,y)

    @property
    def label(self):
        return str(self._label)
    @label.setter
    def label(self,value):
        self._label = value

    def set(self,**dargs):
        if "data" in dargs:
            if dargs["data"] is None:
                self.clear()
            else:
                self._update = status.LineStatus.DATA
                self.data = dargs["data"]
        if "linecolor" in dargs:
            self.linecolor = dargs.get("linecolor",self.linecolor)
        if "linetype" in dargs:
            self.linetype = dargs.get("linetype",self.linetype)

    @property
    def linetype(self):
        return self._linetype
    @linetype.setter
    def linetype(self,value):
        if value in LineType._member_names_:
            if value == "SOLID":
                self._linetype = LineType[value]
                p = skia.Paint(Style=skia.Paint.Style.kStroke_Style,StrokeWidth=0)
                p.setColor4f(self.linecolor.skia4f)
                self._linePaint = p
            elif value == "NONE":
                self._linetype = LineType[value]
                p = skia.Paint(Style=skia.Paint.Style.kStroke_Style,StrokeWidth=0)
                p.setColor4f(self.linecolor.skia4f)
                self._linePaint = p
            else:
                self._linetype = LineType[value]
                self._linePaint.setPathEffect(LineType[value].value)
        elif value in LineType:
            if value == LineType.SOLID:
                self._linetype = value
                p = skia.Paint(Style=skia.Paint.Style.kStroke_Style,StrokeWidth=0)
                p.setColor4f(self.linecolor.skia4f)
                self._linePaint = p
            elif value == LineType.NONE:
                self._linetype = LineType[value]
                p = skia.Paint(Style=skia.Paint.Style.kStroke_Style,StrokeWidth=0)
                p.setColor4f(self.linecolor.skia4f)
                self._linePaint = p
            else:
                self._linePaint.setPathEffect(value.value)
        else:
            raise RuntimeWarning("line type warning")

    @property
    def linecolor(self):
        return color.Color(*self._linePaint.getColor4f())
    @linecolor.setter
    def linecolor(self,value):
        if isinstance(value,int):
            self._linePaint.setColor(value)
        elif isinstance(value,skia.Color4f):
            self._linePaint.setColor4f(value)
        elif isinstance(value,color.Color):
            self._linePaint.setColor4f(value.skia4f)
        else:
            raise RuntimeWarning("line color warning")

    def draw(self):
        self._update &= status.LineStatus.NONE

    def flush(self,canvas):
        # canvas にぶち込む
        paint = skia.Paint(self._linePaint)
        if self.linetype != LineType.NONE:
            canvas.drawPath(self._lpath,paint)

class Image():
    def __init__(self):
        self._update = status.ImageStatus.NONE
        self.data = None
        self.vmin = 0
        self.vmax = 1
        self.auto_left = 25
        self.auto_right = 75
        self.colormap = "parula"
        self.img = None
        self._colorbar = None

    def clear(self):
        self._update &= status.ImageStatus.NONE
        self.data = None
        self.img = None

    def set(self,**dargs):
        if "data" in dargs:
            if dargs["data"] is None:
                self.clear()
            else:
                self._update |= status.ImageStatus.DATA
                self.data = np.array(dargs["data"])
        if {"vmin","vmax","colormap"} & set(dargs.keys()):
            self._update |= status.ImageStatus.VALUE
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

    def make_histogram(self):
        if self.data is None:
            self._histogram = None
        imgmax = int(np.max(self.data))
        bins = imgmax + 1
        self._histogram = np.histogram(self.data,bins=bins,range=(0,bins))[0]
        if self.colorbar is not None:
            self.colorbar._update |= status.GraphStatus.FROM_DATA
        return self._histogram

    def auto_colorrange(self,left=None,right=None):
        if self.data is None:
            self.set(vmin=0,vmax=1)
            return
        self.auto_left = left if left is not None else self.auto_left
        self.auto_right = right if right is not None else self.auto_right
        qleft,qright = np.percentile(self.data,[self.auto_left,self.auto_right])
        self.set(vmin=qleft,vmax=qright)

    def draw(self):
        if (self._update == status.ImageStatus.NONE) or (self.data is None):
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

    def flush(self,canvas):
        canvas.drawImage(self.img,0,0)

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

class Matrix():
    pass

class Fonts():
    segoe = skia.Typeface.MakeFromName("Segoe UI")
    arial = skia.Typeface.MakeFromName("Arial")
    yu = skia.Typeface.MakeFromName("Yu Gothic UI")
    meiryo = skia.Typeface.MakeFromName("Meiryo UI")

class Font():
    def __init__(self,typeface=None,size=None):
        self._typeface = Fonts.yu if typeface is None else typeface
        self._size = 20 if size is None else size

    def size(self,sz=20):
        return Font(self._typeface,sz)

    def typeface(self,typeface):
        return Font(typeface,self._size)

    def __call__(self):
        return skia.Font(self._typeface,self._size)

    def __mul__(self,ratio):
        return Font(self._typeface,self._size*ratio)

    def measureText(self,string,*args,**dargs):
        return self().measureText(string,*args,**dargs)

    def getSize(self):
        return self._size

    def getHeight(self):
        return self().getMetrics().fCapHeight

class Ticks():
    def __init__(self,maxN=11):
        self.minV = None
        self.maxV = None
        self.maxN = maxN
        self.divs = [2,1,0.5,0.2,0.1,0.05]
        self._values = None
        self.step = None
        self._offset = None
        self._scale = 1
        self._translate = 0
        self.raw_range = (-3,3)
        self.format_translate = True
        self.format_scale = True
        # 未実装
        # self.scale_function = lambda x:x

    def set_lim(self,minV,maxV):
        self.minV = minV
        self.maxV = maxV
        d = self.maxV - self.minV
        ord = np.floor(np.log10(d))+1
        step = None
        ord10 = 10.**(ord-1)
        for i in range(1,len(self.divs)):
            a = d/(self.divs[i]*ord10)
            if a > self.maxN:
                step = self.divs[i-1]
                break
        if step is None:
            raise RuntimeError("select step error")
        ftick = np.ceil(self.minV/(step*ord10))
        self.step = step
        self._values = list()
        i = 0
        while True:
            v = (ftick + i)*step*ord10
            if v > self.maxV:
                break
            self._values.append(v)
            i += 1
        self._values = np.array(self._values)

    def value_format(self):
        if self._values is not None:
            ord = int(np.floor(np.log10(np.max(np.abs([self.minV,self.maxV]))))+1)
            dord = int(np.floor(np.log10(self.maxV-self.minV))+1)
            ord10 = 10.**(ord-1)
            dord10 = 10.**(dord-1)
            v_i = self.values.copy()
            self._offset = ""
            if (ord-dord>3) and self.format_translate:
                q = int((10.+0.5*self.step)//self.step)
                p = int(np.ceil(np.min(np.abs([self.minV,self.maxV]))/(self.step*dord10)))
                p = int(p//q)
                offset = (1 if self._values[0] > 0 else -1)*p*q*self.step*dord10
                v_i -= offset
                self._offset += f"{'+' if self._values[0] > 0 else '-'}{abs(offset):1.10g}"
                ord = int(np.floor(np.log10(v_i[-1]-v_i[0]))+1)
                ord10 = 10.**(ord-1)
                v_i /= ord10
                self._offset = f"*10^{ord-1:d}" + self._offset
                return np.array([f"{(round(v,3)):1.10g}" for v in v_i])
            else:
                if (self.raw_range[0]+1 <= ord <= self.raw_range[1]+1) or (not self.format_scale):
                    return np.array([f"{v:1.10g}" for v in v_i])
                else:
                    self._offset = f"*10^{ord-1:d}" + self._offset
                    return np.array([f"{v:1.10g}" for v in v_i/ord10])
        else:
            raise RuntimeError("set Tick value")

    @property
    def texts(self):
        if self._values is not None:
            return self.value_format()
        else:
            raise RuntimeError("set Tick value")

    @property
    def values(self):
        if self._values is not None:
            return self._values
        else:
            raise RuntimeError("set Tick value")

    @property
    def value_text(self):
        if self._values is not None:
            vs = self.values
            ts = self.value_format()
            return vs,ts
        else:
            raise RuntimeError("set Tick value")

    @property
    def offset(self):
        if self._values is not None:
            self.value_format()
            if self._offset is not None:
                return self._offset
            else:
                return ""
        else:
            raise RuntimeError("set Tick value")

class Annotation():
    def __init__(self):
        self._update = status.Status.NONE
        self._point_to = (0,0)
        self._arrow_length = 10
        self._text = ""
        self._bg_color = color.ColorList["white"]
        self._border_color = color.ColorList["black"]
        self._color = color.ColorList["black"]
        self._font = Font(size=15)
        self._visible = False
        self._matrix = skia.Matrix.I()
        self._arrow_line = None # path
        self._textbox = None # rect
        self._blob = None # blob
        self._textpaint = skia.Paint(AntiAlias=True,Color=self._color.skia4f)
        self._borderpaint = skia.Paint(AntiAlias=True,Style=skia.Paint.Style.kStroke_Style,Color=self._border_color.skia4f)
        self._bgpaint = skia.Paint(AntiAlias=True,Style=skia.Paint.Style.kFill_Style,Color=self._bg_color.skia4f)

    def set(self,**dargs):
        if "point_to" in dargs:
            self._update = status.Status.VALUE
            self._point_to = dargs["point_to"]
        if "arrow_length" in dargs:
            self._update = status.Status.VALUE
            self._arrow_length = dargs["arrow_length"]
        if "text" in dargs:
            self._update = status.Status.VALUE
            self._text = dargs["text"]
        if "bg_color" in dargs:
            self._update = status.Status.VALUE
            self._bgpaint.setColor4f(dargs["bg_color"].skia4f)
        if "border_color" in dargs:
            self._update = status.Status.VALUE
            self._borderpaint.setColor4f(dargs["border_color"].skia4f)
        if "color" in dargs:
            self._update = status.Status.VALUE
            self._textpaint.setColor4f(dargs["color"].skia4f)
        if "visible" in dargs:
            self._update = status.Status.VALUE
            self._visible = dargs["visible"]
        if "font" in dargs:
            self._update = status.Status.VALUE
            self._font = dargs["font"]

    def draw(self,matrix,rect=None):
        # lineとかmarkerとか書くやつ
        if self._update == status.Status.NONE and matrix == self._matrix:
            return
        x,y = self._point_to
        x,y = matrix.mapXY(*self._point_to)
        if x == np.inf:
            x = rect.width()
        elif x == -np.inf:
            x = 0
        if y == np.inf:
            y = rect.height()
        elif y == -np.inf:
            y = 0
        signX = 1 if x < (rect.x() + 0.5*rect.width()) else -1
        signY = 1 if y < (rect.y() + 0.5*rect.height()) else -1
        blob = skia.TextBlob.MakeFromString(self._text,self._font())
        tw = self._font.measureText(self._text,paint=self._textpaint)+self._font.getHeight()*0.5
        th = self._font.getHeight()*1.5
        self._arrow_line = skia.Path()
        self._arrow_line.moveTo(x,y)
        self._arrow_line.lineTo(x+signX*self._arrow_length,y+signY*self._arrow_length)
        l,r = (x+signX*self._arrow_length,x+signX*self._arrow_length+tw) if signX>0 else (x+signX*self._arrow_length-tw,x+signX*self._arrow_length)
        t,b = (y+signY*self._arrow_length,y+signY*self._arrow_length+th) if signY>0 else (y+signY*self._arrow_length-th,y+signY*self._arrow_length)
        self._textbox = skia.Rect.MakeLTRB(l,t,r,b)
        self._blob = blob
        self._matrix = matrix
        self._update &= status.Status.NONE

    def flush(self,canvas):
        # canvas にぶち込む
        if self._visible:
            canvas.drawPath(self._arrow_line,self._borderpaint)
            canvas.drawRect(self._textbox,self._bgpaint)
            canvas.drawRect(self._textbox,self._borderpaint)
            canvas.drawTextBlob(self._blob,self._textbox.x()+self._font.getHeight()*0.25,self._textbox.y()+self._font.getHeight()*1.25,self._textpaint)
