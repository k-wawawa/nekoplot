import wx
from wx import glcanvas

import skia

from . import status
from . import panel
from . import item

class TextBox(panel.PanelwoChild):
    def __init__(self,parent):
        super().__init__(parent)
        self._text = ""
        self._font = item.Font()
        self._position = (status.PositionStatus.LT,status.PositionStatus.LT)
        self.paint = skia.Paint(Color=skia.Color(0,0,0),AntiAlias=True)

    @property
    def text(self):
        return self._text
    @text.setter
    def text(self,value):
        self.update()
        self._text = value

    @property
    def font(self):
        return self._font
    @font.setter
    def font(self,value):
        self._font = value
        self.update()

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self,value):
        self._position = value
        self.update()

    def _draw(self,canvas):
        font = self.font*self.sizescale
        blob = skia.TextBlob.MakeFromString(self.text,font())
        tw = font.measureText(self.text,paint=self.paint)
        # th = self.font().getSize()
        th = font.getHeight()
        if self.position[0] == status.PositionStatus.LT:
            l = 0
        elif self.position[0] == status.PositionStatus.MM:
            l = -0.5*tw + self.width*0.5
        elif self.position[0] == status.PositionStatus.RB:
            l = self.width-tw
        if self.position[1] == status.PositionStatus.LT:
            t = th
        elif self.position[1] == status.PositionStatus.MM:
            t = 0.5*th + self.height*0.5
        elif self.position[1] == status.PositionStatus.RB:
            t = self.height - font().getMetrics().fDecent
        tpos = (l,t)
        canvas.drawTextBlob(blob,*tpos,self.paint)

class Legend(panel.PanelwoChild):
    def __init__(self,parent):
        super().__init__(parent)
        self.refs = []
        self._font = item.Font()
        self.paint = skia.Paint(Color=skia.Color(0,0,0),AntiAlias=True)
        self._position = (status.PositionStatus.LT,status.PositionStatus.LT)
        self._border = status.BorderStatus.ALL

    def append_ref(self,linelist):
        self.refs.append(linelist)

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self,value):
        self.update()
        self._position = value

    @property
    def border(self):
        return self._border
    @border.setter
    def border(self,value):
        self._border = value

    def draw_item(self,canvas):
        # 一つ書くやつ
        # lineの描画 -○-みたいになるように
        # label文字の描画
        # -○- linelabel
        # となるようにする
        pass

    def _draw(self,canvas):
        return
        blob = skia.TextBlob.MakeFromString(self.text,self.font())
        tw = self.font.measureText(self.text,paint=self.paint)
        # th = self.font().getSize()
        th = self.font.getHeight()
        if self.position[0] == status.PositionStatus.LT:
            l = 0
        elif self.position[0] == status.PositionStatus.MM:
            l = -0.5*tw + self.width*0.5
        elif self.position[0] == status.PositionStatus.RB:
            l = self.width-tw
        if self.position[1] == status.PositionStatus.LT:
            t = th
        elif self.position[1] == status.PositionStatus.MM:
            t = 0.5*th + self.height*0.5
        elif self.position[1] == status.PositionStatus.RB:
            t = self.height - self.font().getMetrics().fDecent
        tpos = (l,t)
        canvas.drawTextBlob(blob,*tpos,self.paint)