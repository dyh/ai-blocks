# coding:utf-8

import os
import cv2
import socket
import numpy as np

from socket_handle.message import Message


class Client:
    def __init__(self, host='127.0.0.1', port=65432):
        """
        init socket server
        :param host: ip
        :param port: port
        """
        self.host = host
        self.port = port
        pass

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            address = (self.host, self.port)
            client.connect(address)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            print("connecting {0}:{1} ...".format(self.host, self.port))

            image_folder = './pytest/images/'
            files = os.listdir(image_folder)
            # sort by file name
            files.sort()

            message = Message(client, address)

            for file_name in files:
                # filter png files
                if file_name[-4:] == '.png':
                    image_path = image_folder + file_name

                    # load the origin image
                    image_file = cv2.imread(image_path)

                    # clear cache data
                    message.clear()
                    message.write(image_object=image_file, text_message=None)

                    # get text message
                    try:
                        message.read()
                    except RuntimeError as ex:
                        print('RuntimeError:', ex)
                        break
                    pass

                    # print text message
                    print(message.get_result())

                    # clear cache data
                    message.clear()

                    # get image message
                    try:
                        message.read()
                    except RuntimeError as ex:
                        print('RuntimeError:', ex)
                        break
                    pass

                    # convert buffer to array via numpy
                    array_data = np.frombuffer(message.get_result(), dtype=np.uint8)

                    # clear cache data
                    message.clear()

                    # convert array to image via cv2
                    image_origin = cv2.imdecode(array_data, cv2.IMREAD_COLOR)
                    image_tmp = cv2.resize(image_origin, (960, 540))

                    # show image
                    cv2.imshow('client', image_tmp)
                    cv2.waitKey(1)
                    pass
                pass
            pass
            cv2.destroyWindow('client')

            # close socket
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            pass
