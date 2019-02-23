import socket,thread,sys,os

MAX_BUFF_SIZE = 40000 # max size fo requests
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

    isHTTPS, webserver, port, url = parse_req(request)
    print("url = " + url)
    print("webserver = " + webserver)
    print("port = " + str(port))
    if BLOCKED.get(url) == 1:
        conn.send("HTTP/1.0 200 OK\r\n")
        print_msg_browser(conn, "Blocked by Administrator")
        conn.close()
        sys.exit(1)
    else:
        if isHTTPS is True:
            pass
            print("HTTPS REQUEST!!!!")

        else:
            http_connect(conn, webserver, port, request)
#****************************************************************************
#****************************************************************************

def parse_req(request):
    isHTTPS = False
    try:
        first_line = request.split('\n')[0]
        url = first_line.split(' ')[1]
        #HTTPS requests will have "GET" encrypted
        if first_line.find("GET") == -1:
            isHTTPS = True
        # print("Request:",first_line, addr)

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
            port = 80 # default port
            webserver = temp[:webserver_pos]
        else:       # specific port
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]
        if isHTTPS:
            port = 443

        return isHTTPS, webserver, port, url

    except Exception:
        print("Expception")



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

def https_connect(conn):
    pass


def print_msg_browser(conn, string):
            conn.send("Content-Length: 11\r\n")
            conn.send("Content-Type: text/html" + "\r\n")
            conn.send("\r\n")
            conn.send("<html> <h1>" + string + "</h1> </html>\r\n")
            conn.send("\r\n\r\n")

if __name__ == '__main__':
    main()
