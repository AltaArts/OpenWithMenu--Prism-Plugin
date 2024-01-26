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
#
#          OPEN WITH MENU PLUGIN
#           by Joshua Breckeen
#                Alta Arts
#
#   This PlugIn adds a OpenWithMenu to the right-click-menu of an image 
#   in the Media Tab.  By adding program executables to the Open with Menu 
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

import os
import subprocess
import json

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_OpenWithMenu_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        #   Global Settings File
        pluginLocation = os.path.dirname(os.path.dirname(__file__))
        self.settingsFile = os.path.join(pluginLocation, "OpenWithMenu_Config.json")

        #   Callbacks
        self.core.registerCallback("textureLibraryTextureContextMenuRequested", self.textureLibraryTextureContextMenuRequested, plugin=self)
        self.core.registerCallback("mediaPlayerContextMenuRequested", self.mediaPlayerContextMenuRequested, plugin=self)
        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self)
        

    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True
    
    #   Called with Callback
    @err_catcher(name=__name__)
    def mediaPlayerContextMenuRequested(self, origin, menu):        #   Adds OpenWithMenu to Media Image Right-Click-Menu

        if not type(origin.origin).__name__ == "MediaBrowser":
            return

        version = origin.origin.getCurrentVersion()
        if not version:
            return

        if not origin.seq:
            return
        
        #   This helps when a media file is activly playing in the Viewer
        try:
            currentFrame = origin.getCurrentFrame()
            filePath = origin.seq[currentFrame]
        except:
            filePath = origin.seq[0]

        #   Adds Open with Menu
        openWithMenu = QMenu("Open with", origin)
        menu.addMenu(openWithMenu)

        #   Loads SettingsFile
        openwithList = self.loadSettings()

        #   Populates OpenWithMenu and connects function calls
        for item in openwithList:
            progName = item["Name"]
            progPath = item["Path"]

            openWithAct = QAction(progName, openWithMenu)
            openWithAct.triggered.connect(lambda x=None, progPath=progPath: self.openWithProgram(progPath, filePath))
            openWithMenu.addAction(openWithAct)


    #   Called with Callback
    @err_catcher(name=__name__)
    def textureLibraryTextureContextMenuRequested(self, origin, menu):        #   Adds OpenWithMenu to Media Image Right-Click-Menu

        if not type(origin).__name__ == "TextureWidget":
            return

        filePath = origin.path

        if os.path.splitext(filePath)[1] in self.core.media.videoFormats:
            return

        #   Adds Open with Menu
        OpenWithMenu = QMenu("Open with", origin)
        menu.addMenu(OpenWithMenu)

        #   Loads SettingsFile
        openwithList = self.loadSettings()

        #   Populates OpenWithMenu and connects function calls
        for item in openwithList:
            progName = item["Name"]
            progPath = item["Path"]

            openWithAct = QAction(progName, OpenWithMenu)
            openWithAct.triggered.connect(lambda x=None, progPath=progPath: self.openWithProgram(progPath, filePath))
            OpenWithMenu.addAction(openWithAct)
    

    #   Opens Selected Image in Program
    @err_catcher(name=__name__)
    def openWithProgram(self, progPath, filePath):

        cmd = f'"{progPath}" "{filePath}"'
        subprocess.Popen(cmd)

    #   Called with Callback
    @err_catcher(name=__name__)
    def userSettings_loadUI(self, origin):      #   ADDING "Open with Menu" TO SETTINGS

        #   Loads Settings File
        openWithList = self.loadSettings()
        headerLabels = ["Name", "Path"]

        # Create a Widget
        origin.w_openWith = QWidget()
        origin.lo_openWith = QVBoxLayout(origin.w_openWith)

        #   Send To Menu UI List
        gb_openWith = QGroupBox("Open With Programs")
        lo_openWith = QVBoxLayout()
        gb_openWith.setLayout(lo_openWith)

        tw_openWith = QTableWidget()
        tw_openWith.setColumnCount(len(headerLabels))
        tw_openWith.setHorizontalHeaderLabels(headerLabels)
        tw_openWith.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tw_openWith.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        #   Sets initial Table size
        tw_openWith.setMinimumHeight(300)  # Adjust the value as needed

        #   Adds Buttons
        w_openWith = QWidget()
        lo_openWithButtons = QHBoxLayout()
        b_addoOpenWith = QPushButton("Add")
        b_removeoOpenWith = QPushButton("Remove")

        w_openWith.setLayout(lo_openWithButtons)
        lo_openWithButtons.addStretch()
        lo_openWithButtons.addWidget(b_addoOpenWith)
        lo_openWithButtons.addWidget(b_removeoOpenWith)

        lo_openWith.addWidget(tw_openWith)
        lo_openWith.addWidget(w_openWith)
        origin.lo_openWith.addWidget(gb_openWith)

        #   Sets Columns
        tw_openWith.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        #   Makes ReadOnly
        tw_openWith.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #   Executes button actions
        b_addoOpenWith.clicked.connect(lambda: self.addOpenWithExe(origin, tw_openWith))
        b_removeoOpenWith.clicked.connect(lambda: self.removeOpenWithExe(origin, tw_openWith))

        #   Populates lists from Settings File Data
        for item in openWithList:
            row_position = tw_openWith.rowCount()
            tw_openWith.insertRow(row_position)
            tw_openWith.setItem(row_position, 0, QTableWidgetItem(item.get("Name", "")))
            tw_openWith.setItem(row_position, 1, QTableWidgetItem(item.get("Path", "")))

        # Add Tab to User Settings
        origin.addTab(origin.w_openWith, "Open with Menu")


    @err_catcher(name=__name__)
    def addOpenWithExe(self, origin, tw_openWith):

        #   Calls Custon Dialog
        dialog = AddOpenWithDialog(origin)

        #   Adds Name and Path to UI List
        if dialog.exec_() == QDialog.Accepted:
            name, path = dialog.getValues()

            if name and path:
                row_position = tw_openWith.rowCount()
                tw_openWith.insertRow(row_position)
                tw_openWith.setItem(row_position, 0, QTableWidgetItem(name))
                tw_openWith.setItem(row_position, 1, QTableWidgetItem(path))

            #   Saves UI List to JSON file
            self.saveSettings(tw_openWith)


    @err_catcher(name=__name__)
    def removeOpenWithExe(self, origin, tw_openWith):

        selectedRow = tw_openWith.currentRow()

        if selectedRow != -1:
            tw_openWith.removeRow(selectedRow)

            #   Saves UI List to JSON file
            self.saveSettings(tw_openWith)


    @err_catcher(name=__name__)
    def loadSettings(self):

        #   Loads Global Settings File JSON
        try:
            with open(self.settingsFile, "r") as json_file:
                data = json.load(json_file)
                return data
            
        except FileNotFoundError:
            return []


    @err_catcher(name=__name__)
    def saveSettings(self, tw_openWith):

        data = []

        #   Populates data[] from UI List
        for row in range(tw_openWith.rowCount()):
            nameItem = tw_openWith.item(row, 0)
            pathItem = tw_openWith.item(row, 1)

            if nameItem and pathItem:
                name = nameItem.text()
                location = pathItem.text()

                data.append({"Name": name, "Path": location})

        #   Saves to Global JSON File
        with open(self.settingsFile, "w") as json_file:
            json.dump(data, json_file, indent=4)


class AddOpenWithDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        #   Sets up Custon File Selection UI
        self.setWindowTitle("Add Open with Application")

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
        windowTitle = "Select Open with Application"
        fileFilter = "Executable (*.exe);;All files (*)"
        selectedPath, _ = QFileDialog.getOpenFileName(self, windowTitle, "", fileFilter)

        if selectedPath:
            self.l_location.setText(selectedPath)


    def getValues(self):
        name = self.le_name.text()
        location = self.l_location.text()
        return name, location