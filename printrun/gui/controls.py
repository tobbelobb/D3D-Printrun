# This file is part of the Printrun suite.
#
# Printrun is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Printrun is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Printrun.  If not, see <http://www.gnu.org/licenses/>.

import wx

from .xybuttons import XYButtons, XYButtonsMini
from .zbuttons import ZButtons, ZButtonsMini
from .graph import Graph
from .widgets import TempGauge
from wx.lib.agw.floatspin import FloatSpin

from .utils import make_button, make_custom_button
try: import simplejson as json
except ImportError: import json


class XYZControlsSizer(wx.GridBagSizer):

    def __init__(self, root, parentpanel = None):
        super(XYZControlsSizer, self).__init__()
        if not parentpanel: parentpanel = root.panel
        root.xyb = XYButtons(parentpanel, root.moveXY, root.homeButtonClicked, root.spacebarAction, root.bgcolor, zcallback=root.moveZ)
        self.Add(root.xyb, pos = (0, 1), flag = wx.ALIGN_CENTER)
        root.zb = ZButtons(parentpanel, root.moveZ, root.bgcolor)
        self.Add(root.zb, pos = (0, 2), flag = wx.ALIGN_CENTER)
        wx.CallAfter(root.xyb.SetFocus)

def add_extra_controls(self, root, parentpanel, extra_buttons = None, mini_mode = False):
    standalone_mode = extra_buttons is not None
    base_line = 1 if standalone_mode else 2

    if standalone_mode:
        gauges_base_line = base_line + 10
    elif mini_mode and root.display_graph:
        gauges_base_line = base_line + 6
    else:
        gauges_base_line = base_line + 5
    tempdisp_line = gauges_base_line + (2 if root.display_gauges else 0)
    if mini_mode and root.display_graph:
        e_base_line = base_line + 3
    else:
        e_base_line = base_line + 2

    pos_mapping = {
        "htemp_label": (base_line + 0, 0),
        "htemp_off": (base_line + 0, 2),
        "htemp_val": (base_line + 0, 3),
        "htemp_set": (base_line + 0, 4),
        "btemp_label": (base_line + 1, 0),
        "btemp_off": (base_line + 1, 2),
        "btemp_val": (base_line + 1, 3),
        "btemp_set": (base_line + 1, 4),
        "ebuttons": (e_base_line + 0, 0),
        "esettings": (e_base_line + 1, 0),
        "speedcontrol": (e_base_line + 2, 0),
        "htemp_gauge": (gauges_base_line + 0, 0),
        "btemp_gauge": (gauges_base_line + 1, 0),
        "tempdisp": (tempdisp_line, 0),
        "extrude": (3, 0),
        "reverse": (3, 2),
    }

    span_mapping = {
        "htemp_label": (1, 2),
        "htemp_off": (1, 1),
        "htemp_val": (1, 1),
        "htemp_set": (1, 1 if root.display_graph else 2),
        "btemp_label": (1, 2),
        "btemp_off": (1, 1),
        "btemp_val": (1, 1),
        "btemp_set": (1, 1 if root.display_graph else 2),
        "ebuttons": (1, 5 if root.display_graph else 6),
        "esettings": (1, 5 if root.display_graph else 6),
        "speedcontrol": (1, 5 if root.display_graph else 6),
        "htemp_gauge": (1, 5 if mini_mode else 6),
        "btemp_gauge": (1, 5 if mini_mode else 6),
        "tempdisp": (1, 5 if mini_mode else 6),
        "extrude": (1, 2),
        "reverse": (1, 3),
    }

    if standalone_mode:
        pos_mapping["tempgraph"] = (base_line + 5, 0)
        span_mapping["tempgraph"] = (5, 6)
    elif mini_mode:
        pos_mapping["tempgraph"] = (base_line + 2, 0)
        span_mapping["tempgraph"] = (1, 5)
    else:
        pos_mapping["tempgraph"] = (base_line + 0, 5)
        span_mapping["tempgraph"] = (5, 1)

    if mini_mode:
        pos_mapping["etool_label"] = (0, 0)
        pos_mapping["etool_val"] = (0, 1)
        pos_mapping["edist_label"] = (0, 2)
        pos_mapping["edist_val"] = (0, 3)
        pos_mapping["edist_unit"] = (0, 4)
    else:
        pos_mapping["edist_label"] = (0, 0)
        pos_mapping["edist_val"] = (1, 0)
        pos_mapping["edist_unit"] = (1, 1)
        pos_mapping["efeed_label"] = (0, 2)
        pos_mapping["efeed_val"] = (1, 2)
        pos_mapping["efeed_unit"] = (1, 3)

    def add(name, widget, *args, **kwargs):
        kwargs["pos"] = pos_mapping[name]
        if name in span_mapping:
            kwargs["span"] = span_mapping[name]
        if "container" in kwargs:
            container = kwargs["container"]
            del kwargs["container"]
        else:
            container = self
        container.Add(widget, *args, **kwargs)

    # Hotend & bed temperatures #

    # Hotend temp
    add("htemp_label", wx.StaticText(parentpanel, -1, _("Heat:")), flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
    htemp_choices = [root.temps[i] + " (" + i + ")" for i in sorted(root.temps.keys(), key = lambda x:root.temps[x])]

    root.settoff = make_button(parentpanel, _("Off"), lambda e: root.do_settemp("off"), _("Switch Hotend Off"), size = (38, -1), style = wx.BU_EXACTFIT)
    root.printerControls.append(root.settoff)
    add("htemp_off", root.settoff)

    if root.settings.last_temperature not in map(float, root.temps.values()):
        htemp_choices = [str(root.settings.last_temperature)] + htemp_choices
    root.htemp = wx.ComboBox(parentpanel, -1, choices = htemp_choices,
                             style = wx.CB_DROPDOWN, size = (80, -1))
    root.htemp.SetToolTip(wx.ToolTip(_("Select Temperature for Hotend")))
    root.htemp.Bind(wx.EVT_COMBOBOX, root.htemp_change)

    add("htemp_val", root.htemp)
    root.settbtn = make_button(parentpanel, _("Set"), root.do_settemp, _("Switch Hotend On"), size = (38, -1), style = wx.BU_EXACTFIT)
    root.printerControls.append(root.settbtn)
    add("htemp_set", root.settbtn, flag = wx.EXPAND)

    # Bed temp
    add("btemp_label", wx.StaticText(parentpanel, -1, _("Bed:")), flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
    btemp_choices = [root.bedtemps[i] + " (" + i + ")" for i in sorted(root.bedtemps.keys(), key = lambda x:root.temps[x])]

    root.setboff = make_button(parentpanel, _("Off"), lambda e: root.do_bedtemp("off"), _("Switch Heated Bed Off"), size = (38, -1), style = wx.BU_EXACTFIT)
    root.printerControls.append(root.setboff)
    add("btemp_off", root.setboff)

    if root.settings.last_bed_temperature not in map(float, root.bedtemps.values()):
        btemp_choices = [str(root.settings.last_bed_temperature)] + btemp_choices
    root.btemp = wx.ComboBox(parentpanel, -1, choices = btemp_choices,
                             style = wx.CB_DROPDOWN, size = (80, -1))
    root.btemp.SetToolTip(wx.ToolTip(_("Select Temperature for Heated Bed")))
    root.btemp.Bind(wx.EVT_COMBOBOX, root.btemp_change)
    add("btemp_val", root.btemp)

    root.setbbtn = make_button(parentpanel, _("Set"), root.do_bedtemp, _("Switch Heated Bed On"), size = (38, -1), style = wx.BU_EXACTFIT)
    root.printerControls.append(root.setbbtn)
    add("btemp_set", root.setbbtn, flag = wx.EXPAND)

    root.btemp.SetValue(str(root.settings.last_bed_temperature))
    root.htemp.SetValue(str(root.settings.last_temperature))

    # added for an error where only the bed would get (pla) or (abs).
    # This ensures, if last temp is a default pla or abs, it will be marked so.
    # if it is not, then a (user) remark is added. This denotes a manual entry

    for i in btemp_choices:
        if i.split()[0] == str(root.settings.last_bed_temperature).split('.')[0] or i.split()[0] == str(root.settings.last_bed_temperature):
            root.btemp.SetValue(i)
    for i in htemp_choices:
        if i.split()[0] == str(root.settings.last_temperature).split('.')[0] or i.split()[0] == str(root.settings.last_temperature):
            root.htemp.SetValue(i)

    if '(' not in root.btemp.Value:
        root.btemp.SetValue(root.btemp.Value + ' (user)')
    if '(' not in root.htemp.Value:
        root.htemp.SetValue(root.htemp.Value + ' (user)')

    # Speed control #
    speedpanel = root.newPanel(parentpanel)
    speedsizer = wx.BoxSizer(wx.HORIZONTAL)
    speedsizer.Add(wx.StaticText(speedpanel, -1, _("Print speed:")), flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)

    root.speed_slider = wx.Slider(speedpanel, -1, 100, 1, 300)
    speedsizer.Add(root.speed_slider, 1, flag = wx.EXPAND)

    root.speed_spin = FloatSpin(speedpanel, -1, value = 100, min_val = 1, max_val = 300, digits = 0, style = wx.ALIGN_LEFT, size = (80, -1))
    speedsizer.Add(root.speed_spin, 0, flag = wx.ALIGN_CENTER_VERTICAL)
    root.speed_label = wx.StaticText(speedpanel, -1, _("%"))
    speedsizer.Add(root.speed_label, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)

    def speedslider_set(event):
        root.do_setspeed()
        root.speed_setbtn.SetBackgroundColour(wx.NullColour)
    root.speed_setbtn = make_button(speedpanel, _("Set"), speedslider_set, _("Set print speed factor"), size = (38, -1), style = wx.BU_EXACTFIT)
    root.printerControls.append(root.speed_setbtn)
    speedsizer.Add(root.speed_setbtn, flag = wx.ALIGN_CENTER)
    speedpanel.SetSizer(speedsizer)
    add("speedcontrol", speedpanel, flag = wx.EXPAND)

    def speedslider_spin(event):
        value = root.speed_spin.GetValue()
        root.speed_setbtn.SetBackgroundColour("red")
        root.speed_slider.SetValue(value)
    root.speed_spin.Bind(wx.EVT_SPINCTRL, speedslider_spin)

    def speedslider_scroll(event):
        value = root.speed_slider.GetValue()
        root.speed_setbtn.SetBackgroundColour("red")
        root.speed_spin.SetValue(value)
    root.speed_slider.Bind(wx.EVT_SCROLL, speedslider_scroll)

    # Temperature gauges #

    if root.display_gauges:
        root.hottgauge = TempGauge(parentpanel, size = (-1, 24), title = _("Heater:"), maxval = 300, bgcolor = root.bgcolor)
        add("htemp_gauge", root.hottgauge, flag = wx.EXPAND)
        root.bedtgauge = TempGauge(parentpanel, size = (-1, 24), title = _("Bed:"), maxval = 150, bgcolor = root.bgcolor)
        add("btemp_gauge", root.bedtgauge, flag = wx.EXPAND)

        def hotendgauge_scroll_setpoint(e):
            rot = e.GetWheelRotation()
            if rot > 0:
                root.do_settemp(str(root.hsetpoint + 1))
            elif rot < 0:
                root.do_settemp(str(max(0, root.hsetpoint - 1)))

        def bedgauge_scroll_setpoint(e):
            rot = e.GetWheelRotation()
            if rot > 0:
                root.do_settemp(str(root.bsetpoint + 1))
            elif rot < 0:
                root.do_settemp(str(max(0, root.bsetpoint - 1)))
        root.hottgauge.Bind(wx.EVT_MOUSEWHEEL, hotendgauge_scroll_setpoint)
        root.bedtgauge.Bind(wx.EVT_MOUSEWHEEL, bedgauge_scroll_setpoint)

    # Temperature (M105) feedback display #
    root.tempdisp = wx.StaticText(parentpanel, -1, "", style = wx.ST_NO_AUTORESIZE)

    def on_tempdisp_size(evt):
        root.tempdisp.Wrap(root.tempdisp.GetSize().width)
    root.tempdisp.Bind(wx.EVT_SIZE, on_tempdisp_size)

    def tempdisp_setlabel(label):
        wx.StaticText.SetLabel(root.tempdisp, label)
        root.tempdisp.Wrap(root.tempdisp.GetSize().width)
        root.tempdisp.SetSize((-1, root.tempdisp.GetBestSize().height))
    root.tempdisp.SetLabel = tempdisp_setlabel
    add("tempdisp", root.tempdisp, flag = wx.EXPAND)

    # Temperature graph #

    if root.display_graph:
        root.graph = Graph(parentpanel, wx.ID_ANY, root)
        add("tempgraph", root.graph, flag = wx.EXPAND | wx.ALL, border = 5)
        root.graph.Bind(wx.EVT_LEFT_DOWN, root.graph.show_graph_window)

    # Extrusion controls #

    # Extrusion settings
    esettingspanel = root.newPanel(parentpanel)
    esettingssizer = wx.GridBagSizer()
    esettingssizer.SetEmptyCellSize((0, 0))
    root.edist = FloatSpin(esettingspanel, -1, value = root.settings.last_extrusion, min_val = 0, max_val = 1000, size = (90, -1), digits = 1)
    root.edist.SetBackgroundColour((225, 200, 200))
    root.edist.SetForegroundColour("black")
    root.edist.Bind(wx.EVT_SPINCTRL, root.setfeeds)
    root.edist.Bind(wx.EVT_TEXT, root.setfeeds)
    add("edist_label", wx.StaticText(esettingspanel, -1, _("Length:")), container = esettingssizer, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.RIGHT | wx.LEFT, border = 5)
    add("edist_val", root.edist, container = esettingssizer, flag = wx.ALIGN_CENTER | wx.RIGHT, border = 5)
    unit_label = _("mm") if mini_mode else _("mm @")
    add("edist_unit", wx.StaticText(esettingspanel, -1, unit_label), container = esettingssizer, flag = wx.ALIGN_CENTER | wx.RIGHT, border = 5)
    root.edist.SetToolTip(wx.ToolTip(_("Amount to Extrude or Retract (mm)")))
    if not mini_mode:
        root.efeedc = FloatSpin(esettingspanel, -1, value = root.settings.e_feedrate, min_val = 0, max_val = 50000, size = (90, -1), digits = 1)
        root.efeedc.SetToolTip(wx.ToolTip(_("Extrude / Retract speed (mm/min)")))
        root.efeedc.SetBackgroundColour((225, 200, 200))
        root.efeedc.SetForegroundColour("black")
        root.efeedc.Bind(wx.EVT_SPINCTRL, root.setfeeds)
        root.efeedc.Bind(wx.EVT_TEXT, root.setfeeds)
        add("efeed_val", root.efeedc, container = esettingssizer, flag = wx.ALIGN_CENTER | wx.RIGHT, border = 5)
        add("efeed_label", wx.StaticText(esettingspanel, -1, _("Speed:")), container = esettingssizer, flag = wx.ALIGN_LEFT)
        add("efeed_unit", wx.StaticText(esettingspanel, -1, _("mm/\nmin")), container = esettingssizer, flag = wx.ALIGN_CENTER)
    else:
        root.efeedc = None
    esettingspanel.SetSizer(esettingssizer)
    add("esettings", esettingspanel, flag = wx.ALIGN_LEFT)

    if not standalone_mode:
        ebuttonspanel = root.newPanel(parentpanel)
        ebuttonssizer = wx.BoxSizer(wx.HORIZONTAL)
        if root.settings.extruders > 1:
            etool_sel_panel = esettingspanel if mini_mode else ebuttonspanel
            etool_label = wx.StaticText(etool_sel_panel, -1, _("Tool:"))
            if root.settings.extruders == 2:
                root.extrudersel = wx.Button(etool_sel_panel, -1, "0", style = wx.BU_EXACTFIT)
                root.extrudersel.SetToolTip(wx.ToolTip(_("Click to switch current extruder")))

                def extrudersel_cb(event):
                    if root.extrudersel.GetLabel() == "1":
                        new = "0"
                    else:
                        new = "1"
                    root.extrudersel.SetLabel(new)
                    root.tool_change(event)
                root.extrudersel.Bind(wx.EVT_BUTTON, extrudersel_cb)
                root.extrudersel.GetValue = root.extrudersel.GetLabel
                root.extrudersel.SetValue = root.extrudersel.SetLabel
            else:
                choices = [str(i) for i in range(0, root.settings.extruders)]
                root.extrudersel = wx.ComboBox(etool_sel_panel, -1, choices = choices,
                                               style = wx.CB_DROPDOWN | wx.CB_READONLY,
                                               size = (50, -1))
                root.extrudersel.SetToolTip(wx.ToolTip(_("Select current extruder")))
                root.extrudersel.SetValue(choices[0])
                root.extrudersel.Bind(wx.EVT_COMBOBOX, root.tool_change)
            root.printerControls.append(root.extrudersel)
            if mini_mode:
                add("etool_label", etool_label, container = esettingssizer, flag = wx.ALIGN_CENTER)
                add("etool_val", root.extrudersel, container = esettingssizer)
            else:
                ebuttonssizer.Add(etool_label, flag = wx.ALIGN_CENTER)
                ebuttonssizer.Add(root.extrudersel)

        for key in ["extrude", "reverse"]:
            desc = root.cpbuttons[key]
            btn = make_custom_button(root, ebuttonspanel, desc,
                                     style = wx.BU_EXACTFIT)
            ebuttonssizer.Add(btn, 1, flag = wx.EXPAND)

        ebuttonspanel.SetSizer(ebuttonssizer)
        add("ebuttons", ebuttonspanel, flag = wx.EXPAND)
    else:
        for key, btn in extra_buttons.items():
            add(key, btn, flag = wx.EXPAND)

class QCControlsSizer(wx.BoxSizer):
    """ Buttons for quality control check of newly assembled 3D printer in chronological order with implicit dependencies """
    def __init__(self, root, parentpanel = None, standalone_mode = False):
        super(QCControlsSizer, self).__init__(wx.VERTICAL)
        if not parentpanel: parentpanel = root.panel
        fgsizer = wx.FlexGridSizer(rows = 13, cols = 4, vgap = 5, hgap = 5)
        #self.Add((-1, 12))

        # Step 1
        root.moverightbutton = wx.Button(parentpanel, label = "Move 10 mm away from origo along X-axis")  # G1 X10 F600
        root.moveright_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        root.step1helpbutton = wx.Button(parentpanel, label="Step 1 help")
        root.step1helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                                      "Should show X-carriage moving 10 mm to the right.",
                                      "Step 1 Help",
                                      style=wx.OK).ShowModal())
        # Save button size and use for rest of buttons
        buttonwidth = root.moverightbutton.Size[0]
        buttonheight = root.moverightbutton.Size[1]
        # Step 2
        root.moveforwardbutton = wx.Button(parentpanel, label = "Move 10 mm away from origo along Y-axis")  # G1 Y10 F600
        root.moveforward_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        root.step2helpbutton = wx.Button(parentpanel, label="Step 2 help")
        root.step2helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                                      "Should show video where printer moves its bed 10 mm forwards.",
                                      "Step 2 Help",
                                      style=wx.OK).ShowModal())
        # Step 3
        root.moveupwardbutton = wx.Button(parentpanel, label = "Move 1 mm upwards", size=(buttonwidth, -1))  # G1 Z1 F200
        root.step3helpbutton = wx.Button(parentpanel, label="Step 3 help")
        root.step3helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                     "This box should contain a little video showing a print head travelling happily 1 mm upwards.",
                                      "Step 3 Help",
                                      style=wx.OK).ShowModal())
        root.moveupward_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        ## Step 4
        root.endstopbutton = wx.Button(parentpanel, label = "Check endstop statuses", size=(buttonwidth, -1))  # M119
        root.step4helpbutton = wx.Button(parentpanel, label="Step 4 help")
        root.step4helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                "Confirm that X-max and Y-min only triggers when pressed." +
                " Hold metal object (preferrably a heat bed) directly below Z-probe to trigger it." +
                " LED should light up.",
                                      "Step 4 Help",
                                      style=wx.OK).ShowModal())
        root.endstop_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        ## Step 5
        root.homexbutton = wx.Button(parentpanel, label = "Home X axis", size=(buttonwidth, -1))  # G28 X
        root.step5helpbutton = wx.Button(parentpanel, label="Step 5 help")
        root.step5helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                "The print head should move towards the X-limit switch while searching for X home." +
                " After homing X, the printer knows where the print head is along the X-axis (right/left-direction)." +
                " This help dialog should show a little video.",
                                      "Step 5 Help",
                                      style=wx.OK).ShowModal())
        root.homex_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        ## Step 6
        root.homeybutton = wx.Button(parentpanel, label = "Home Y axis", size=(buttonwidth, -1))  # G28 Y
        root.step6helpbutton = wx.Button(parentpanel, label="Step 6 help")
        root.step6helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                "The print bed should move towards the Y-limit switch while searching for Y home." +
                " After homing Y, the printer knows where the bed is." +
                " This help dialog should show a little video.",
                                      "Step 6 Help",
                                      style=wx.OK).ShowModal())
        root.homey_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        ## Step 7
        root.homeallbutton = wx.Button(parentpanel, label = "Home all axes", size=(buttonwidth, -1))  # G28. G1 Z1?
        root.step7helpbutton = wx.Button(parentpanel, label="Step 7 help")
        root.step7helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                "This re-homes the X and Y axes before trying to trigger the Z-probe at the center of the print bed." +
                " When the Z-sensor has triggered, the printer knows where the print head is along the Z-axis (up/down-direction).",
                                      "Step 7 Help",
                                      style=wx.OK).ShowModal())
        root.homeall_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        # Step 8
        root.bedtempreadingbutton = wx.Button(parentpanel, label = "Read Print Bed Temperature", size=(buttonwidth, -1))  # M105 printbedsomething
        root.step8helpbutton = wx.Button(parentpanel, label="Step 8 help")
        root.step8helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                "Check that print bed temperature readings are close to ambient temperature (probably 18C - 30C).",
                                      "Step 8 Help",
                                      style=wx.OK).ShowModal())
        root.bedtempreading_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        # Step 9
        root.headtempreadingbutton = wx.Button(parentpanel, label = "Read Print Head Temperature", size=(buttonwidth, -1))  # M105 headsomething
        root.step9helpbutton = wx.Button(parentpanel, label="Step 9 help")
        root.step9helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                "Check that print head temperature readings are close to ambient temperature (probably 19C - 30C).",
                                      "Step 9 Help",
                                      style=wx.OK).ShowModal())
        root.headtempreading_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        ## Step 10
        root.setbedtempbutton = wx.Button(parentpanel, label = "Set print bed temp to 40C", size=(buttonwidth, -1))  # M140 S40
        root.step10helpbutton = wx.Button(parentpanel, label="Step 10 help")
        root.step10helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                "This will run current through the print bed heater element for the first time." +
                " Pull the plug if something melts or burns." +
                " Use temp reading button to verify that bed temperature increases towards 40C.",
                                      "Step 10 Help",
                                      style=wx.OK).ShowModal())
        root.setbedtemp_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        # Step 11
        root.setheadtempbutton = wx.Button(parentpanel, label = "Set print head temp to 200C", size=(buttonwidth, -1))  # M104 S200
        root.step11helpbutton = wx.Button(parentpanel, label="Step 11 help")
        root.step11helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                "This will run current through the print head heater element for the first time." +
                " Pull the plug if something melts or burns." +
                " Use temp reading button to verify that bed temperature increases towards 200C.",
                                      "Step 11 Help",
                                      style=wx.OK).ShowModal())
        root.setheadtemp_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        ## Step 12
        root.extrude10mmbutton = wx.Button(parentpanel, label = "Extrude 10mm", size=(buttonwidth, -1))  # What command? See pronsole extrude
        root.step12helpbutton = wx.Button(parentpanel, label="Step 12 help")
        root.step12helpbutton.Bind(wx.EVT_BUTTON, lambda event: wx.MessageDialog(parentpanel,
                "Feed filament to the extruder manually until it grips it." +
                " The extruder should feed the filament down to the print head." +
                " Verify that molten plastic flows freely.",
                                      "Step 12 Help",
                                      style=wx.OK).ShowModal())
        root.extrude10mm_works = wx.CheckBox(parentpanel, wx.ID_ANY)
        # Step 13
        root.done = wx.Button(parentpanel, label = "Victory! Open Pronterface to print a cube!")
        root.done.Bind(wx.EVT_BUTTON, lambda event: self.ondoneclick(event, root))
        # Texts for leftmost column
        step1text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 1: ")
        step2text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 2: ")
        step3text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 3: ")
        step4text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 4: ")
        step5text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 5: ")
        step6text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 6: ")
        step7text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 7: ")
        step8text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 8: ")
        step9text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 9: ")
        step10text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 10: ")
        step11text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 11: ")
        step12text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 12: ")
        step13text = wx.StaticText(parentpanel, wx.ID_ANY, " Step 13: ")
        # Bind all checkboxes to the quality control buttons' reload function
        root.moveright_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.moveforward_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.moveupward_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.endstop_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.homex_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.homey_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.homeall_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.bedtempreading_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.headtempreading_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.setbedtemp_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.setheadtemp_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        root.extrude10mm_works.Bind(wx.EVT_CHECKBOX, root.qcbuttons_reload)
        # Add widgets to FlexGridSizer
        fgsizer.AddMany([(step1text, 0, wx.ALIGN_CENTER),
                         (root.moverightbutton, 0, wx.ALIGN_CENTER),
                         (root.step1helpbutton, 0, wx.ALIGN_CENTER),
                         (root.moveright_works, 0, wx.ALIGN_CENTER),
                         (step2text, 0, wx.ALIGN_CENTER),
                         (root.moveforwardbutton, 0, wx.ALIGN_CENTER),
                         (root.step2helpbutton, 0, wx.ALIGN_CENTER),
                         (root.moveforward_works, 0, wx.ALIGN_CENTER),
                         (step3text, 0, wx.ALIGN_CENTER),
                         (root.moveupwardbutton, 0, wx.ALIGN_CENTER),
                         (root.step3helpbutton, 0, wx.ALIGN_CENTER),
                         (root.moveupward_works, 0, wx.ALIGN_CENTER),
                         (step4text, 0, wx.ALIGN_CENTER),
                         (root.endstopbutton, 0, wx.ALIGN_CENTER),
                         (root.step4helpbutton, 0, wx.ALIGN_CENTER),
                         (root.endstop_works, 0, wx.ALIGN_CENTER),
                         (step5text, 0, wx.ALIGN_CENTER),
                         (root.homexbutton, 0, wx.ALIGN_CENTER),
                         (root.step5helpbutton, 0, wx.ALIGN_CENTER),
                         (root.homex_works, 0, wx.ALIGN_CENTER),
                         (step6text, 0, wx.ALIGN_CENTER),
                         (root.homeybutton, 0, wx.ALIGN_CENTER),
                         (root.step6helpbutton, 0, wx.ALIGN_CENTER),
                         (root.homey_works, 0, wx.ALIGN_CENTER),
                         (step7text, 0, wx.ALIGN_CENTER),
                         (root.homeallbutton, 0, wx.ALIGN_CENTER),
                         (root.step7helpbutton, 0, wx.ALIGN_CENTER),
                         (root.homeall_works, 0, wx.ALIGN_CENTER),
                         (step8text, 0, wx.ALIGN_CENTER),
                         (root.bedtempreadingbutton, 0, wx.ALIGN_CENTER),
                         (root.step8helpbutton, 0, wx.ALIGN_CENTER),
                         (root.bedtempreading_works, 0, wx.ALIGN_CENTER),
                         (step9text, 0, wx.ALIGN_CENTER),
                         (root.headtempreadingbutton, 0, wx.ALIGN_CENTER),
                         (root.step9helpbutton, 0, wx.ALIGN_CENTER),
                         (root.headtempreading_works, 0, wx.ALIGN_CENTER),
                         (step10text, 0, wx.ALIGN_CENTER),
                         (root.setbedtempbutton, 0, wx.ALIGN_CENTER),
                         (root.step10helpbutton, 0, wx.ALIGN_CENTER),
                         (root.setbedtemp_works, 0, wx.ALIGN_CENTER),
                         (step11text, 0, wx.ALIGN_CENTER),
                         (root.setheadtempbutton, 0, wx.ALIGN_CENTER),
                         (root.step11helpbutton, 0, wx.ALIGN_CENTER),
                         (root.setheadtemp_works, 0, wx.ALIGN_CENTER),
                         (step12text, 0, wx.ALIGN_CENTER),
                         (root.extrude10mmbutton, 0, wx.ALIGN_CENTER),
                         (root.step12helpbutton, 0, wx.ALIGN_CENTER),
                         (root.extrude10mm_works, 0, wx.ALIGN_CENTER),
                         (step13text, 0, wx.ALIGN_CENTER),
                         (root.done, 0, wx.ALIGN_CENTER),
                         ])
        self.Add(fgsizer, 1, flag=wx.EXPAND, border = 0)

    def ondoneclick(self, event, root):
        """ To be executed when Quality control is done. Takes user to standard interface with first print loaded. """
        root.settings.uimode = "Standard"
        root.reload_ui()
        try:
            recent_files = json.loads(root.settings.recentfiles)
            root.loadfile(event, recent_files[0])  # Try to load recent file
        except:
            pass

class ControlsSizer(wx.GridBagSizer):

    def __init__(self, root, parentpanel = None, standalone_mode = False, mini_mode = False):
        super(ControlsSizer, self).__init__()
        if not parentpanel: parentpanel = root.panel
        if mini_mode: self.make_mini(root, parentpanel)
        else: self.make_standard(root, parentpanel, standalone_mode)

    def make_standard(self, root, parentpanel, standalone_mode):
        lltspanel = root.newPanel(parentpanel)
        llts = wx.BoxSizer(wx.HORIZONTAL)
        lltspanel.SetSizer(llts)
        self.Add(lltspanel, pos = (0, 0), span = (1, 6))
        xyzpanel = root.newPanel(parentpanel)
        self.xyzsizer = XYZControlsSizer(root, xyzpanel)
        xyzpanel.SetSizer(self.xyzsizer)
        self.Add(xyzpanel, pos = (1, 0), span = (1, 6), flag = wx.ALIGN_CENTER)

        self.extra_buttons = {}
        pos_mapping = {"extrude": (4, 0),
                       "reverse": (4, 2),
                       }
        span_mapping = {"extrude": (1, 2),
                        "reverse": (1, 3),
                        }
        for key, desc in root.cpbuttons.items():
            if not standalone_mode and key in ["extrude", "reverse"]:
                continue
            panel = lltspanel if key == "motorsoff" else parentpanel
            btn = make_custom_button(root, panel, desc)
            if key == "motorsoff":
                llts.Add(btn)
            elif not standalone_mode:
                self.Add(btn, pos = pos_mapping[key], span = span_mapping[key], flag = wx.EXPAND)
            else:
                self.extra_buttons[key] = btn

        root.xyfeedc = wx.SpinCtrl(lltspanel, -1, str(root.settings.xy_feedrate), min = 0, max = 50000, size = (97, -1))
        root.xyfeedc.SetToolTip(wx.ToolTip(_("Set Maximum Speed for X & Y axes (mm/min)")))
        llts.Add(wx.StaticText(lltspanel, -1, _("XY:")), flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        llts.Add(root.xyfeedc)
        llts.Add(wx.StaticText(lltspanel, -1, _("mm/min Z:")), flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        root.zfeedc = wx.SpinCtrl(lltspanel, -1, str(root.settings.z_feedrate), min = 0, max = 50000, size = (90, -1))
        root.zfeedc.SetToolTip(wx.ToolTip(_("Set Maximum Speed for Z axis (mm/min)")))
        llts.Add(root.zfeedc,)

        root.xyfeedc.Bind(wx.EVT_SPINCTRL, root.setfeeds)
        root.zfeedc.Bind(wx.EVT_SPINCTRL, root.setfeeds)
        root.xyfeedc.Bind(wx.EVT_TEXT, root.setfeeds)
        root.zfeedc.Bind(wx.EVT_TEXT, root.setfeeds)
        root.zfeedc.SetBackgroundColour((180, 255, 180))
        root.zfeedc.SetForegroundColour("black")

        if not standalone_mode:
            add_extra_controls(self, root, parentpanel, None)

    def make_mini(self, root, parentpanel):
        root.xyb = XYButtonsMini(parentpanel, root.moveXY, root.homeButtonClicked,
                                 root.spacebarAction, root.bgcolor,
                                 zcallback = root.moveZ)
        self.Add(root.xyb, pos = (1, 0), span = (1, 4), flag = wx.ALIGN_CENTER)
        root.zb = ZButtonsMini(parentpanel, root.moveZ, root.bgcolor)
        self.Add(root.zb, pos = (0, 4), span = (2, 1), flag = wx.ALIGN_CENTER)
        wx.CallAfter(root.xyb.SetFocus)

        pos_mapping = {"motorsoff": (0, 0),
                       }
        span_mapping = {"motorsoff": (1, 4),
                        }
        btn = make_custom_button(root, parentpanel, root.cpbuttons["motorsoff"])
        self.Add(btn, pos = pos_mapping["motorsoff"], span = span_mapping["motorsoff"], flag = wx.EXPAND)

        add_extra_controls(self, root, parentpanel, None, True)
