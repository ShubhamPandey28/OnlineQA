import socket
import threading
import struct
import json

import threading
from .common_utils import Question

global NEW_QUES_ID, ANSWERS

NEW_QUES_ID = 0
ANSWERS = dict()

def read_questions(filepath):
    global NEW_QUES_ID, ANSWERS
    questions = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines), 4):
            question = lines[i][9:].strip()
            options = lines[i+1][8:].strip().split('~')
            answer = lines[i+2][7:].strip()
            explaination = lines[i+3][13:].strip()
            questions.append(Question(NEW_QUES_ID, question, options))
            ANSWERS[NEW_QUES_ID] = [answer, explaination]
            NEW_QUES_ID += 1
    return questions


class MAP(dict):
    lock = threading.Lock()


class ServerSocket(socket.socket):

    BUFFER_SIZE = 1024
    HEADER_SIZE = 16
    NEW_CLIENT_ID = 0

    def __init__(self, host, port):
        super(ServerSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.host, self.port = host, port
    
    def _listen(self, max_connections):
        self.bind((self.host, self.port))
        self.listen(max_connections)
        print('Listening at port', self.port)
    
    def _send(self, client_connection, message):
        header = str(len(message))
        header = (self.HEADER_SIZE-len(header))*'0' + header
        message = header + message
        message = message.encode('utf-8')
        client_connection.send(message)
    
    def _recieve(self, client_connection):
        message = ""
        message_len = int(client_connection.recv(self.HEADER_SIZE).decode('utf-8'))
        while message_len > 0:
            message += client_connection.recv(self.BUFFER_SIZE).decode('utf-8')
            message_len -= self.BUFFER_SIZE
        return message


class ClientThread(threading.Thread):

    def __init__(self, function, *args):
        super(ClientThread, self).__init__()
        self.args = args
        self.function = function

    def run(self):
        self.function(*self.args)