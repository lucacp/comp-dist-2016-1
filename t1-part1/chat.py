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
	def __init__(self,k,t,p):
		self.a = k
		self.t = t
		self.p = None
		if p == None:
			self.p = [("localhost:8080",0)]
		else:
			self.p = []
			for i in range(0,len(p)-1):
				ad = (p[i],p[i+1])
				i=i+2
				self.p.append(ad)
			
	def __eq__(self, other):
		return (self.procuraT(other.a) == other.t and len(self.p) == len(other.p))
	def procuraT(self,k):
		for i in range(len(self.p)):
			if k == self.p[i][0]:
				return self.p[i][1]
		return -1
	def addin(self,k,t):
		if k != self.a:	
			for i in range(len(self.p)):
				if self.p[i][0] == k:
					if self.p[i][1] < t:
						self.p[i] = [k,t]
						return True
					return False
			ad=(k,t)
			self.p.append(ad)
			return True
		else:
			return False
	def atualiza(self,a,t):
		return self.addin(a,t)
	def exportar(self):
		ad = ([self.a,self.t])
		if len(self.p) == 0:
			ad.append(None)
		else:
			pe = []
			for i in self.p:
				pe.append(i)
			ad.append(pe)
		return ad
		
tempo = VecClock(str(sys.argv[1])+":"+str(sys.argv[2]),0,None)

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
	flag=False
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
	return json.dumps(tempo.exportar())
	
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
					s = requests.get("http://"+i+'/peers')
				except requests.exceptions.RequestException as e:
					print("Timeout: http://"+i)
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
			if i != ad and not tempo.addin(i,0):
				try:
					aux = requests.get("http://"+i+'/peers/time')
					s = requests.get("http://"+i+'/peers/msg')
				except requests.exceptions.RequestException as e:
					print("Timeout: http://"+i)
					continue
				au = json.loads(aux.content.decode("UTF-8"))
				ns = json.loads(s.content.decode("UTF-8"))
				print(au)
				ti=VecClock(au[0],au[1],au[2])	
				if tempo.atualiza(ti.a,ti.t):
					msg=getMsg(ns,i)
					flag = False
					for j in range(len(msg)):
						for k in range(len(messages)):
							if messages[k] == msg[j]:
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
