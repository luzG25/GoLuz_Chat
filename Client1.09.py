import socket
from cryptography.fernet import Fernet
import threading
import os
from time import sleep as sl

version = 1.09

def rmv_old_version(version):
    for c in range(1, 10):
        v = version - c * 0.01
        if f'Client{v}.py' in os.listdir():
            os.remove(f'Client{v}.py')
            print('\n#SISTEM: Versão anterior eliminada')

def updating(message, ver):
    file = f'Client{ver:.2f}.py'
    
    if message == '#finished#':
        print('\n///VERSÃO MAIS ATUALIZADA DISPONIVEL NO DISPOSITIVO!////\n')

    elif message == '#Starting Updating#':
        print('#Atualizando')
        app = open(file, 'wb')
        app.close()

    else:
        app = open(file, 'rb')
        app_code = app.read()
        app.close()
        
        app = open(file, 'wb')
        content  = app_code.decode() + message
        app.write(content.encode())
        app.close()


def file_recv(nome, file, hash_file, f, tipo):
    from hashlib import sha1
    print(int(len(file)))
    content = file.encode()
    hash_recv = sha1(content).hexdigest()
    if hash_recv == hash_file:
        content = f.decrypt(content)
        saver = open(nome, 'wb')
        saver.write(content)
        saver.close()
        print(f'\nFicheiro {tipo} salvo\n')
    else:
        print('ficheiro adulterado')

def files_sender(dir, client, f, destino, nome, check, tipo):
    from hashlib import sha1
    file = open(dir, 'rb')
    content = f.encrypt(file.read())
    hash_file = sha1(content).hexdigest()
    file.close()
    content = content.decode()
    cont = 1
    full_cont = len(content)
    part = ''
    #destino/tipo/nome/fullsize/hash_file
    client.send(f'{destino}/{tipo}/{nome}/{full_cont}/{hash_file}'.encode())
    print(len(content))
    for c in content:
        part += str(c)
        if len(part) == 30000:
            # destino/tipo/nome/part/content
            client.send(f'{destino}/{tipo}/{nome}/{cont}/{part}'.encode())
            part = ''
            cont += 1

            while True:
                if check[0] == 1:
                    check[0] = 0
                    break
    client.send(f'{destino}/{tipo}/{nome}/{cont}/{part}'.encode())
    print(f'Ficheiro {tipo} enviado')

def generate_key(n, g, client, vars):
    from random import randint
    private_key = randint(89012, 100000)
    public_key = g ** private_key % n
    send_keys(public_key, client)
    vars.clear()
    vars.append(private_key)
    vars.append(public_key)


def send_keys(public_key, client):
    key = f'/key_in/{public_key}'
    client.send(key.encode())


def recive_public_vars(mess, vars):
    c = 0
    N = ''
    g = ''
    n = ''
    info = ''
    for p in mess:
        if p == '/':
            c += 1
        elif c == 0:
            N += p
        elif c == 1:
            n += str(p)
        elif c == 2:
            g += str(p)
        else:
            info += str(p)
    vars.append(info)
    vars.append(int(g))
    vars.append(int(n))
    vars.append(int(N))
    print(vars)
    sl(5)

def recive_key(message, private_key, n, key_l):
    from hashlib import sha1
    key0 = int(message)
    key = int(key0) ** private_key % n
    key = sha1(str(key).encode()).hexdigest()
    key = f'{key}AAb='
    key_l.append(key)


def send_message(f, client, destino, check_mp3):
    print('Enviar Mensagem')
    message = str(input('Digite sua Messagem:'))

    if '.mp3' in message[(len(message) - 6):]:
        if '"' in message[:2] or '"' in message[len(message) - 2:]:
            message = message[1: len(message) - 1]
            #
            print(message)

        nome = message
        sair = 0
        while True:
            try:
                nome = nome[(nome.index('/') + 1):]
            except:
                sair = 1
            if sair == 1:
                break
        sair = 0
        while True:
            try:

                nome = nome[(nome.index(' \ '.strip()) + 1):]
            except:
                sair = 1
            if sair == 1:
                break

        threading.Thread(target=files_sender, args=(message, client, f, destino, nome, check_mp3, 'mp3',)).start()

    else:
        message = f.encrypt(message.encode())
        message = f'{destino}/sms/{message.decode()}'
        client.send(message.encode())
        print('Mensagem Enviada!')



def recive_messages(client, f, destino, id, check_mp3):
    files = []
    file_data = [0, 0, 0, 0, 0, '']
    contagem = 0
    while True:
        message = client.recv(1048576).decode()
        if message != b'' or message != b' ':
            tipo = message[:4]
            message = message[4:]

            if tipo == 'sms/':
                message = f.decrypt(message.encode())
                print('\n', message.decode(), id)

            elif tipo == 'upd/':
                ver = float(message[:4])
                message = message[5:]
                threading.Thread(target=updating, args=(message, ver,)).start()

            elif tipo == 'mp3/':
                content = message
                # [nome0,n,fullcont,hash,cont,file]
                nome = content[:(content.index('/'))]
                content = content[(content.index('/') + 1):]

                if file_data[0] != 0:
                    if file_data[0] == nome:
                        # part / content
                        file_data[4] = content[:(content.index('/'))]
                        content = content[(content.index('/') + 1):]
                        file_data[5] += str(content)
                        tamanho = len(file_data[5])
                        print(tamanho)
                        if int(file_data[2]) == tamanho:
                            print(f'::Ficheiro {file_data[0]} Recibido!')
                            threading.Thread(target=file_recv,
                                             args=(file_data[0], file_data[5], file_data[3], f, tipo,)).start()
                            file_data = [0, 0, 0, 0, 0, '']
                            tamanho = 0
                        else:
                            client.send(f'{destino}/mp3/#recived001/'.encode())

                elif nome == '#recived001':
                    check_mp3[0] = 1


                else:
                    file_data[0] = nome
                    file_data[1] = contagem
                    file_data[2] = content[:(content.index('/'))]
                    print(file_data[2])
                    file_data[3] = content[(content.index('/') + 1):]
                    contagem += 1


target_host = '192.168.88.22'
target_port = 9999

# Socket Object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the client to the Server
client.connect((target_host, target_port))
info_server = client.recv(1024).decode()
N = info_server[:1]
info_server = info_server[1:]
vars = []
recive_public_vars(info_server, vars)
g = vars[1]
n = vars[2]
print(vars)
generate_key(n, g, client, vars)
print('chaves geradas e enviadas!')
private_key = vars[0]
public_key = vars[1]

f = Fernet(key)


if int(N) == 1:
    destino = 0
else:
    destino = 1

recv_mp3_checkup = [0]
threading.Thread(target=recive_messages, args=(client, f, destino, '', recv_mp3_checkup,)).start()

info = f's/ver/{version}'.encode()
client.send(info)
threading.Thread(target=rmv_old_version, args=(version,)).start()


while True:
    send_message(f, client, destino, recv_mp3_checkup)
