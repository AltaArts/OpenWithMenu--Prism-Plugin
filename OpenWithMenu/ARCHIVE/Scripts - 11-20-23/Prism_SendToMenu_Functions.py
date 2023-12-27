# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2023 Richard Frangenberg
# Copyright (C) 2023 Prism Software GmbH
#
# Licensed under GNU LGPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.


try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

import os, subprocess

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_SendToMenu_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        self.core.callbacks.registerCallback("mediaPlayerContextMenuRequested", self.mediaPlayerContextMenuRequested, plugin=self)

    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True
    

    @err_catcher(name=__name__)
    def mediaPlayerContextMenuRequested(self, origin, menu):

        if not type(origin.origin).__name__ == "MediaBrowser":
            return

        version = origin.origin.getCurrentVersion()
        if not version:
            return

        if not origin.seq:
            return

        filePath = origin.seq[0]
        if os.path.splitext(filePath)[1] in self.core.media.videoFormats:
            return

        sendToMenu = QMenu("Send to", origin)
        menu.addMenu(sendToMenu)

        sendToProgs = ["Gimp", "fSpy", "SynthEyes"]          #   TODO  - HARDCODED

        for prog in sendToProgs:
            sendToAct = QAction(prog, sendToMenu)
            sendToAct.triggered.connect(lambda x=None, prog=prog: self.sendToProgram(prog, filePath))
            sendToMenu.addAction(sendToAct)


    @err_catcher(name=__name__)
    def sendToProgram(self, prog, filePath):

        if prog == "Gimp":                                                      #   TODO HARDCODED
            exe = r"C:\Program Files\GIMP 2\bin\gimp-2.10.exe"

        if prog == "fSpy":
            exe = r"C:\Program Files\fSpy-1.0.3-win\fspy-opener.bat"

        if prog == "SynthEyes":
            exe = r"C:\Program Files\Andersson Technologies LLC\SynthEyes\SynthEyes64.exe"

        cmd = f'"{exe}" "{filePath}"'
        subprocess.Popen(cmd)