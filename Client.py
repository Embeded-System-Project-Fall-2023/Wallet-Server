import pickle
from socket import *
from enum import Enum


SERVER_IP = '37.152.183.210'
SERVER_PORT = 8090
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)


class ResponseType(Enum):
    OK = 1
    ERROR = 2


class Response:
    def __init__(self, response_type, client_amount, message, client_password, last_transaction):
        self.response_type = response_type
        self.client_amount = client_amount
        self.client_password = client_password
        self.message = message
        self.last_transaction = last_transaction


class Request:
    def __init__(self, user_id, request_type, amount):
        self.user_id = user_id
        self.request_type = request_type
        self.amount = amount


class RequestType(Enum):
    MODIFY = 1
    GET = 2
    LAST_TRANSACTION = 3
    CHANGE_PASSWORD = 4


class Client:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect(SERVER_ADDRESS)
        print(f'Connected to {SERVER_IP}:{SERVER_PORT}')

    def __send_request(self, request):
        self.socket.sendall(pickle.dumps(request))
        plane_data = self.socket.recv(4096)
        data = pickle.loads(plane_data)
        return data

    def __extract_user_info(self, data):
        if data.response_type == ResponseType.ERROR:
            return None, None, None
        client_amount = data.client_amount
        client_password = data.client_password
        client_last_transaction = data.last_transaction
        return client_amount, client_password, client_last_transaction

    def get_user_info(self, user_id):
        get_request = Request(user_id, RequestType.GET, None)
        data = self.__send_request(get_request)
        return self.__extract_user_info(data)

    def update_user_amount(self, user_id, amount):
        modify_request = Request(user_id, RequestType.MODIFY, amount)
        data = self.__send_request(modify_request)
        return self.__extract_user_info(data)

    def update_user_password(self, user_id, new_password):
        update_password_request = Request(user_id, RequestType.CHANGE_PASSWORD, str(new_password))
        data = self.__send_request(update_password_request)
        return self.__extract_user_info(data)



