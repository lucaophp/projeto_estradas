# -*- coding: utf-8 -*-
import sqlite3
import math
import csv

from ..model.config import extractZIP, Config, compactZIP
from ..model.helper.calculos import *
from ..model.estacas import Estacas


class Curves():
    TYPES = ('Curva Entrada', 'Curva Saída')
    CURVA_ID = 0
    CURVA_TIPO = 1
    VELOCIDADE = 2
    RAIO_UTILIZADO = 3
    EMAX = 4
    ESTACA_INICIAL_ID = 5
    ESTACA_FINAL_ID = 6

    def __init__(self, project_id,tipo,classe):
        self.project_id = project_id
        self.tipo = tipo
        self.classe = classe

    def list_estacas(self):
        extractZIP(Config.fileName)

        con = sqlite3.connect("tmp/data/data.db")
        est = con.execute(
            "SELECT id,estaca,descricao,progressiva,norte,este,cota,azimute FROM ESTACA WHERE TABLEESTACA_id = ? AND (estaca LIKE '%%+%%' OR estaca LIKE '0')",
            (int(self.project_id),)).fetchall()
        con.close()
        compactZIP(Config.fileName)

        return est


    def list_curvas(self):
        extractZIP(Config.fileName)
        con = sqlite3.connect("tmp/data/data.db")
        curvas = con.execute(
            "SELECT CURVA.id,CURVA.tipo,CURVA.velocidade,CURVA.raio_utilizado,CURVA.emax,CURVA.estaca_inicial_id,CURVA.estaca_final_id FROM CURVA INNER JOIN TABLECURVA ON CURVA.TABLECURVA_id=TABLECURVA.id WHERE TABLECURVA.TABLEESTACA_id=%d  ORDER BY CURVA.estaca_inicial_id ASC" % self.project_id).fetchall()
        con.close()
        compactZIP(Config.fileName)
        return curvas

    def get_curva_details(self, id_estaca=-1, id_curva=-1):
        extractZIP(Config.fileName)
        con = sqlite3.connect("tmp/data/data.db")
        if id_curva == -1:
            curva = con.execute(
                "SELECT CURVA_id,g20,t,d,epi,epc,ept FROM CURVA_SIMPLES INNER JOIN CURVA ON CURVA_SIMPLES.CURVA_id=CURVA.id WHERE estaca_final_id=%d" % (
                id_estaca,)).fetchall()
        else:
            curva = con.execute(
                "SELECT CURVA_id,g20,t,d,epi,epc,ept FROM CURVA_SIMPLES INNER JOIN CURVA ON CURVA_SIMPLES.CURVA_id=CURVA.id WHERE CURVA.id=%d" % (
                id_curva,)).fetchall()
        con.close()
        compactZIP(Config.fileName)
        if len(curva) > 0:
            return curva[0]
        else:
            return None

    def save(self,data,edit_id = 0):
        '''Verifico se há curva para o traçado'''
        extractZIP(Config.fileName)
        con = sqlite3.connect("tmp/data/data.db")
        curvaTracado = con.execute(
            "SELECT id FROM TABLECURVA WHERE TABLEESTACA_id = ?",
            (int(self.project_id),)).fetchall()
        if curvaTracado is None or len(curvaTracado) == 0:
            # insiro a curvaTracado
            con.execute("INSERT INTO TABLECURVA (TABLEESTACA_id) VALUES (?)", (int(self.project_id),))
            con.commit()
        curvaTracado = con.execute(
            "SELECT id FROM TABLECURVA WHERE TABLEESTACA_id = ?",
            (int(self.project_id),)).fetchall()[0]
        if edit_id > 0:
            con.execute(
            "UPDATE CURVA SET TABLECURVA_id = ?,estaca_inicial_id=?,estaca_final_id=?,tipo=?,velocidade=?,raio_utilizado=?,emax=? WHERE id = ?",
            (curvaTracado[0],data['e1'][Estacas.ID_ESTACA], data['e2'][Estacas.ID_ESTACA], data['tipoCurva'], data['velocidade'], data['raioUtilizado'], data['emax'],edit_id))
            con.commit()
            id_curva = edit_id
            con.execute("DELETE FROM CURVA_SIMPLES WHERE CURVA_id=?",(id_curva,))
            con.commit()
        else:
            con.execute(
                "INSERT INTO CURVA (TABLECURVA_id,estaca_inicial_id,estaca_final_id,tipo,velocidade,raio_utilizado,emax) values (?,?,?,?,?,?,?)",
                (curvaTracado[0], data['e1'][Estacas.ID_ESTACA], data['e2'][Estacas.ID_ESTACA], data['tipoCurva'], data['velocidade'], data['raioUtilizado'], data['emax']))
            con.commit()
            id_curva = con.execute("SELECT last_insert_rowid()").fetchall()[0][0]

        if data['tipoCurva'] == Curves.TYPES[0]:
            con.execute("INSERT INTO CURVA_SIMPLES (CURVA_id,g20,t,d,epi,epc,ept) VALUES (?,?,?,?,?,?,?)", (
                id_curva, data['g20'], data['t'], data['d'], data['epi'], data['epc'],
                data['ept']))
            con.commit()
        con.close()
        compactZIP(Config.fileName)

    def delete(self,id_curva):
        extractZIP(Config.fileName)
        con = sqlite3.connect("tmp/data/data.db")
        con.execute("DELETE FROM CURVA_SIMPLES WHERE CURVA_id=?",(id_curva,))
        con.execute("DELETE FROM CURVA WHERE id=?",(id_curva,))
        con.commit()
        con.close()
        compactZIP(Config.fileName)

    def gerador_estacas(self,dist):
        curvas = self.list_curvas()
        estacas = self.list_estacas_vertices()
        estacas_nova = []
        inicial = None
        for curva in curvas:

            try:
                estaca_inicial = estacas[estacas_id.index(curva[self.ESTACA_INICIAL_ID])]
            except:
                estaca_inicial = estacas[0]
            try:
                estaca_final = estacas[estacas_id.index(curva[self.ESTACA_FINAL_ID])]
            except:
                estaca_final = estacas[-1]

            tipo = curva[self.CURVA_TIPO]
            raio = curva[self.RAIO_UTILIZADO]
            velocidade = curva[self.VELOCIDADE]
            prog = estaca_inicial[Estacas.PROGRESSIVA]
            if tipo == self.TYPES[0]:
                detalhes = self.get_curva_details(id_curva = curva[self.CURVA_ID])
                epc = float(detalhes[5])
                ept = float(detalhes[6])
                g20 = float(detalhes[1])
                estaca_start_vert = epc//dist
                estaca_end_vert = ept//dist
                estaca_start_sobra = float((epc/dist)-estaca_start_vert)*dist
                estaca_end_sobra = float((ept/dist)-estaca_end_vert)*dist
                estaca_ini_original = self.get_estaca_by_estaca_ref(estaca_start_vert)
                if estaca_ini_original is None:
                    estaca_ini_original = estacas[0]
                estaca_end_original = self.get_estaca_by_estaca_ref(estaca_end_vert)
                if estaca_end_original is None:
                    estaca_end_original = estacas[-1]
                estaca_inicial_north = float(estaca_ini_original[Estacas.NORTH])+(epc-float(estaca_ini_original[Estacas.PROGRESSIVA]))*math.cos(float(estaca_ini_original[Estacas.AZIMUTE])*math.pi/180)
                estaca_inicial_este = float(estaca_ini_original[Estacas.ESTE])+(epc-float(estaca_ini_original[Estacas.PROGRESSIVA]))*math.sin(float(estaca_ini_original[Estacas.AZIMUTE])*math.pi/180)
                estaca_inicial = [
                                    '%d+%f'%(estaca_start_vert,estaca_start_sobra),
                                    'epc',
                                    '%f'%epc,
                                    '%f'%estaca_inicial_north,
                                    '%f'%estaca_inicial_este,
                                    '%f'%float(estaca_ini_original[Estacas.COTA]),
                                    '%f'%float(estaca_ini_original[Estacas.AZIMUTE])
                                ]
                estacas_nova.append(estaca_inicial)
                deflexao_acumulada = 0.0
                progressiva = float(estaca_ini_original[Estacas.PROGRESSIVA])
                count = 0
                for i in range(abs(int(estaca_end_vert-estaca_start_vert))):
                    count += 1
                    progressiva += dist
                    deflexao = (20.-estaca_start_sobra) * (g20/40.) if count == 1 else g20/2
                    deflexao_acumulada += deflexao
                    azimute = float(estaca_ini_original[Estacas.AZIMUTE])-deflexao_acumulada

                    north = float(estaca_ini_original[Estacas.NORTH])+(progressiva-float(estaca_ini_original[Estacas.PROGRESSIVA]))*math.cos(azimute*math.pi/180)
                    este = float(estaca_ini_original[Estacas.ESTE])+(progressiva-float(estaca_ini_original[Estacas.PROGRESSIVA]))*math.sin(azimute*math.pi/180)
                    estaca = [
                                '%d'%(estaca_start_vert+i,),
                                '',
                                '%f'%progressiva,
                                '%f'%north,
                                '%f'%este,
                                '%f'%float(estaca_ini_original[Estacas.COTA]),
                                '%f'%azimute
                            ]
                    estacas_nova.append(estaca)
                #ept
                deflexao = estaca_end_sobra*(g20/40.)
                deflexao_acumulada += deflexao
                azimute = float(estaca_ini_original[Estacas.AZIMUTE])-deflexao_acumulada
                north = float(estaca_ini_original[Estacas.NORTH])+(float(ept)-float(estaca_ini_original[Estacas.PROGRESSIVA]))*math.cos(azimute*math.pi/180)
                este = float(estaca_ini_original[Estacas.ESTE])+(float(ept)-float(estaca_ini_original[Estacas.PROGRESSIVA]))*math.sin(azimute*math.pi/180)
                estaca = [
                                '%d+%f'%(estaca_end_vert,float(estaca_end_sobra)),
                                'EPT',
                                '%f'%ept,
                                '%f'%north,
                                '%f'%este,
                                '%f'%float(estaca_end_original[Estacas.COTA]),
                                '%f'%abs(azimute)
                            ]
                estacas_nova.append(estaca)
        return estacas_nova

    
    def get_estaca_by_estaca_ref(self,estaca_ref):
        extractZIP(Config.fileName)
        con = sqlite3.connect("tmp/data/data.db")
        estacas = con.execute(
            "SELECT id,estaca,descricao,progressiva,norte,este,cota,azimute FROM ESTACA WHERE TABLEESTACA_id = ? AND estaca LIKE ?",
            (int(self.project_id),str(int(estaca_ref)))).fetchall()
        if len(estacas) == 0:
            print estaca_ref
            print 'Nao'
            return None
        est = estacas[0]

        con.close()
        compactZIP(Config.fileName)
        return est

    def save_CSV(self, filename, estacas):
        delimiter = str(Config.CSV_DELIMITER.strip()[0])
        with open(filename, "wb") as fo:
            writer = csv.writer(fo, delimiter=delimiter, dialect='excel')
            for r in estacas:
                writer.writerow(r)

    #LISTA OS VERTICES
    def list_estacas(self):
        extractZIP(Config.fileName)
        con = sqlite3.connect("tmp/data/data.db")
        est = con.execute(
            "SELECT id,estaca,descricao,progressiva,norte,este,cota,azimute FROM ESTACA WHERE TABLEESTACA_id = ? AND (estaca LIKE '%%+%%' OR estaca LIKE '0')",
            (int(self.project_id),)).fetchall()
        con.close()
        compactZIP(Config.fileName)
        return est

    def list_estacas_vertices(self):
        extractZIP(Config.fileName)
        con = sqlite3.connect("tmp/data/data.db")
        est = con.execute(
            "SELECT id,estaca,descricao,progressiva,norte,este,cota,azimute FROM ESTACA WHERE TABLEESTACA_id = ? AND not(estaca LIKE '%%+%%')",
            (int(self.project_id),)).fetchall()
        con.close()
        compactZIP(Config.fileName)
        return est

    def get_estaca_by_id(self,ident):
        extractZIP(Config.fileName)
        con = sqlite3.connect("tmp/data/data.db")
        estacas = con.execute(
            "SELECT id,estaca,descricao,progressiva,norte,este,cota,azimute FROM ESTACA WHERE id = ?",
            (int(ident),)).fetchall()
        con.close()
        compactZIP(Config.fileName)
        return [] if len(estacas)==0 else estacas[0]

    def get_estacas_interval(self,de,ate):
        extractZIP(Config.fileName)
        con = sqlite3.connect("tmp/data/data.db")
        
        estacas = con.execute(
            "SELECT estaca,descricao,progressiva,norte,este,cota,azimute FROM ESTACA WHERE TABLEESTACA_id = ? AND (cast(progressiva as REAL)>=? OR cast(progressiva as REAL)<=?)",
            (int(self.project_id),float(de),float(ate))).fetchall()
        
        con.close()
        compactZIP(Config.fileName)
        return estacas


    def gera_estacas_intermediarias(self,dist,epc,ept,g20):
        estacas = []
        estaca_start_vert = epc//dist
        estaca_end_vert = ept//dist
        estaca_start_sobra = float((epc/dist)-estaca_start_vert)*dist
        estaca_end_sobra = float((ept/dist)-estaca_end_vert)*dist
        extractZIP(Config.fileName)
        con = sqlite3.connect("tmp/data/data.db")
        estaca_start = con.execute(
            "SELECT id,estaca,descricao,progressiva,norte,este,cota,azimute FROM ESTACA WHERE TABLEESTACA_id = ? AND estaca LIKE ?",
            (int(self.project_id),'%d%%'%estaca_start_vert)).fetchall()
        estaca_end = con.execute(
            "SELECT id,estaca,descricao,progressiva,norte,este,cota,azimute FROM ESTACA WHERE TABLEESTACA_id = ? AND estaca LIKE ?",
            (int(self.project_id),'%d%%'%estaca_end_vert)).fetchall()
        con.close()
        compactZIP(Config.fileName)
        estaca_inicial_north = float(estaca_start[0][4])+(epc-float(estaca_start[0][3]))*math.cos(float(estaca_start[0][7])*math.pi/180)
        estaca_inicial_este = float(estaca_start[0][5])+(epc-float(estaca_start[0][3]))*math.sin(float(estaca_start[0][7])*math.pi/180)
        estaca_inicial = [
                            '%d+%f'%(estaca_start_vert,estaca_start_sobra),
                            'epc',
                            '%f'%epc,
                            '%f'%estaca_inicial_north,
                            '%f'%estaca_inicial_este,
                            '%f'%float(estaca_start[0][6]),
                            '%f'%float(estaca_start[0][7])
                        ]
        estacas.append(estaca_inicial)
        deflexao_acumulada = 0.0
        progressiva = float(estaca_start[0][3])
        est = estaca_start_vert
        for i in range(abs(int(estaca_end_vert-estaca_start_vert))):
            progressiva+=dist
            est += 1
            deflexao = (20.-estaca_start_sobra)*(g20/40) if deflexao_acumulada == 0.0 else (g20/2)
            deflexao_acumulada += deflexao

            azimute = float(estaca_start[0][7])-deflexao_acumulada
            north = float(estaca_start[0][4])+(progressiva-float(estaca_start[0][3]))*math.cos(float(azimute)*math.pi/180)
            este = float(estaca_start[0][5])+(progressiva-float(estaca_start[0][3]))*math.sin(float(azimute)*math.pi/180)
            estaca = [
                            '%d'%est,
                            '',
                            '%f'%progressiva,
                            '%f'%north,
                            '%f'%este,
                            '%f'%float(estaca_start[0][6]),
                            '%f'%azimute
                        ]
            estacas.append(estaca)

        deflexao = estaca_end_sobra*(g20/40.)
        deflexao_acumulada += deflexao
        azimute = float(estaca_start[0][7])-deflexao_acumulada
        estaca_end_north = float(estaca_start[0][4])+(epc-float(estaca_start[0][3]))*math.cos(float(azimute)*math.pi/180)
        estaca_end_este = float(estaca_start[0][5])+(epc-float(estaca_start[0][3]))*math.sin(float(azimute)*math.pi/180)
        
        estaca = [
                            '%d+%f'%(estaca_end_vert,estaca_end_sobra),
                            'ept',
                            '%f'%ept,
                            '%f'%estaca_end_north,
                            '%f'%estaca_end_este,
                            '%f'%float(estaca_start[0][6]),
                            '%f'%azimute
                        ]
        estacas.append(estaca)
        return estacas

    def gera_estacas(self,dist):
        curvas = self.list_curvas() 
        estacas = []
        indice = 0
        for curva in curvas:
            curva_detalhes = self.get_curva_details(id_curva=int(curva[0]))
            if curva_detalhes is None:
                continue
            estaca_inicial = self.get_estaca_by_id(int(curva[5]))
            estaca_final = self.get_estaca_by_id(int(curva[6]))
            estacas_ant = self.get_estacas_interval(float(estaca_inicial[3]),float(estaca_final[3]))
            estacas.extend(estacas_ant)
            
            g20 = float(curva_detalhes[1])
            epc = float(curva_detalhes[5])
            ept = float(curva_detalhes[6])

            estacas.extend(self.gera_estacas_intermediarias(dist,epc,ept,g20))
        return estacas


    '''def gera_estacas(self,curvas,estacas):
        self.curvas = curvas
        estacas_id = [estaca[Estacas.ID_ESTACA] for estaca in self.estacas]
        novas_estacas = []
        for curva in self.curvas:
            estaca_inicial = estacas[estacas_id.index(curva[self.ESTACA_INICIAL_ID])]
            estaca_final = estacas[estacas_id.index(curva[self.ESTACA_FINAL_ID])]
            tipo = curva[self.CURVA_TIPO]
            raio = curva[self.RAIO_UTILIZADO]
            velocidade = curva[self.VELOCIDADE]'''




    def calcParams(self,data):
        curvas = self.list_curvas()
        if data['e1'][Estacas.PROGRESSIVA]==data['e2'][Estacas.PROGRESSIVA]:
            return None
        if len(curvas)==0 or float(data['e1'][Estacas.PROGRESSIVA])==0.0:
            eptAnt = -1
        else:
            detalhes = self.get_curva_details(int(data['e1'][Estacas.ID_ESTACA]))
            eptAnt = -1 if detalhes is None else detalhes[6]

        i = calculeI(float(data['e1'][Estacas.PROGRESSIVA]),float(data['e2'][Estacas.PROGRESSIVA]),float(data['e1'][Estacas.COTA]),float(data['e2'][Estacas.COTA]))
        v = velocidade(float(i),self.classe,self.tipo)
        delta_val = delta(float(data['e1'][Estacas.AZIMUTE]),float(data['e2'][Estacas.AZIMUTE]))
        g20_val = g20(float(data['raioUtilizado']))
        t_val = t(float(data['raioUtilizado']),delta_val)
        d_val = d_curva_simples(float(data['raioUtilizado']),delta_val)
        e_max = float(data['emax'])
        f_max = fmax(int(v[0]))
        r_min = rmin(int(v[0]),e_max,f_max)
        epi_val = epi(eptAnt,float(data['e2'][Estacas.PROGRESSIVA]),float(data['e1'][Estacas.PROGRESSIVA]),t_val)
        epc_val = epc(epi_val,t_val)
        ept_val = ept(epc_val,d_curva_simples(float(data['raioUtilizado']),delta_val))
        return {'i':i,'velocidade':int(v[0]),'delta':delta_val,'raioMin':r_min,'g20':g20_val,'t':t_val,'d':d_val,'fmax':f_max,'epi':epi_val,'epc':epc_val,'ept':ept_val}

        
