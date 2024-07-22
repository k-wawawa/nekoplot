
import time
import wx
from wx import glcanvas
from types import MethodType
# from OpenGL.GL import GL_RGBA8
GL_RGBA8 = 32856
GL_SampleCnt = None

import skia

from . import status
from . import color
from . import event
from . import layout

class SkPlotExcept(Exception):
    def __init__(self,s):
        self.s = s

    def __str__(self):
        return self.s

class GLPanel(glcanvas.GLCanvas):
    def __init__(self, parent,attribute,*args,**dargs):
        glcanvas.GLCanvas.__init__(self, parent, attribute, *args,**dargs)
        self.wxctx = glcanvas.GLContext(self)
        self.SetCurrent(self.wxctx)
        self.ctx = skia.GrDirectContext.MakeGL()
        self.figure = self.makeLayer()
        self.figureMinSize = self.FromDIP((400,300))
        self.picture = None
        self.panel = Panel(self)
        self.panel.wx = self
        self.panel._deviceXY = 0,0
        self.panel._width,self.panel._height = self.Size
        self._resizing = False
        self.glBG = color.ColorList["white"]
        self._update = None

# いろいろなイベント
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_IDLE,self.on_idle)
        self.Bind(wx.EVT_IDLE, self.panel.OnIdle)
        self.Bind(wx.EVT_CLOSE,self.on_close)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_mouse_left_dclick)

        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_mouse_right_up)
        self.Bind(wx.EVT_RIGHT_DCLICK, self.on_mouse_right_dclick)

        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_mouse_middle_down)
        self.Bind(wx.EVT_MIDDLE_UP, self.on_mouse_middle_up)
        self.Bind(wx.EVT_MIDDLE_DCLICK, self.on_mouse_middle_dclick)

        self.Bind(wx.EVT_MOUSE_AUX1_DOWN, self.on_mouse_aux1_down)
        self.Bind(wx.EVT_MOUSE_AUX1_UP, self.on_mouse_aux1_up)
        self.Bind(wx.EVT_MOUSE_AUX1_DCLICK, self.on_mouse_aux1_dclick)

        self.Bind(wx.EVT_MOUSE_AUX2_DOWN, self.on_mouse_aux2_down)
        self.Bind(wx.EVT_MOUSE_AUX2_UP, self.on_mouse_aux2_up)
        self.Bind(wx.EVT_MOUSE_AUX2_DCLICK, self.on_mouse_aux2_dclick)

        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)

        self.Bind(wx.EVT_KEY_DOWN, self.on_keyboard)
        self.Bind(wx.EVT_KEY_UP, self.on_keyboard_up)

        # self.Bind(wx.EVT_MOUSE_CAPTURE_CHANGED, self.panel._OnCaptureLost)
        # self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.panel._OnCaptureLost)

    def end(self):
        # self.ctx.freeGpuResources()
        self.ctx.abandonContext()

    def __del__(self):
        self.end()

    def on_close(self,event):
        print("close")
        self.end()
        event.Skip()

    def on_size(self,e):
        if False:
            self.update()
            self.panel.width,self.panel.height = e.Size
            # self.panel._update |= status.GraphStatus.UPDATE
            size = wx.SizeEvent(wx.Size(self.panel.width,self.panel.height))
            size.SetRect(wx.Rect(0,0,self.panel.width,self.panel.height))
            self.panel.OnSize(size)
            e.Skip()
        else:
            evt = event.SizeEvent.fromWx(e)
            self.panel.LTWH = evt.LTWH
            e.Skip()

    def on_paint(self,event):
        self.draw()

    def on_idle(self,event):
        pass

    def on_keyboard(self,e):
        evt = event.KeyEvent.fromWx(e)
        self.panel._OnKeyboard(evt)
    def on_keyboard_up(self,e):
        evt = event.KeyEvent.fromWx(e)
        self.panel._OnKeyboardUp(evt)

    def on_mouse_enter(self,e):
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnEnter(evt)
    def on_mouse_leave(self,e):
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnLeave(evt)
    def on_mouse_left_down(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseLDown(evt)
    def on_mouse_left_up(self,e):
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseLUp(evt)
    def on_mouse_left_dclick(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseLDClick(evt)
    def on_mouse_middle_down(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseMDown(evt)
    def on_mouse_middle_up(self,e):
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseMUp(evt)
    def on_mouse_middle_dclick(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseMDClick(evt)
    def on_mouse_right_down(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseRDown(evt)
    def on_mouse_right_up(self,e):
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseRUp(evt)
    def on_mouse_right_dclick(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseRDClick(evt)
    def on_mouse_aux1_down(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseAUX1Down(evt)
    def on_mouse_aux1_up(self,e):
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseAUX1Up(evt)
    def on_mouse_aux1_dclick(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseAUX1DClick(evt)
    def on_mouse_aux2_down(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseAUX2Down(evt)
    def on_mouse_aux2_up(self,e):
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseAUX2Up(evt)
    def on_mouse_aux2_dclick(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseAUX2DClick(evt)
    def on_mouse_motion(self,e):
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseMotion(evt)
    def on_mouse_wheel(self,e):
        self.SetFocus()
        evt = event.MouseEvent.fromWx(e)
        self.panel._OnMouseWheel(evt)

    def makeLayer(self,width = None,height=None):
        global GL_SampleCnt
        if width is None:
            w,_ = self.GetSize()
            width = w
        if height is None:
            _,h = self.GetSize()
            height = h
        if GL_SampleCnt is None:
            for i in [4,2,1,0]:
                GL_SampleCnt = i
                brt = skia.GrBackendRenderTarget(width,height,GL_SampleCnt,8,skia.GrGLFramebufferInfo(0,GL_RGBA8))
                layer = skia.Surface.MakeFromBackendRenderTarget(
                        self.ctx,brt,skia.kBottomLeft_GrSurfaceOrigin,
                        skia.kRGBA_8888_ColorType,skia.ColorSpace.MakeSRGB()
                        )
                if layer is not None:
                    break
            print(f"OpenGL Sample Count : {GL_SampleCnt}")
            if layer is None:
                with wx.MessageDialog(self, "Can't Open OpenGL Target. exit this program.", caption="OpenGL Error",
                    style=wx.OK|wx.CENTRE, pos=wx.DefaultPosition) as dlg:
                    dlg.ShowModal()
                import sys
                sys.exit(0)
        else:
            brt = skia.GrBackendRenderTarget(width,height,GL_SampleCnt,8,skia.GrGLFramebufferInfo(0,GL_RGBA8))
        # brt = skia.GrBackendRenderTarget(width,height,4,8,skia.GrGLFramebufferInfo(0,GL_RGBA8))
        layer = skia.Surface.MakeFromBackendRenderTarget(
            self.ctx,brt,skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType,skia.ColorSpace.MakeSRGB()
        )
        return layer

    def draw(self):
        if self._update:
            recorder = skia.PictureRecorder()
            w,h = max(self.figureMinSize[0],self.ClientSize[0]),max(self.figureMinSize[1],self.ClientSize[1])
            canvas = recorder.beginRecording(w,h)
            canvas.clear(self.glBG.skia4f)
            self.panel.draw(canvas)
            # canvas.flush()
            self.picture = recorder.finishRecordingAsPicture()
            self._update = False
        self.cache_draw()

    def cache_draw(self):
        self.SetCurrent(self.wxctx)
        w,h = max(self.figureMinSize[0],self.ClientSize[0]),max(self.figureMinSize[1],self.ClientSize[1])
        if not (self.figure.width() == w and self.figure.height() == h):
            self.figure = self.makeLayer(w,h)
        canvas = self.figure.getCanvas()
        canvas.clear(self.glBG.skia4f)
        canvas.drawPicture(self.picture)
        canvas.flush()
        self.SwapBuffers()
        self.Refresh()
        self.ctx.freeGpuResources()

    def add(self,child):
        self.panel.add(child)

    def update(self):
        self._update = True

class Panel:
    def __init__(self,parent):
        self._update = status.GraphStatus.NONE
        self.layout = layout.NullLayout()
        self._wx = None
        self._left = 0
        self._top = 0
        self._width = 1
        self._height = 1
        # self._background = skia.Color4f.kTransparent
        self._background = skia.Color4f.kWhite
        self._background = color.Color(0,0,0,0)
        if isinstance(parent,(GLPanel,ImagePanel)):
            self.parent = None
            self._wx = parent
            self._wx.panel = self
            self._left,self._top,self._width,self._height = (0,0,*self.wx.Size)
        elif isinstance(parent,Panel):
            self.parent = parent
        else:
            raise TypeError("parent must be GLPanel, Panel or ImagePanel")
        self.children = list()
        self._capture_mouse = status.MouseStatus.NONE
        self.px,self.py = 0,0
        if self.parent is not None:
            self.parent.children.append(self)

    def Bind(self,evttype,function):
        if evttype == event.Type.SIZE:
            self.OnSize = MethodType(function,self)
        elif evttype == event.Type.KEY:
            self.OnKeyboard = MethodType(function,self)
        elif evttype == event.Type.KEY_UP:
            self.OnKeyboardUp = MethodType(function,self)
        elif evttype == event.Type.MOUSE_ENTER:
            self.OnEnter = MethodType(function,self)
        elif evttype == event.Type.MOUSE_LEAVE:
            self.OnLeave = MethodType(function,self)
        elif evttype == event.Type.MOUSE_L_DOWN:
            self.OnMouseLDown = MethodType(function,self)
        elif evttype == event.Type.MOUSE_L_UP:
            self.OnMouseLUp = MethodType(function,self)
        elif evttype == event.Type.MOUSE_L_DCLICK:
            self.OnMouseLDClick = MethodType(function,self)
        elif evttype == event.Type.MOUSE_R_DOWN:
            self.OnMouseRDown = MethodType(function,self)
        elif evttype == event.Type.MOUSE_R_UP:
            self.OnMouseRUp = MethodType(function,self)
        elif evttype == event.Type.MOUSE_R_DCLICK:
            self.OnMouseRDClick = MethodType(function,self)
        elif evttype == event.Type.MOUSE_M_DOWN:
            self.OnMouseMDown = MethodType(function,self)
        elif evttype == event.Type.MOUSE_M_UP:
            self.OnMouseMUp = MethodType(function,self)
        elif evttype == event.Type.MOUSE_M_DCLICK:
            self.OnMouseMDClick = MethodType(function,self)
        elif evttype == event.Type.MOUSE_A1_DOWN:
            self.OnMouseAUX1Down = MethodType(function,self)
        elif evttype == event.Type.MOUSE_A1_UP:
            self.OnMouseAUX1Up = MethodType(function,self)
        elif evttype == event.Type.MOUSE_A1_DCLICK:
            self.OnMouseAUX1DClick = MethodType(function,self)
        elif evttype == event.Type.MOUSE_A2_DOWN:
            self.OnMouseAUX2Down = MethodType(function,self)
        elif evttype == event.Type.MOUSE_A2_UP:
            self.OnMouseAUX2Up = MethodType(function,self)
        elif evttype == event.Type.MOUSE_A2_DCLICK:
            self.OnMouseAUX2DClick = MethodType(function,self)
        elif evttype == event.Type.MOUSE_MOTION:
            self.OnMouseMotion = MethodType(function,self)
        elif evttype == event.Type.MOUSE_WHEEL:
            self.OnMouseWheel = MethodType(function,self)

    def contains(self,x,y):
        xx,yy = self._deviceXY
        xx += self.width
        yy += self.height
        if self._deviceXY[0]<=x<xx or xx<=x<self._deviceXY[0]:
            if self._deviceXY[1]<=y<yy or yy<=y<self._deviceXY[1]:
                return True
        return False

    def ChangeCursor(self,cursor):
        self.wx.SetCursor(wx.Cursor(cursor.value))

    @property
    def root(self):
        return (self.parent is None)

    @property
    def wx(self):
        if self.root:
            return self._wx
        else:
            return self.parent.wx
    @wx.setter
    def wx(self,value):
        if self.root:
            self._wx = value
        else:
            raise SkPlotExcept("this panel is not root")

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
        self._width = value[2]-value[0]+1
        self._height = value[3]-value[1]+1
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
        self._width = value[2]
        self._height = value[3]
        se = event.SizeEvent()
        se.LTWH = value
        self._OnSize(se)

    # 今までの負債で書く必要があるやつ(いつか消したい)
    @property
    def _deviceXY(self):
        return (self.left,self.top)
    @_deviceXY.setter
    def _deviceXY(self,value):
        pl,pt = self._deviceXY
        if (pl==value[0]) and (pt==value[1]):
            return
        self._left = value[0]
        self._top = value[1]
        se = event.SizeEvent()
        se.LTWH = self.LTWH
        self._OnSize(se)

    def root_refresh(self):
        if self.root:
            self.wx.draw()
            self.wx.Refresh()

    def update(self):
        self._update = status.GraphStatus.UPDATE
        if self.root:
            self.wx.update()
        else:
            self.parent.update()

    def event2child(self,event):
        evt = event.Clone()
        evt.SetX(event.x-self._deviceXY[0])
        evt.SetY(event.y-self._deviceXY[1])
        return evt

    def _OnSize(self,event):
        self.update()
        self.layout.calcurate(*event.WH)
        self.OnSize(event)
        self.root_refresh()
    def OnSize(self,event):
        # サイズが変わった事による処理
        # 例えば、あるchildの要素を右から10pxの位置に置くとか
        pass

    def OnPaint(self,event):
        pass
        # for child in self.children:
        #     child.OnPaint(event)

    def OnIdle(self,event):
        pass
        # if self.contains(*event.Size):
        #     print("Idle")
        #     for child in self.children:
        #         child.OnIdle(event)
        #         return

    def _OnMouseLDown(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseLDown(evt)
        if not evt.Skipped:
            self.OnMouseLDown(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseLDown(self,event):
        # 何かしらの処理
        pass

    def _OnMouseLUp(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseLUp(evt)
        if not evt.Skipped:
            self.OnMouseLUp(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseLUp(self,event):
        pass

    def _OnMouseRDown(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseRDown(evt)
        if not evt.Skipped:
            self.OnMouseRDown(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseRDown(self,event):
        pass

    def _OnMouseRUp(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseRUp(evt)
        if not evt.Skipped:
            self.OnMouseRUp(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseRUp(self,event):
        pass

    def _OnMouseMDown(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseMDown(evt)
        if not evt.Skipped:
            self.OnMouseMDown(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseMDown(self,event):
        pass

    def _OnMouseMUp(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseMUp(evt)
        if not evt.Skipped:
            self.OnMouseMUp(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseMUp(self,event):
        pass

    def _OnMouseMotion(self,event):
        evt = self.event2child(event)
        for child in self.children:
            child._OnMouseMotion(evt)
        if not evt.Skipped:
            self.OnMouseMotion(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseMotion(self,event):
        pass

    def _OnMouseLDClick(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseLDClick(evt)
        if not evt.Skipped:
            self.OnMouseLDClick(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseLDClick(self,event):
        pass

    def _OnMouseMDClick(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseMDClick(evt)
        if not evt.Skipped:
            self.OnMouseMDClick(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseMDClick(self,event):
        pass

    def _OnMouseRDClick(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseRDClick(evt)
        if not evt.Skipped:
            self.OnMouseRDClick(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseRDClick(self,event):
        pass

    def _OnMouseAUX1Down(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseAUX1Down(evt)
        if not evt.Skipped:
            self.OnMouseAUX1Down(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseAUX1Down(self,event):
        pass

    def _OnMouseAUX1Up(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseAUX1Up(evt)
        if not evt.Skipped:
            self.OnMouseAUX1Up(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseAUX1Up(self,event):
        pass

    def _OnMouseAUX2Down(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseAUX2Down(evt)
        if not evt.Skipped:
            self.OnMouseAUX2Down(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseAUX2Down(self,event):
        pass

    def _OnMouseAUX2Up(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseAUX2Up(evt)
        if not evt.Skipped:
            self.OnMouseAUX2Up(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseAUX2Up(self,event):
        pass

    def _OnMouseAUX1DClick(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseAUX1DClick(evt)
        if not evt.Skipped:
            self.OnMouseAUX1DClick(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseAUX1DClick(self,event):
        pass

    def _OnMouseAUX2DClick(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseAUX2DClick(evt)
        if not evt.Skipped:
            self.OnMouseAUX2DClick(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseAUX2DClick(self,event):
        pass

    def _OnKeyboard(self,event):
        evt = event.Clone()
        evt = self.event2child(event)
        evt.KeyStr = event.KeyStr
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnKeyboard(evt)
        if not evt.Skipped:
            self.OnKeyboard(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnKeyboard(self,event):
        pass

    def _OnMouseWheel(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnMouseWheel(evt)
        if not evt.Skipped:
            self.OnMouseWheel(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnMouseWheel(self,event):
        pass

    def _OnKeyboardUp(self,event):
        # evt = self.event2child(event)
        evt = event.Clone()
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnKeyboardUp(evt)
        if not evt.Skipped:
            self.OnKeyboardUp(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnKeyboardUp(self,event):
        pass

    def _OnEnter(self,event):
        evt = self.event2child(event)
        for child in self.children:
            if child.contains(evt.x,evt.y):
                child._OnEnter(evt)
        if not evt.Skipped:
            self.OnEnter(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnEnter(self,event):
        pass

    def _OnLeave(self,event):
        evt = self.event2child(event)
        for child in self.children:
            child._OnLeave(evt)
            return
        if not evt.Skipped:
            self.OnLeave(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnLeave(self,event):
        pass

    def _OnCaptureLost(self,event):
        evt = self.event2child(event)
        for child in self.children:
            child._OnCaptureLost(evt)
            return
        if not evt.Skipped:
            self.OnCaptureLost(event)
        else:
            event.Skip()
        self.root_refresh()
    def OnCaptureLost(self,event):
        pass

    def draw(self,canvas):
        if self._update:
            recorder = skia.PictureRecorder()
            rec = recorder.beginRecording(self.deviceRect)
            rec.save()
            rec.clear(self._background.skia4f)
            for child in self.children:
                child.draw(rec)
            # rec.flush()
            rec.restore()
            self.picture = recorder.finishRecordingAsPicture()
            self.picture = skia.Image.MakeFromPicture(self.picture,skia.ISize.Make(int(self._width),int(self._height)),None,None,skia.Image.BitDepth.kU8,skia.ColorSpace.MakeSRGB())
            self._update &= status.GraphStatus.NONE
        canvas.save()
        canvas.translate(*self._deviceXY)
        # canvas.drawPicture(self.picture)
        canvas.drawImage(self.picture,0,0)
        canvas.restore()

    @property
    def deviceRect(self):
        return skia.Rect.MakeXYWH(0,0,self.width,self.height)

    @property
    def clipRect(self):
        return skia.Rect.MakeXYWH(-1,-1,self.width+2,self.height+2)

    @property
    def left(self):
        return self._left
    @left.setter
    def left(self,value):
        if self.left == value:
            return
        self._left = int(value)
        se = event.SizeEvent()
        se.LTWH = self.LTWH
        self._OnSize(se)
    @property
    def top(self):
        return self._top
    @top.setter
    def top(self,value):
        if self.top == value:
            return
        self._top = int(value)
        se = event.SizeEvent()
        se.LTWH = self.LTWH
        self._OnSize(se)
    @property
    def width(self):
        return self._width
    @width.setter
    def width(self,value):
        if self.width == value:
            return
        self._width = int(value)
        se = event.SizeEvent()
        se.LTWH = self.LTWH
        self._OnSize(se)
    @property
    def height(self):
        return self._height
    @height.setter
    def height(self,value):
        if self.height == value:
            return
        self._height = int(value)
        se = event.SizeEvent()
        se.LTWH = self.LTWH
        self._OnSize(se)

class PanelwoChild:
    def __init__(self,parent):
        self._update = status.GraphStatus.NONE
        if isinstance(parent,GLPanel):
            self.parent = None
            self.wx = parent
        elif isinstance(parent,Panel):
            self.parent = parent
        else:
            raise TypeError("parent must be GLPanel or Panel")
        self._left = 0
        self._top = 0
        self._width = 1
        self._height = 1
        self._background = color.ColorList["white"]
        if self.parent is not None:
            self.parent.children.append(self)

    @property
    def root(self):
        return (self.parent is None)

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
        self._width = value[2]-value[0]+1
        self._height = value[3]-value[1]+1
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
        self._width = value[2]
        self._height = value[3]
        se = event.SizeEvent()
        se.LTWH = value
        self._OnSize(se)

    # 今までの負債で書く必要があるやつ(いつか消したい)
    @property
    def _deviceXY(self):
        return (self.left,self.top)
    @_deviceXY.setter
    def _deviceXY(self,value):
        pl,pt = self._deviceXY
        if (pl==value[0]) and (pt==value[1]):
            return
        self._left = value[0]
        self._top = value[1]
        se = event.SizeEvent()
        se.LTWH = self.LTWH
        self._OnSize(se)

    def contains(self,x,y):
        xx,yy = self._deviceXY
        xx += self.width
        yy += self.height
        if self._deviceXY[0]<=x<xx or xx<=x<self._deviceXY[0]:
            if self._deviceXY[1]<=y<yy or yy<=y<self._deviceXY[1]:
                return True
        return False

    def root_refresh(self):
        if self.root:
            self.wx.draw()
            self.wx.Refresh()

    def update(self):
        self._update = status.GraphStatus.UPDATE
        if self.root:
            self.wx.update()
        else:
            self.parent.update()

    def _OnSize(self,event):
        self.update()
        self.OnSize(event)
        self.root_refresh()
    def OnSize(self,event):
        pass

    def _OnMouseLDown(self,event):
        self.OnMouseLDown(event)
        self.root_refresh()
    def OnMouseLDown(self,event):
        # 何かしらの処理
        pass

    def _OnMouseLUp(self,event):
        self.OnMouseLUp(event)
        self.root_refresh()
    def OnMouseLUp(self,event):
        pass

    def _OnMouseRDown(self,event):
        self.OnMouseRDown(event)
        self.root_refresh()
    def OnMouseRDown(self,event):
        pass

    def _OnMouseRUp(self,event):
        self.OnMouseRUp(event)
        self.root_refresh()
    def OnMouseRUp(self,event):
        pass

    def _OnMouseMDown(self,event):
        self.OnMouseMDown(event)
        self.root_refresh()
    def OnMouseMDown(self,event):
        pass

    def _OnMouseMUp(self,event):
        self.OnMouseMUp(event)
        self.root_refresh()
    def OnMouseMUp(self,event):
        pass

    def _OnMouseMotion(self,event):
        self.OnMouseMotion(event)
        self.root_refresh()
    def OnMouseMotion(self,event):
        pass

    def _OnMouseLDClick(self,event):
        self.OnMouseLDClick(event)
        self.root_refresh()
    def OnMouseLDClick(self,event):
        pass

    def _OnMouseMDClick(self,event):
        self.OnMouseMDClick(event)
        self.root_refresh()
    def OnMouseMDClick(self,event):
        pass

    def _OnMouseRDClick(self,event):
        self.OnMouseRDClick(event)
        self.root_refresh()
    def OnMouseRDClick(self,event):
        pass

    def _OnMouseAUX1Down(self,event):
        self.OnMouseAUX1Down(event)
        self.root_refresh()
    def OnMouseAUX1Down(self,event):
        pass

    def _OnMouseAUX1Up(self,event):
        self.OnMouseAUX1Up(event)
        self.root_refresh()
    def OnMouseAUX1Up(self,event):
        pass

    def _OnMouseAUX2Down(self,event):
        self.OnMouseAUX2Down(event)
        self.root_refresh()
    def OnMouseAUX2Down(self,event):
        pass

    def _OnMouseAUX2Up(self,event):
        self.OnMouseAUX2Up(event)
        self.root_refresh()
    def OnMouseAUX2Up(self,event):
        pass

    def _OnMouseAUX1DClick(self,event):
        self.OnMouseAUX1DClick(event)
        self.root_refresh()
    def OnMouseAUX1DClick(self,event):
        pass

    def _OnMouseAUX2DClick(self,event):
        self.OnMouseAUX2DClick(event)
        self.root_refresh()
    def OnMouseAUX2DClick(self,event):
        pass

    def _OnKeyboard(self,event):
        if self.root:
            pos = wx.GetMouseState()
            x,y = self.wx.ScreenToClient(pos.x,pos.y)
            event.x = x
            event.y = y
            event.SetKey(event)
        self.OnKeyboard(event)
        self.root_refresh()
    def OnKeyboard(self,event):
        pass

    def _OnMouseWheel(self,event):
        self.OnMouseWheel(event)
        self.root_refresh()
    def OnMouseWheel(self,event):
        pass

    def _OnKeyboardUp(self,event):
        self.OnKeyboardUp(event)
        self.root_refresh()
    def OnKeyboardUp(self,event):
        pass

    def _OnEnter(self,event):
        self.OnEnter(event)
        self.root_refresh()
    def OnEnter(self,event):
        pass

    def _OnLeave(self,event):
        self.OnLeave(event)
        self.root_refresh()
    def OnLeave(self,event):
        pass

    def _OnCaptureLost(self,event):
        self.OnCaptureLost(event)
        self.root_refresh()
    def OnCaptureLost(self,event):
        pass

    def draw(self,canvas):
        if self._update:
            recorder = skia.PictureRecorder()
            w,h = self.deviceRect.width(),self.deviceRect.height()
            rec = recorder.beginRecording(w,h)
            rec.save()
            rec.clipRect(self.deviceRect,skia.ClipOp.kIntersect)
            rec.clear(self._background.skia4f)
            self._draw(rec)
            # rec.flush()
            rec.restore()
            self.picture = recorder.finishRecordingAsPicture()
            self._update &= status.GraphStatus.NONE
        canvas.save()
        canvas.translate(*self._deviceXY)
        canvas.drawPicture(self.picture)
        canvas.restore()

    @property
    def deviceRect(self):
        return skia.Rect.MakeXYWH(0,0,self.width,self.height)

    @property
    def clipRect(self):
        return skia.Rect.MakeXYWH(-1,-1,self.width+2,self.height+2)

    @property
    def left(self):
        return self._left
    @left.setter
    def left(self,value):
        if self.left == value:
            return
        self._left = int(value)
        se = event.SizeEvent()
        se.LTWH = self.LTWH
        self._OnSize(se)
    @property
    def top(self):
        return self._top
    @top.setter
    def top(self,value):
        if self.top == value:
            return
        self._top = int(value)
        se = event.SizeEvent()
        se.LTWH = self.LTWH
        self._OnSize(se)
    @property
    def width(self):
        return self._width
    @width.setter
    def width(self,value):
        if self.width == value:
            return
        self._width = int(value)
        se = event.SizeEvent()
        se.LTWH = self.LTWH
        self._OnSize(se)
    @property
    def height(self):
        return self._height
    @height.setter
    def height(self,value):
        if self.height == value:
            return
        self._height = int(value)
        se = event.SizeEvent()
        se.LTWH = self.LTWH
        self._OnSize(se)

class ImagePanel:
    def __init__(self,width=800,height=600):
        self.width = width
        self.height = height
        self.panel = Panel(self)
        self.glBG = skia.ColorWHITE

    @property
    def Size(self):
        return (self.width,self.height)

    def makeLayer(self,width = None,height=None):
        w = width if width is not None else self.width
        h = height if height is not None else self.height
        layer = skia.Surface.MakeRasterN32Premul(w,h)
        return layer

    def draw(self,width=None,height=None):
        w = width if width is not None else self.width
        h = height if height is not None else self.height
        self.figure = self.makeLayer(w,h)
        canvas = self.figure.getCanvas()
        canvas.clear(self.glBG)
        self.panel.draw(canvas)
        canvas.flush()

    def update(self):
        pass
    def Refresh(self):
        pass

    def saveas(self,filename,width=None,height=None,format=skia.EncodedImageFormat.kJPEG,quality=100):
        w = width if width is not None else self.width
        h = height if height is not None else self.height
        size = event.SizeEvent()
        size.LTWH = (0,0,w,h)
        self.panel._OnSize(size)
        self.draw(w,h)
        img = skia.Image.fromarray(self.figure.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType),colorType=skia.ColorType.kRGBA_8888_ColorType)
        data = img.encodeToData(format,quality)
        with open(filename,"wb") as f:
            f.write(data.bytes())
