from bottle import run, get, post, view, request, redirect, put
import threading
import time
import json
import requests
import sys
servers = ["http://localhost:8080"]
messages = [("Nobody", "Hello guys!")]
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
	m=request.forms.get('message')
	n=request.forms.get('nick')	
	messages.append([n, m])
	redirect('/'+n)

@get('/peers')
def getPeers():
	global servers
	return json.dumps(servers)	

@get('/peers/add/<server>')
def getPeers(server):
	global servers
	ad = str("http://"+server)
	if server not in servers:
		servers.append(ad)
	return json.dumps(servers)	
		
@get('/peers/msg')
def getMsg():
	global messages
	return json.dumps(messages)
	
def clientServ():
	while True:
		global servers
		ad=str("http://"+sys.argv[1]+":"+sys.argv[2])
		if ad not in servers:
			servers.append(ad)
		print(servers)
		for i in servers:
			time.sleep(3)
			if i != ad:
				requests.get(i+"/peers/add/"+str(sys.argv[1]+':'+sys.argv[2]))
				s = requests.get(i+'/peers')
				ns = json.loads(s.content.decode("UTF-8"))
				for j in ns:
					if j not in servers:
						servers.append(j)

def clientMsg():
	while True:
		time.sleep(2)
		global messages
		global servers
		#if ip not in servers:
		#	servers.append(ip)
			
		for i in servers:
			time.sleep(4)
			ad = str("http://"+sys.argv[1]+":"+sys.argv[2])
			if i != ad:
				s = requests.get(i+'/peers/msg')
				ns = json.loads(s.content.decode("UTF-8"))
				for j in ns:
					if j not in messages:
						messages.append(j)
						print(j)
				
	
threading.Thread(target=clientServ).start()

threading.Thread(target=clientMsg).start()
	
threading.Thread(target=run,kwargs=dict(host=str(sys.argv[1]), port=str(sys.argv[2]))).start()


