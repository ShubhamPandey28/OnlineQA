import os
import json

import threading
from .utils import *


global  PASSWORDS, server_socket, questions

PASSWORDS = MAP()
questions = dict()
server_socket : ServerSocket = None


def authenticate(client_connection):
    cnt = 10
    new = int(server_socket._recieve(client_connection))
    while cnt:
        
        user_id, password = server_socket._recieve(client_connection).split('|')
        
        if new and not user_id in PASSWORDS:
            PASSWORDS.lock.acquire()
            PASSWORDS[user_id] = password
            PASSWORDS.lock.release()
            print(f'Client {user_id} is successfully signed in.')
            server_socket._send(client_connection, '1')
            return 1

        elif not user_id in PASSWORDS:
            server_socket._send(client_connection, '-1')

        elif PASSWORDS[user_id] == password:
            print(f'Client {user_id} is successfully logged in.')
            server_socket._send(client_connection, '1')
            return 1

        else:
            server_socket._send(client_connection, '0')
        cnt -= 1

    return 0


def resolve_client(client_connection):

    if not authenticate(client_connection):
        return
    
    while True:
        topic = server_socket._recieve(client_connection)

        for ques in questions[topic]:
            cont = server_socket._recieve(client_connection)
            if cont == 'm':
                break
            server_socket._send(client_connection, ques.serialize())
            answered = int(server_socket._recieve(client_connection))
            # scoring
            server_socket._send(client_connection, '|'.join(ANSWERS[ques.id]))
        
        server_socket._send(client_connection, '#')



def run(host, port):

    questions['T'] = read_questions('Questions/threads.txt')
    questions['M'] = read_questions('Questions/memory.txt')
    questions['S'] = read_questions('Questions/scheduling.txt')

    global server_socket
    server_socket = ServerSocket(host, port)
    server_socket._listen(5)

    threads = []

    while True :
        client_connection, client_address = server_socket.accept()
        print("Connected to client  %s, %s" %client_address)
        
        thread = ClientThread(resolve_client,client_connection)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    
