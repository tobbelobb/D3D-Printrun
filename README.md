# D3D-Printrun

This version of Printrun adds a Quality Control user interface mode to Pronterface.
QC-mode is intented to help beginners run functionality checks on newly assembled RepRaps.
It is part of the D3D Workshop Kit, and its documentation will live here: http://opensourceecology.org/wiki/3D_Printer_Quality_Control_Interface

If you're not interested in QC-mode, then use https://github.com/kliment/Printrun instead.

For more on D3D, see http://opensourceecology.org/wiki/D3D_Development

# Installation

D3D-Printrun has the same dependencies as Printrun and does not remove or interfere with any functionality from Printrun.
Installation and usage instructions at https://github.com/kliment/Printrun will work.
Ubuntu/Debian and D3D Porteus instructions are included here for easier reference, since those are the distros used by the D3D Project.

## Ubuntu/Debian

You can run Printrun directly from source. Fetch and install the dependencies using

`sudo apt-get install python-serial python-wxgtk2.8 python-pyglet python-numpy cython python-libxml2 python-gobject python-dbus python-psutil python-cairosvg git`

Clone the repository

`git clone https://github.com/tobbelobb/D3D_Printrun.git`

and you can start using D3D-Printrun from the D3D-Printrun directory created by the git clone command, for example by typing

`./D3D_Printrun/pronterface`

## D3D-Porteus

This program is intended for inclusion by default in the D3D Porteus USB stick that participants recieve during workshops.

# Using D3D-Printrun

To use the Quality Control user interface, go through the menus

`Settings -> Options -> User interface -> Interface mode -> QC`

and click OK.

To hard-code Pronterface to start directly into QC mode, add the following line to the bottom of .pronsolerc

`set uimode QC`

# LICENSE

```
D3D-Printrun is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

D3D-Printrun is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Printrun.  If not, see <http://www.gnu.org/licenses/>.
```

All scripts should contain this license note, if not, feel free to ask us. Please note that files where it is difficult to state this license note (such as images) are distributed under the same terms.
