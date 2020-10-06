# coding:utf-8

import cv2
import time
import socket
import datetime
import numpy as np
from threading import Thread
from multiprocessing import Manager

import utils
import config
from license_plate import tricks
from socket_handle.message import Message
from lane_line.wrapper_erfnet import WrapperERFNet
from lane_line.wrapper_vpgnet import WrapperVPGNet
from license_plate.wrapper_hyperlpr_v2 import WrapperHyperLPRV2


class Server:
    def __init__(self, host='0.0.0.0', port=65432, timeout=30):
        """
        init socket server
        :param host: ip
        :param port: port
        :param timeout: default 30 secs
        """
        # -----------初始化神经网络-----------
        # 色盘
        self.color_map_mat = np.zeros((19, 3), dtype=np.uint8)
        # lane_color = np.array([0, 255, 0], dtype=np.uint8)
        # vp_color_map_mat = np.array([[0, 255, 0], [0, 0, 255]], dtype=np.uint8)
        # 色盘，随机颜色，除了background之外，其余17个类别，17种颜色
        # 新增第18种，erfnet的车道线mask
        # bgr
        for i in range(0, 19):
            if i == 1:
                # lane_solid_white
                self.color_map_mat[i] = (255, 255, 255)
            elif i == 4:
                # lane_solid_yellow
                self.color_map_mat[i] = (0, 255, 255)
            elif i == 6:
                # lane_double_yellow
                self.color_map_mat[i] = (0, 255, 255)
            elif i == 18:
                # erfnet_mask
                self.color_map_mat[i] = (0, 0, 255)
            pass
        pass

        self.wrapper_hyperlpr_v2_object = WrapperHyperLPRV2()
        self.vpgnet1 = WrapperVPGNet()
        self.erfnet1 = WrapperERFNet()

        # 空白图片，用于缩放
        # blank_image_erfnet = np.zeros((590, 1640, 3), dtype=np.uint8)
        self.blank_image_1920x1080_erfnet = np.zeros((1080, 1920), dtype=np.uint8)

        # ---------------------------------
        # -----------初始化socket-----------

        sync_manager = Manager()
        # record the latest timestamp of each socket message
        self.dict_latest_message_timestamp = sync_manager.dict()
        # record the flag of loop, set its value to False when you want to close a socket
        self.dict_loop_flag = sync_manager.dict()

        self.host = host
        self.port = port
        # timeout value of socket
        self.timeout = timeout

        # thread of timeout daemon
        self.thread_timeout_daemon = Thread(target=self._timeout_handle)
        # terminated with main thread
        self.thread_timeout_daemon.daemon = True
        pass

    def _timeout_handle(self):
        # to judge whether the socket has timeout
        while True:
            for key, value in self.dict_latest_message_timestamp.items():

                if (time.time() - value) > self.timeout:
                    print('#' * 5, 'socket {0} timeout.'.format(key), '#' * 5)
                    # remove loop flag, close socket
                    self.dict_loop_flag.pop(key)
                    # remove timestamp
                    self.dict_latest_message_timestamp.pop(key)
                pass

            time.sleep(self.timeout)
        pass

    def start(self):
        # start the timeout daemon thread
        self.thread_timeout_daemon.start()

        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

                server.bind((self.host, self.port))
                server.listen()
                print("listening {0}:{1} ...".format(self.host, self.port))

                socket_obj, address_obj = server.accept()

                # begin time of one socket
                begin_time = time.time()

                thread_name = str(begin_time)

                thread_obj = Thread(target=self._socket_handle, args=(socket_obj, address_obj, thread_name))
                thread_obj.daemon = True

                self.dict_loop_flag[thread_name] = True

                # start socket thread
                thread_obj.start()
            pass
        pass

    def _socket_handle(self, socket_obj, address_obj, thread_name):
        """
        function of handle socket
        :param thread_name:
        :param socket_obj:
        :param address_obj:
        :return:
        """
        # receive messages from tcp-client
        with socket_obj:
            print("accepted connection from", address_obj)
            message = Message(socket_obj, address_obj)

            # flag of loop
            while True:
                # if this thread has not timeout
                if self.dict_loop_flag.get(thread_name) is True:
                    pass
                else:
                    print('process {0} closed'.format(thread_name))
                    break
                pass

                # clear socket buffer
                message.clear()

                try:
                    message.read()
                except RuntimeError as ex:
                    print('RuntimeError:', ex)
                    break
                pass

                # 单张图片的整体时间
                # --------------------------时间测试--------------------------
                # 车牌检测开始时间
                start_time_single_image = datetime.datetime.now()
                # --------------------------时间测试--------------------------

                # convert buffer to array via numpy
                array_data = np.frombuffer(message.get_result(), dtype=np.uint8)
                # convert array to image via cv2
                image_origin = cv2.imdecode(array_data, cv2.IMREAD_COLOR)

                # do some image processing here
                copy_image_origin_plate = image_origin.copy()

                # 一个文件的临时车牌所有信息们
                list_plates_all_info_temp = []

                # ------------------hyperlpr_v2单层检测------------------
                list_all_position_result = self.wrapper_hyperlpr_v2_object. \
                    get_single_line_position_from_big_image(copy_image_origin_plate)

                plates_list_result = []

                # 识别一张大图片中的车牌
                if len(list_all_position_result) > 0:
                    # ------------------hyperlpr_v2单层识别------------------
                    plates_list_result += self.wrapper_hyperlpr_v2_object.get_single_line_plates_from_position(
                        copy_image_origin_plate, list_all_position_result)

                    # ------------------hyperlpr_v2双层识别------------------
                    # plates_list_result = wrapper_hyperlpr_v2_object.get_double_line_plates_from_position(
                    #     copy_image_origin, list_all_position_result)

                    if len(plates_list_result) > 0:
                        for list_one_plate in plates_list_result:
                            # list_one_plate = str_one_plate.split(',')
                            # 一个车牌list
                            # '辽AXXXX1,蓝牌,0.91000001,400,1010,150,60;辽AXXXX2,蓝牌,0.91000001,800,1010,162,70'
                            plate_name = list_one_plate[0]
                            plate_type = list_one_plate[1]
                            plate_confidence = float(list_one_plate[2])
                            # x1 = float(list_one_plate[3])
                            # y1 = float(list_one_plate[4])
                            w = float(list_one_plate[5])
                            h = float(list_one_plate[6])

                            # 判断车牌是否有效
                            temp_flag = tricks.all_tricks_filter(plate_name, plate_type, plate_confidence,
                                                                 plate_width=w, plate_height=h,
                                                                 confidence1=config.tricks_confidence_primary,
                                                                 confidence2=config.tricks_confidence_secondary)

                            if temp_flag:
                                # 识别到的，一个文件中的，车牌列表
                                list_plates_all_info_temp.append(list_one_plate)
                                pass
                            pass

                        # 保存新图片，覆盖原始图片
                        for list_one_plate in list_plates_all_info_temp:
                            plate_name = list_one_plate[0]
                            plate_type = list_one_plate[1]
                            plate_confidence = float(list_one_plate[2])
                            x1 = float(list_one_plate[3])
                            y1 = float(list_one_plate[4])
                            w = float(list_one_plate[5])
                            h = float(list_one_plate[6])

                            # 画框
                            copy_image_origin_plate = utils.draw_rect_box(
                                copy_image_origin_plate, (x1, y1, w, h), plate_name + " " + plate_type + " " + str(
                                    round(plate_confidence, 3)))

                            pass
                        pass

                    pass

                # --------------------------时间测试--------------------------
                if config.print_running_time:
                    # 检测结束时间
                    # print('')
                    print(' # ' + thread_name + ', 车牌数量: ' + str(len(list_all_position_result)) +
                          ', 车牌用时: ' + str(datetime.datetime.now() - start_time_single_image) + ', ', end='')

                    # 车道线检测开始时间
                    start_time_laneline = datetime.datetime.now()
                pass

                # -------------erfnet检测车道线-------------
                # 先剪裁掉 0.4
                copy_image_origin_erfnet = tricks.preprocess_clip_image_top(image_origin.copy(),
                                                                            config.tricks_erfnet_prep_clip_image_top)

                copy_image_origin_erfnet = cv2.resize(copy_image_origin_erfnet, (1640, 350))
                #
                # 此函数包含resize到976x208，不用预先resize
                obj_mask_pred_976x208_erfnet = self.erfnet1.get_lane_line_from_image_1640x350(copy_image_origin_erfnet)

                # -------------vpgnet检测车道线-------------
                # 将 1920x1080 resize到 640x480
                copy_image_origin_vpgnet = cv2.resize(image_origin.copy(), (640, 480))
                obj_mask_pred_160x120_vpgnet = self.vpgnet1.get_lane_line_from_image_640x480(copy_image_origin_vpgnet)

                # obj_mask_pred_1920x1080_vpgnet = np.resize(obj_mask_pred_160x120_vpgnet, (4, 1080, 1920))

                # vpgnet车道线开始
                lane_solid_white = utils.resize_array(obj_mask_pred_160x120_vpgnet[0, :, :], (1080, 1920))
                lane_solid_yellow = utils.resize_array(obj_mask_pred_160x120_vpgnet[1, :, :], (1080, 1920))
                lane_double_yellow = utils.resize_array(obj_mask_pred_160x120_vpgnet[2, :, :], (1080, 1920))

                # 用erfnet的车道线位置，筛选vpgnet的车道线
                mask_filter_erfnet = obj_mask_pred_976x208_erfnet[
                                     0, :, :] + obj_mask_pred_976x208_erfnet[
                                                1, :, :] + obj_mask_pred_976x208_erfnet[
                                                           2, :, :] + obj_mask_pred_976x208_erfnet[3, :, :]

                mask_filter_erfnet = utils.resize_array(
                    mask_filter_erfnet, (int(1080 * (1 - config.tricks_erfnet_prep_clip_image_top)), 1920))

                # mask_filter_erfnet = mask_filter_erfnet * 60

                mask_filter_1920x1080_erfnet = self.blank_image_1920x1080_erfnet.copy()

                # 把下半段贴到空白的160x120上
                mask_filter_1920x1080_erfnet[int(
                    1080 * config.tricks_erfnet_prep_clip_image_top):, :] = mask_filter_erfnet

                # 过滤vpgnet
                lane_solid_white = lane_solid_white + mask_filter_1920x1080_erfnet
                lane_solid_yellow = lane_solid_yellow + mask_filter_1920x1080_erfnet
                lane_double_yellow = lane_double_yellow + mask_filter_1920x1080_erfnet

                # 得到与erfnet重叠的vpgnet
                # 60-过滤，0-不过滤
                # lane_solid_white = (lane_solid_white > 60).astype(int)
                # lane_solid_yellow = (lane_solid_yellow > 60).astype(int)
                # lane_double_yellow = (lane_double_yellow > 60).astype(int)

                # lane_solid_white = (lane_solid_white > 0).astype(int)
                # lane_solid_yellow = (lane_solid_yellow > 0).astype(int)
                # lane_double_yellow = (lane_double_yellow > 0).astype(int)

                mask_filter_1920x1080_erfnet = (mask_filter_1920x1080_erfnet * 18).astype(int)

                # 分类
                prob_map_lane_solid_white = lane_solid_white * 1
                prob_map_lane_solid_yellow = lane_solid_yellow * 4
                prob_map_lane_double_yellow = lane_double_yellow * 6

                # 上色，转成图片
                seg_image_lane_solid_white = self.color_map_mat[prob_map_lane_solid_white]
                seg_image_lane_solid_yellow = self.color_map_mat[prob_map_lane_solid_yellow]
                seg_image_lane_double_yellow = self.color_map_mat[prob_map_lane_double_yellow]

                # 显示erfnet
                erfnet_image = self.color_map_mat[mask_filter_1920x1080_erfnet]

                # 融合3个车道线
                # alpha = 0.8
                # beta = 1 - alpha
                gamma = 0
                img_lane_all = cv2.addWeighted(seg_image_lane_solid_yellow, 1, seg_image_lane_solid_white, 1, gamma)
                img_lane_all = cv2.addWeighted(seg_image_lane_double_yellow, 1, img_lane_all, 1, gamma)
                img_lane_all = cv2.addWeighted(erfnet_image, 0.4, img_lane_all, 0.6, gamma)

                # img_lane_all = cv2.addWeighted(seg_image_lane_solid_white, 1, seg_image_lane_solid_yellow, 1, 0)
                # img_lane_all = cv2.addWeighted(img_lane_all, 1, seg_image_lane_double_yellow, 1, 0)
                # img_lane_all = cv2.addWeighted(img_lane_all, 1, erfnet_image, 1, 0)

                # blur
                img_lane_all = cv2.blur(img_lane_all, (9, 9))

                # 融合 车牌 和 vpgnet车道线all
                image_result = cv2.addWeighted(copy_image_origin_plate, 1, img_lane_all, 1, 0)

                # --------------------------时间测试--------------------------
                # 识别结束时间
                if config.print_running_time:
                    str_time_lane_line = str(datetime.datetime.now() - start_time_laneline)
                    print('车道线用时: ' + str_time_lane_line + ', ', end='')

                    # 检测结束时间
                    str_time_single_image = str(datetime.datetime.now() - start_time_single_image)
                    print('单张图片总用时: ' + str(datetime.datetime.now() - start_time_single_image))
                # --------------------------时间测试--------------------------

                text_message = 'data: ' + repr(list_plates_all_info_temp) + ', time: ' + str_time_single_image

                # send image object
                message.write(image_result, text_message)

                if self.dict_loop_flag.get(thread_name) is True:
                    # update the timestamp of each latest message
                    self.dict_latest_message_timestamp[thread_name] = time.time()
                else:
                    # if there is no more loop flag, then close socket
                    print('process {0} closed'.format(thread_name))
                    break
                pass

                time.sleep(0.00001)
            pass

            # close socket
            socket_obj.shutdown(socket.SHUT_RDWR)
            socket_obj.close()
            pass

