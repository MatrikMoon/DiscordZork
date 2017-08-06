import discord
import socket
import sys
import os
import time
import tkinter as tk
import threading
import asyncio

loop = asyncio.get_event_loop() 
client = discord.Client()
currentChannel = ""

@client.event
async def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == client.user:
		return
	if str(message.channel) == "zork":
		currentChannel = message.channel
		zorkSend("!z " + message.content, message.channel.id)
	elif message.content.startswith("!z "):
		zorkSend(message.content, message.channel.id)
	if message.content.startswith("!zSave"):
		if str(message.author) != "[user]":
			await client.send_message(message.channel, "Only the admin can do that.")
		else:
			zorkSend(message.content, str(message.channel.id))
	if message.content.startswith("!zRestore"):
		if str(message.author) != "[user]":
			await client.send_message(message.channel, "Only the admin can do that.")
		else:
			zorkSend(message.content, str(message.channel.id))
	if message.content == "!zorkStart":
		if str(message.author) != "[user]":
			await client.send_message(message.channel, "Only the admin can do that.")
		else:
			zorkSend(message.content, str(message.channel.id))
	if message.content == "!summon":
		summoned_channel = message.author.voice_channel
		if summoned_channel is None:
			await client.send_message(message.channel, "You are not in a voice channel.")
			return
		voice = await client.join_voice_channel(summoned_channel)
		player = await voice.create_ytdl_player("https://www.youtube.com/watch?v=hh9x4NqW0Dw")
		player.start()
		
@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

def discordSend(destination, data):
	asyncio.run_coroutine_threadsafe(client.send_message(destination, data), loop)

def zorkSend(data, sender):
	data = "/android_zork -j " + sender + " -m \\\"" + data + "\\\""
	send(data)

def parseServerCommands(data):
	if data.startswith("Server> "):
		data = data[8:]
	if data.startswith("/zorkServer"):
		split = data.split(" ")
		channel = ""
		message = ""
		replymessage = ""
		
		i = 0
		for item in split:
			if item == "-j":
				channel = split[i + 1]
			if item == "-m":
				message = data[data.index("-m") + 3:]
				replymessage = message[:message.index('\n')]
				message = message[message.index('\n'):]
			i += 1
		discordSend(client.get_channel(channel), replymessage + "```" + message + "```")
		
	if data == "/requesting_data":
		sendIntroData()
	print(data)

def receiver():
	while True:
		try:
			data = sock.recv(1024)
			data = data.decode().split("<EOF>")
			data = data[0]
			parseServerCommands(data)
		except ConnectionAbortedError:
			print("Connection to zork server closed.")
			break
		except ConnectionResetError:
			print("Connection to zork server severed.")
			
			break
		except Exception as ex:
			template = "An exception of type {0} occurred. Arguments:\n{1!r}"
			message = template.format(type(ex).__name__, ex.args)
			print(message)

def inputloop():
	while True:
		toSend = input()
		discordSend(currentChannel, toSend)
		print("SENT")

def send(data):
	try:
		sock.sendall(str(data + "<EOF>\0").encode())
	except Exception as ex:
		template = "An exception of type {0} occurred. Arguments:\n{1!r}"
		message = template.format(type(ex).__name__, ex.args)
		print(message)

def sendIntroData():
	# Send intro data
	localip = socket.gethostbyname(socket.gethostname())
	root = tk.Tk()
	screen_width = root.winfo_screenwidth()
	screen_height = root.winfo_screenheight()
	xmessage = "/add_x " + str(screen_width)
	ymessage = "/add_y " + str(screen_height)
	ipmessage = "/add_ip " + localip
	pathmessage = "/add_path " + os.path.realpath(__file__)
	namemessage = "/add_name DiscordZork"
	
	send(xmessage)
	send(ymessage)
	send(ipmessage)
	send(pathmessage)
	send(namemessage)
	
try:
	# ZorkServer connection state
	serverconnected = False
	
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = ("192.168.1.103", 10150)
	try:
		sock.connect(server_address)
		serverconnected = True
		#serverconnected = False
	except TimeoutError:
		print("Zork connection timed out")
		serverconnected = False

	if serverconnected:
		# Set up receiving
		t = threading.Thread(target=receiver)
		t.daemon = True
		t.start()
	
		sendIntroData()
		
	# Set up receiving
	#t2 = threading.Thread(target=inputloop)
	#t2.daemon = True
	#t2.start()
	
	print("Will you be logging in as a bot or a user today? [Default: bot]: ")
	opt = input()
	email = ""
	password = ""
	token = ""
	if opt == "user":
		email = input("email: ")
		if len(email) < 3:
			loop.run_until_complete(client.start("[email]", "[password]"))
		password = input("password: ")
		loop.run_until_complete(client.start(email, password))
	if opt == "bot":
		token = input("token [defaults to Moon-Bot]:")
		if len(token) < 3:
			token = "[token]"
		client.run(token)
	else:
		client.run("[token]")
except Exception as ex:
	template = "An exception of type {0} occurred. Arguments:\n{1!r}"
	message = template.format(type(ex).__name__, ex.args)
	print(message)
finally:
	sock.close()