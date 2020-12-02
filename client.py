import os
import getpass
import socket

from common_utils import Question

HOST = '127.0.0.1'
PORT = 5001
loggedin = False
user_id = ''


class ClientSocket(socket.socket):

    HEADER_SIZE = 16
    BUFFER_SIZE = 2048

    def __init__(self):
        super(ClientSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)

    def _send(self, message : str):
        header = str(len(message))
        header = (self.HEADER_SIZE-len(header))*'0' + header
        message = header + message
        message = message.encode('utf-8')
        self.send(message)

    def _recieve(self):
        message = ''
        message_len = int(self.recv(self.HEADER_SIZE).decode('utf-8'))
        while message_len > 0:
            message += self.recv(self.BUFFER_SIZE).decode('utf-8')
            message_len -= self.BUFFER_SIZE
        print(message)
        return message


def cli_input():
    string  = input('#> ').strip()
    if string.lower() == 'q':
        print('Thank you participating.')
        exit()
    elif string == 'clear':
        os.system('clear')
        return cli_input()
    return string


def signup(client_socket):
    print("Only alphabets and numbers are allowed in userid and password.")
    userid = input('Enter your userid : ')
    password = getpass.getpass('Enter a password : ')
    repass = getpass.getpass('reEnter the password : ')
    if password != repass:
        print('Mismatching passwords above. Please try again.')
        signup(client_socket)
    client_socket._send(userid + '|' + password)
    ok = int(client_socket._recieve())
    if not ok:
        print('Userid already registered please try a different one.')
        signup(client_socket)
    print('registered successfully')
    global user_id, loggedin
    loggedin = True
    user_id = userid


def login(client_socket):
    if input('Are you registered? (y/n) : ').lower().strip() == 'n' :
        client_socket._send('1')
        signup(client_socket)
        return
    client_socket._send('0')
    userid = input('Enter your userid : ')
    password = getpass.getpass('Enter password : ')
    client_socket._send(userid + '|' + password)
    ok = int(client_socket._recieve())
    if ok == -1:
        print('Unable to login. Wrong userid. Please try again.')
        login(client_socket)
    elif ok == 0:
        print('Unable to login. Wrong password. Please try again.')
        login(client_socket)
    print('Logged in successfully.')
    global user_id, loggedin
    loggedin = True
    user_id = userid


def cli_init(client_socket):
    if not loggedin:
        login(client_socket)
    message = ''
    while message != '#':
        print("Enter :\n 'q' to quit\n 'c' for continue\n 'm' for return to menu.")
        inp = cli_input()
        if inp.strip().lower() == 'm':
            return
        client_socket._send(inp)
        message = client_socket._recieve()
        ques = Question(string = message)
        answered = ques.ask()
        client_socket._send(str(answered))
        answer, explaination = client_socket._recieve().split('|')
        answer = int(answer)
        if (answered == answer):
            print('Correct')
        else:
            print('Wrong')
        print(f'Correct Answer : {ques.options[answer]} \nExplaination : {explaination}')
    print('You have attempted all of the questions.')


if __name__ == "__main__":

    client_socket = ClientSocket()
    try:
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError as e:
        print('Unable to reach the server. Try sometime later.')
        exit()

    login(client_socket)

    while True:
        print('''
        Welcome to Quizar, an online quizing platform.
        Enter 'q' anytime to quit.
        ''')

        print('''
        [TOPIC] Choose topic
            Enter 'T' for threading
            Enter 'S' for scheduling
            Enter 'M' for memory management
        ''')

        topic = cli_input()
        
        client_socket._send(topic)

        cli_init(client_socket)
