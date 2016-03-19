#!/usr/bin/env python

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

import sys
import getopt

try:
    import wx  # NOQA
except:
    print("wxPython is not installed. This program requires wxPython to run.")
    if sys.version_info.major >= 3:
        print("""\
As you are currently running python3, this is most likely because wxPython is
not yet available for python3. You should try running with python2 instead.""")
        sys.exit(-1)
    else:
        raise

from printrun.pronterface import PronterApp

if __name__ == '__main__':

    from printrun.printcore import __version__ as printcore_version

    usage = "Usage:\n" + \
            "  pronterface [OPTION]\n\n" + \
            "Options:\n" + \
            "  -V, --version\t\t\tPrint program's version number and exit\n" + \
            "  -h, --help\t\t\tPrint this help message and exit\n"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hV", ["help", "version"])
    except getopt.GetoptError, err:
        print str(err)
        print usage
        sys.exit(2)
    for o, a in opts:
        if o in ('-V', '--version'):
            print "printrun " + printcore_version
            sys.exit(0)
        elif o in ('-h', '--help'):
            print usage
            sys.exit(0)

    app = PronterApp(False)
    try:
        app.MainLoop()
    except KeyboardInterrupt:
        pass
    del app
