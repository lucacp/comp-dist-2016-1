from bottle import run, get, post, view, request, redirect, put
import threading
import time
import json
import requests
import sys
import hashlib

servers = [("localhost:8080")]
messages = [("Nobody", "Hello guys!", 0)]
tempo = [("localhost:8080",0)]

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

    def insert(self, k, v,n):
        for sk in subkeys(k):
            print(sk)
            if sk in self.h:
                if not self.h[sk]:
                    self.h[sk] = (k, v)
                    return sk
                else:
                    (k0,v0) = self.h[sk]
                    try:
                        if v0 != n:
                             r = requests.put("http://"+v0+"/dht/"+n+"/"+v)
                             print("DHT_OK:_'"+"http://"+v0+"/dht/"+n+"/"+v+"'")
                        else:
                             o=len(k)-1
                             self.insert(k[0:o],v,n)
                    except requests.exceptions.RequestException as e:
                        print("DHT_Error:_'"+"http://"+v0+"/dht/"+n+"/"+v+"'")
                        continue
                    return v0
					
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
    return {'messages': messages,'nick': '','time':tempo[0][1]}

@get('/<nick>')
@view('index')
def index(nick):
	global tempo
	return {'messages': messages,'nick': nick,'time':tempo[0][1]}

@post('/send')
def sendMessage():
	global tempo
	tempo[0]=(tempo[0][0],tempo[0][1]+1)
	m=request.forms.get('message')
	n=request.forms.get('nick')
	messages.append([n, m, tempo[0][1]])
	redirect('/'+n)

@get('/peers')
def getPeers():
	global servers
	return json.dumps(servers)

@get('/peers/add/<server>')
def getPeers(server):
	global servers
	global tempo
	flag=None
	if server not in servers:
		if len(servers) < 6:
			servers.append(server)
			tempo.append((server,0))
			flag=True
	return json.dumps(flag)
		
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
			r = None
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
			ad=str(sys.argv[1])+":"+str(sys.argv[2])
			if ad != tempo[0][0]:
				tempo.insert(0,(ad,tempo[0][1]))
			if i != ad:
				try:
					aux = requests.get("http://"+i+'/peers/time')
					s = requests.get("http://"+i+'/peers/msg')
				except requests.exceptions.RequestException as e:
					print("Connect_Error "+"http://"+i)
					continue
				au = json.loads(aux.content.decode("UTF-8"))
				ns = json.loads(s.content.decode("UTF-8"))
				for tin in range(0,len(tempo)):
					for tout in range(0,len(au)):
						if tempo[tin][0] == au[tout][0]:
							if tempo[tin][1] < au[tout][1]:
								dif = au[tout][1]-tempo[tin][1]
								tempo[tin] = au[tout]
								if len(messages) < len(ns):
									for j in range(len(messages),0):
										if messages[j] == ns[j] and dif > 0:
											for nov in range(j-1,len(ns)):
												messages.append(ns[nov])
												dif-=1
				for m in ns:
					print(m)
				for nm in au:
					print(nm)

@get('/dht/<key>')
def dht_lookup(key):
    global dht
    return json.dumps(dht.lookup(hashFunc(key)))

@put('/dht/<key>/<value>')
def dht_insert(key, value):
    global dht
    return json.dumps(dht.insert(hashFunc(key), value,key))
	
threading.Thread(target=clientServ).start()

threading.Thread(target=clientMsg).start()
	
threading.Thread(target=run,kwargs=dict(host=str(sys.argv[1]), port=str(sys.argv[2]))).start()
