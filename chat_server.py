from socket import *
from threading import Thread
import time

def Accept_Connection():
	global Numbers_of_People
	while True:
		client, client_address = Server.accept()
		print("%s:%s has connected." % client_address)
		Numbers_of_People += 1
		client.send(bytes("<Welcome to the chat room!>", "utf8"))
		time.sleep(0.3)
		client.send(bytes("<Please type your name to start the chat!>", "utf8"))
		Thread(target=Handle_Client, args=(client,)).start()

def Handle_Client(client):
	global Numbers_of_People
	name = client.recv(BuffferSize).decode("utf8")
	if name != "{quit}":
		greeting = '<Welcome %s! Feel free to say anthing!>' %name
		client.send(bytes(greeting, "utf8"))
		msg = "<%s joins the chat!>" %name
		Broadcast(bytes(msg, "utf8"))
		time.sleep(0.3)
		clients[client] = name
		name_list.append(name)
		sendNameList()
		
		while True:
			msg = client.recv(BuffferSize)
			if msg != bytes("{quit}", "utf8"):
				Broadcast(msg, name+": ")
			else:
				del clients[client]
				name_list.remove(name)
				client.close()
				Numbers_of_People -= 1
				if Numbers_of_People > 0:
					sendNameList()
					time.sleep(0.2)
					Broadcast(bytes("<%s left the chat. QAQ>" % name, "utf8"))
				break
	else:
		client.close()
		Numbers_of_People -= 1


def sendNameList():
	msg = ""
	for i in range(len(name_list)):
		msg += (name_list[i]+",")
	for people in clients:
		people.send(bytes("{modifyList}"+msg, "utf8"))

def Broadcast(msg, prefix=""):
	for people in clients:
		people.send(bytes(prefix, "utf8")+msg)


clients = {}
name_list = []

Host = ''
Port = 12000
BuffferSize = 1024
Addr = (Host, Port)

Server = socket(AF_INET, SOCK_STREAM)
Server.bind(Addr)


Capacity = 10
Numbers_of_People = 0

if __name__ == "__main__":
	Server.listen(Capacity)
	print("Server strated.")
	print("Waiting for connection...")
	New_Thread = Thread(target=Accept_Connection)
	New_Thread.start()
	New_Thread.join()
	Server.close()