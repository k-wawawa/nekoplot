
import copy
from enum import Flag,auto
import wx

# glcanvasでwx.EventをここのEventに必要なデータだけ移してpanel.Panel以降はこのeventで済ませたい

class Type(Flag):
    SIZE=auto()
    KEY = auto()
    KEY_UP = auto()
    MOUSE_ENTER = auto()
    MOUSE_LEAVE = auto()
    MOUSE_L_DOWN = auto()
    MOUSE_L_UP = auto()
    MOUSE_L_DCLICK = auto()
    MOUSE_R_DOWN = auto()
    MOUSE_R_UP = auto()
    MOUSE_R_DCLICK = auto()
    MOUSE_M_DOWN = auto()
    MOUSE_M_UP = auto()
    MOUSE_M_DCLICK = auto()
    MOUSE_A1_DOWN = auto()
    MOUSE_A1_UP = auto()
    MOUSE_A1_DCLICK = auto()
    MOUSE_A2_DOWN = auto()
    MOUSE_A2_UP = auto()
    MOUSE_A2_DCLICK = auto()
    MOUSE_MOTION = auto()
    MOUSE_WHEEL = auto()

class Event:
    def __init__(self):
        self._Skipped = False

    @property
    def Skipped(self):
        return self._Skipped
    @Skipped.setter
    def Skipped(self,value):
        self._Skipped = bool(value)

    def Skip(self):
        self._Skipped = True

    def Clone(self):
        return copy.deepcopy(self)

class SizeEvent(Event):
    def __init__(self):
        super().__init__()
        self.left = 0
        self.top = 0
        self.right = 1
        self.bottom = 1

    @classmethod
    def fromWx(cls,event):
        evt = cls()
        w,h = event.Size
        evt.LTRB = (0,0,w,h)
        return evt

    @property
    def LTRB(self):
        return (self.left,self.top,self.right,self.bottom)
    @LTRB.setter
    def LTRB(self,value):
        self.left = value[0]
        self.top = value[1]
        self.right = value[2]
        self.bottom = value[3]

    @property
    def LTWH(self):
        return (self.left,self.top,self.right-self.left+1,self.bottom-self.top+1)
    @LTWH.setter
    def LTWH(self,value):
        self.left = value[0]
        self.top = value[1]
        self.right = value[0]+value[2]+1
        self.bottom = value[1]+value[3]+1

    @property
    def WH(self):
        return (self.right-self.left+1,self.bottom-self.top+1)

KeyboardKeys = {
    wx.WXK_CONTROL: "ctrl",
    wx.WXK_SHIFT: "shift",
    wx.WXK_ALT: "alt",
    wx.WXK_LEFT: "left",
    wx.WXK_UP: "up",
    wx.WXK_RIGHT: "right",
    wx.WXK_DOWN: "down",
    wx.WXK_ESCAPE: "esc"
}

class KeyEvent(Event):
    def __init__(self):
        super().__init__()
        self.KeyCode = 0
        self.x = 0
        self.y = 0
        self.KeyStr = ""
        self.shift = False
        self.ctrl = False
        self.alt = False

    @classmethod
    def fromWx(cls,event):
        evt = cls()
        evt.KeyCode = event.KeyCode
        pos = wx.GetMouseState()
        x,y = event.EventObject.ScreenToClient(pos.x,pos.y)
        evt.x = x
        evt.y = y
        event.SetKey(event)
        return evt

    def SetKey(self,event):
        code = event.KeyCode
        key = ""
        if code in KeyboardKeys:
            key = KeyboardKeys[code]
        if code == wx.WXK_SHIFT:
            self.shift = True
        if code == wx.WXK_CONTROL:
            self.ctrl = True
        if code == wx.WXK_ALT:
            self.alt = True
        elif 1<=code<=26:
            # ctrl + az
            key = chr(code+96)
            self.ctrl = True
            if event.ShiftDown():
                key = key.upper()
                self.shift = True
        elif 65<=code<=90:
            # shift + az
            key = chr(code)
            self.shift = True
        elif 97<=code<=122:
            key = chr(code).lower()
        mod = [name for i,name in enumerate(["alt","ctrl","shift"]) if ((event.GetModifiers()>>(i))&1)]
        if ("shift" in mod) and key.isupper():
            mod.remove("shift")
        self.KeyStr = "+".join(mod+[key])

    def SetX(self,value):
        self.x = value

    def SetY(self,value):
        self.y = value

class MouseEvent(Event):
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.rot = 0

    @classmethod
    def fromWx(cls,event):
        evt = cls()
        evt.x = event.x
        evt.y = event.y
        evt.rot = event.GetWheelRotation()
        return evt

    def SetX(self,value):
        self.x = value

    def SetY(self,value):
        self.y = value

    def GetPosition(self):
        return (self.x,self.y)

    def GetWheelRotation(self):
        return self.rot
