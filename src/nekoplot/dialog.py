import wx

import numpy as np

from . import status
from . import scale

class FloatInput(wx.TextCtrl):
    def __init__(self,*args,**dargs):
        super().__init__(*args,**dargs)
        self.Bind(wx.EVT_TEXT,self.OnTextChange)

    def OnTextChange(self,event):
        txt = self.GetValue()
        try:
            if not np.isfinite(float(txt)):
                raise ValueError()
            self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        except ValueError:
            self.SetBackgroundColour("red")
        self.Refresh()

    @property
    def Value(self):
        txt = self.GetValue()
        try:
            if not np.isfinite(float(txt)):
                raise ValueError
            return float(txt)
        except ValueError:
            return np.NaN
    @Value.setter
    def Value(self,value):
        try:
            if not np.isfinite(float(value)):
                raise ValueError()
            self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            self.SetValue(str(value))
        except ValueError:
            self.SetBackgroundColour("red")
            self.SetValue(str(value))
        self.Refresh()

class AxisDialog(wx.Dialog):
    def __init__(self,graph,*args,**dargs):
        self.axis = graph
        super().__init__(self.axis.wx,*args,style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE,**dargs)
        axmin,axmax = self.axis.ref.xlim if self.axis.type == status.AxisType.X else self.axis.ref.ylim
        self.scale = self.axis.ref.xscale if self.axis.type == status.AxisType.X else self.axis.ref.yscale
        self.axminctrl = FloatInput(self,-1,value=str(axmin))
        self.axmaxctrl = FloatInput(self,-1,value=str(axmax))
        layout = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(layout)
        layout.AddSpacer(5)

        llayout = wx.BoxSizer(wx.HORIZONTAL)
        llayout.Add(wx.StaticText(self,-1,"scale:"),0,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(10)
        self.scale_ax = wx.ComboBox(self,-1)
        self.scale_ax.Append(f"{str(scale.LinearScale())}",scale.LinearScale())
        if not self.axis.ref.has_image():
            self.scale_ax.Append(f"{str(scale.Log10Scale())}",scale.Log10Scale())
            self.scale_ax.Append(f"{str(scale.LnScale())}",scale.LnScale())
            self.scale_ax.Append(f"{str(scale.ASinhScale())}",scale.ASinhScale())
            self.scale_ax.Append(f"{str(scale.ASinh10Scale())}",scale.ASinh10Scale())
        self.scale_ax.SetStringSelection(f"{str(self.scale)}")
        llayout.Add(self.scale_ax,0,wx.ALIGN_CENTER_VERTICAL)
        layout.Add(llayout,0,wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT,border=10)
        layout.AddSpacer(10)

        layout.Add(wx.StaticText(self,-1,"view range"),0,wx.ALIGN_CENTER)
        layout.AddSpacer(5)

        llayout = wx.BoxSizer(wx.HORIZONTAL)
        llayout.Add(wx.StaticText(self,-1,"min:"),0,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(5)
        llayout.Add(self.axminctrl,0,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(10)
        llayout.Add(wx.StaticText(self,-1,"max:"),0,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(5)
        llayout.Add(self.axmaxctrl,0,wx.ALIGN_CENTER_VERTICAL)
        layout.Add(llayout,0,wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT,border=10)
        go = wx.Button(self,-1,"auto adjust")
        go.Bind(wx.EVT_BUTTON,self.OnGo_axis)
        layout.AddSpacer(5)
        layout.Add(go,0,wx.ALIGN_CENTER)

        layout.AddSpacer(10)
        layout.Add(wx.StaticLine(self,-1,size=(-1,2)),0,wx.EXPAND)
        layout.AddSpacer(10)

        ok = wx.Button(self,-1,"OK")
        cancel = wx.Button(self,-1,"Cancel")
        apply = wx.Button(self,-1,"Apply")
        llayout = wx.BoxSizer(wx.HORIZONTAL)
        llayout.Add(ok,0)
        llayout.Add(cancel,0)
        llayout.Add(apply,0)
        layout.Add(llayout,0,wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT,border=10)
        layout.AddSpacer(5)

        ok.Bind(wx.EVT_BUTTON,self.OnOK)
        self.scale_ax.Bind(wx.EVT_COMBOBOX,self.OnScaleCB)
        cancel.Bind(wx.EVT_BUTTON,lambda e:self.EndModal(wx.ID_CANCEL))
        apply.Bind(wx.EVT_BUTTON,self.OnApply)

        self.Fit()

    def ShowModal(self):
        return super().ShowModal() == wx.ID_OK

    def OnApply(self,event):
        if self.min >= self.max:
            return
        if not np.isfinite([self.min,self.max]).all():
            wx.MessageBox(f"invalid data")
            return
        if self.axis.type == status.AxisType.X:
            self.axis.ref.xscale = self.scale
            self.axis.ref.xlim = (self.min,self.max)
        else:
            self.axis.ref.yscale = self.scale
            self.axis.ref.ylim = (self.min,self.max)
        self.axis.ref.update()
        self.axis.wx.Refresh()
        wx.Yield()

    def OnGo_axis(self,event):
        self.axis.ref.autorange()
        axmin,axmax = self.axis.ref.xlim if self.axis.type == status.AxisType.X else self.axis.ref.ylim
        scale = self.axis.ref.xscale if self.axis.type == status.AxisType.X else self.axis.ref.yscale
        self.axminctrl.Value = self.scale(scale.inv(axmin))
        self.axmaxctrl.Value = self.scale(scale.inv(axmax))
        self.axis.ref.update()
        self.axis.wx.Refresh()
        wx.Yield()

    def OnScaleCB(self,event):
        sc = self.scale_ax.GetClientData(self.scale_ax.Selection)
        axmin,axmax = self.scale.inv([self.min,self.max])
        self.scale = sc
        self.axminctrl.Value = str(self.scale(axmin))
        self.axmaxctrl.Value = str(self.scale(axmax))

    def OnOK(self,event):
        if not np.isfinite([self.min,self.max]).all():
            wx.MessageBox(f"invalid data")
            return
        else:
            self.EndModal(wx.ID_OK)

    @property
    def min(self):
        return float(self.axminctrl.Value)
    @property
    def max(self):
        return float(self.axmaxctrl.Value)

class ColorBarAxisDialog(wx.Dialog):
    def __init__(self,graph,*args,**dargs):
        self.axis = graph
        super().__init__(self.axis.wx,*args,style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE,**dargs)
        axmin,axmax = self.axis.ref.xlim if self.axis.type == status.AxisType.X else self.axis.ref.ylim
        self.scale = self.axis.ref.xscale if self.axis.type == status.AxisType.X else self.axis.ref.yscale
        vmin,vmax = self.axis.ref.image.vmin,self.axis.ref.image.vmax
        self.axminctrl = FloatInput(self,-1,value=str(axmin))
        self.axmaxctrl = FloatInput(self,-1,value=str(axmax))
        self.vminctrl = FloatInput(self,-1,value=str(vmin))
        self.vmaxctrl = FloatInput(self,-1,value=str(vmax))
        layout = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(layout)
        layout.AddSpacer(5)

        llayout = wx.BoxSizer(wx.HORIZONTAL)
        llayout.Add(wx.StaticText(self,-1,"scale:"),0,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(10)
        self.scale_cb = wx.ComboBox(self,-1)
        self.scale_cb.Append(f"{str(scale.LinearScale())}",scale.LinearScale())
        self.scale_cb.Append(f"{str(scale.Log10Scale())}",scale.Log10Scale())
        self.scale_cb.Append(f"{str(scale.LnScale())}",scale.LnScale())
        self.scale_cb.Append(f"{str(scale.ASinhScale())}",scale.ASinhScale())
        self.scale_cb.Append(f"{str(scale.ASinh10Scale())}",scale.ASinh10Scale())
        self.scale_cb.SetStringSelection(f"{str(self.scale)}")
        llayout.Add(self.scale_cb,0,wx.ALIGN_CENTER_VERTICAL)
        layout.Add(llayout,0,wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT,border=10)
        layout.AddSpacer(10)

        layout.Add(wx.StaticText(self,-1,"view range"),0,wx.ALIGN_CENTER)
        layout.AddSpacer(5)

        llayout = wx.BoxSizer(wx.HORIZONTAL)
        llayout.Add(wx.StaticText(self,-1,"min:"),0,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(5)
        llayout.Add(self.axminctrl,1,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(10)
        llayout.Add(wx.StaticText(self,-1,"max:"),0,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(5)
        llayout.Add(self.axmaxctrl,1,wx.ALIGN_CENTER_VERTICAL)
        layout.Add(llayout,0,wx.EXPAND|wx.LEFT|wx.RIGHT,border=10)
        go = wx.Button(self,-1,"auto adjust")
        go.Bind(wx.EVT_BUTTON,self.OnGo_axis)
        layout.AddSpacer(5)
        layout.Add(go,0,wx.ALIGN_CENTER)

        layout.AddSpacer(10)
        layout.Add(wx.StaticLine(self,-1,size=(-1,2)),0,wx.EXPAND)
        layout.AddSpacer(10)

        layout.Add(wx.StaticText(self,-1,"color range"),0,wx.ALIGN_CENTER)
        layout.AddSpacer(5)

        self.vcheck = wx.CheckBox(self,-1,"scaled value")
        layout.Add(self.vcheck,0,wx.ALIGN_CENTER)
        layout.AddSpacer(5)
        llayout = wx.BoxSizer(wx.HORIZONTAL)
        llayout.Add(wx.StaticText(self,-1,"value min:"),0,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(5)
        llayout.Add(self.vminctrl,1,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(10)
        llayout.Add(wx.StaticText(self,-1,"value max:"),0,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(5)
        llayout.Add(self.vmaxctrl,1,wx.ALIGN_CENTER_VERTICAL)
        layout.Add(llayout,0,wx.EXPAND|wx.LEFT|wx.RIGHT,border=10)

        layout.AddSpacer(5)
        llayout = wx.BoxSizer(wx.HORIZONTAL)
        llayout.Add(wx.StaticText(self,-1,"auto color adjustment:"),0,wx.ALIGN_CENTER_VERTICAL)
        llayout.AddSpacer(10)
        al,ar = self.axis.ref.ref.image.auto_left,self.axis.ref.ref.image.auto_right
        self.autocolor_cb = wx.ComboBox(self,-1)
        self.autocolor_cb.Append(f"0/100",(0,100))
        self.autocolor_cb.Append(f"10/90",(10,90))
        self.autocolor_cb.Append(f"25/75",(25,75))
        self.autocolor_cb.SetStringSelection(f"{al}/{ar}")
        llayout.Add(self.autocolor_cb,0,wx.ALIGN_CENTER_VERTICAL)
        go = wx.Button(self,-1,"auto adjust")
        go.Bind(wx.EVT_BUTTON,self.OnGo)
        llayout.AddSpacer(5)
        llayout.Add(go,0)
        layout.Add(llayout,0,wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT,border=10)

        layout.AddSpacer(10)
        layout.Add(wx.StaticLine(self,-1,size=(-1,2)),0,wx.EXPAND)
        layout.AddSpacer(10)

        ok = wx.Button(self,-1,"OK")
        cancel = wx.Button(self,-1,"Cancel")
        apply = wx.Button(self,-1,"Apply")
        llayout = wx.BoxSizer(wx.HORIZONTAL)
        llayout.Add(ok,0)
        llayout.Add(cancel,0)
        llayout.Add(apply,0)
        layout.Add(llayout,0,wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT,border=10)
        layout.AddSpacer(5)

        self.scale_cb.Bind(wx.EVT_COMBOBOX,self.OnScaleCB)
        self.autocolor_cb.Bind(wx.EVT_COMBOBOX,self.OnAutoColorCB)
        self.vcheck.Bind(wx.EVT_CHECKBOX,self.OnVCheck)
        ok.Bind(wx.EVT_BUTTON,self.OnOK)
        cancel.Bind(wx.EVT_BUTTON,lambda e:self.EndModal(wx.ID_CANCEL))
        apply.Bind(wx.EVT_BUTTON,self.OnApply)

        self.Fit()

    def ShowModal(self):
        return super().ShowModal() == wx.ID_OK

    def OnApply(self,event):
        if self.min >= self.max:
            return
        if self.vmin > self.vmax:
            return
        if not np.isfinite([self.min,self.max,self.vmin,self.vmax]).all():
            wx.MessageBox(f"invalid data")
            return
        self.axis.ref.ref.vscale = self.scale_cb.GetClientData(self.scale_cb.Selection)
        if self.axis.type == status.AxisType.X:
            self.axis.ref.xlim = (self.min,self.max)
        else:
            self.axis.ref.ylim = (self.min,self.max)
        self.axis.ref.ref.set(vmin=self.vmin,vmax=self.vmax)
        self.axis.ref.update()
        self.axis.wx.Refresh()
        wx.Yield()

    def OnVCheck(self,event):
        if self.vcheck.IsChecked():
            self.vminctrl.Value = str(self.scale(float(self.vminctrl.Value)))
            self.vmaxctrl.Value = str(self.scale(float(self.vmaxctrl.Value)))
        else:
            self.vminctrl.Value = str(self.scale.inv(float(self.vminctrl.Value)))
            self.vmaxctrl.Value = str(self.scale.inv(float(self.vmaxctrl.Value)))

    def OnScaleCB(self,event):
        sc = self.scale_cb.GetClientData(self.scale_cb.Selection)
        axmin,axmax = self.scale.inv([self.min,self.max])
        vmin,vmax = self.vmin,self.vmax
        self.scale = sc
        self.axminctrl.Value = str(self.scale(axmin))
        self.axmaxctrl.Value = str(self.scale(axmax))
        self.vminctrl.Value = str(self.scale(vmin)) if self.vcheck.IsChecked() else str(vmin)
        self.vmaxctrl.Value = str(self.scale(vmax)) if self.vcheck.IsChecked() else str(vmax)

    def OnAutoColorCB(self,event):
        sc = self.autocolor_cb.GetClientData(self.autocolor_cb.Selection)
        self.axis.ref.ref.image.auto_left,self.axis.ref.ref.image.auto_right = sc
        self.axis.ref.ref.update()

    def OnGo_axis(self,event):
        self.axis.ref.autorange()
        axmin,axmax = self.axis.ref.xlim if self.axis.type == status.AxisType.X else self.axis.ref.ylim
        scale = self.axis.ref.xscale if self.axis.type == status.AxisType.X else self.axis.ref.yscale
        self.axminctrl.Value = self.scale(scale.inv(axmin))
        self.axmaxctrl.Value = self.scale(scale.inv(axmax))
        self.axis.ref.update()
        self.axis.wx.Refresh()
        wx.Yield()

    def OnGo(self,event):
        self.axis.ref.ref.image.auto_colorrange()
        vmin,vmax = self.axis.ref.image.vmin,self.axis.ref.image.vmax
        if self.vcheck.IsChecked():
            self.vminctrl.Value = self.scale(vmin)
            self.vmaxctrl.Value = self.scale(vmax)
        else:
            self.vminctrl.Value = vmin
            self.vmaxctrl.Value = vmax
        self.axis.ref.update()
        self.axis.wx.Refresh()
        wx.Yield()

    def OnOK(self,event):
        if not np.isfinite([self.min,self.max,self.vmin,self.vmax]).all():
            wx.MessageBox(f"invalid data")
            return
        else:
            self.EndModal(wx.ID_OK)

    @property
    def min(self):
        return float(self.axminctrl.Value)
    @property
    def max(self):
        return float(self.axmaxctrl.Value)
    @property
    def vmin(self):
        if self.vcheck.IsChecked():
            return float(self.scale.inv(float(self.vminctrl.Value)))
        else:
            return float(self.vminctrl.Value)
    @property
    def vmax(self):
        if self.vcheck.IsChecked():
            return float(self.scale.inv(float(self.vmaxctrl.Value)))
        else:
            return float(self.vmaxctrl.Value)