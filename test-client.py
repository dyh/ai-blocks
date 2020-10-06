from socket_handle.client import Client

if __name__ == '__main__':
    print('socket client is starting...')

    client = Client(host='192.168.31.21', port=65432)
    client.start()

    pass
