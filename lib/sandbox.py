#!/usr/bin/python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebPage


class Sandbox(object):  
    """Execute javascript in webkit browser."""
    def __init__(self, parent=None):
    	app = QApplication(['dummy'])
    	self.app = app
        self.webpage = QWebPage()
        self.webframe = self.webpage.mainFrame()
        self.webframe.load(QUrl(''))

    def execute(self, script):
        a = self.webframe.evaluateJavaScript(script)
        if a:
            return str(a.toString())

    def close(self):
    	self.app.exit()

