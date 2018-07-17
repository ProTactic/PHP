import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import socket
import threading
import sys
""" 
    client gui contain two frames
    Main() is the root window
    Connection_Window() - the connection frame
    Chat_Window() - the chat frame
"""

LARGE_FONT = ("Verdana", 12)
RECV_RUN = 0
RECV = 0

def send_error_info(text, main_socket):
    """
        Establish a connection with the log server
        and then send the error message
    """
    
    ip, _ = main_socket.getpeername()
    socket_object = socket.socket()
    socket_object.connect((ip, 20001))
    socket_object.send(text.encode('UTF-8'))
    socket_object.close()  

class Main(tk.Tk):
    """
        The main window, root
        Inheret from tk.Tk makes it a tk.Tk() objcet
        functions : add_frame, show_frame, port_checker,
        ip_checker, get_correct_data, connect_to_server,
        send_text, recv_info
    """

    def __init__(self, *args, **kwargs):

        # Inheret from tk.Tk()
        # Create master frame the other frames based on
        # Set self.frames as dictionary the will contain all frames,
        # at start set Connection_Window() frame to apply the settings
        # on the root
        
        tk.Tk.__init__(self, *args, **kwargs)
        self.container = tk.Frame(self)

        self.container.pack(side="top", fill="both", expand = True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        frame = Connection_Window(self.container, self)
        self.frames[Connection_Window] = frame
        frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame(Connection_Window)

    def add_frame(self, frame_to_add):

        # Add a frame to the self.frames dictionary
        
        frame = frame_to_add(self.container, self)
        self.frames[frame_to_add] = frame
        frame.grid(row=0, column=0, sticky='nsew')

    def show_frame(self, cont):

        # Pops up a certain frame
        
        frame = self.frames[cont]
        frame.tkraise()

    def port_checker(self, port):

        # Check if the port is valid
        # Port need to be an int, in range 1024-56536
        # Return a message with the error if there are
        
        error_message = ''
        try: int(port)
        except ValueError:
            error_message = 'Port is a number\n'
            return error_message
        if(int(port) < 1024 or int(port) > 56536):
            error_message = error_message + 'Port range : 1024 - 65356\n'

        return error_message

    def ip_checker(self, ip):

        # Check if the ip is valid
        # Example ip 225.42.2.1
        # Ip need to contain 4 octets
        # Each octet is a number between 0-256
        # Return a message with the error if there are
        
        error_message = ''
        list_of_ip_octs = ip.split('.')
        if (not(len(list_of_ip_octs) == 4)):
            error_message = 'The ip contain 4 octets\nExample: 225.42.2.1\n'
        try:
            for i in list_of_ip_octs:
                int(i)
                if (not(len(i) > 0 and len(i) < 4) or (int(i) > 255)): 
                    error_message = error_message + 'Each octet range : 0-256\n'
        except ValueError:
            error_message = error_message + 'The ip octets are numbers'

        return error_message
    
    def get_correct_data(self, name, ip, port):

        # Check if all name, ip, port are valid
        # First check if all entrys are filled
        # Combain the port_checker with ip checker methods
        # Create a message and show it if its not empty
        # Return 0 if there are error, 1 if not
        
        if(len(ip) == 0 or len(port) == 0 or len(name) ==0):
            messagebox.showinfo(message='Please fill all boxes')
            return 0

        message = ''
        if(len(name) > 16):
            message = 'The maximum lenght of a name is 16\n'
        message = message + self.port_checker(port)
        message = message + self.ip_checker(ip)

        if(message != ''):
            messagebox.showinfo(message=message)
            return 0
        return 1
                
    def connect_to_server(self, event, name, ip, port):

        # Check if all data is valid if not brake from the function
        # Show message box if there is an error - mainly from s.connect
        # Add the Chat frame and bring it up fornt
        # Send the name to the server

        
        if(not(self.get_correct_data(name, ip, port))):
            return            

        self.socket_object = socket.socket()
        self.name = name
        try:
            self.socket_object.connect((ip, int(port)))
            self.add_frame(Chat_Window)
            self.show_frame(Chat_Window)
            self.socket_object.send(name.encode('UTF-8'))
        except TimeoutError:
            messagebox.showinfo('Connection error\nPlease check the ip and port')
        except Exception as e:
            message = 'Error: {}.{}, line:{}'.format(sys.exc_info()[0],
                                                     sys.exc_info()[1],
                                                     sys.exc_info()[2])
            print(message)
            send_error_info('In recv_info, Content-Type', self.socket_object)
            self.socket_object.close()


    def send_text(self, event, message_box, text):

        # Clear the entry in the Chat frame
        # Encode the text and send it
        # Add the text to the text box
        message_box.delete(0,len(message_box.get()))
        self.socket_object.send(text.encode('UTF-8'))
        frame = self.frames[Chat_Window]
        frame.insert_text('Send : ' + text + '\n')

    def recv_info(self, list_box, main_socket, name):

        # Runs in a thread
        # Waits for a message then split it to lines
        # split the first line by ' : '
        # if the first line is Content-Type:Names clear the
        # list box and then add them
        # if the first line is Content-Type:Message add the
        # message to the text box
        try:
            while(True):
                message = main_socket.recv(1024)
                message = message.decode('UTF-8')
                message_parts = message.split('\n')
                if(message_parts[0].split(':') == ['Content-Type','Names']):
                    list_box.delete(0,list_box.size())
                    for i in message_parts[1].split(','):
                        list_box.insert('end', i)
                elif(message_parts[0].split(':') == ['Content-Type','Message']):
                    frame = self.frames[Chat_Window]
                    if(name != (message_parts[1].split(':'))[0]):
                        frame.insert_text(message_parts[1] + '\n')
                else:
                    send_error_info('In recv_info, Content-Type', main_socket)
        except Exception as e:
            print(str(e))
                

class Connection_Window(tk.Frame):

    """
        This class inherent from tk.Frame that makes it tk.Frame object
        Initiaite the labels, entries, button
    """

    def __init__(self, parent, controller):

        # Set the main frame as fixed size
        # Set the button release event to invoke
        # the Main.connect_to_server(args) function
        
        tk.Frame.__init__(self, parent)
        controller.resizable(False, False)
        
        name_label = tk.Label(self, text='Name')
        name = tk.Entry(self)
        name_label.grid(row=0)
        name.grid(row=0, column=1)
        
        ip_label = tk.Label(self, text='IP Address')
        ip = tk.Entry(self)
        ip_label.grid(row=1)
        ip.grid(row=1, column=1)

        port_label = tk.Label(self, text='Port')
        port = tk.Entry(self)
        port_label.grid(row=2)
        port.grid(row=2, column=1)

        con_button = ttk.Button(self, text='Connect')
        con_button.bind('<ButtonRelease-1>',
                        lambda event: controller.connect_to_server(event,
                                                                   name.get(),
                                                                   ip.get(),
                                                                   port.get()))
        con_button.grid(row=3, column=1)


class Chat_Window(tk.Frame):

    """
        This class inherent from tk.Frame that makes it tk.Frame object
        Initiaite the text_box, entry, button, list_box
    """
    
    def __init__(self, parent, controller):

        # Set the button release event to invoke
        # the Main.send_text(args) function
        # Start the thread that recive packets from the server
        
        tk.Frame.__init__(self, parent)
        
        self.text = tk.Text(self, width=55, height=34, state='disabled')
        self.text.grid(row=0, column=0, sticky='nsew')
        
        list_box = tk.Listbox(self, height=36)
        list_box.grid(row=0, column=1, sticky='nsew')
        
        message = tk.Entry(self, width=62)
        message.grid(row=1, column=0, sticky='nsew')
        
        con_buttom = ttk.Button(self, text='Send')
        con_buttom.bind('<ButtonRelease-1>', lambda event: controller.send_text(event, message,
                                                                                message.get()))
        con_buttom.grid(row=1, column=1)

        global RECV_RUN
        if(not RECV_RUN):
            print('start thread')
            threading.Thread(target=controller.recv_info,
                             args=(list_box, controller.socket_object,
                                   controller.name),
                             daemon=True).start()
            RECV_RUN = 1

    def insert_text(self, text):

        # Insert text to new line in the text box
        
        self.text.configure(state='normal')
        self.text.insert(tk.END, text)
        self.text.configure(state='disabled')

if __name__ == '__main__':

    try:
        a = Main()
        a.mainloop()
    finally:
        a.socket_object.close()
