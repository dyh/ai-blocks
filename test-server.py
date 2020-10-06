import os

from socket_handle.server import Server

# 禁用CUDA
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

if __name__ == '__main__':
    print('socket server is starting...')

    server = Server(host='0.0.0.0', port=65432, timeout=30)
    server.start()

    pass
