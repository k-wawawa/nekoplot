import time
from enum import Flag, auto,Enum
import skia
import numpy as np

from . import status
from . import color
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
        self._update = status.LineStatus.NONE
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
        # input N*2 [[x1,y1],[x2,y2],...]
        if value is None:
            self.xrange = (np.inf,-np.inf)
            self.yrange = (np.inf,-np.inf)
            self._data = None
            self._lpath = skia.Path()
            return
        d = np.array(value,dtype=np.float64).T
        self.xrange = (np.min(d[0]),np.max(d[0]))
        self.yrange = (np.min(d[1]),np.max(d[1]))
        self._data = d
        self._lpath = skia.Path()
        self._lpath.moveTo(*d.T[0])
        for x,y in d.T[1:]:
            self._lpath.lineTo(x,y)
        self._update = status.LineStatus.DATA
        # self._lpath.close()

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
        # ここがおかしい？？？？？？mat==self.matのはんてい
        if self._update == status.LineStatus.NONE and (tuple(matrix.get9()) == tuple(self.matrix.get9())):
            return
        if self._data is None:
            self._lpath = skia.Path()
            self._aff_data = skia.Path()
            self._update = status.LineStatus.NONE
            return
        self._aff_data = skia.Path()
        self._lpath.transform(matrix,self._aff_data)
        self.matrix = matrix
        self._update = status.LineStatus.NONE

    def flush(self,canvas):
        # canvas にぶち込む
        if self.linetype != LineType.NONE:
            canvas.drawPath(self._aff_data,self._linePaint)
        if self.markertype != MarkerType.NONE:
            canvas.drawPoints(skia.Canvas.kPoints_PointMode,self._aff_data.getPoints(),self._markerPaint)

class LineV2(Line):
    def __init__(self):
        super().__init__()
        self._scaled_data = None
        self._xscale = lambda x:x
        self._yscale = lambda x:x

    def clear(self):
        super().clear()
        self._scaled_data = None

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
            self._scaled_data = None
            self._lpath = skia.Path()
            return
        d = np.array(value,dtype=np.float64).T
        self._data = d
        sd = np.array([self._xscale(d[0]),self._yscale(d[1])])
        self._scaled_data = sd
        self.xrange = (np.min(sd[0][np.isfinite(sd[0])]),np.max(sd[0][np.isfinite(sd[0])]))
        self.yrange = (np.min(sd[1][np.isfinite(sd[1])]),np.max(sd[1][np.isfinite(sd[1])]))
        self._lpath = skia.Path()
        if self.data is not None:
                sd = np.array([self._xscale(self.data[0]),self._yscale(self.data[1])])
                self._scaled_data = sd
                finite = np.all(np.isfinite(sd),axis=0)
                self.xrange = (np.min(sd[0][finite]),np.max(sd[0][finite]))
                self.yrange = (np.min(sd[1][finite]),np.max(sd[1][finite]))
                self._lpath = skia.Path()
                connect = False
                for x,y,ok in np.vstack([sd,finite]).T:
                    if connect and ok:
                        self._lpath.lineTo(x,y)
                    elif (not connect) and ok:
                        self._lpath.moveTo(x,y)
                        self._lpath.lineTo(x,y)
                        connect = True
                    elif connect and (not ok):
                        connect = False
                    else:
                        pass
        self._update = status.LineStatus.DATA
        # self._lpath.close()
        # _dta 3*N

    def set(self,**dargs):
        if "data" in dargs:
            if dargs["data"] is None:
                self.clear()
            else:
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
        if "xscale" in dargs:
            self.xscale = dargs.get("xscale",self.xscale)
        if "yscale" in dargs:
            self.yscale = dargs.get("yscale",self.yscale)

    @property
    def xscale(self):
        return self._xscale
    @xscale.setter
    def xscale(self,value):
        if callable(value):
            self._xscale = value
            if self.data is not None:
                sd = np.array([self._xscale(self.data[0]),self._yscale(self.data[1])])
                self._scaled_data = sd
                finite = np.all(np.isfinite(sd),axis=0)
                self.xrange = (np.min(sd[0][finite]),np.max(sd[0][finite]))
                self.yrange = (np.min(sd[1][finite]),np.max(sd[1][finite]))
                self._lpath = skia.Path()
                connect = False
                for x,y,ok in np.vstack([sd,finite]).T:
                    if connect and ok:
                        self._lpath.lineTo(x,y)
                    elif (not connect) and ok:
                        self._lpath.moveTo(x,y)
                        self._lpath.lineTo(x,y)
                        connect = True
                    elif connect and (not ok):
                        connect = False
                    else:
                        pass
                self._update = status.LineStatus.DATA
        else:
            raise RuntimeWarning("numpy array callable only")

    @property
    def yscale(self):
        return self._yscale
    @yscale.setter
    def yscale(self,value):
        if callable(value):
            self._yscale = value
            if self.data is not None:
                sd = np.array([self._xscale(self.data[0]),self._yscale(self.data[1])])
                self._scaled_data = sd
                finite = np.all(np.isfinite(sd),axis=0)
                self.xrange = (np.min(sd[0][finite]),np.max(sd[0][finite]))
                self.yrange = (np.min(sd[1][finite]),np.max(sd[1][finite]))
                self._lpath = skia.Path()
                connect = False
                for x,y,ok in np.vstack([sd,finite]).T:
                    if connect and ok:
                        self._lpath.lineTo(x,y)
                    elif (not connect) and ok:
                        self._lpath.moveTo(x,y)
                        self._lpath.lineTo(x,y)
                        connect = True
                    elif connect and (not ok):
                        connect = False
                    else:
                        pass
                self._update = status.LineStatus.DATA
        else:
            raise RuntimeWarning("numpy array callable only")

    @property
    def xyscale(self):
        return (self.xscale,self.yscale)
    @xyscale.setter
    def xyscale(self,value):
        if callable(value[0]) and callable(value[1]):
            self._xscale = value[0]
            self._yscale = value[1]
            if self.data is not None:
                sd = np.array([self._xscale(self.data[0]),self._yscale(self.data[1])])
                self._scaled_data = sd
                finite = np.all(np.isfinite(sd),axis=0)
                self.xrange = (np.min(sd[0][finite]),np.max(sd[0][finite]))
                self.yrange = (np.min(sd[1][finite]),np.max(sd[1][finite]))
                self._lpath = skia.Path()
                connect = False
                for x,y,ok in np.vstack([sd,finite]).T:
                    if connect and ok:
                        self._lpath.lineTo(x,y)
                    elif (not connect) and ok:
                        self._lpath.moveTo(x,y)
                        self._lpath.lineTo(x,y)
                        connect = True
                    elif connect and (not ok):
                        connect = False
                    else:
                        pass
                self._update = status.LineStatus.DATA
        else:
            raise RuntimeWarning("2-Tuple of numpy array callable only")

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
            return
        d = np.array(value,dtype=np.float64).T
        self.xrange = (np.min(d[0]),np.max(d[0]))
        self.yrange = (np.min(d[1]),np.max(d[1]))
        self._data = d
        self._lpath = skia.Path()
        self._lpath.moveTo(*value[0])
        for x,y in value[1:]:
            self._lpath.lineTo(x,y)
        self._update = status.LineStatus.DATA

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
        self._update = status.LineStatus.NONE

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
                self.data = np.array(dargs.pop("data"))
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
            return self._histogram
        if np.issubdtype(self.data.dtype,np.integer):
            arr = self.data
            vmin,vmax = np.min(arr),np.max(arr)
            bins = int(vmax - vmin +1)
            r = (vmin-0.5,vmax+0.5)
        elif np.issubdtype(self.data.dtype,np.floating):
            arr = self.data[np.isfinite(self.data)]
            bins = "auto"
            r = (np.min(arr),np.max(arr))
        else:
            raise RuntimeWarning("only integer or float")
        counts,edges = np.histogram(arr,bins=bins,range=r)
        self._histogram = np.array([(edges[:-1]+edges[1:])*0.5,counts])
        if self.colorbar is not None:
            self.colorbar._update |= status.GraphStatus.FROM_DATA
        return self._histogram

    def auto_colorrange(self,left=None,right=None):
        if self.data is None:
            self.set(vmin=0,vmax=1)
            return
        self.auto_left = left if left is not None else self.auto_left
        self.auto_right = right if right is not None else self.auto_right
        qleft,qright = np.percentile(self.data[np.isfinite(self.data)],[self.auto_left,self.auto_right])
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
            d = 255./(self.vmax-self.vmin)
            tmp[np.isnan(tmp)] = self.vmin
            small = tmp<self.vmin
            large = tmp>self.vmax
            tmp[small] = self.vmin
            tmp[large] = self.vmax
            tmp -= self.vmin
            tmp *= d
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

class ImageV2(Image):
    def __init__(self):
        super().__init__()
        self._vscale = lambda x:x
        self._scaled_data = None

    def clear(self):
        super().clear()
        self._scaled_data = None

    def set(self,**dargs):
        if "data" in dargs:
            if dargs["data"] is None:
                self.clear()
            else:
                self._update |= status.ImageStatus.DATA
                self.data = np.array(dargs.pop("data"))
                self._scaled_data = self.vscale(self.data.astype(np.float32))
        if {"vmin","vmax","vscale","colormap"} & set(dargs.keys()):
            self._update |= status.ImageStatus.VALUE
        if "vmin" in dargs:
            self.vmin = dargs.get("vmin",self.vmin)
        if "vmax" in dargs:
            self.vmax = dargs.get("vmax",self.vmax)
        if self.vmin >= self.vmax:
            self.vmax = self.vmin
        if "vscale" in dargs:
            self.vscale = dargs.get("vscale",self.vscale)
        if "colormap" in dargs:
            self.colormap = dargs.get("colormap")
            if self.colorbar is not None:
                self.colorbar._update |= status.GraphStatus.UPDATE
        if len(dargs)>0:
            if self.colorbar is not None:
                self.colorbar.image.set(**dargs)

    def auto_colorrange(self,left=None,right=None):
        if self.data is None:
            self.set(vmin=1,vmax=1)
            return
        self.auto_left = left if left is not None else self.auto_left
        self.auto_right = right if right is not None else self.auto_right
        qleft,qright = np.percentile(self.data,[self.auto_left,self.auto_right])
        self.set(vmin=qleft,vmax=qright)

    def draw(self):
        if (self._update == status.ImageStatus.NONE) or (self.data is None):
            return
        # Apply color map
        tmp = self._scaled_data.copy()
        vmin,vmax = self.vscale(self.vmin),self.vscale(self.vmax)
        if vmin==vmax:
            tmp[np.isnan(tmp)] = vmin
            small = tmp<=vmin
            large = tmp>vmax
            tmp[small] = 0
            tmp[large] = 255
        else:
            d = 255./(vmax-vmin)
            tmp[np.isnan(tmp)] = vmin
            small = tmp<vmin
            large = tmp>vmax
            tmp[small] = vmin
            tmp[large] = vmax
            tmp -= vmin
            tmp *= d
        tmp = self.colormap.apply(tmp).copy()
        self.img = skia.Image.fromarray(tmp,skia.ColorType.kRGBA_8888_ColorType)
        self._update &= status.ImageStatus.NONE

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
