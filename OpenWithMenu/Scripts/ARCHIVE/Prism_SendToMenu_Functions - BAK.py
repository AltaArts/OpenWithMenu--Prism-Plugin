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

import os, subprocess, platform

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_SendToMenu_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        self.core.callbacks.registerCallback("mediaPlayerContextMenuRequested", self.mediaPlayerContextMenuRequested, plugin=self)
        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self)                                        #   ADDED

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


    @err_catcher(name=__name__)                                                                         #   ADDED
    def userSettings_loadUI(self, origin):      #   ADDING "Send To Menu" TO SETTINGS

        sendToAppList = {
            "Gimp": "C:\Gimp",
            "fSpy": "C:\fSpy"
        }

        headerLabels = ["Name", "Location"]


        # create a widget
        origin.w_sendTo = QWidget()
        origin.lo_sendTo = QVBoxLayout(origin.w_sendTo)

        #   Send To Menu UI List
        gb_sendTo = QGroupBox("Send To Programs")
        lo_sendTo = QVBoxLayout()
        gb_sendTo.setLayout(lo_sendTo)


        tw_sendTo = QTableWidget()
        tw_sendTo.setColumnCount(len(headerLabels))
        tw_sendTo.setHorizontalHeaderLabels(headerLabels)

#        tw_sendTo.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tw_sendTo.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tw_sendTo.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)


        w_sendTo = QWidget()
        lo_sendToButtons = QHBoxLayout()
        b_addSendTo = QPushButton("Add")
        b_removeSendTo = QPushButton("Remove")

        w_sendTo.setLayout(lo_sendToButtons)
        lo_sendToButtons.addStretch()
        lo_sendToButtons.addWidget(b_addSendTo)
        lo_sendToButtons.addWidget(b_removeSendTo)

        lo_sendTo.addWidget(tw_sendTo)
        lo_sendTo.addWidget(w_sendTo)
        origin.lo_sendTo.addWidget(gb_sendTo)

        tw_sendTo.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        )

        b_addSendTo.clicked.connect(lambda: self.addSendToExe(origin, tw_sendTo))
        b_removeSendTo.clicked.connect(lambda: self.removeSendToExe(origin, tw_sendTo))

        # add tab to User Settings
        origin.addTab(origin.w_sendTo, "Send To Menu")


    @err_catcher(name=__name__)                                                                         #   ADDED
    def addSendToExe(self, origin, tw_sendTo):

        dialog = AddSendToDialog(origin)

        if dialog.exec_() == QDialog.Accepted:
            name, location = dialog.getValues()

            if name and location:
                row_position = tw_sendTo.rowCount()
                tw_sendTo.insertRow(row_position)
                tw_sendTo.setItem(row_position, 0, QTableWidgetItem(name))
                tw_sendTo.setItem(row_position, 1, QTableWidgetItem(location))



    @err_catcher(name=__name__)                                                                         #   ADDED
    def removeSendToExe(self, origin, tw_sendTo):

        selectedRow = tw_sendTo.currentRow()

        if selectedRow != -1:
            tw_sendTo.removeRow(selectedRow)



#    @err_catcher(name=__name__)            #   NEEDED????
#    def refreshPlugins(self):
#        self.tw_plugins.setRowCount(0)
#        self.tw_plugins.setSortingEnabled(False)
#        plugins = self.core.plugins.getPlugins()

class AddSendToDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Send To Application")

        self.l_name = QLabel("Name:")
        self.le_name = QLineEdit()

        self.l_location = QLabel("Location:")
        self.but_location = QPushButton("Select Location")
        self.but_location.clicked.connect(self.selectLocation)

        self.but_ok = QPushButton("OK")
        self.but_ok.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.l_name)
        layout.addWidget(self.le_name)
        layout.addWidget(self.l_location)
        layout.addWidget(self.but_location)
        layout.addWidget(self.but_ok)

        self.setLayout(layout)
        self.setFixedWidth(300)


    def selectLocation(self):
        windowTitle = "Select Send To Application"
        fileFilter = "Executable (*.exe);;All files (*)"
        selectedPath, _ = QFileDialog.getOpenFileName(self, windowTitle, "", fileFilter)

        if selectedPath:
            self.l_location.setText(selectedPath)

    def getValues(self):
        name = self.le_name.text()
        location = self.l_location.text()
        return name, location