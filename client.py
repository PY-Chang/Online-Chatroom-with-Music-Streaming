from socket import *
import threading
from threading import Thread
import tkinter
import pyaudio
import time

def Receive():
	while True:
		try:
			msg = client_socket.recv(BuffferSize).decode("utf8")
			if msg[0:12] == "{modifyList}":
				setNameList(msg[12:])
			else:
				msg_list.insert(tkinter.END, msg)
		except OSError:
			break
			
def setNameList(ll):
	online_list.delete('0','end')
	name_list = ll.split(",")
	for i in range(len(name_list)):
		online_list.insert(tkinter.END, name_list[i])
	return
	
def Receive_audio():
	CHUNK = 1024
	FORMAT = 8
	CHANNELS = 2
	RATE = 44100
	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
	Break = False
	first_time_end = threading.local()
	first_time_end = True
	
	while True:
		try:
			data = audio_socket.recv(CHUNK)
		except:
			p.terminate()
			sn_socket.close()
			audio_socket.close()
			break
		while len(data) > 0 and any(data):
			first_time_end = True
			if Playing:
				stream.write(data)
				try:
					data = audio_socket.recv(CHUNK)
				except:
					p.terminate()
					sn_socket.close()
					audio_socket.close()
					Break = True
					break
			else:
				p.terminate()
				sn_socket.close()
				audio_socket.close()
				Break = True
				break
				
		if first_time_end:
			try:
				song_name = sn_socket.recv(1024).decode("utf8")
			except:
				p.terminate()
				sn_socket.close()
				audio_socket.close()
				break
			playing_name.config(text=song_name)
			first_time_end = False
		if Break:
			break 

def Send(event=None):
	msg = my_msg.get()
	my_msg.set("")
	client_socket.send(bytes(msg, "utf8"))


def Leave(event=None):
	my_msg.set("{quit}")
	Send()
	audio_socket.close()
	client_socket.close()
	sn_socket.close()
	Window.quit()


def PlayPause(event=None):
	global Playing, Host, audio_port, audio_socket, sn_socket, sn_port
	if Playing:
		audio_socket.close()
		play_button.config(text="▶︎")
		playing_name.config(text="None")
		Playing = False
	else:
		Playing = True
		play_button.config(text="◼︎")
		audio_socket = socket(AF_INET, SOCK_STREAM)
		audio_socket.connect((Host, audio_port))
		sn_socket = socket(AF_INET, SOCK_STREAM)
		sn_socket.connect((Host, sn_port))
		song_name = sn_socket.recv(1024).decode("utf8")
		playing_name.config(text=song_name)
		audio_receive_thread = Thread(target=Receive_audio)
		audio_receive_thread.start()


def On_Closing(event=None):
	my_msg.set("{quit}")
	Send()
	audio_socket.close()
	client_socket.close()
	sn_socket.close()
	Window.quit()


# tkinter gui
Window = tkinter.Tk()
Window.title("Chat Room")
Window.geometry("608x427+379+173")
Window.minsize(1, 1)
Window.maxsize(1425, 870)
Window.resizable(1, 1)

# main message display
msg_list = tkinter.Listbox(Window, font=('Arial', 14))
msg_list.place(relx=0.033, rely=0.141, relheight=0.714, relwidth=0.683)
msg_list.configure(background="#d9d9d9")
msg_list.configure(relief="flat")

my_msg = tkinter.StringVar()
my_msg.set("Type your messages here...")

# online label
online_label = tkinter.Label(Window, font=('Arial', 17))
online_label.place(relx=0.757, rely=0.164, height=28, width=106)
online_label.configure(background="#ffffff")
online_label.configure(text="Online User")
	
# online list
online_list = tkinter.Listbox(Window, font=('Arial', 17), justify = "center")
online_list.place(relx=0.74, rely=0.234, relheight=0.571, relwidth=0.204)
online_list.configure(background="#90A4AE")
online_list.configure(relief="flat")

# typing field
entry_field = tkinter.Entry(Window, font=('Arial', 14), textvariable=my_msg)
entry_field.bind("<Return>", Send)
entry_field.place(relx=0.03, rely=0.867,height=40, relwidth=0.683)

# send button
send_button = tkinter.Button(Window, text="Send", font=('Arial', 20), command=Send)
send_button.place(relx=0.757, rely=0.867,width=100, height=40)
send_button.configure(foreground="black")
send_button.configure(highlightbackground="#1565C0")
send_button.configure(relief="flat")

# leave button
leave_button = tkinter.Button(Window, text="Leave", font=('Arial', 14), command=Leave)
leave_button.place(relx=0.872, rely=0.023, height=28, width=69)
leave_button.configure(foreground="black")
leave_button.configure(highlightbackground="#D32F2F")

# play button
play_button = tkinter.Button(Window, text="▶︎", font=('Arial', 25), command=PlayPause)
play_button.configure(anchor = 's')
play_button.place(relx=0.033, rely=0.023, height=40, width=60)
play_button.configure(highlightbackground="#FFC400")

# now playing label
now_playing = tkinter.Label(Window, text="Now Playing:", font=('Arial', 18))
now_playing.place(relx=0.140, rely=0.023, height=48)

# playing name label
playing_name = tkinter.Label(Window, text="None", font=('Arial', 18))
playing_name.place(relx=0.320, rely=0.047, height=28)

Window.protocol("WM_DELETE_WINDOW", On_Closing)


# main
Host = '127.0.0.1'
Port = 12000
BuffferSize = 1024
Addr = (Host, Port)

Playing = False
name_list = []

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(Addr)

audio_socket = socket(AF_INET, SOCK_STREAM)
audio_port = 12002

sn_socket = socket(AF_INET, SOCK_STREAM)
sn_port = 12003

receive_thread = Thread(target=Receive)
receive_thread.start()
tkinter.mainloop()  # loop GUI execution.

receive_thread.join()