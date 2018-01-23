import socket  # Import socket module
import DHK
from  Crypto.Cipher import AES
import binascii
import threading as tr

def DH_establish_client(deffiehc,sokcetC):              # Setting Deffie Hellman key. args: deffiehc as the DHK object ,SokectC as sokect connection
    message='ACK:' + str(deffiehc.get_public_key())     # set an ACK message with the public key of the client
    sokcetC.send(message.encode('utf-8'))               # encode the message and sent it to the server
    message=(sokcetC.recv(1024)).decode('utf-8')        # set the varuble message to be the data that the server sent, the server public key
    deffiehc.set_shared_key(int(message))               # set a shared key with the public key of the server
    print('Successfull key exchange')

def recv_message(connection,cipher):                    # function to receive messages for thread uses
    try:
        while(True):
            message = connection.recv(1024)
            message = (cipher.decrypt(message)).decode('utf-8')
            print(clear_message(message))
    except:
        print("Server closed the connection")
        exit()

def pad(padS):                                          # padding for AES encryption
    return padS + ((16-len(padS)%16) * '{')

def clear_message(message):
    while(True):
        if(message[-1] == '{'):
            message = message[:len(message)-1]
        else:
            break
    return message

if __name__=='__main__':

    client_name = input("Please enter your name: ")     # get the user name
    s = socket.socket()                                 # Create a socket object
    host = socket.gethostname()                         # Get local machine name
    port = 20000                                        # Reserve a port for your service.

    s.connect(('127.0.0.1', port))
    group=int((s.recv(1024)).decode('utf-8'))           # receve the group from the server,dencode it and set it to the varuble group
    DeffieHC=DHK.DHK(group)                             # Establish shared key with the server
    print('==========================')
    print('Setting DH key..')
    DH_establish_client(DeffieHC,s)
    print(DeffieHC.shared_key)
    print('==========================')
    key = binascii.unhexlify(DeffieHC.hashed_key)        # set the key to be hex value
    chiper = AES.new(key, AES.MODE_ECB)                  # create an AES encryption object

    chipertext = chiper.encrypt(pad(client_name).encode('utf-8'))  # encode the client name
    s.send(chipertext)                                   # send it to the server

    recvT = tr.Thread(target=recv_message,args=(s,chiper),daemon=True)  # set the receving thread
    recvT.start()                                        # start the thread
    try:
        while True:                                      # sending messages
                clientinput=input()
                if(clientinput !="-1"):
                    chipertext = chiper.encrypt(pad(clientinput).encode('utf-8'))
                    s.send(chipertext)
                else:
                    s.close()
    except:
        pass
