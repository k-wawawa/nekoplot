
import time

import skia
import numpy as np

TEST_PAINT = skia.Paint(StrokeWidth=0,Color=skia.Color(0,0,0,255),AntiAlias=False,Style=skia.Paint.kStroke_Style)

from . import status
from . import item
from . import color
from . import graph
from . import panel
from . import event
from . import utility
from . import scale
from . import dialog

class FLines:
    def __init__(self):
        self._update = False
        self.lines = []
        self.picture = None

    def __len__(self):
        return len(self.lines)

    def update(self):
        self._update = True

    def draw(self):
        if self._update:
            recorder = skia.PictureRecorder()
            rec = recorder.beginRecording(skia.Rect.MakeEmpty())
            rec.save()
            rec.clear(color.Color.fromU8(0,0,0,0).skia4f)
            self._draw(rec)
            rec.restore()
            # rec.flush()
            self.picture = recorder.finishRecordingAsPicture()
            self._update = False

    def _draw(self,canvas):
        for line in self.lines:
            line.draw()
            line.flush(canvas)

    def flush(self,canvas,rect,mat):
        canvas.save()
        canvas.clipRect(rect)
        p = skia.Paint()
        p.setAntiAlias(False)
        canvas.drawPicture(self.picture,mat)
        canvas.restore()

    def append(self,fline):
        fline.layer = self
        self.lines.append(fline)
        self.update()

    def extend(self,flines):
        for l in flines:
            l.layer = self
            self.lines.append(l)
        self.update()

    def __iter__(self):
        return self.lines.__iter__()

class Graph(graph.Graph):
    def __init__(self,parent,rotate=status.RotateStatus.NONE):
        super().__init__(parent,rotate)
        self.flines = FLines()

    def _draw(self,recorder):
        self.draw_images(recorder)
        self.draw_lines(recorder)
        self.draw_annotation(recorder)

    def draw(self,canvas,xlim=None,ylim=None):
        self.make_mat9(xlim,ylim)
        # if self._update:
        #     recorder = skia.PictureRecorder()
        #     rec = recorder.beginRecording(self.deviceRect)
        #     rec.save()
        #     rec.clipRect(self.deviceRect,skia.ClipOp.kIntersect)
        #     rec.clear(self._background.skia4f)
        #     self._draw(rec)
        #     rec.restore()
        #     # rec.flush()
        #     self.picture = recorder.finishRecordingAsPicture()
        #     self.picture = skia.Image.MakeFromPicture(self.picture,skia.ISize.Make(int(self._width),int(self._height)),None,None,skia.Image.BitDepth.kU8,skia.ColorSpace.MakeSRGB())
        #     self._update &= status.GraphStatus.NONE
        canvas.save()
        canvas.translate(*self._deviceXY)
        if self._devicerotate == status.RotateStatus.FLIP:
            canvas.translate(self.height,0)
        rotate = 0 if (self._devicerotate == status.RotateStatus.NONE) else 90
        canvas.rotate(rotate)
        # canvas.drawPicture(self.picture)
        # canvas.drawImage(self.picture,0,0)
        self.flines.draw()
        self.flines.flush(canvas,self.deviceRect,skia.Matrix.MakeAll(*self.mat9))
        # rec.clipRect(self.clipRect,skia.ClipOp.kIntersect)
        self.grapharea(canvas)
        if self.rubber_rect is not None:
            canvas.save()
            canvas.clipRect(self.deviceRect,skia.ClipOp.kIntersect)
            canvas.concat(skia.Matrix.MakeAll(*self.mat9))
            canvas.drawRect(self.rubber_rect,skia.Paint(Style=skia.Paint.kStroke_Style))
            canvas.restore()
        canvas.restore()