import socket, select
from collections import deque
import os

tasks = deque()
recv_wait = {}
conn_list = []

def get_ip():
    
    f = os.popen('ifconfig wlan0 | grep "inet addr:" | cut -f 2 -d ":" | cut -f 1 -d " "')
    ip = f.read()
    f.close()
    return ip

def run():

    while(True):
        while(not tasks):
            list_recv, _, _ = select.select(recv_wait, [], [], 0.1)
            for s in list_recv:
                tasks.append(recv_wait.pop(s))

        try:

            task = tasks.popleft()
            info, task_socket = next(task)
            
            if(info == 'recv_client'):
                recv_wait[task_socket] = task 	  
            if(info == 'name'):
                recv_wait[task_socket] = task
            if(info == 'recv'):
                recv_wait[task_socket] = task
        
        except StopIteration:
            pass
        except Exception as e:
            print(str(e))

def start_server():
   
    server_socket = socket.socket()
    server_socket.bind((get_ip(), 20000))
    #server_socket.setblocking(False)
    server_socket.listen(5)
    conn_list.append([server_socket, ''])

    while(True):
        yield 'recv_client', server_socket
        client, addr = server_socket.accept()
        print('Connection from' +str(addr))
        tasks.append(handle_client_name(client))

def get_clients_name():
    
    names = ''
    for i in conn_list[1:]:
        names = names + i[1] + ','
    return names[:-1]

def get_client_name(client):
   
    for i in conn_list[1:]:
        if(i[0] == client):
            return i[1]

def send_to_all(data):
   
    for i in conn_list[1:]:
        i[0].send(data)

def close_connection(client):
  
    names = ''
    temp = 0
    name = ''
    for i in range(1, len(conn_list)):
        if(conn_list[i][0] == client):
            name = (conn_list.pop(i))[1]
            client.close()
            temp = i
            break
        names = names + conn_list[i][1] + ','

    for i in range(temp, len(conn_list)): 
        names = names + conn_list[i][1] + ','

    print('Close connection : ' + name)
    message = 'Content-Type:Names\n' + names[:-1]
    send_to_all(message.encode('UTF-8')) #

def handle_client_name(client):

    yield 'name', client
    name = (client.recv(1024)).decode('UTF-8')
    conn_list.append([client, name])
    message = 'Content-Type:Names\n' + get_clients_name()
    send_to_all(message.encode('UTF-8')) #
    tasks.append(handle_client(client))    

def handle_client(client):

    while(True):
        yield 'recv', client
        try:
            data = (client.recv(1024)).decode('UTF-8')
        except:
            close_connection(client)
            break  
        print('Got:' + data)
        if(not data):
            close_connection(client)
            break
        data = 'Content-Type:Message\n' + get_client_name(client) + ':' + data
        send_to_all(data.encode('UTF-8')) #

if __name__ == '__main__':

    tasks.append(start_server())
    run()
