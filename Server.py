import socket
import threading
from random import randint
from time import sleep as sl

def updates(client, version):
    app = open(f'Client{version}.py', 'rb')
    upd = f'upd/{version:.2f}/#Starting Updating#'
    client.send(upd.encode())

    sl(1)
    upd = app.read().decode()
    part = ''
    for c in upd:
        part += c
        if len(part) == 100:
            upd_content= f'upd/{version:.2f}/{part}'
            client.send(upd_content.encode())
            part = ''
            sl(1)
    upd_content = f'upd/{version:.2f}/{part}'
    client.send(upd_content.encode())
    app.close()

    sl(1)
    upd = f'upd/{version:.2f}/#finished#'
    client.send(upd.encode())
    print(f'ATUALIZADO{client}')

#This is our client-handling thread
def handle_client(client_socket, clients, keys ,ver):
    while True:
        recive_message(client_socket, clients, keys, ver)

keys = {}

def recive_message(client, clients, keys, version):
    message = client.recv(67108864).decode()
    if '/' in message:
        #emissor/tipo/content/
        emissor = message[:(message.index('/'))]
        message = message[:(message.index('/'))]
        tipo = message[:(message.index('/'))]
        if 'key_in/' in message[:2]:
            chave = message[(message.index('/') + 1):(message.index('/'))]
            keys[emissor] = chave
            for c in clients:
                print(keys)
                message = f'server/keys/{keys}'
                c.send(keys.encode())

        elif message != '' and message[:1] in '0123456789':
            destino = int(message[:1])
            message = message[2:]
            #destino/tipo/conteudo
            threading.Thread(target=send_message, args=(clients, message, destino,)).start()
            print(f'de: {client} \nconteudo: {message}\npara: {clients[destino]}')

        elif 's/' in message[:2]:
            message = message[2:]
            if 'ver/' == message[:4]:
                client_ver = float(message[4:])
                if client_ver < version:
                    updater = threading.Thread(target=updates, args=(client,  version))
                    updater.start()

def send_message(clients, message, destino):
    clients[destino].send(message.encode())

version = 1.09
n = randint(1000, 19999)
g = randint(2, 100)

bind_ip = '192.168.88.22'
bind_port = 9999
clients = []

#socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print(f'[*] Escutando {bind_ip}:{bind_port}')

while True:
    client, addr = server.accept()
    print(f'Accepted connection from: {addr[0]}:{addr[1]}')
    clients.append(client)
    # spin up our client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client, args=(client, clients, keys, version,))
    client_handler.start()
    client.send(f'{len(clients)-1}/{n}/{g}/CONECTADO AO SERVIDOR N={len(clients) - 1}'.encode())
