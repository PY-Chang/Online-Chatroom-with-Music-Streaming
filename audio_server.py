from socket import *
from threading import Thread
import wave
import select
import time
import soundfile as sf
import numpy as np

CHUNK = 1024
FORMAT = 8
CHANNELS = 2
RATE = 44100
file_path = ["理想混蛋-夏夜煙火.wav", "理想混蛋-煙花2.wav"]
song_data = [["理想混蛋-夏夜煙火", 0, 0], 
			["理想混蛋-煙花", 0, 0]] # [name, secs, frame_per_sec]
frames = []
now_playing  = 0

def format_music():
	global file_path, song_data, frames
	
	for i in range (0, len(file_path)):
		frames.append([])
		count = 0
		wf = wave.open(file_path[i], 'rb')
		frame = wf.readframes(CHUNK)
		while (len(frame)>0):
			count += 1
			frames[i].append(frame)
			temp = frame
			frame = wf.readframes(CHUNK)
		f = sf.SoundFile(file_path[i])
		song_data[i][1] = int(len(f) / f.samplerate)
		song_data[i][2] = (int(len(f) / f.samplerate)) /count
	print("Music ready...")
	
def accept_connection():
	global people
	people += 1
	while True:
		client, client_address = Server.accept()
		sn_client, sn_client_address = server_sn.accept()
		Thread(target=handle_client, args=[client, sn_client]).start()


def handle_client(client, sn_client):
	global people, main_time, song_data, frames, now_playing
	clients[client] = people
	
	local_time = time.time()
	val = local_time-main_time

	temp = 0
	for k in range (0, now_playing+1):
		temp += song_data[k][1] 

	if val > temp:
		now_playing += 1
		val -= temp

	
	j = round(val/song_data[now_playing][2])
	
	now_playing_local = now_playing
	
	try:
		sn_client.send(bytes(song_data[now_playing_local][0], "utf8"))
	except:
		client.close()
		sn_client.close()
	
	Break = False
	
	while now_playing_local < len(song_data):
		for j in range (j, len(frames[now_playing_local])):
			try:
				client.send(frames[now_playing_local][j])
			except:
				client.close()
				sn_client.close()
				Break = True
				break
		if Break:
			break
			
		now_playing_local += 1
		j=0
		try:
			sn_client.send(bytes(song_data[now_playing_local][0], "utf8"))
		except:
			client.close()
			sn_client.close()
			break

clients = {}

Host = ''
Port = 12002
Addr = (Host, Port)

Server = socket(AF_INET, SOCK_STREAM)
Server.bind(Addr)

server_sn = socket(AF_INET, SOCK_STREAM)
server_sn.bind((Host, 12003))
Capacity = 10
people = 0

if __name__ == "__main__":
	main_time = time.time()
	format_music()
	
	Server.listen(Capacity)
	server_sn.listen(Capacity)
	print("Server started.")
	print("Waiting for connection...")
	new_Thread = Thread(target=accept_connection)
	new_Thread.start()
	new_Thread.join()
	Server.close()
	server_sn.close()
