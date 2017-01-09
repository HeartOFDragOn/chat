import threading
import base64, hashlib
import struct, socket

class MyWebSocket(threading.Thread):

	def __init__(self, name, conn):
		threading.Thread.__init__(self)
		self.name = name
		self.conn = conn
		self.buff = ""

	def shakehand(self):
		headers = {}
		shake = self.conn.recv(1024)

		if not len(shake):
			return False

		header, data = shake.split('\r\n\r\n', 1)
		for line in header.split('\r\n')[1:]:
			key, value = line.split(": ", 1)
			headers[key] = value
		if headers.has_key("Sec-WebSocket-Key") == False:
			print "this is not a socket connection"
			self.conn.close()
			return False

		origin = headers["Origin"]
		swKey = self.get_key(headers["Sec-WebSocket-Key"])
		swHost = headers["Host"]

		shake_data = "HTTP/1.1 101 Switching Protocols\r\n" \
                    "Upgrade:websocket\r\n"\
                    "Connection: Upgrade\r\n"\
                    "Sec-WebSocket-Accept:"+ swKey + "\r\n" \
                    "WebSocket-Origin:" + origin + "\r\n" \
                    "WebSocket-Location: ws://" + swHost + "/WebManagerSocket\r\n" \
                    "WebSocket-Protocol:WebManagerSocket\r\n\r\n"
		print shake_data
		self.conn.send(shake_data)
		return True

	def get_key(self, key):
		return base64.b64encode(hashlib.sha1(key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())

	def recv_data(self):
		try:
			data = self.conn.recv(1024)
			if not len(data):
				return False
		except:
			return False
		else:
			code_length = ord(data[1]) & 127
			if code_length == 126:
				masks = data[4:8]
				data = data[8:]
			elif code_length == 127:
				masks = data[10:14]
				data = data[14:]
			else:
				masks = data[2:6]
				data = data[6:]
		raw_str = ""
		i = 0
		for d in data:
			raw_str += chr(ord(d) ^ ord(masks[i%4]))
			i += 1
		return raw_str

	def run(self):
		if not self.shakehand():
			print "fail to create connection"
		else:
			send_message("welcome " + self.name, True)
			while True:
				data = self.recv_data()
				if data == False:
					break
				self.buff = data
				send_message(data, False)
				print self.name + ": " + data

connectionList = {}

def send_message(data, welcome):
	if not data:
		return False
	else:
		data = str(data)
	token = "\x81"
	length = len(data)
	if length < 126:
		token += struct.pack("B", length)
	elif length <= 0xFFFF:
		token += struct.pack("!BH", 126, length)
	else:
		token += struct.pack("!BQ", 127, length)
	data = '%s%s' % (token, data) 
	global connectionList
	if not welcome:
		for socket in connectionList.values():
			socket.conn.send(socket.name + ": \r\n" + "\t" + data + "\r\n")
	else:
		for socket in connectionList.values():
			socket.conn.send("\t" + data + "\r\n")
	return True

class SocketServer(object):

	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.sock.bind(("localhost", 8080))
			self.sock.listen(100)
			print("server listening...")
		except Exception as e:
			print("server exception....", e)

	def begin(self):
		global connectionList
		i = 1
		while True:
			connection, address = self.sock.accept()
			mysocket = MyWebSocket(address[0], connection)
			mysocket.start()
			connectionList["connection" + str(i)] = mysocket
			i += 1

if __name__ == '__main__':
	server = SocketServer()
	server.begin()