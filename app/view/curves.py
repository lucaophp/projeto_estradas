# -*- coding: utf-8 -*-
import os
import sip

sip.setapi('QString', 2)
from PyQt4 import Qt

from PyQt4 import QtGui, uic

import qgis

import shutil
from ..model.config import extractZIP, Config, compactZIP
from PyQt4.QtCore import QSettings
from PyQt4.QtGui import QAbstractItemView

from qgis._core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis._core import QgsMapLayerRegistry
from qgis._core import QgsRectangle
from qgis._core import QgsVectorFileWriter
from qgis._core import QgsVectorLayer
from qgis._core import QGis
from qgis._gui import QgsMapCanvasLayer
from qgis.utils import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QAction

from ..model.helper.calculos import *
from ..model.curves import Curves as CurvasModel
from ..model.estacas import Estacas

FORMCURVA_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), '../view/ui/Topo_dialog_curva_manager.ui'))


class Curves(QtGui.QDialog, FORMCURVA_CLASS):
    def __init__(self, iface, id_project_estacas, curvas, tipoClasseProjeto):
        self.curvas = curvas

        super(Curves, self).__init__(None)
        self.setupUi(self)

    def calcular(self):
        filename = QtGui.QFileDialog.getSaveFileName()
        return filename

    def prompt_distancia(self):
        distancia, ok = QtGui.QInputDialog.getText(None, "Distancia", u"Qual a distancia entre estacas que deseja?")
        if not ok:
            return None
        return distancia
    def confirm_delete(self):
        msg = u"Você realmente deseja excluir está curva?"
        msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Question, "AVISO",
                                   u"%s" % msg,
                                   QtGui.QMessageBox.NoButton, None)
        msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        #msgBox.addButton("OK", QtGui.QMessageBox.AcceptRole)
        # msgBox.addButton("&Continue", QtGui.QMessageBox.RejectRole)
        return msgBox.exec_() == QtGui.QMessageBox.Yes

    def fill_estacas(self, estacas):
        p1 = self.cmbBeginPoint
        p2 = self.cmbEndPoint
        self.estacas = estacas
        self.estacas_id = [int(estaca[Estacas.ID_ESTACA]) for estaca in estacas]
        self.cmbBeginPoint.clear()
        self.cmbEndPoint.clear()
        self.cmbBeginPoint.addItems([str(estaca[Estacas.ESTACA]) for estaca in estacas])
        self.cmbEndPoint.addItems([str(estaca[Estacas.ESTACA]) for estaca in estacas])
        self.cmbBeginPoint.setCurrentIndex(0)
        self.cmbEndPoint.setCurrentIndex(1)
        return self

    def fill_data_curva(self,data_curva):
        if data_curva is None:
            return self
        self.lblCurvaI.setText(str(data_curva['i']))
        self.lblCurvaDelta.setText(str(data_curva['delta']))
        self.lblCurvaRaio.setText(str(data_curva['raioMin']))
        self.lblCurvaT.setText(str(data_curva['t']))
        self.lblCurvaD.setText(str(data_curva['d']))
        self.lblCurvaG20.setText(str(data_curva['g20']))
        self.lblCurvaEPI.setText(str(data_curva['epi']))
        self.lblCurvaEPIN.setText(str(data_curva['epi']))
        self.lblCurvaEPC.setText(str(data_curva['epc']))
        self.lblCurvaEPT.setText(str(data_curva['ept']))
        return self

    def change_p1(self, pos):
        self.lblP1North.setText(self.estacas[pos][Estacas.NORTH])
        self.lblP1Este.setText(self.estacas[pos][Estacas.ESTE])
        self.lblP1Nome.setText(self.estacas[pos][Estacas.DESCRICAO])
        self.lblP1Cota.setText(self.estacas[pos][Estacas.COTA])
        self.lblP1Azimute.setText(self.estacas[pos][Estacas.AZIMUTE])
        return self

    def change_p2(self, pos):
        self.lblP2North.setText(self.estacas[pos][Estacas.NORTH])
        self.lblP2Este.setText(self.estacas[pos][Estacas.ESTE])
        self.lblP2Nome.setText(self.estacas[pos][Estacas.DESCRICAO])
        self.lblP2Cota.setText(self.estacas[pos][Estacas.COTA])
        self.lblP2Azimute.setText(self.estacas[pos][Estacas.AZIMUTE])
        return self

    def actions_on_init(self, flag=True):
        self.tblCurvas.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tblCurvas.setEnabled(flag)
        self.btnNovo.setEnabled(flag)
        self.btnEdit.setEnabled(not (flag))
        self.btnDelete.setEnabled(not (flag))
        self.btnCalcular.setEnabled(flag)
        self.btnSave.setEnabled(not (flag))
        self.btnCancel.setEnabled(not (flag))
        self.cmbTipoCurva.setEnabled(not (flag))
        self.cmbBeginPoint.setEnabled(not (flag))
        self.cmbEndPoint.setEnabled(not (flag))
        self.txtVelocidade.setEnabled(not (flag))
        self.txtRaio.setEnabled(not (flag))
        self.txtEMAX.setEnabled(not (flag))
        return self
    def actions_on_item_click(self,flag=True):
        self.actions_on_init()
        self.btnEdit.setEnabled(flag)
        self.btnDelete.setEnabled(flag)
        

    def actions_on_inserting(self, flag=False):
        if not(self.curvas is None) and len(self.curvas)>0:
            self.cmbBeginPoint.setCurrentIndex(self.estacas_id.index(max([curva[CurvasModel.ESTACA_FINAL_ID] for curva in self.curvas])))
        self.tblCurvas.setEnabled(flag)
        self.btnNovo.setEnabled(flag)
        self.btnEdit.setEnabled(flag)
        self.btnDelete.setEnabled(flag)
        self.btnCalcular.setEnabled(flag)
        self.btnSave.setEnabled(not (flag))
        self.btnCancel.setEnabled(not (flag))
        self.cmbTipoCurva.setEnabled(not (flag))
        self.cmbBeginPoint.setEnabled(not (flag))
        self.cmbEndPoint.setEnabled(not (flag))
        self.txtVelocidade.setEnabled(not (flag))
        self.txtRaio.setEnabled(not (flag))
        self.txtEMAX.setEnabled(not (flag))

        return self

    def actions_after_inserting(self):
        return self.actions_on_init()

    def actions_on_editing(self,curva = None , flag=False):
        if curva != None:
            self.cmbTipoCurva.setCurrentIndex(0)
            self.estacas_id = [estaca[0] for estaca in self.estacas]
            self.cmbBeginPoint.setCurrentIndex(self.estacas_id.index(curva[CurvasModel.ESTACA_INICIAL_ID])) 
            self.cmbEndPoint.setCurrentIndex(self.estacas_id.index(curva[CurvasModel.ESTACA_FINAL_ID]))  
            self.txtVelocidade.setText(str(curva[CurvasModel.VELOCIDADE]))
            self.txtRaio.setText(str(curva[CurvasModel.RAIO_UTILIZADO]))
            self.txtEMAX.setText(str(curva[CurvasModel.EMAX]))
                       
        self.tblCurvas.setEnabled(flag)
        self.btnNovo.setEnabled(flag)
        self.btnEdit.setEnabled(flag)
        self.btnDelete.setEnabled(flag)
        self.btnCalcular.setEnabled(flag)
        self.btnSave.setEnabled(not (flag))
        self.btnCancel.setEnabled(not (flag))
        self.cmbTipoCurva.setEnabled(not (flag))
        self.cmbBeginPoint.setEnabled(not (flag))
        self.cmbEndPoint.setEnabled(not (flag))
        self.txtVelocidade.setEnabled(not (flag))
        self.txtRaio.setEnabled(not (flag))
        self.txtEMAX.setEnabled(not (flag))
        return self

    def actions_after_editing(self):
        return self.actions_on_init()

    def actions_after_deleting(self):
        return self.actions_on_init()

    def actions_estaca_change(self, estaca):
        self.indice_p1 = self.cmbBeginPoint.currentIndex()
        self.indice_p2= self.cmbEndPoint.currentIndex()
        return self

    def clear(self):
        self.tblCurvas.setRowCount(0)
        self.tblCurvas.clearContents()

    def fill_table(self, curvas):
        self.curvas = curvas
        self.clear()
        for i, c in enumerate(curvas):
            self.tblCurvas.insertRow(self.tblCurvas.rowCount())
            k = self.tblCurvas.rowCount() - 1
            self.tblCurvas.setItem(k, 0, QtGui.QTableWidgetItem(u"%s" % self.estacas[self.estacas_id.index(int(c[5]))][Estacas.ESTACA]))
            self.tblCurvas.setItem(k, 1, QtGui.QTableWidgetItem(u"%s" % self.estacas[self.estacas_id.index(int(c[6]))][Estacas.ESTACA]))
            self.tblCurvas.setItem(k, 2, QtGui.QTableWidgetItem(u"%s" % c[1]))
            self.tblCurvas.setItem(k, 3, QtGui.QTableWidgetItem(u"%s km/h" % c[2]))
            self.tblCurvas.setItem(k, 4, QtGui.QTableWidgetItem(u"%s" % c[3]))
            self.tblCurvas.setItem(k, 5, QtGui.QTableWidgetItem(u"%s" % c[4]))
        return self
        
    def save(self):
        velocidade = self.txtVelocidade.text()
        raioUtilizado = self.txtRaio.text()
        emax = self.txtEMAX.text()
        self.indice_p1 = self.cmbBeginPoint.currentIndex()
        self.indice_p2= self.cmbEndPoint.currentIndex()
        e1 = self.estacas[self.indice_p1]
        e2 = self.estacas[self.indice_p2]
        tipoCurva = CurvasModel.TYPES[self.cmbTipoCurva.currentIndex()]
        i = self.lblCurvaI.text()
        delta = self.lblCurvaDelta.text()
        raio = self.lblCurvaRaio.text()
        t = self.lblCurvaT.text()
        g20 = self.lblCurvaG20.text()
        d = self.lblCurvaD.text()
        epi = self.lblCurvaEPI.text()
        epin = self.lblCurvaEPIN.text()
        epc = self.lblCurvaEPC.text()
        ept = self.lblCurvaEPT.text()
        return {'e1':e1,'e2':e2,'velocidade':velocidade,'raioUtilizado':raioUtilizado,'emax':emax,'tipoCurva':tipoCurva,'i':i,'delta':delta,'raio':raio,'t':t,'g20':g20,'d':d,'epi':epi,'epin':epin,'epc':epc,'ept':ept}



    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('TopoGrafia', message)
