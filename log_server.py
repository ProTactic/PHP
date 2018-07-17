"""MIT License

Copyright (c) 2018 ProTactic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

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
