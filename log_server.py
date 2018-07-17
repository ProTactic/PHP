import os
import socket
import threading

PORT = 20001
FILE_PATH = 'log.txt'

print_pause = threading.Lock()

def get_ip():
	f = os.popen('ifconfig wlan0 | grep "inet addr" | cut -f 2 -d ":" | cut -f 1 -d " "')
	ip = f.read()
	f.close()
	return ip

def log_info(conn, addr):
	global FILE_PATH
	global print_pause
	
	log = ''

	while(True):
		text = (conn.recv(1024)).decode('UTF-8')
		if(not text):
			break
		log = log + text

	with print_pause:
		with open(FILE_PATH, 'a') as f:
			f.write(log)

	print('Got the info closing connection:',str(addr))
	conn.close

socket_object = socket.socket()
socket_object.bind((get_ip(), PORT))
socket_object.listen(5)

while(True):
	conn, addr = socket_object.accept()
	print('Connection from:', addr)
	threading.Thread(target=log_info, args=(conn,addr)).start()
 
socket_object.close()
