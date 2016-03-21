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

import logging

try:
    import wx
except:
    logging.error(_("WX is not installed. This program requires WX to run."))
    raise

from printrun.utils import install_locale
install_locale('pronterface')

from .controls import ControlsSizer, add_extra_controls, QCControlsSizer
from .viz import VizPane
from .log import LogPane
from .toolbar import MainToolbar

class ToggleablePane(wx.BoxSizer):

    def __init__(self, root, label, parentpanel, parentsizers):
        super(ToggleablePane, self).__init__(wx.HORIZONTAL)
        if not parentpanel: parentpanel = root.panel
        self.root = root
        self.visible = True
        self.parentpanel = parentpanel
        self.parentsizers = parentsizers
        self.panepanel = root.newPanel(parentpanel)
        self.button = wx.Button(parentpanel, -1, label, size = (22, 18), style = wx.BU_EXACTFIT)
        self.button.Bind(wx.EVT_BUTTON, self.toggle)

    def toggle(self, event):
        if self.visible:
            self.Hide(self.panepanel)
            self.on_hide()
        else:
            self.Show(self.panepanel)
            self.on_show()
        self.visible = not self.visible
        self.button.SetLabel(">" if self.button.GetLabel() == "<" else "<")

class LeftPaneToggleable(ToggleablePane):
    def __init__(self, root, parentpanel, parentsizers):
        super(LeftPaneToggleable, self).__init__(root, "<", parentpanel, parentsizers)
        self.Add(self.panepanel, 0, wx.EXPAND)
        self.Add(self.button, 0)

    def set_sizer(self, sizer):
        self.panepanel.SetSizer(sizer)

    def on_show(self):
        for sizer in self.parentsizers:
            sizer.Layout()

    def on_hide(self):
        for sizer in self.parentsizers:
            # Expand right splitterwindow
            if isinstance(sizer, wx.SplitterWindow):
                if sizer.shrinked:
                    button_width = self.button.GetSize()[0]
                    sizer.SetSashPosition(sizer.GetSize()[0] - button_width)
            else:
                sizer.Layout()

class LogPaneToggleable(ToggleablePane):
    def __init__(self, root, parentpanel, parentsizers):
        super(LogPaneToggleable, self).__init__(root, ">", parentpanel, parentsizers)
        self.Add(self.button, 0)
        pane = LogPane(root, self.panepanel)
        self.panepanel.SetSizer(pane)
        self.Add(self.panepanel, 1, wx.EXPAND)
        self.splitter = self.parentpanel.GetParent()

    def on_show(self):
        self.splitter.shrinked = False
        self.splitter.SetSashPosition(self.splitter.GetSize()[0] - self.orig_width)
        self.splitter.SetMinimumPaneSize(self.orig_min_size)
        self.splitter.SetSashGravity(self.orig_gravity)
        if hasattr(self.splitter, "SetSashSize"): self.splitter.SetSashSize(self.orig_sash_size)
        if hasattr(self.splitter, "SetSashInvisible"): self.splitter.SetSashInvisible(False)
        for sizer in self.parentsizers:
            sizer.Layout()

    def on_hide(self):
        self.splitter.shrinked = True
        self.orig_width = self.splitter.GetSize()[0] - self.splitter.GetSashPosition()
        button_width = self.button.GetSize()[0]
        self.orig_min_size = self.splitter.GetMinimumPaneSize()
        self.orig_gravity = self.splitter.GetSashGravity()
        self.splitter.SetMinimumPaneSize(button_width)
        self.splitter.SetSashGravity(1)
        self.splitter.SetSashPosition(self.splitter.GetSize()[0] - button_width)
        if hasattr(self.splitter, "SetSashSize"):
            self.orig_sash_size = self.splitter.GetSashSize()
            self.splitter.SetSashSize(0)
        if hasattr(self.splitter, "SetSashInvisible"): self.splitter.SetSashInvisible(True)
        for sizer in self.parentsizers:
            sizer.Layout()

class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # this list will contain all controls that should be only enabled
        # when we're connected to a printer
        self.panel = wx.Panel(self, -1)
        self.reset_ui()
        self.statefulControls = []

    def reset_ui(self):
        self.panels = []
        self.printerControls = []

    def newPanel(self, parent, add_to_list = True):
        panel = wx.Panel(parent)
        self.registerPanel(panel, add_to_list)
        return panel

    def registerPanel(self, panel, add_to_list = True):
        panel.SetBackgroundColour(self.bgcolor)
        if add_to_list: self.panels.append(panel)

    def createQCGui(self):
        self.outermost_vbox = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.outermost_vbox)  # Outermost structure is a stack

        # Create the toolbar (port menu, connect button). Don't register it
        upperpanel = self.newPanel(self.panel)
        self.toolbarsizer = MainToolbar(self, upperpanel, reduced = True)
        upperpanel.SetSizer(self.toolbarsizer)
        self.outermost_vbox.Add(upperpanel, 0, wx.EXPAND)  # Place toolbar on top of outermost stack

        # Split the lower part of outermost_vbox in two
        outermost_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.outermost_vbox.Add(outermost_hbox, 1, wx.EXPAND)

#        splitter = wx.SplitterWindow(self, style = wx.SP_BORDER)

        # Create the lower box with buttons and serial
        controls_sizer = QCControlsSizer(self)  # Controls sizer holds all buttons
        outermost_hbox.Add(controls_sizer, 2, wx.EXPAND)

        # Create the log
        log_pane = LogPane(self)
        outermost_hbox.Add(log_pane, 1, wx.EXPAND)


        # Make sure we exit correctly
        self.Bind(wx.EVT_CLOSE, self.kill)

    def createTabbedGui(self):
        self.notesizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook = wx.Notebook(self.panel)
        self.notebook.SetBackgroundColour(self.bgcolor)
        page1panel = self.newPanel(self.notebook)
        page2panel = self.newPanel(self.notebook)
        self.mainsizer_page1 = wx.BoxSizer(wx.VERTICAL)
        page1panel1 = self.newPanel(page1panel)
        page1panel2 = self.newPanel(page1panel)
        self.toolbarsizer = MainToolbar(self, page1panel1, use_wrapsizer = True)
        page1panel1.SetSizer(self.toolbarsizer)
        self.mainsizer_page1.Add(page1panel1, 0, wx.EXPAND)
        self.lowersizer = wx.BoxSizer(wx.HORIZONTAL)
        page1panel2.SetSizer(self.lowersizer)
        leftsizer = wx.BoxSizer(wx.VERTICAL)
        controls_sizer = ControlsSizer(self, page1panel2, True)
        leftsizer.Add(controls_sizer, 1, wx.ALIGN_CENTER)
        rightsizer = wx.BoxSizer(wx.VERTICAL)
        extracontrols = wx.GridBagSizer()
        add_extra_controls(extracontrols, self, page1panel2, controls_sizer.extra_buttons)
        rightsizer.AddStretchSpacer()
        rightsizer.Add(extracontrols, 0, wx.ALIGN_CENTER)
        self.lowersizer.Add(leftsizer, 0, wx.ALIGN_CENTER | wx.RIGHT, border = 10)
        self.lowersizer.Add(rightsizer, 1, wx.ALIGN_CENTER)
        self.mainsizer_page1.Add(page1panel2, 1)
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.splitterwindow = wx.SplitterWindow(page2panel, style = wx.SP_3D)
        page2sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        page2panel1 = self.newPanel(self.splitterwindow)
        page2sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        page2panel2 = self.newPanel(self.splitterwindow)
        vizpane = VizPane(self, page2panel1)
        page2sizer1.Add(vizpane, 1, wx.EXPAND)
        page2sizer2.Add(LogPane(self, page2panel2), 1, wx.EXPAND)
        page2panel1.SetSizer(page2sizer1)
        page2panel2.SetSizer(page2sizer2)
        self.splitterwindow.SetMinimumPaneSize(1)
        self.splitterwindow.SetSashGravity(0.5)
        self.splitterwindow.SplitVertically(page2panel1, page2panel2,
                                            self.settings.last_sash_position)
        self.mainsizer.Add(self.splitterwindow, 1, wx.EXPAND)
        page1panel.SetSizer(self.mainsizer_page1)
        page2panel.SetSizer(self.mainsizer)
        self.notesizer.Add(self.notebook, 1, wx.EXPAND)
        self.notebook.AddPage(page1panel, _("Commands"))
        self.notebook.AddPage(page2panel, _("Status"))
        if self.settings.uimode == _("Tabbed with platers"):
            from printrun.stlplater import StlPlaterPanel
            from printrun.gcodeplater import GcodePlaterPanel
            page3panel = StlPlaterPanel(parent = self.notebook,
                                        callback = self.platecb,
                                        build_dimensions = self.build_dimensions_list,
                                        circular_platform = self.settings.circular_bed,
                                        simarrange_path = self.settings.simarrange_path,
                                        antialias_samples = int(self.settings.antialias3dsamples))
            page4panel = GcodePlaterPanel(parent = self.notebook,
                                          callback = self.platecb,
                                          build_dimensions = self.build_dimensions_list,
                                          circular_platform = self.settings.circular_bed,
                                          antialias_samples = int(self.settings.antialias3dsamples))
            self.registerPanel(page3panel)
            self.registerPanel(page4panel)
            self.notebook.AddPage(page3panel, _("Plater"))
            self.notebook.AddPage(page4panel, _("G-Code Plater"))
        self.panel.SetSizer(self.notesizer)
        self.panel.Bind(wx.EVT_MOUSE_EVENTS, self.editbutton)
        self.Bind(wx.EVT_CLOSE, self.kill)

        # Custom buttons
        if wx.VERSION > (2, 9): self.cbuttonssizer = wx.WrapSizer(wx.HORIZONTAL)
        else: self.cbuttonssizer = wx.GridBagSizer()
        self.cbuttonssizer = wx.GridBagSizer()
        self.centerpanel = self.newPanel(page1panel2)
        self.centerpanel.SetSizer(self.cbuttonssizer)
        rightsizer.Add(self.centerpanel, 0, wx.ALIGN_CENTER)
        rightsizer.AddStretchSpacer()

        self.panel.SetSizerAndFit(self.notesizer)

        self.cbuttons_reload()
        minsize = self.lowersizer.GetMinSize()  # lower pane
        minsize[1] = self.notebook.GetSize()[1]
        self.SetMinSize(self.ClientToWindowSize(minsize))  # client to window
        self.Fit()

    def createGui(self, compact = False, mini = False):
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        upperpanel = self.newPanel(self.panel, False)  # upperpanel holds Connect button and such
        self.toolbarsizer = MainToolbar(self, upperpanel)
        self.lowersizer = wx.BoxSizer(wx.HORIZONTAL)
        lowerpanel = self.newPanel(self.panel)  # lowerpanel unaffected by color change
        upperpanel.SetSizer(self.toolbarsizer)
        lowerpanel.SetSizer(self.lowersizer)
        leftpanel = self.newPanel(lowerpanel)  # leftpanel holds arrow to fold away all controllers left of plater
        left_pane = LeftPaneToggleable(self, leftpanel, [self.lowersizer])
        leftpanel.SetSizer(left_pane)
        left_real_panel = left_pane.panepanel
        # Controls panel holds all controls. The complete left side of Pronterface window
        controls_panel = self.newPanel(left_real_panel)
        controls_sizer = ControlsSizer(self, controls_panel, mini_mode = mini)
        controls_panel.SetSizer(controls_sizer)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(controls_panel, 1, wx.EXPAND)
        left_pane.set_sizer(left_sizer)
        self.lowersizer.Add(leftpanel, 0, wx.EXPAND)
        if not compact:  # Use a splitterwindow to group viz and log
            rightpanel = self.newPanel(lowerpanel)
            rightsizer = wx.BoxSizer(wx.VERTICAL)
            rightpanel.SetSizer(rightsizer)
            self.splitterwindow = wx.SplitterWindow(rightpanel, style = wx.SP_3D)
            self.splitterwindow.SetMinimumPaneSize(150)
            self.splitterwindow.SetSashGravity(0.8)
            rightsizer.Add(self.splitterwindow, 1, wx.EXPAND)
            vizpanel = self.newPanel(self.splitterwindow)
            logpanel = self.newPanel(self.splitterwindow)  # Logpanel holds fold button for the log
            self.splitterwindow.SplitVertically(vizpanel, logpanel,
                                                self.settings.last_sash_position)
            self.splitterwindow.shrinked = False
        else:
            vizpanel = self.newPanel(lowerpanel)
            logpanel = self.newPanel(left_real_panel)
        viz_pane = VizPane(self, vizpanel)
        # Custom buttons
        if wx.VERSION > (2, 9): self.cbuttonssizer = wx.WrapSizer(wx.HORIZONTAL)
        else: self.cbuttonssizer = wx.GridBagSizer()
        self.centerpanel = self.newPanel(vizpanel)
        self.centerpanel.SetSizer(self.cbuttonssizer)
        viz_pane.Add(self.centerpanel, 0, flag = wx.ALIGN_CENTER)
        vizpanel.SetSizer(viz_pane)
        if compact:
            log_pane = LogPane(self, logpanel)
        else:
            log_pane = LogPaneToggleable(self, logpanel, [self.lowersizer])
            left_pane.parentsizers.append(self.splitterwindow)
        logpanel.SetSizer(log_pane)
        if not compact:
            self.lowersizer.Add(rightpanel, 1, wx.EXPAND)
        else:
            left_sizer.Add(logpanel, 1, wx.EXPAND)
            self.lowersizer.Add(vizpanel, 1, wx.EXPAND)
        self.mainsizer.Add(upperpanel, 0, wx.EXPAND)
        self.mainsizer.Add(lowerpanel, 1, wx.EXPAND)
        self.panel.SetSizer(self.mainsizer)
        self.panel.Bind(wx.EVT_MOUSE_EVENTS, self.editbutton)
        self.Bind(wx.EVT_CLOSE, self.kill)

        self.mainsizer.Layout()
        # This prevents resizing below a reasonnable value
        # We sum the lowersizer (left pane / viz / log) min size
        # the toolbar height and the statusbar/menubar sizes
        minsize = [0, 0]
        minsize[0] = self.lowersizer.GetMinSize()[0]  # lower pane
        minsize[1] = max(viz_pane.GetMinSize()[1], controls_sizer.GetMinSize()[1])
        minsize[1] += self.toolbarsizer.GetMinSize()[1]  # toolbar height
        displaysize = wx.DisplaySize()
        minsize[0] = min(minsize[0], displaysize[0])
        minsize[1] = min(minsize[1], displaysize[1])
        self.SetMinSize(self.ClientToWindowSize(minsize))  # client to window

        self.cbuttons_reload()

    # There's a comment in MainWindow's __init__ saying
    # "this list will contain all controls that should be only enabled
    #  when we're connected to a printer"
    # xy/z-buttons are explicitly enabled/disabled in gui_set_(dis)connected
    def qcbuttons_reload(self, event):
        """ Handles all dependencies between control buttons in QC uimode """
        # All buttons that depend only on working connection
        # Try to enable few but disable many
        if self.p.online:
            self.moverightbutton.Enable()
            self.moveright_works.Enable()
            self.moveforwardbutton.Enable()
            self.moveforward_works.Enable()
            self.moveupwardbutton.Enable()
            self.moveupward_works.Enable()
            self.endstopbutton.Enable()
            self.endstop_works.Enable()
            self.bedtempreadingbutton.Enable()
            self.bedtempreading_works.Enable()
            self.headtempreadingbutton.Enable()
            self.headtempreading_works.Enable()
        else:
            self.moverightbutton.Disable()  # No step 1, 2, 3 or 4 (moving + endstops)
            self.moveright_works.Disable()
            self.moveforwardbutton.Disable()
            self.moveforward_works.Disable()
            self.moveupwardbutton.Disable()
            self.moveupward_works.Disable()
            self.endstopbutton.Disable()
            self.endstop_works.Disable()
            self.homexbutton.Disable()  # No step 5, 6 or 7 (homing)
            self.homex_works.Disable()
            self.homeybutton.Disable()
            self.homey_works.Disable()
            self.homeallbutton.Disable()
            self.homeall_works.Disable()
            self.bedtempreadingbutton.Disable()  # No step 8, 9, 10 or 11 (temps)
            self.bedtempreading_works.Disable()
            self.headtempreadingbutton.Disable()
            self.headtempreading_works.Disable()
            self.setbedtempbutton.Disable()
            self.setbedtemp_works.Disable()
            self.setheadtempbutton.Disable()
            self.setheadtemp_works.Disable()
            self.extrude10mmbutton.Disable()  # No step 12 (extruder)
            self.extrude10mm_works.Disable()
            self.done.Disable()  # Can't be done with QC
        # Buttons that depend on moveright
        if self.moveright_works.IsChecked() and self.endstop_works.IsChecked():
            self.homexbutton.Enable()
            self.homex_works.Enable()
        else:
            self.homexbutton.Disable()
            self.homex_works.Disable()
            self.homeallbutton.Disable()
            self.homeall_works.Disable()
        # Buttons that depend on moveforward
        if self.moveforward_works.IsChecked() and self.endstop_works.IsChecked():
            self.homeybutton.Enable()
            self.homey_works.Enable()
        else:
            self.homeybutton.Disable()
            self.homey_works.Disable()
            self.homeallbutton.Disable()
            self.homeall_works.Disable()
        if not self.moveupward_works.IsChecked() or not self.endstop_works.IsChecked():
            self.homeallbutton.Disable()
            self.homeall_works.Disable()
        if(self.moveright_works.IsChecked() and
           self.moveforward_works.IsChecked() and
           self.moveupward_works.IsChecked() and
           self.endstop_works.IsChecked() and
           self.homex_works.IsChecked() and
           self.homey_works.IsChecked()):
            self.homeallbutton.Enable()
            self.homeall_works.Enable()
        else:
            self.homeallbutton.Disable()
            self.homeall_works.Disable()
        if self.bedtempreading_works.IsChecked():
            self.setbedtempbutton.Enable()
            self.setbedtemp_works.Enable()
        else:
            self.setbedtempbutton.Disable()
            self.setbedtemp_works.Disable()
        if self.headtempreading_works.IsChecked():
            self.setheadtempbutton.Enable()
            self.setheadtemp_works.Enable()
        else:
            self.setheadtempbutton.Disable()
            self.setheadtemp_works.Disable()
            self.extrude10mmbutton.Disable()
            self.extrude10mm_works.Disable()
        if self.setheadtemp_works.IsChecked():
            self.extrude10mmbutton.Enable()
            self.extrude10mm_works.Enable()
        if (self.moveright_works.IsChecked() and
           self.moveforward_works.IsChecked() and
           self.moveupward_works.IsChecked() and
           self.endstop_works.IsChecked() and
           self.homex_works.IsChecked() and
           self.homey_works.IsChecked() and
           self.homeall_works.IsChecked() and
           self.bedtempreading_works.IsChecked() and
           self.headtempreading_works.IsChecked() and
           self.setbedtemp_works.IsChecked() and
           self.setheadtemp_works.IsChecked() and
           self.extrude10mm_works.IsChecked()):
            self.done.Enable()
        else:
            self.done.Disable()


    def gui_set_connected(self):
        if self.settings.uimode == "QC":
            self.qcbuttons_reload(None)
        else:
            self.xyb.enable()
            self.zb.enable()
        for control in self.printerControls:
            control.Enable()

    def gui_set_disconnected(self):
        if self.settings.uimode == "QC":
            self.qcbuttons_reload(None)
        else:
            self.xyb.disable()
            self.zb.disable()
        self.printbtn.Disable()
        self.pausebtn.Disable()
        self.recoverbtn.Disable()
        for control in self.printerControls:
            control.Disable()
