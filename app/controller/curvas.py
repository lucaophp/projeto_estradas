from ..model.curves import Curves as CurvasModel
from ..view.curves import Curves as CurvasView


class Curvas:
    def __init__(self, iface, id_project, tipoClasseProjeto,estacasController):
        self.tipo = tipoClasseProjeto[0]
        self.classe = tipoClasseProjeto[1]
        self.model = CurvasModel(id_project,self.tipo,self.classe)
        self.curvas = self.model.list_curvas()
        self.view = CurvasView(curvas=self.model.list_curvas(), iface=iface, id_project_estacas=id_project,
                               tipoClasseProjeto=tipoClasseProjeto)
        
        self.estacas = self.model.list_estacas()
        self.estacasController = estacasController
        self.edit = False
        self.insert = False
        self.eventos()

    def eventos(self):
        self.view.btnNovo.clicked.connect(self.inserting)
        self.view.btnEdit.clicked.connect(self.editing)
        self.view.btnSave.clicked.connect(self.save)
        self.view.btnCancel.clicked.connect(self.cancel)
        self.view.btnDelete.clicked.connect(self.delete)
        self.view.btnCalcular.clicked.connect(self.calcular)
        self.view.cmbBeginPoint.currentIndexChanged.connect(self.change_p1)
        self.view.cmbEndPoint.currentIndexChanged.connect(self.change_p2)
        self.view.tblCurvas.itemClicked.connect(self.item_click)
        self.view.txtVelocidade.editingFinished.connect(self.velocidade_update)
        self.view.actions_on_init()
        self.fill_estacas()
        self.view.fill_table(self.curvas)

    def fill_estacas(self):
    	#estacas_id = [row[1] for row in self.estacas]
    	self.view.fill_estacas(self.estacas)

    def item_click(self, item):
        self.view.actions_on_item_click()

        self.item = self.curvas[item.row()]


    def change_p1(self, pos):
        self.view.change_p1(pos)
        data = self.view.save()
        data_curva = self.model.calcParams(data)
        self.view.fill_data_curva(data_curva)

    def change_p2(self, pos):
        self.view.change_p2(pos)
        data = self.view.save()
        data_curva = self.model.calcParams(data)
        self.view.fill_data_curva(data_curva)

    def velocidade_update(self,velocidade=0):
        data = self.view.save()
        data_curva = self.model.calcParams(data)
        self.view.fill_data_curva(data_curva)


    def inserting(self):
        self.view.actions_on_inserting()
        self.insert = True

    def editing(self):
        self.edit_id = self.item[0]
        self.view.actions_on_editing(self.item)
        self.edit = True        

    def cancel(self):
        self.view.actions_on_init()
        self.insert = False
        self.edit = False

    def save(self):
        if (self.insert):
            self.view.actions_after_inserting()
            self.model.save(self.view.save())
            self.insert = False
        elif (self.editing):
            self.view.actions_after_editing()
            self.model.save(self.view.save(),self.edit_id)
            self.update = False
            self.edit_id = 0
        curvas = self.model.list_curvas()
        self.view.fill_table(curvas)
        self.curvas = curvas

    def delete(self):
        if not(self.view.confirm_delete()): return
        codigo = self.item[0]
        if not (codigo in [None, 0]):
            self.model.delete(codigo)
            curvas = self.model.list_curvas()
            self.view.fill_table(curvas)
            self.curvas = curvas
        self.view.actions_after_deleting()

    def calcular(self):
        filename = self.view.calcular()
        estacas = self.model.gerador_estacas(self.estacasController.model.distancia)
        self.model.save_CSV(filename, estacas)

    # salvar em csv;
    def run(self):
        self.view.exec_()
