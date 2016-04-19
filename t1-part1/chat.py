from bottle import run, get, post, view, request, redirect, put
import threading
import time
import json
import requests
import sys
import hashlib
servers = [("localhost","8080")]
messages = [("Nobody", "Hello guys!", 0)]
tempo = 0
@get('/')
@view('index')
def index():
    return {'messages': messages,'nick': ''}

@get('/<nick>')
@view('index')
def index(nick):
	return {'messages': messages,'nick': nick}

@post('/send')
def sendMessage():
	global tempo
	m=request.forms.get('message')
	n=request.forms.get('nick')	
	messages.append([n, m, ++tempo])
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
		if len(servers) < 3:
			servers.append(ad)
	return json.dumps(servers)	
		
@get('/peers/msg')
def getMsg():
	global messages
	return json.dumps(messages)
	
def clientServ():
	while True:
		global servers
		ad=[str(sys.argv[1]),str(sys.argv[2])]
		#if ad not in servers:
		#	servers.append(ad)
		#print(ad)
		for i in servers:
			time.sleep(5)
			if i[0] != ad[0] and i[1] != ad[1]:
				requests.get("http://"+i[0]+":"+i[1]+"/peers/add/"+str(sys.argv[1]+':'+sys.argv[2]))
				s = requests.get("http://"+i[0]+":"+i[1]+'/peers')
				ns = json.loads(s.content.decode("UTF-8"))
				for j in ns:
					if j not in servers:
						if len(servers) < 3:
							servers.append(j)

def clientMsg():
	while True:
		time.sleep(2)
		global messages
		global servers
		global tempo
		for i in servers:
			tempo+=1
			time.sleep(1)
			ad=[str(sys.argv[1]),str(sys.argv[2])]
			if i != ad:
				s = requests.get("http://"+i[0]+':'+i[1]+'/peers/msg')
				ns = json.loads(s.content.decode("UTF-8"))
				for j in ns:
					if j[2] >= tempo:
						if j not in messages:
							messages.append(j)
							print(j)

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

dht = DHT("abcd")

@get('/dht/<key>')
def dht_lookup(key):
    global dht
    return json.dumps(dht.lookup(dht,key))

@put('/dht/<key>/<value>')
def dht_insert(key, value):
    global dht
    return json.dumps(dht.insert(dht,key, value))

	
threading.Thread(target=clientServ).start()

threading.Thread(target=clientMsg).start()
	
threading.Thread(target=run,kwargs=dict(host=str(sys.argv[1]), port=str(sys.argv[2]))).start()
