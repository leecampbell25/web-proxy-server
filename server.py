import socket,thread,sys,os

MAX_BUFF_SIZE = 40000 # max size for requests
BACKLOG = 10 # number of incoming connections that can be queued for acceptance
host = '' # localhost(blank)
port = 8080 # alt-http-port
BLOCKED = {"http://www.learnprolognow.org/lpnpage.php?pagetype=html&pageid=lpn-htmlse1":1}
def main():

    try:
        print("HTTP Proxy Server running on local host,","port",port)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create Socket
        s.bind((host, port)) # Bind socket to a host and port
        s.listen(BACKLOG)  # Listen for incoming connection attempts

    except socket.error as e:
        if s:
            s.close()
        print (e)
        sys.exit(1)

    while True:

        conn, addr = s.accept()
        request = conn.recv(MAX_BUFF_SIZE)
        thread.start_new_thread(request_thread, (conn, addr, request))



#*********** Get the request from browser *********************************
def request_thread(conn, addr, request):

    try:
        ssl, webserver, port, url = parse_req(request)
        print("url = " + url)
        print("webserver = " + webserver)
        print("port = " + str(port))
        if BLOCKED.get(url) == 1:
            conn.send("HTTP/1.0 200 OK\r\n")
            print_msg_browser(conn, "Blocked by Administrator")
            conn.close()
            sys.exit(1)
        else:
            if ssl is True:
                print("HTTPS REQUEST!!!!")
                https_connect(conn, webserver, port, request)

            else:
                http_connect(conn, webserver, port, request)
    except Exception:
        pass
#****************************************************************************
#****************************************************************************

def parse_req(request):
    try:
        first_line = request.split('\n')[0]
        url = first_line.split(' ')[1]
        print(first_line)
        # Tunneling request
        if "CONNECT" in first_line:
            ssl = True
        else:
            ssl = False
#*********** Parse request for webserver and port *************************

        http_pos = url.find("://")          # find position of ://

        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):]       # extract remaining url

        port_pos = temp.find(":")           # find port position (if exists)

#*********** Find Web Server **********************************************

        webserver_pos = temp.find("/") #Find end of web server
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos):
            if ssl is True:
                port = 443 # default ssl port
            else:
                port = 80 # default standard port
                webserver = temp[:webserver_pos]
        else:       # specific port
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        return ssl, webserver, port, url

    except Exception:
        pass
        print("Exception")



#****************************************************************************
#****************************************************************************

def http_connect(conn, webserver, port, request):
#*********** Connect to Web Server ****************************************
    try:
        # create a socket to connect to the web server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(request)         # send request to webserver

        while True:
            # receive data from web server
            data = s.recv(MAX_BUFF_SIZE)

            if not data:
                break
            conn.send(data)

        s.close()
        conn.close()

    except socket.error as e:
        if s:
            s.close()
        if conn:
            conn.close()
        print(e) #RST

#****************************************************************************
#****************************************************************************

def https_connect(conn, webserver, port, request):
    try:

        #The proxy accepts the connection on its port 8080, receives the
        #request, and connects to the destination server on the port requested by the client
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))

        #Proxy replies to the client that a connection is established
        conn.sendall("HTTP/1.0 200 Connection established\r\nProxy-Agent: Pyx\r\n\r\n")

        # Indiscriminately forward bytes using SSL tunneling
        s.setblocking(0)
        conn.setblocking(0)
        while True:
            try:
                request = conn.recv(MAX_BUFF_SIZE)
                s.sendall(request) # send browser request to web server
            except socket.error as err:
                pass
            try:
                reply = s.recv(MAX_BUFF_SIZE)
                conn.sendall(reply) # send server reply to browser
            except socket.error as err:
                pass

        s.close()
        conn.close()

    except socket.error as err:
        # If the connection could not be established, exit
        # Should properly handle the exit with http error code here
        print(err)
        #break

def print_msg_browser(conn, string):
            conn.send("Content-Length: 11\r\n")
            conn.send("Content-Type: text/html" + "\r\n")
            conn.send("\r\n")
            conn.send("<html> <h1>" + string + "</h1> </html>\r\n")
            conn.send("\r\n\r\n")

if __name__ == '__main__':
    main()
