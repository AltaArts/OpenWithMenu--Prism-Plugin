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
#
####################################################
####################################################
#
#           SEND TO MENU PLUGIN
#           by Joshua Breckeen
#                Alta Arts
#
#   This PlugIn adds a SendToMenu to the right-click-menu of an image 
#   in the Media Tab.  By adding program executables to the Send To Menu 
#   list in the Prism Settings, a user can quickly open an image in an 
#   editor of choice.
#
####################################################


try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

import os, subprocess, json

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_SendToMenu_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        #   Global Settings File
        pluginLocation = os.path.dirname(os.path.dirname(__file__))
        global settingsFile
        settingsFile = os.path.join(pluginLocation, "SendToMenu_Config.json")

        #   Callbacks
        self.core.registerCallback("mediaPlayerContextMenuRequested", self.mediaPlayerContextMenuRequested, plugin=self)
        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self)
        

    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True
    
    #   Called with Callback
    @err_catcher(name=__name__)
    def mediaPlayerContextMenuRequested(self, origin, menu):        #   Adds SendToMenu to Media Image Right-Click-Menu

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

        #   Adds Send To Menu
        sendToMenu = QMenu("Send to", origin)
        menu.addMenu(sendToMenu)

        #   Loads SettingsFile
        sendToList = self.loadSettings()

        #   Populates SendToMenu and connects function calls
        for item in sendToList:
            progName = item["Name"]
            progPath = item["Path"]

            sendToAct = QAction(progName, sendToMenu)
            sendToAct.triggered.connect(lambda x=None, progPath=progPath: self.sendToProgram(progPath, filePath))
            sendToMenu.addAction(sendToAct)

    #   Opens Selected Image in Program
    @err_catcher(name=__name__)
    def sendToProgram(self, progPath, filePath):

        cmd = f'"{progPath}" "{filePath}"'
        subprocess.Popen(cmd)

    #   Called with Callback
    @err_catcher(name=__name__)
    def userSettings_loadUI(self, origin):      #   ADDING "Send To Menu" TO SETTINGS

        #   Loads Settings File
        sendToList = self.loadSettings()
        headerLabels = ["Name", "Path"]

        # Create a Widget
        origin.w_sendTo = QWidget()
        origin.lo_sendTo = QVBoxLayout(origin.w_sendTo)

        #   Send To Menu UI List
        gb_sendTo = QGroupBox("Send To Programs")
        lo_sendTo = QVBoxLayout()
        gb_sendTo.setLayout(lo_sendTo)

        tw_sendTo = QTableWidget()
        tw_sendTo.setColumnCount(len(headerLabels))
        tw_sendTo.setHorizontalHeaderLabels(headerLabels)
        tw_sendTo.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tw_sendTo.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        #   Adds Buttons
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

        #   Sets Columns
        tw_sendTo.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        #   Makes ReadOnly
        tw_sendTo.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #   Executes button actions
        b_addSendTo.clicked.connect(lambda: self.addSendToExe(origin, tw_sendTo))
        b_removeSendTo.clicked.connect(lambda: self.removeSendToExe(origin, tw_sendTo))

        #   Populates lists from Settings File Data
        for item in sendToList:
            row_position = tw_sendTo.rowCount()
            tw_sendTo.insertRow(row_position)
            tw_sendTo.setItem(row_position, 0, QTableWidgetItem(item.get("Name", "")))
            tw_sendTo.setItem(row_position, 1, QTableWidgetItem(item.get("Path", "")))

        # Add Tab to User Settings
        origin.addTab(origin.w_sendTo, "Send To Menu")


    @err_catcher(name=__name__)
    def addSendToExe(self, origin, tw_sendTo):

        #   Calls Custon Dialog
        dialog = AddSendToDialog(origin)

        #   Adds Name and Path to UI List
        if dialog.exec_() == QDialog.Accepted:
            name, path = dialog.getValues()

            if name and path:
                row_position = tw_sendTo.rowCount()
                tw_sendTo.insertRow(row_position)
                tw_sendTo.setItem(row_position, 0, QTableWidgetItem(name))
                tw_sendTo.setItem(row_position, 1, QTableWidgetItem(path))

            #   Saves UI List to JSON file
            self.saveSettings(tw_sendTo)


    @err_catcher(name=__name__)
    def removeSendToExe(self, origin, tw_sendTo):

        selectedRow = tw_sendTo.currentRow()

        if selectedRow != -1:
            tw_sendTo.removeRow(selectedRow)

            #   Saves UI List to JSON file
            self.saveSettings(tw_sendTo)


    @err_catcher(name=__name__)
    def loadSettings(self):

        #   Loads Global Settings File JSON
        try:
            with open(settingsFile, "r") as json_file:
                data = json.load(json_file)
                return data
            
        except FileNotFoundError:
            return []


    @err_catcher(name=__name__)
    def saveSettings(self, tw_sendTo):

        data = []

        #   Populates data[] from UI List
        for row in range(tw_sendTo.rowCount()):
            nameItem = tw_sendTo.item(row, 0)
            pathItem = tw_sendTo.item(row, 1)

            if nameItem and pathItem:
                name = nameItem.text()
                location = pathItem.text()

                data.append({"Name": name, "Path": location})

        #   Saves to Global JSON File
        with open(settingsFile, "w") as json_file:
            json.dump(data, json_file, indent=4)


class AddSendToDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        #   Sets up Custon File Selection UI
        self.setWindowTitle("Add Send To Application")

        self.l_name = QLabel("Short Name (displayed in Menus):")
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

        #   Calls native File Dialog
        windowTitle = "Select Send To Application"
        fileFilter = "Executable (*.exe);;All files (*)"
        selectedPath, _ = QFileDialog.getOpenFileName(self, windowTitle, "", fileFilter)

        if selectedPath:
            self.l_location.setText(selectedPath)


    def getValues(self):
        name = self.le_name.text()
        location = self.l_location.text()
        return name, location