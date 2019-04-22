import socket
import sys
import os
import os.path
from thread import *
import time
HOST = ''
PORT = 9999
file_check = sys.argv[1]+"/end_process.txt"
def connect(conn):
	activeFileName = False
	fileName = '\n'
	fileNameContent = ''
	conn.send("connected")
	while True:
		try:
		
			data = conn.recv(1024).strip()
			if not(activeFileName):
				activeFileName = True
				fileName = data
			elif activeFileName:
				if not(data in [False,'',None]):
					fileNameContent+=data
					with open(sys.argv[1]+"/"+fileName,'w') as fp:
						fp.write(fileNameContent)
					activeFileName = False
					fileName = '\n'
					fileNameContent = ''

			if os.path.isfile(file_check):
				break
				
			reply = data
			if not data:
				break
		except:
			conn.sendall("falha")
		#conn.sendall(reply)
	conn.close()

	
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
	s.bind((HOST,PORT))
except:
	print "Bind Failed"
	sys.exit()
s.listen(10)
timeout_start = time.time()
timeout = 60
while time.time() < timeout_start + timeout:
	if os.path.isfile(file_check):
		time.sleep(5)
		os.remove(file_check)
		break
	conn,addr = s.accept()
	print 'Connected with '+addr[0]+':'+str(addr[1])
	start_new_thread(connect,(conn,))

s.close()
os.remove(file_check)
