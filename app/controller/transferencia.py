import socket
import sys
from thread import *
class Transferencia:
	def __init__(self,folder):
		self.folder = folder
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.host = ''
		self.port = 9999

	def get_hostname(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]

	def desconnect(self):
		#cria uma conexao cliente TCP.
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect(("127.0.0.1", 9999))
			s.send("END");
			msg = "Encerrado com sucesso"
		except:
			msg = "O servidor nao quer responder..."

		s.close()
		return msg



	def connect(self,conn):
		activeFileName = False
		fileName = '\n'
		fileNameContent = ''
		conn.send("Bem vindo ao servidor")
		while True:
			data = conn.recv(1024).strip()
			if not(activeFileName):
				activeFileName = True
				fileName = data
				print 'ativado'
			elif activeFileName:
				if not(data in [False,'',None]):
					fileNameContent+=data
					print 'GRAVANDO'
					with open(self.folder+fileName,'w') as fp:
						fp.write(fileNameContent)
					activeFileName = False
					fileName = '\n'
					fileNameContent = ''
				
				
			print data+'\n'+fileName
				
			reply = data
			if not data:
				break
			#conn.sendall(reply)
		conn.close()
		
	def run(self):
		try:
			self.socket.bind((self.host,self.port))

		except:
			print "Bind Failed"
			return False

		self.socket.listen(10)
		while True:
			conn,addr = self.socket.accept()
			print 'Connected with '+addr[0]+':'+str(addr[1])
			start_new_thread(connect,(self,conn,))
		self.socket.close()
		return True
