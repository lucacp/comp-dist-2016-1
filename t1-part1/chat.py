from bottle import run, get, post, view, request, redirect, put
import threading
import time
import json
import requests
import sys
import hashlib

servers = [("localhost:8080")]
messages = [("Nobody", "Hello guys!", 0)]
tempo = 0

def subkeys(k):
    for i in range(len(k), 0, -1):
        yield k[:i]
    yield ""

class DHT:
    def __init__(self, k):
        self.k = k
        self.h = {}

        for sk in subkeys(self.k):
            self.h[sk] = None

    def insert(self, k, v):
        for sk in subkeys(k):
            print("sk: "+sk)
            if sk in self.h:
                if not self.h[sk]:
                    self.h[sk] = (k, v)
                    return sk
        return None

    def lookup(self, k):
        print(list(subkeys(k)))
        for sk in subkeys(k):
            print(sk)
            print(self.h)
            if sk in self.h:
                if self.h[sk]:
                    (ki, vi) = self.h[sk]
                    if ki == k:
                        return vi
        return None

    def __repr__(self):
        return "<<DHT:"+ repr(self.h) +">>"
	
def hashFunc(h):
	print("in: "+h)
	d = hashlib.md5()
	d.update(h.encode('utf-8'))
	print("hex.hash: "+d.hexdigest())
	i = int(d.hexdigest(),16)
	print("int.hash: "+str(i))
	j = str(i)
	l=""
	for k in range(0,len(j)):
		l += str(int(j[k])%2)
	print("out: "+l)
	return l

dht = DHT(hashFunc(str(sys.argv[1])+":"+str(sys.argv[2])))

@get('/')
@view('index')
def index():
    global tempo
    return {'messages': messages,'nick': '','time':tempo}

@get('/<nick>')
@view('index')
def index(nick):
	global tempo
	return {'messages': messages,'nick': nick,'time':tempo}

@post('/send')
def sendMessage():
	global tempo
	tempo+=1
	m=request.forms.get('message')
	n=request.forms.get('nick')	
	messages.append([n, m, tempo])
	redirect('/'+n)

@get('/peers')
def getPeers():
	global servers
	return json.dumps(servers)	

@get('/peers/add/<server>')
def getPeers(server):
	global servers
	ad = server.split(':')
	if ad not in servers:
		if len(servers) < 6:
			servers.append(ad)
	return json.dumps(servers)	
		
@get('/peers/msg')
def getMsg():
	global messages
	return json.dumps(messages)

@get('/peers/time')
def getTime():
	global tempo
	return json.dumps(tempo)
	
def clientServ():
	while True:
		global servers
		ad=str(sys.argv[1])+":"+str(sys.argv[2])
		if ad not in servers:
			servers.insert(0,ad)
		#print(ad)
		for i in servers:
			time.sleep(3)
			if i != ad:
				try:
					requests.get("http://"+i+"/peers/add/"+str(sys.argv[1]+':'+sys.argv[2]))
				except requests.exceptions.RequestException as e:
					print("Connect_Error "+"http://"+i)
				try:
					s = requests.get("http://"+i+'/peers')
				except requests.exceptions.RequestException as e:
					print("Connect_Error "+"http://"+i)
					continue
				ns = json.loads(s.content.decode("UTF-8"))
				for j in ns:
					if j not in servers:
						if len(servers) < 6:
							servers.append(j)

def clientMsg():
	while True:
		global messages
		global servers
		global tempo
		for i in servers:
			time.sleep(1)
			flag = None
			ad=str(sys.argv[1])+":"+str(sys.argv[2])
			if i[0] != ad[0] or i[1] != ad[1]:
				try:
					aux = requests.get("http://"+i+'/peers/time')
				except requests.exceptions.RequestException as e:
					print("Connect_Error "+"http://"+i)
					continue
				au = json.loads(aux.content.decode("UTF-8"))
				if au > tempo:
					tempo = au
					flag = True
				try:
					s = requests.get("http://"+i+'/peers/msg')
				except requests.exceptions.RequestException as e:
					print("Connect_Error "+"http://"+i)
					continue
				ns = json.loads(s.content.decode("UTF-8"))
				for j in ns:
					if j not in messages and j[2]!=0:
						if flag:
							messages.insert(j[2],j)
						else:
							messages.append(j)
						print(j)

@get('/dht/<key>')
def dht_lookup(key):
    global dht
    return json.dumps(dht.lookup(hashFunc(key)))

@put('/dht/<key>/<value>')
def dht_insert(key, value):
    global dht
    return json.dumps(dht.insert(hashFunc(key), value))
	
threading.Thread(target=clientServ).start()

threading.Thread(target=clientMsg).start()
	
threading.Thread(target=run,kwargs=dict(host=str(sys.argv[1]), port=str(sys.argv[2]))).start()
