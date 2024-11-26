from socket import *
from threading import Thread
import time

list_peer = []
def get_host_default_interface_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    try:
       s.connect(('8.8.8.8',1))
       ip = s.getsockname()[0]
    except Exception:
       ip = '127.0.0.1'
    finally:
       s.close()
    ip = 'localhost'
    return ip

def Connect_to_peer(trackerip, trackerport):
    trackersocket = socket(AF_INET, SOCK_STREAM)
    trackersocket.bind((trackerip, trackerport))

    trackersocket.listen(10)
    while True:
        conn, addr = trackersocket.accept()
        nconn = Thread(target=new_connection, args=(conn, addr))
        nconn.start()
def new_connection(conn,addr):
    while True:
        peer_request = conn.recv(1024).decode('utf-8')
        if peer_request == 'GET_LIST_PEER':
            Send_list(conn,list_peer)
            break
        if peer_request == 'SUMIT_INFO':
            Add_list(list_peer,conn)
    conn.close()

def Add_list(peer_list, trackersocket):
    trackersocket.send('OK'.encode())
    peer_serverthread_ip = trackersocket.recv(1024).decode('utf-8')
    trackersocket.send('OK'.encode())
    peer_serverthread_port = trackersocket.recv(1024).decode('utf-8')
    peer_list.append([peer_serverthread_ip,int(peer_serverthread_port)])
    print(peer_list)
def Send_list(trackersocket,peer_list):
    for peerip, peerport in peer_list:
        trackersocket.send(peerip.encode('utf-8'))
        trackersocket.recv(1024)
        trackersocket.send(str(peerport).encode('utf-8'))
        trackersocket.recv(1024)
    trackersocket.send('FINISH'.encode('utf-8'))


if __name__ == "__main__":
    #hostname = socket.gethostname()
    hostip = get_host_default_interface_ip()
    port = 22222
    print("Listening on: {}:{}".format(hostip,port))
    Connect_to_peer(hostip, port)

