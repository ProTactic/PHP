"""MIT License

Copyright (c) 2018 CodeItISR

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

import socket, select
from collections import deque
import os


"""
    This is a multi-socket server based on schedular and not threading.
    The function get_ip works on unix based  os with bash shell.
"""

tasks = deque() # Tasks queue
recv_wait = {}  # Waiting list for data
conn_list = []  # Contain list of lists each list [socket, user name]
                # first item in the list is the main socket list

def get_ip():
    
    """ Take the ip using Linux shell commands - wlan(wifi) connection"""

    f = os.popen('ifconfig wlan0 | grep "inet addr:" | cut -f 2 -d ":" | cut -f 1 -d " "')
    ip = f.read()
    f.close()
    return ip

def run():

    """
        The main schedular
        First check if there is any tasks in tasks queue,
        if not wait untill any other data from the connection is ready for reading
        if there are tasks, call next on them - fowrad the task and then
        append it again to the wait list untill data will arrived
    """

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

    """
        Create the main socket object and append it
        to the connection list
        yield before recving a connection,
        when received append the handle client name function to the
        tasks list
    """
    
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

    """ Create A list of all the client names """
    
    names = ''
    for i in conn_list[1:]:
        names = names + i[1] + ','
    return names[:-1]  # Return the string without the last ','

def get_client_name(client):

    """ Get the client name and return it """
   
    for i in conn_list[1:]:
        if(i[0] == client):
            return i[1]

def send_to_all(data):

    """ send to all client the data """
   
    for i in conn_list[1:]:
        i[0].send(data)

def close_connection(client):

    """
        Function that do few things:
        Remove the client that closed the connection from the list
        Create a list that contain all the client names
        and then send the new client list name to all connected clients
    """
  
    names = ''
    temp = 0 # Save the loction of next client after removing the closed one
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
    send_to_all(message.encode('UTF-8')) 

def handle_client_name(client):

    """
        The First function after the client connected
        Append the client to the connection list
        then send new name list to all
    """
    
    yield 'name', client
    name = (client.recv(1024)).decode('UTF-8')
    conn_list.append([client, name])
    message = 'Content-Type:Names\n' + get_clients_name()
    send_to_all(message.encode('UTF-8')) 
    tasks.append(handle_client(client))    

def handle_client(client):

    """
        The main function to recive data from user
        Get the message and send it to all clients
    """

    while(True):
        yield 'recv', client
        try: # if the is any error close the connection
            data = (client.recv(1024)).decode('UTF-8')
        except:
            close_connection(client)
            break  
        print('Got:' + data)
        if(not data):
            close_connection(client)
            break
        data = 'Content-Type:Message\n' + get_client_name(client) + ':' + data
        send_to_all(data.encode('UTF-8')) 

if __name__ == '__main__':

    tasks.append(start_server())
    run() # start the program
