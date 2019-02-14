import socket

host = '' # localhost(blank)
port = 8080 # alt-http-port

try:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create Socket
    s.bind((host, port)) # Bind socket to a host and port

except socket.error as err:
        if s:
            s.close()
        print ("Socket could not be opened")
        sys.exit(0)
