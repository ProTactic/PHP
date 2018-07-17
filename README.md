# Synchronized server-client

## Server contain 2 main progrmas:

  server.py - the main server that handle the connections, based on schedular
              use selcet() in order to not wait for IO from the socket.
              
  log_server.py - the server that saves client errors.

## Client contain 1 main program:
  
  client.pyw - GUI interface: Connection and the chat box.
