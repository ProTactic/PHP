import socket
import DHK
import binascii
from Crypto.Cipher import AES
import threading as tr

pause = tr.Lock()                                              #privent from thearding access a var at the same time
con_list = []                                                  #global connection list will posses [connection object,name,chiper]

def DH_establish_server(deffiehc,sokcetC):                     #Setting Deffie Hellman key. args: deffiehc as the DHK object ,SokectC as sokect connection
    sokcetC.send((str(deffiehc.group)).encode('utf-8'))        #send the group to the client,encode sets the str as binary object
    replay=(sokcetC.recv(1024).decode('utf-8')).split(':')     #receve the data, the public of the client
    if(replay[0]=='ACK'):
        deffiehc.set_shared_key(int(replay[1]))                #set the shared key with the public key from client
        message=str(deffiehc.get_public_key())                 #set the message to be the public key of the server
        sokcetC.send(message.encode('utf-8'))                  #send it to client
        print('Successfull key exchange')
    else:
        raise Exception("Client error")

def sendall_handler(socketC,message):
    global con_list                                            #get the global connation list
    with pause:                                                #use the puase object to privent colision
        try:                                                   #for all connection exept the sender,sending the encrypted message
            l=len(con_list)
            for i in range(l):
                if(con_list[i][0] != socketC):
                    chipertext = con_list[i][1].encrypt(message.encode('utf-8'))
                    con_list[i][0].send(chipertext)
        except Exception as e:
            print(e)
            print("Error sending the message")

def receive_handler(socketC,chiperO,client_name = "Client Name"):
    try:                                                       #wait for receiving a message, decode it and print it
        recv=socketC.recv(1024)
        recv=(chiperO.decrypt(recv)).decode('utf-8')
        print(client_name + " : " +clear_message(recv))
        return recv
    except:                                                   #return -1 as an error
        return "-1"

def close_connection_handler(connection):                     #remove the client from the connection list
    global con_list
    temp=[]
    with pause:
        l = len(con_list)
        for i in range(l):
            if(con_list[i][0] == connection):
                temp= con_list.pop(i)
                break
    message = temp[2] + " closed  the connection"              # append the client name to the meesage
    message = pad(message)
    sendall_handler(connection,message)
def pad(padS):                                                #AES gets plaintext the is a multiplation of 128 or 256 bit in this case
    return padS + ((16-len(padS)%16) * '{')

def clear_message(message):
    while(True):
        if(message[-1] == '{'):
            message = message[:len(message)-1]
        else:
            break
    return message

def client_thread(connection ,ip,port):                       #client main function handler
    global con_list
    with pause:
        DeffieHS=DHK.DHK()
        print('\n==========================')
        print('Setting DH key..')
        DH_establish_server(DeffieHS,connection)              #Establish shared key with the client
        print(DeffieHS.shared_key)
        key=binascii.unhexlify(DeffieHS.hashed_key)           #set key var to be in hex reprisntion
        chiper = AES.new(key,AES.MODE_ECB)                    #set a AES chiper object
        client_name=clear_message(receive_handler(connection,chiper))  #get the client name
        print('==========================\n')
        client_info = [connection,chiper,client_name]         #make a list with the connection object and the chiper object,client name
        con_list.append(client_info)                          #append it to the connection list, as a new client

    is_active=True
    while(is_active):
        client_input=receive_handler(connection,chiper,client_name)       #get the input from the clientbbbbbbb

        if(client_input=="--EXIT--" or client_input=="-1"):   #check if to close the connection
            print("Closing connection from " + client_name)
            connection.close()
            close_connection_handler(connection)
            is_active=False
        else:
            client_input = pad(client_name + " : " + client_input)  #padding the client name with the message in order to encode it in AES
            sendall_handler(connection,client_input)          #sends all clients the message

if __name__=='__main__':
    s = socket.socket()                                       # Create a socket object
    host = socket.gethostname()                               # Get local machine name
    port = 20000                                              # Reserve a port for your service.
    s.bind(('0.0.0.0', port))                                 # Bind to the port

    print(host)
    s.listen(5)                                               # Now wait for client connection.

    while True:
        (c, addr) = s.accept()                                # Establish connection with client.
        ip,port=str(addr[0]),str(addr[1])
        print("Connection from " + ip + ":" + port)
        try:
            tr.Thread(target=client_thread,args=(c,ip,port)).start()  #starting the client thread
        except Exception as e:
            print(e)
            print("Thread did not start.")
