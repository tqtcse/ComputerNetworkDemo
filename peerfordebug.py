from socket import *
import time
from threading import Thread
import os
#  khai bao
#port serverthead 3000
filename = 'torrent_file.txt'
request = {
    'GET_LIST_PEER': 'GET_LIST_PEER',
    'ASK_PIECE': 'ASK_PIECE',
    'SUMIT_INFO': 'SUMIT_INFO',
    'DOWN_PIECE': 'DOWN_PIECE',
    'FINISH_DOWN':'FINISH_DOWN'
}
list_peers = []
serverthread_info = []
my_bitfield = ['1','1','1','1','1','1','0','0','0','0'] # the hien xem minh dang co piece nao
other_peers_bitfield = []
numthread_client = 0
peer_dataa_folder = 'peer1_data'
#
def Handle_torrentfile(filename):
    with open(filename, mode = "r+",encoding = 'utf-8') as file:
        data = file.read()
        i = 0
        torrent_dict = {}
        while i < len(data) and data[i] != 'e':
            s_key = ''
            listt = []
            if data[i] == 'd':
                i += 1
                k = 0
            if data[i] <= '9' and data[i] >= '0':
                s_key = s_key + data[i]
                i = i + 1
                if data[i] == ':':
                    slength_key = int(s_key)
                    s_key = data[i+1: i+slength_key+1]
                    i = i + slength_key +1
                    k = k + 1
            if data[i] == 'l':
                i = i+1
                listt = []
                while data[i] != 'e':
                    s = ''
                    while data[i] != ':':
                        if data[i] <= '9' and data[i] >= '0':
                            s = s + data[i]
                            i = i + 1
                            if data[i] == ':':
                                slength = int(s[0:len(s)])
                                s = data[i + 1: i + slength + 1]
                                i = i + slength + 1
                                break
                    listt.append(s)
                    del s
                k = k + 1
            if k == 2:
                torrent_dict[s_key] = listt
                del s_key
                k = 0
                i = i + 1
    return torrent_dict

def Connect_tracker(trakerip, trackerport,list_peer,serversocket):
    peer_to_tracker_socket = socket(AF_INET, SOCK_STREAM)
    peer_to_tracker_socket.connect((trakerip, trackerport))

    Submit_info(serversocket,peer_to_tracker_socket,request['SUMIT_INFO'])
    Get_list(peer_to_tracker_socket,request['GET_LIST_PEER'],list_peer)
    peer_to_tracker_socket.close()

def Submit_info(serversocket,peer_to_tracker_socket ,request):
    peer_ip_server_thread = serversocket.getsockname()[0]
    peer_port_server_thread = serversocket.getsockname()[1]

    peer_to_tracker_socket.send(request.encode('utf-8'))

    peer_to_tracker_socket.recv(1024)
    #print(peer_ip_server_thread)
    peer_to_tracker_socket.send(peer_ip_server_thread.encode('utf-8'))
    peer_to_tracker_socket.recv(1024)
    #print(peer_port_server_thread)
    peer_to_tracker_socket.send(str(peer_port_server_thread).encode('utf-8'))
def Get_list(p2t_socket,request,list_peer):

    p2t_socket.send(request.encode('utf-8'))
    state = p2t_socket.recv(1024).decode('utf-8')
    while state != 'FINISH':
        peer_ip = state
        p2t_socket.send('OK'.encode())
        peet_port = p2t_socket.recv(1024).decode('utf-8')
        p2t_socket.send('Continue'.encode())
        state = p2t_socket.recv(1024).decode('utf-8')

        list_peer.append([peer_ip,int(peet_port)])
        #print(list_peer)







def Connect_peer_clientthread(serverip, serverport,threadclient_id):
    count_thread = 0
    clientsocket = socket(AF_INET, SOCK_STREAM)
    clientsocket.connect((serverip, serverport))

    Ask_piece(clientsocket,threadclient_id)
    print('in Connect_peer_clientthread' , len(other_peers_bitfield),numthread_client)
    while numthread_client != len(other_peers_bitfield):
        pass
    piece_need_to_down = Map_piece_to_peer(threadclient_id)
    Download_piece(piece_need_to_down,clientsocket)

    count_thread += 1
    if count_thread == numthread_client:
        print('Hoàn thành tải file')
    #threads = Thread(target=new_connection_clientthread, args=(threadid,serverip, serverport))
    #threads.start()

    # TODO: wait for all threads to finish
    #[t.join() for t in threads]

    #day la 1 thread, co the la se chayj 1 vong for de ket noi voi tat ca cac peer server
def Ask_piece(clientsocket,threadclient_id):
    print('in Ask_piece')
    clientsocket.send(request['ASK_PIECE'].encode('utf-8'))
    bitf_list = clientsocket.recv(1024).decode('utf-8')
    print(bitf_list)
    other_peers_bitfield.append([threadclient_id, bitf_list.split(' ')])
def Map_piece_to_peer(id):# tim piece can down trong cac peer khac
    print('in Map_piece_to_peer')
    my_bfield_list = my_bitfield
    dict_bitfield_serverthread = {}# id la dict_bitfield[key]
    piece_need_to_down = ['0','0','0','0','0','0','0','0','0','0']
    for i in other_peers_bitfield:
        dict_bitfield_serverthread[i[0]] = i[1]
    for piece in range(0,len(my_bfield_list)):
        for Key in dict_bitfield_serverthread:
            if my_bfield_list[piece] == '0' and dict_bitfield_serverthread[Key][piece] == '1' and Key == id:
                piece_need_to_down[piece] = '1'
    #piece_need_to_down = ' '.join(piece_need_to_down)# chuyen sang list sang str
    print(piece_need_to_down)
    return piece_need_to_down
def Download_piece(piece_need_to_down,clientsocket):
    print('in Download_piece')
    piece_id = []
    for piece in range(0,len(piece_need_to_down)):#chuyen tu bitfile sang piece_id(trong torrent_file)
        if piece_need_to_down[piece] == '1':
            piece_id.append(torrent['piece'][piece])
        else:
            piece_id.append('0')

    for i in range(0, len(my_bitfield)):# tai file dong thoi cap nhap lai my_bitfield
         if piece_id[i] != '0' and my_bitfield[i] == '0':
            if my_bitfield[i] == '1':
                continue
            clientsocket.send(request['DOWN_PIECE'].encode('utf-8'))
            clientsocket.send(piece_id[i].encode('utf-8'))#gui id piece can download
            print(piece_id[i])
            if my_bitfield[i] == '1':
                continue
            Save_piece(clientsocket)
            my_bitfield[i] = '1'

    clientsocket.send(request['FINISH_DOWN'].encode('utf8'))
def Save_piece(clientsocket):
    print('in Save_piece')
    print('in Save_piece1')
    piece = clientsocket.recv(100).decode('utf-8')
    print('in Save_piece2')
    piece_size = clientsocket.recv(100).decode('utf-8')
    print('in Save_piece3')

    peer_data_name = peer_dataa_folder
    current_work_dir = os.getcwd()
    file_name = torrent['filename'][0]
    piecepath = '\\' + peer_data_name + '\\' + str(file_name)

    if os.path.exists(current_work_dir+piecepath) == False:
        os.mkdir(current_work_dir+piecepath)

    print(current_work_dir+piecepath+'\\'+piece)
    with open(current_work_dir+piecepath+'\\'+piece, mode='wb') as file:
        count = 0
        while count < int(piece_size):
            data = clientsocket.recv(1024)
            if not (data):
                break
            file.write(data)
            print(data,int(piece_size))
            count += len(data)
            print('downloading',count)
#def new_connection_clientthread(threadid,serverip, serverport):#ket noi voi tung serverthread cua cac peer de tai file
#    pass







def Connect_peer_serverthread(serverip, serverport,torrent_file_encoded,list_peer):
    serversocket = socket(AF_INET, SOCK_STREAM)
    serversocket.bind((serverip, serverport))
    Connect_tracker(torrent_file_encoded['announce'][0],int(torrent_file_encoded['announce'][1]),list_peer,serversocket)
    #print(list_peer)
    serversocket.listen(1)
    while True:
        print('in serverthread1')
        conn, addr = serversocket.accept()
        nconn = Thread(target=new_connection_serverthread, args=(conn, addr))
        print('in serverthread2')
        nconn.start()
def new_connection_serverthread(conn, addr):# xu li cac request cua cac clientthread cua cac peer
    print('in new_connection_serverthread')
    request = conn.recv(200).decode('utf-8')
    print (request)
    while True:
        if request == 'ASK_PIECE':
            Answer_piece(conn,request)
            print(request)
        if request == 'DOWN_PIECE':
            Upload_piece(conn, request)
            print(request)
        if request == 'FINISH_DOWN':
            break
        request = conn.recv(200).decode('utf-8')
        print(request,'000')
def Answer_piece(conn,request):# chuyen sang list sang str
    print('in Answer_piece')
    conn.send(' '.join(my_bitfield).encode('utf-8'))
def Upload_piece(conn,request):
    print('in Upload_piece')

    peer_data_name = peer_dataa_folder
    print('Upload_piece1')
    pieceid = conn.recv(100).decode('utf-8')
    print('Upload_piece2')
    current_work_dir = os.getcwd()
    file_name = torrent['filename'][0]
    piecepath = '\\' + peer_data_name + '\\' + str(file_name) + '\\' + pieceid + '.txt'
    piece_size = os.path.getsize(current_work_dir+piecepath)

    conn.send(str(pieceid+'.txt').encode('utf-8'))
    conn.send(str(piece_size).encode('utf-8'))
    with open(current_work_dir+piecepath, mode='rb') as file:
        count = 0
        while count < int(piece_size):
            data = file.read(1024)
            if not (data):
                break
            conn.sendall(data)
            print(data,int(piece_size))
            count += len(data)
            print('uploading',count)

#print(torrent)
#Connect_tracker(torrent['announce'][0],int(torrent['announce'][1]),list_peer)
torrent = Handle_torrentfile(filename)
print('Torrent file content:',torrent)

if __name__ == "__main__":
    #hostname = socket.gethostname(
    server_thread_ip = 'localhost'
    server_thread_port = 3500
    print("Peer0 server thread listening on: {}:{}".format(server_thread_ip,server_thread_port))
    #chay serverthread
    t_server = Thread(target=Connect_peer_serverthread,args=(server_thread_ip, server_thread_port,torrent,list_peers))
    t_server.start()
    #chay clientthread
    while True:
        lenh = input('Nhập lệnh: ')
        if lenh == 'run':
            numthread_client = len(list_peers) - 1
            threadclient_id = 0
            for i in list_peers:
                if ['127.0.0.1',server_thread_port] == i:
                    continue
                t = Thread(target=Connect_peer_clientthread,
                       args=(i[0], int(i[1]),threadclient_id))
                t.start()
                print('clientthread run')
                threadclient_id += threadclient_id
            break
        else:
            print('nhap lai lenh')