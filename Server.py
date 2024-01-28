from socket import *
import json
from threading import Thread
from enum import Enum

SERVER_IP = '37.152.183.210'
SERVER_PORT = 8090
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)


class RequestType(Enum):
    MODIFY = 1
    GET = 2


class ResponseType(Enum):
    OK = 1
    ERROR = 2


class Request:
    def __init__(self):
        self.user_id = None
        self.request_type = None
        self.amount = None


class Response:
    def __init__(self, response_type, client_amount, message):
        self.response_type = response_type
        self.client_amount = client_amount
        self.message = message


class ClientHandler(Thread):
    def __init__(self, client_connection, client_address):
        super().__init__()
        self.client_connection = client_connection
        self.client_address = client_address

    def extract_amount(self, amount):
        if amount[0] == 'A':
            return int(amount[1:])

        elif amount[0] == 'B':
            return -1 * int(amount[1:])
        else:
            print(f'The sign of the amount is not valid.')

    def get_user_by_user_id(self, user_id, users):
        if users.keys().__contains__():
            return int(users[user_id])
        else:
            users[user_id] = 0
            return 0

    def modify_user_wallet(self, user_id, amount):
        users_file = open('users.json')
        users = json.load(users_file)
        client_amount = self.get_user_by_user_id(user_id, users)
        modify_amount = self.extract_amount(amount)
        client_amount += modify_amount
        users[user_id] = client_amount
        json.dump(users, users_file, indent=2)
        users_file.close()
        return client_amount

    def get_user_amount(self, user_id):
        users_file = open('users.json')
        users = json.load(users_file)
        client_amount = self.get_user_by_user_id(user_id, users)
        return client_amount

    def handle_request(self, request):
        user_id = request.user_id
        request_type = request.request_type
        if request_type == RequestType.MODIFY:
            return self.modify_user_wallet(user_id, request.amount)
        elif request_type == RequestType.GET:
            return self.get_user_amount(user_id)
        else:
            return -1

    def send_response(self, response):
        self.client_connection.sendall(json.dumps(response))

    def run(self):
        plane_data = self.client_connection.recv(4096)
        request = json.loads(plane_data)
        client_amount = self.handle_request(request)
        response = None
        if client_amount != -1:
            response = Response(ResponseType.OK, client_amount, 'Request accepted')
        else:
            response = Response(ResponseType.ERROR, None, 'An error occurred')
        self.send_response(response)
        self.client_connection.close()


if __name__ == '__main__':
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen()
    print(f'Server is running on {SERVER_IP}:{SERVER_PORT} :')
    while True:
        connection, address = server_socket.accept()
        print(f"Established connection from {address}")
        client_handler = ClientHandler(client_connection=connection, client_address=address)
        client_handler.start()
