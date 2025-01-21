
import numpy as np
import wx
from wx import glcanvas
import skia

from nekoplot import color as skcolor
from nekoplot import item as skitem
from nekoplot import status as skstatus
from nekoplot import event as skevent
from nekoplot import panel as skpanel
from nekoplot import layout as sklayout
from nekoplot import graph as skgraph
from nekoplot import control as skcontrol
from nekoplot import layer as sklayer

class SimplePlot(skpanel.Panel):
    def __init__(self,parent=None,statusbar=None,*args,**dargs):
        super().__init__(parent,*args,**dargs)
        self.layout = sklayout.GridLayout()
        self.layout.addColumn(sklayout.LayoutSize(0,20))
        self.layout.addColumn(sklayout.LayoutSize(0,40))
        self.layout.addColumn(sklayout.LayoutSize(1,0))
        self.layout.addColumn(sklayout.LayoutSize(0,20))
        self.layout.addRow(sklayout.LayoutSize(0,40))
        self.layout.addRow(sklayout.LayoutSize(1,0))
        self.layout.addRow(sklayout.LayoutSize(0,40))
        self.filename = skcontrol.TextBox(self)
        self.filename.text = ""
        self.filename.font = self.filename.font.size(12)
        self.filename.position = (skstatus.PositionStatus.MM,skstatus.PositionStatus.MM)
        self.MainArea = skgraph.Graph(self)
        self.MainArea._flipy = True
        self.MainArea.Bind(skevent.Type.MOUSE_WHEEL,lambda s,e:self.MainAreaOnWheel(e))
        self.MainArea.Bind(skevent.Type.MOUSE_L_DOWN,lambda s,x:self.MainAreaOnLDown(x))
        self.MainArea.Bind(skevent.Type.MOUSE_L_UP,lambda s,x:self.MainAreaOnLUp(x))
        self.MainArea.Bind(skevent.Type.MOUSE_MOTION,lambda s,x:self.MainAreaOnMotion(x))
        self.MainArea.Bind(skevent.Type.MOUSE_L_DCLICK,lambda s,x:self.MainAreaOnLDClick(x))
        self.MainArea.Bind(skevent.Type.MOUSE_R_DOWN,lambda s,x:self.MainAreaOnRDown(x))
        self.MainArea.Bind(skevent.Type.MOUSE_R_UP,lambda s,x:self.MainAreaOnRUp(x))
        self.MainArea.Bind(skevent.Type.MOUSE_R_DCLICK,lambda s,x:self.MainAreaOnRDClick(x))
        self.mainXTick = skgraph.GraphTick(self,skstatus.Direction.LtoR)
        self.MainArea.xtick = self.mainXTick
        self.mainYTick = skgraph.GraphTick(self,skstatus.Direction.DtoU)
        self.mainYTick.flipy = skstatus.Direction.DtoU
        self.MainArea.ytick = self.mainYTick

        self.layout.add(self.filename,1,1,2,1)
        self.layout.add(self.MainArea,2,1,1,1)
        self.layout.add(self.mainXTick,2,2,1,1)
        self.layout.add(self.mainYTick,1,1,1,1)

        self._xlim = (0,1)
        self._ylim = (0,1)
        self.statusbar = statusbar


    def MainAreaOnWheel(self, evt):
        bairitsu = 0.15
        if evt.GetWheelRotation() > 0:
            scale = 1-bairitsu
        else:
            scale = 1+bairitsu
        vl,vr = self.MainArea.xlim
        vb,vt = self.MainArea.ylim
        vx,vy = self.MainArea.toData(*evt.GetPosition())
        if (vx-scale*(vx-vl) >= vx+scale*(vr-vx)) or (vy-scale*(vy-vb) >= vy+scale*(vt-vy)):
            return
        self.MainArea.xlim = (vx-scale*(vx-vl) , vx+scale*(vr-vx))
        self.MainArea.ylim = (vy-scale*(vy-vb) , vy+scale*(vt-vy))
        self.update()

    def MainAreaOnLDown(self,evt):
        self.MainArea._capture_mouse |= skstatus.MouseStatus.LEFT
        self.MainArea.px,self.MainArea.py = evt.GetPosition()

    def MainAreaOnLUp(self,evt):
        if skstatus.MouseStatus.LEFT in self.MainArea._capture_mouse:
            self.MainArea._capture_mouse ^= skstatus.MouseStatus.LEFT

    def MainAreaOnLDClick(self,evt):
        self.MainArea.autorange()
        self.update()

    def MainAreaOnRDown(self,evt):
        self.MainArea._capture_mouse |= skstatus.MouseStatus.RIGHT
        self.MainArea.px,self.MainArea.py = evt.GetPosition()

    def MainAreaOnRUp(self,evt):
        if skstatus.MouseStatus.RIGHT in self.MainArea._capture_mouse:
            self.MainArea._capture_mouse ^= skstatus.MouseStatus.RIGHT
            px,py = self.MainArea.toData(self.MainArea.px,self.MainArea.py)
            x,y = self.MainArea.toData(*evt.GetPosition())
            if px==x and py==y:
                self.MainArea.rubber_rect = None
                self.MainArea.update()
                self.wx.draw()
                self.wx.Refresh()
                return
            startx,endx = min(px,x),max(px,x)
            starty,endy = min(py,y),max(py,y)
            self.MainArea.xlim = (startx , endx)
            self.MainArea.ylim = (starty , endy)
            self.MainArea.rubber_rect = None
            self.update()

    def MainAreaOnRDClick(self,evt):
        self.MainAreaOnLDClick(evt)

    def MainAreaOnMotion(self,evt):
        if self.statusbar is not None:
            x,y = self.MainArea.toData(*evt.GetPosition())
            self.statusbar.SetStatusText(f"({x:.5g},{y:.5g})")
        if skstatus.MouseStatus.LEFT in self.MainArea._capture_mouse:
            px,py = self.MainArea.toData(self.MainArea.px,self.MainArea.py)
            x,y = self.MainArea.toData(*evt.GetPosition())
            self.MainArea.xlim = (self.MainArea.xlim[0]-x+px , self.MainArea.xlim[1]-x+px)
            self.MainArea.ylim = (self.MainArea.ylim[0]-y+py , self.MainArea.ylim[1]-y+py)
            self.MainArea.px,self.MainArea.py = evt.GetPosition()
        elif skstatus.MouseStatus.RIGHT in self.MainArea._capture_mouse:
            px,py = self.MainArea.px,self.MainArea.py
            x,y = evt.GetPosition()
            startx,endx = min(int(px),int(x)),max(int(px),int(x))
            starty,endy = min(int(py),int(y)),max(int(py),int(y))
            if starty == endy:
                return
            if startx == endx:
                return
            startx,starty = self.MainArea.toData(startx,starty)
            endx,endy = self.MainArea.toData(endx,endy)
            self.MainArea.rubber_rect = (startx,starty,endx,endy)
        self.update()

    def MainAreaOnLeave(self,evt):
        self.MainArea._capture_mouse = skstatus.MouseStatus.NONE

class SimpleImagePlot(skpanel.Panel):
    def __init__(self,parent=None,statusbar=None,*args,**dargs):
        super().__init__(parent,*args,**dargs)
        self.layout = sklayout.GridLayout()
        self.layout.addColumn(sklayout.LayoutSize(0,50)) # メモリ
        self.layout.addColumn(sklayout.LayoutSize(1,0)) # メイン
        self.layout.addColumn(sklayout.LayoutSize(0,10)) # 隙間
        self.layout.addColumn(sklayout.LayoutSize(0,50)) # メモリ
        self.layout.addColumn(sklayout.LayoutSize(0,75)) # カラーバー
        self.layout.addColumn(sklayout.LayoutSize(0,20)) # マージン

        self.layout.addRow(sklayout.LayoutSize(0,40))
        self.layout.addRow(sklayout.LayoutSize(1,0))
        self.layout.addRow(sklayout.LayoutSize(0,40))
        self.filename = skcontrol.TextBox(self)
        self.filename.text = ""
        self.filename.font = self.filename.font.size(12)
        self.filename.position = (skstatus.PositionStatus.MM,skstatus.PositionStatus.MM)
        self.MainArea = skgraph.Graph1Image(self)
        self.MainArea._flipy = True
        self.MainArea.Bind(skevent.Type.MOUSE_WHEEL,lambda s,e:self.MainAreaOnWheel(e))
        self.MainArea.Bind(skevent.Type.MOUSE_L_DOWN,lambda s,x:self.MainAreaOnLDown(x))
        self.MainArea.Bind(skevent.Type.MOUSE_L_UP,lambda s,x:self.MainAreaOnLUp(x))
        self.MainArea.Bind(skevent.Type.MOUSE_MOTION,lambda s,x:self.MainAreaOnMotion(x))
        self.MainArea.Bind(skevent.Type.MOUSE_L_DCLICK,lambda s,x:self.MainAreaOnLDClick(x))
        self.MainArea.Bind(skevent.Type.MOUSE_R_DOWN,lambda s,x:self.MainAreaOnRDown(x))
        self.MainArea.Bind(skevent.Type.MOUSE_R_UP,lambda s,x:self.MainAreaOnRUp(x))
        self.MainArea.Bind(skevent.Type.MOUSE_R_DCLICK,lambda s,x:self.MainAreaOnRDClick(x))
        self.mainXTick = skgraph.GraphTick(self,skstatus.Direction.LtoR)
        self.MainArea.xtick = self.mainXTick
        self.mainYTick = skgraph.GraphTick(self,skstatus.Direction.DtoU)
        self.mainYTick.flipy = skstatus.Direction.DtoU
        self.MainArea.ytick = self.mainYTick

        self.ColorBar = skgraph.GraphColorBar(self, rotate=skstatus.RotateStatus.FLIP)
        self.ColorBar.flipx = skstatus.Direction.RtoL
        self.ColorBar.flipy = skstatus.Direction.DtoU
        self.MainArea.colorbar = self.ColorBar
        self.CBXTick = skgraph.GraphTick(self,skstatus.Direction.DtoU)
        self.CBXTick.flipx = skstatus.Direction.RtoL
        self.CBXTick.flipy = skstatus.Direction.DtoU
        self.ColorBar.xtick = self.CBXTick

        self.layout.add(self.filename,1,1,2,1)
        self.layout.add(self.MainArea,1,1,1,1)
        self.layout.add(self.mainXTick,1,2,1,1)
        self.layout.add(self.mainYTick,0,1,1,1)
        self.layout.add(self.ColorBar,4,1,1,1)
        self.layout.add(self.CBXTick,3,1,1,1)

        self._xlim = (0,1)
        self._ylim = (0,1)
        self.statusbar = statusbar

    def MainAreaOnWheel(self, evt):
        bairitsu = 0.15
        if evt.GetWheelRotation() > 0:
            scale = 1-bairitsu
        else:
            scale = 1+bairitsu
        vl,vr = self.MainArea.xlim
        vb,vt = self.MainArea.ylim
        vx,vy = self.MainArea.toData(*evt.GetPosition())
        if (vx-scale*(vx-vl) >= vx+scale*(vr-vx)) or (vy-scale*(vy-vb) >= vy+scale*(vt-vy)):
            return
        self.MainArea.xlim = (vx-scale*(vx-vl) , vx+scale*(vr-vx))
        self.MainArea.ylim = (vy-scale*(vy-vb) , vy+scale*(vt-vy))
        self.update()

    def MainAreaOnLDown(self,evt):
        self.MainArea._capture_mouse |= skstatus.MouseStatus.LEFT
        self.MainArea.px,self.MainArea.py = evt.GetPosition()

    def MainAreaOnLUp(self,evt):
        if skstatus.MouseStatus.LEFT in self.MainArea._capture_mouse:
            self.MainArea._capture_mouse ^= skstatus.MouseStatus.LEFT

    def MainAreaOnLDClick(self,evt):
        self.MainArea.autorange()
        self.update()

    def MainAreaOnRDown(self,evt):
        self.MainArea._capture_mouse |= skstatus.MouseStatus.RIGHT
        self.MainArea.px,self.MainArea.py = evt.GetPosition()

    def MainAreaOnRUp(self,evt):
        if skstatus.MouseStatus.RIGHT in self.MainArea._capture_mouse:
            self.MainArea._capture_mouse ^= skstatus.MouseStatus.RIGHT
            px,py = self.MainArea.toData(self.MainArea.px,self.MainArea.py)
            x,y = self.MainArea.toData(*evt.GetPosition())
            if px==x and py==y:
                self.MainArea.rubber_rect = None
                self.MainArea.update()
                self.wx.draw()
                self.wx.Refresh()
                return
            startx,endx = min(px,x),max(px,x)
            starty,endy = min(py,y),max(py,y)
            self.MainArea.xlim = (startx , endx)
            self.MainArea.ylim = (starty , endy)
            self.MainArea.rubber_rect = None
            self.update()

    def MainAreaOnRDClick(self,evt):
        self.MainAreaOnLDClick(evt)

    def MainAreaOnMotion(self,evt):
        if self.statusbar is not None:
            if self.MainArea.contains(*evt.GetPosition()):
                x,y = self.MainArea.toData(*evt.GetPosition())
                self.statusbar.SetStatusText(f"({x:.5g},{y:.5g})")
        if skstatus.MouseStatus.LEFT in self.MainArea._capture_mouse:
            px,py = self.MainArea.toData(self.MainArea.px,self.MainArea.py)
            x,y = self.MainArea.toData(*evt.GetPosition())
            self.MainArea.xlim = (self.MainArea.xlim[0]-x+px , self.MainArea.xlim[1]-x+px)
            self.MainArea.ylim = (self.MainArea.ylim[0]-y+py , self.MainArea.ylim[1]-y+py)
            self.MainArea.px,self.MainArea.py = evt.GetPosition()
        elif skstatus.MouseStatus.RIGHT in self.MainArea._capture_mouse:
            px,py = self.MainArea.px,self.MainArea.py
            x,y = evt.GetPosition()
            startx,endx = min(int(px),int(x)),max(int(px),int(x))
            starty,endy = min(int(py),int(y)),max(int(py),int(y))
            if starty == endy:
                return
            if startx == endx:
                return
            startx,starty = self.MainArea.toData(startx,starty)
            endx,endy = self.MainArea.toData(endx,endy)
            self.MainArea.rubber_rect = (startx,starty,endx,endy)
        self.update()

    def MainAreaOnLeave(self,evt):
        self.MainArea._capture_mouse = skstatus.MouseStatus.NONE

class PlotFrame(wx.Frame):
    def __init__(self,*args,**dargs):
        super().__init__(*args,**dargs)
        self.SetMinClientSize((400,300))
        self.SetSizer(wx.BoxSizer())
        self.statusbar = self.CreateStatusBar(1)
        attribute = glcanvas.GLAttributes()
        attribute.PlatformDefaults().MinRGBA(8,8,8,8).DoubleBuffer().FrameBuffersRGB().Depth(16).SampleBuffers(1).Samplers(16).Stencil(8).EndList()
        self.graph_gl = skpanel.GLPanel(self,attribute,size=wx.Size(500,500))
        self.graph = SimplePlot(self.graph_gl,self.statusbar)
        self.Sizer.Add(self.graph_gl,1,wx.EXPAND)

    def plot(self,data,**dargs):
        self.graph.MainArea.lines.clear()
        self.graph.MainArea.flines.clear()
        line = skitem.Line()
        line.set(xscale=self.graph.MainArea.xscale,yscale=self.graph.MainArea.yscale)
        line.set(data=data,**dargs)
        self.graph.MainArea.append(line)
        self.graph.MainArea.update()
        self.graph_gl.Refresh()
        return line

    def replot(self,data,**dargs):
        line = skitem.Line()
        line.set(xscale=self.graph.MainArea.xscale,yscale=self.graph.MainArea.yscale)
        line.set(data=data,**dargs)
        self.graph.MainArea.append(line)
        self.graph.MainArea.update()
        self.graph_gl.Refresh()
        return line

    def fplot(self,data,**dargs):
        self.graph.MainArea.lines.clear()
        self.graph.MainArea.flines.clear()
        line = skitem.FLine()
        line.set(xscale=self.graph.MainArea.xscale,yscale=self.graph.MainArea.yscale)
        line.set(data=data,**dargs)
        self.graph.MainArea.append(line)
        self.graph.MainArea.update()
        self.graph_gl.Refresh()
        return line
    
    def freplot(self,data,**dargs):
        line = skitem.FLine()
        line.set(xscale=self.graph.MainArea.xscale,yscale=self.graph.MainArea.yscale)
        line.set(data=data,**dargs)
        self.graph.MainArea.append(line)
        self.graph.MainArea.update()
        self.graph_gl.Refresh()
        return line

class PlotImageFrame(wx.Frame):
    def __init__(self,*args,**dargs):
        super().__init__(*args,**dargs)
        self.SetMinClientSize((400,300))
        self.SetSizer(wx.BoxSizer())
        self.statusbar = self.CreateStatusBar(1)
        attribute = glcanvas.GLAttributes()
        attribute.PlatformDefaults().MinRGBA(8,8,8,8).DoubleBuffer().FrameBuffersRGB().Depth(16).SampleBuffers(1).Samplers(16).Stencil(8).EndList()
        self.graph_gl = skpanel.GLPanel(self,attribute,size=wx.Size(500,500))
        self.graph = SimpleImagePlot(self.graph_gl,self.statusbar)
        self.Sizer.Add(self.graph_gl,1,wx.EXPAND)

    def plot(self,data,**dargs):
        self.graph.MainArea.set(data=data,**dargs)
        self.graph.MainArea.autorange()
        self.graph.MainArea.image.make_histogram()
        self.graph.MainArea.image.auto_colorrange()
        self.graph.ColorBar.autorange()


if __name__ == "__main__":
    xs = np.linspace(0,2*np.pi,10000)
    ys1 = np.sin(xs)
    ys2 = np.cos(xs)
    app = wx.App()
    frame = PlotFrame(None,-1,"test")
    frame.MinClientSize = frame.FromDIP((400,300))
    frame.fplot(np.array([xs,ys1]).T,linecolor=skcolor.ColorList["red"])
    frame.replot(np.array([xs,ys2]).T,linecolor=skcolor.ColorList["blue"],linetype=skitem.LineType.DASH,markertype=skitem.MarkerType.RECT,markercolor=skcolor.ColorList["blue"])
    frame.Show()

    imframe = PlotImageFrame(frame,-1,"tetest")
    imframe.MinClientSize = frame.FromDIP((400,300))
    imframe.plot(np.random.rand(100,200))
    imframe.Show()
    app.MainLoop()
