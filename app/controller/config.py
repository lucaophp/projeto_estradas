# -*- coding: utf-8 -*-

from PyQt4 import QtGui

from ..model.config import Config as ModelConfig
from ..view.config import TopoConfig
from ..controller.transferencia import Transferencia
from ..view.transferencia import Transferencia as TransferenciaView
from thread import *
from subprocess import *
import os
import sys
import signal
import re
def kill(proc_pid):
    '''process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()'''
    os.kill(proc_pid, 9)

class Config:
    def __init__(self,iface):
        """
            ----view------
            criacao da tela config
        """
        self.conf = TopoConfig(iface)
        #defino o modelo de dados
        self.model = ModelConfig()
        self.events()
        self.crs = self.model.crs
        self.ordem_mapa = self.model.ordem_mapa

        self.update()

    def events(self):
        self.conf.txtCRS.textChanged.connect(self.listCRS)
        # self.txtCRS.textChanged(self.listCRS)
        self.conf.tableCRS.itemClicked.connect(self.itemClick)
        self.conf.comboClasse.currentIndexChanged.connect(self.mudancaClasseProjeto)
        self.conf.comboMap.currentIndexChanged.connect(self.mudancaMapa)
        self.conf.comboUnits.currentIndexChanged.connect(self.mudancaUnits)

    def changeCRS(self):
        self.conf.changeCRS(self.model.crs)

    def listCRS(self, txt=''):
        crs = self.model.listCRS(txt)
        self.conf.tableCRS.clearContents()
        k = 0
        for x in crs:
            self.conf.tableCRS.insertRow(self.conf.tableCRS.rowCount())
            self.conf.tableCRS.setItem(k, 0, QtGui.QTableWidgetItem(str(x[1])))
            self.conf.tableCRS.setItem(k, 1, QtGui.QTableWidgetItem(str(x[0])))
            k += 1

    def itemClick(self, item):
        crs = int(self.conf.tableCRS.item(item.row(), 0).text())
        self.model.itemClick(crs)

    def mudancaClasseProjeto(self, pos):
        self.model.mudancaClasseProjeto(pos)

    def mudancaMapa(self, pos):
        pos -= 1
        if pos < 0:
            self.model.tipo_mapa = self.ordem_mapa[0]
        else:
            self.model.tipo_mapa = self.ordem_mapa[pos]

    def mudancaUnits(self, pos):
        
        self.model.UNITS = self.model.ordem_units[pos]

    def newfile(self):
        filename = u"%s" % self.conf.new_file()
        if filename in ["",None]:
            return
        self.model.newfile(filename)

    def openfile(self):
        filename = u"%s" % self.conf.open_file()
        if filename in ["",None] or not(filename.endswith('lzip')):
            self.conf.error('SELECIONE UM ARQUIVO lzip PARA SER ABERTO')
            return
        self.model.openfile(filename)
        self.update()
        self.carregamapa()

    def savefile(self):
        self.model.filename = u"%s" % self.model.filename
        try:
            self.model.savefile()
            self.update()
        except:
            self.newfile()
            if self.model.filename not in [None, '']:
                self.savefile()
            else:
                return None
        return self.model.filename

    def carregamapa(self):
        self.changeCRS()
        self.conf.carregamapa(self.model.tipo_mapa)

    def transferencia(self):
        self.changeCRS()
        folder_name = self.conf.folder_choice()
        if folder_name in [None,'']:
            return
        #inicia servidor
        t = Transferencia(folder_name)
        basepath = os.path.dirname(os.path.realpath(__file__))
        os.chdir(basepath)
        if not re.match("win{1}.*", os.sys.platform) is None:
            os.environ['PYTHON_PATH'] = "c:\\PROGRA~1\\QGIS2~1.18\\apps\\Python27\\Lib"
            os.environ['PYTHONHOME'] = "c:\\PROGRA~1\\QGIS2~1.18\\apps\\Python27"
        num_p = Popen(["python", "server_qt.py",r"%s"%folder_name], shell=True)
        
        #start_new_thread(t.run,(t,))
        ip = t.get_hostname()
        tview = TransferenciaView(ip)
        tview.exec_()
        with open(folder_name+"/end_process.txt","w") as fp:
            fp.write("terminar servidor")

        t.desconnect()

        kill(num_p.pid)



    def carregacarta(self):
        self.conf.carregacarta(self.model)

    def update(self):
        self.changeCRS()
        txt = self.model.listCRSID()
        self.conf.update(self.model, txt)

    def run(self):
        self.conf.show()
        crs = self.crs
        result = self.conf.exec_()
        if result:
            self.changeCRS()

            self.dataTopo = [
                self.conf.cmpPlanoMin.value(),
                self.conf.cmpPlanoMax.value(),
                self.conf.cmpOnduladoMin.value(),
                self.conf.cmpOnduladoMax.value(),
                self.conf.cmpMontanhosoMin.value(),
                self.conf.cmpMontanhosoMax.value()
            ]
            self.model.dataTopo = self.dataTopo
            self.model.CSV_DELIMITER = self.conf.txtCSV.text()
            print self.model.CSV_DELIMITER
            print self.model.UNITS
            self.crs = self.model.crs
            self.update()
        else:
            self.model.crs = crs
