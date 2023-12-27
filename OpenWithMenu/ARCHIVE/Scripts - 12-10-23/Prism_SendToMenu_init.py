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


from Prism_SendToMenu_Variables import Prism_SendToMenu_Variables
from Prism_SendToMenu_Functions import Prism_SendToMenu_Functions


class Prism_SendToMenu(Prism_SendToMenu_Variables, Prism_SendToMenu_Functions):
    def __init__(self, core):
        Prism_SendToMenu_Variables.__init__(self, core, self)
        Prism_SendToMenu_Functions.__init__(self, core, self)
