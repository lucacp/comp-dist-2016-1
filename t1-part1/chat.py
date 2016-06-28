from bottle import run, get, post, view, request, redirect, put
import threading
import time
import json
import requests
import sys
import hashlib

servers = ["localhost:8080"]
messages = [("0.0.0.0:80","Nobody", "Hello guys!", 0)]

def subkeys(k):
    for i in range(len(k), 0, -1):
        yield k[:i]
    yield ""

class VecClock:
	def __init__(self,k):
		self.a = k
		self.t = 0
		self.p = {}
	
	def procuraT(self,k):
		for i in range(self.p):
			if k == self.p[i][0]:
				return self.p[i][1]
	def compara(self,k,t):
		if self.procuraT(k) == t:
			return True
		return False
	def addin(self,k,t):
		if k != self.a:	
			for i in range(self.p):
				if self.p[i][0] == k:
					if self.p[i][1] < t:
						self.p[i] = (k,t)
						return True
					return False
			self.p.append(k,t)
			return True
		else:
			
	def atualiza(self,v1):
		if compara(v1.a,v1.t):
			return False
		else:
			return addin(v1.a,v1.t)
	def getOthers(self):
		return self.p
		
tempo = VecClock(str(sys.argv[1])+":"+str(sys.argv[2]))

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
                             if len(k) > 2:
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
    return {'server': tempo.a,'messages': messages,'nick': '','time':tempo.t}

@get('/<nick>')
@view('index')
def index(nick):
	global tempo
	return {'server': tempo.a,'messages': messages,'nick': nick,'time':tempo.t}

@post('/send')
def sendMessage():
	global tempo
	tempo.t = tempo.t+1
	m=request.forms.get('message')
	n=request.forms.get('nick')
	messages.append([tempo.a,n, m, tempo.t])
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
			tempo.addin(server,0)
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

def getMsg(msg,a):
	f=None
	for i in range(len(msg)):
		if msg[i][0] == a:
			f.append(msg[i])
	return f

def clientMsg():
	while True:
		global messages
		global servers
		global tempo
		for i in servers:
			time.sleep(1)
			ad=str(sys.argv[1])+":"+str(sys.argv[2])
			if i != ad:
				try:
					aux = requests.get("http://"+i+'/peers/time')
					s = requests.get("http://"+i+'/peers/msg')
				except requests.exceptions.RequestException as e:
					print("Connect_Error "+"http://"+i)
					continue
				au = json.loads(aux.content.decode("UTF-8"))
				ns = json.loads(s.content.decode("UTF-8"))
				if atualiza(au):
					msg=getMsg(ns,i)
					flag = False
					for j in range(len(msg)):
						for k in range(len(messages)):
							if messages[k][0] == msg[j][0] and messages[k][1] == msg[j][1] and messages[k][2] == msg[j][2] and messages[k][3] == msg[j][3]:
								flag = True
						if flag == False:
							messages.append(msg[j])
					
				for m in messages:
					print(m)
				for nm in tempo.p:
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
