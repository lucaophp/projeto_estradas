# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'estacas.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

import os
import sip
from PyQt4 import QtCore, QtGui
from PyQt4 import uic

from PyQt4.QtCore import QObject
from PyQt4.QtCore import QVariant, SIGNAL
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QDialog
from qgis._core import QgsCoordinateReferenceSystem
from qgis._core import QgsFeature
from qgis._core import QgsField
from qgis._core import QgsGeometry
from qgis._core import QgsMapLayerRegistry
from qgis._core import QgsPoint
from qgis._core import QgsRectangle
from qgis._core import QgsVectorLayer
from qgis._gui import QgsMapCanvasLayer
from qgis._gui import QgsMapToolEmitPoint
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *

from ..model.utils import decdeg2dms
import subprocess
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
sip.setapi('QString',2)
sip.setapi('QVariant',2)
FORMTRANSFERENCIA_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../view/ui/Topo_dialog_server.ui'))
class Transferencia(QtGui.QDialog,FORMTRANSFERENCIA_CLASS):
	def __init__(self, ip):
		super(Transferencia, self).__init__(None)
		self.ip = ip
		self.setupUi(self)
		self.lblIP.setText("%s"%ip)
