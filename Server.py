import pickle
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


class UserNotFound(Exception):
    def __init__(self):
        pass


class Request:
    def __init__(self, user_id, request_type, amount):
        self.user_id = user_id
        self.request_type = request_type
        self.amount = amount



class Response:
    def __init__(self, response_type, client_amount, message, client_password):
        self.response_type = response_type
        self.client_amount = client_amount
        self.client_password = client_password
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

    def get_user_by_user_id(self, user_id):
        users = self.read_users_file()
        if users.keys().__contains__(user_id):
            return users.get(user_id), users
        else:
            raise UserNotFound

    def read_users_file(self):
        users_file = open('users.json', 'r+')
        users = json.load(users_file)
        users_file.close()
        return users

    def modify_user_wallet(self, user_id, amount):
        user_info, users = self.get_user_by_user_id(user_id)
        modify_amount = self.extract_amount(amount)
        user_info[0] = user_info[0] + modify_amount
        self.save_new_amounts(users)
        return user_info

    @staticmethod
    def save_new_amounts(users):
        users_file = open('users.json', 'w')
        json.dump(users, users_file, indent=2)
        users_file.close()

    def get_user_amount(self, user_id):
        user_info, users = self.get_user_by_user_id(user_id)
        return user_info

    def handle_request(self, request):
        user_id = str(request.user_id)
        request_type = request.request_type
        if request_type.value == RequestType.MODIFY.value:
            return self.modify_user_wallet(user_id, request.amount)
        elif request_type.value == RequestType.GET.value:
            return self.get_user_amount(user_id)
        else:
            raise UserNotFound

    def send_response(self, response):
        self.client_connection.sendall(pickle.dumps(response))

    def get_request(self):
        plane_data = self.client_connection.recv(4096)
        request = pickle.loads(plane_data)
        return request

    def run(self):
        response = None
        try:
            request = self.get_request()
            user_info = self.handle_request(request)
            response = Response(ResponseType.OK, user_info[0], 'Request accepted', user_info[1])
        except UserNotFound:
            response = Response(ResponseType.ERROR, None, 'An error occurred', None)
        finally:
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
