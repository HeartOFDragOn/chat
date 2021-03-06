import socket,threading,struct
import sys
import base64, hashlib

def InitWebSocketServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("localhost",8080)) 
        sock.listen(100)
        print "listening....."
    except:
        print("Server is already running,quit")
        sys.exit()
    while True:  
        connection,address = sock.accept()
        if(handshake(connection) != False): 
            t = threading.Thread(target=DoRemoteCommand,args=(connection,))
            t.start()


def handshake(client):
    headers = {}
    shake = client.recv(1024)
    
    if not len(shake):
        return False
    
    header, data = shake.split('\r\n\r\n', 1)
    for line in header.split("\r\n")[1:]:
        key, value = line.split(": ", 1)
        headers[key] = value
    
    if(headers.has_key("Sec-WebSocket-Key") == False):
        print("this socket is not websocket,close")
        client.close()
        return False
    print headers
    szOrigin = headers["Origin"]
    szKey = base64.b64encode(hashlib.sha1(headers["Sec-WebSocket-Key"] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
    szHost = headers["Host"]
    
    our_handshake = "HTTP/1.1 101 Switching Protocols\r\n" \
                    "Upgrade:websocket\r\n"\
                    "Connection: Upgrade\r\n"\
                    "Sec-WebSocket-Accept:"+ szKey + "\r\n" \
                    "WebSocket-Origin:" + szOrigin + "\r\n" \
                    "WebSocket-Location: ws://" + szHost + "/WebManagerSocket\r\n" \
                    "WebSocket-Protocol:WebManagerSocket\r\n\r\n"
                    
    client.send(our_handshake)
    return True

def RecvData(nNum,client):
    try:
        pData = client.recv(nNum)
        if not len(pData):
            return False
    except:
        return False
    else:
        code_length = ord(pData[1]) & 127
        if code_length == 126:
            masks = pData[4:8]
            data = pData[8:]
        elif code_length == 127:
            masks = pData[10:14]
            data = pData[14:]
        else:
            masks = pData[2:6]
            data = pData[6:]
        
        raw_str = ""
        i = 0
        for d in data:
            raw_str += chr(ord(d) ^ ord(masks[i%4]))
            i += 1
            
        return raw_str
        
        
def SendData(pData,client):
    if(pData == False):
        return False
    else:
        pData = str(pData)
        
    token = "\x81"
    length = len(pData)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)
    pData = '%s%s' % (token,pData)

    client.send(pData)
    
    return True

def DoRemoteCommand(connection):
    while 1:
        szBuf = RecvData(8196,connection)
        print szBuf
        SendData("11", connection)
        if(szBuf == False):
            break

if __name__ == '__main__':
    InitWebSocketServer()