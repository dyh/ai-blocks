import datetime

import cv2
import numpy as np

import config
from license_plate.hyperlpr_v2.hyperlpr_pip_pkg.hyperlpr import LPR
# from license_plate.wrapper_hyperlpr_v1_color_type import get_plate_type_from_cropped_image
from license_plate.wrapper_hyperlpr_v1_color_type import WrapperHyperLPRV1


class WrapperHyperLPRV2:
    _pr_object = None

    def __init__(self):
        self._pr_object = LPR("./license_plate/hyperlpr_v2/hyperlpr_pip_pkg/hyperlpr/models")

        self.lpr_v1 = WrapperHyperLPRV1()

        pass

    # 获取大图片中所有车牌的位置
    def get_single_line_position_from_big_image(self, origin_image):
        """
        获取大图片中所有车牌的位置
        :param origin_image: 要识别的原始大图片
        :return: 车牌位置的 list[(x,y,w,h)]
        """
        list_position = []
        cropped_images = self._pr_object.detect_ssd(origin_image)
        for x1, y1, x2, y2 in cropped_images:
            list_position.append((x1, y1, x2 - x1, y2 - y1))
            pass
        return list_position

    # 根据车牌位置，获取大图片中所有车牌的信息
    def get_single_line_plates_from_position(self, origin_image, list_position):
        """
        获取大图片中所有车牌的信息
        :param origin_image: 要识别的原始大图片
        :param list_position: 车牌位置的 list[(x,y,w,h)]
        :return: 车牌信息list[(plate_name, str_plate_type, plate_confidence, left, top, w, h)]
        """
        list_result = []
        for _, (left, top, w, h) in enumerate(list_position):
            right = left + w
            bottom = top + h
            # left, top, right, bottom = plate
            # print(left, top, right, bottom)

            # # --------------------------时间测试--------------------------
            # # 识别开始时间
            # start1 = datetime.datetime.now()
            # # --------------------------时间测试--------------------------

            cropped = self._pr_object.loose_crop(origin_image, [int(left), int(top), int(right), int(bottom)], 120 / 48)
            cropped_finetuned = self._pr_object.finetune(cropped)

            plate_name, plate_confidence = self._pr_object.segmentation_free_recognition(cropped_finetuned)

            # # --------------------------时间测试--------------------------
            # # 识别结束时间
            # if config.print_running_time:
            #     print('文字用时: ' + str(datetime.datetime.now() - start1) + ', ', end='')
            # # --------------------------时间测试--------------------------

            # # --------------------------时间测试--------------------------
            # # 识别开始时间
            # start2 = datetime.datetime.now()
            # # --------------------------时间测试--------------------------

            # 调用 hyperlpr_v1 的车牌颜色检测
            str_plate_type = self.lpr_v1.get_plate_type_from_cropped_image(cropped_finetuned)
            # str_plate_type = '蓝牌'

            # # --------------------------时间测试--------------------------
            # # 识别结束时间
            # if config.print_running_time:
            #     print('颜色用时: ' + str(datetime.datetime.now() - start2) + ', ', end='')
            # # --------------------------时间测试--------------------------

            list_result.append((plate_name, str_plate_type, plate_confidence, left, top, w, h))
        pass
        return list_result

    # 获取大图片中所有 双层黄牌 的信息
    def get_double_line_plates_from_position(self, origin_image, list_position):
        """
        获取大图片中所有 双层黄牌 的信息
        :param origin_image: 要识别的原始大图片
        :param list_position: 车牌位置的 list[(x,y,w,h)]
        :return: 车牌信息list[(plate_name, str_plate_type, plate_confidence, left, top, w, h)]
        """
        list_result = []
        for _, (left, top, w, h) in enumerate(list_position):
            right = left + w
            bottom = top + h

            plate = origin_image[int(top):int(bottom), int(left):int(right), :]
            crop_up = plate[int(h * 0.05):int(h * 0.4), int(w * 0.2):int(w * 0.75)]
            crop_down = plate[int(h * 0.4):int(h), int(w * 0.05):w]
            crop_up = cv2.resize(crop_up, (64, 40))
            crop_down = cv2.resize(crop_down, (96, 40))
            cropped_finetuned = np.concatenate([crop_up, crop_down], 1)

            # 双层车牌，颜色固定
            str_plate_type = '双层黄牌'

            plate_name, plate_confidence = self._pr_object.segmentation_free_recognition(cropped_finetuned)
            list_result.append((plate_name, str_plate_type, plate_confidence, left, top, w, h))
            pass
        return list_result

    # 获取大图片中所有 双层黄牌 的位置
    def get_double_line_position_from_big_image(self, origin_image):
        """
        获取大图片中所有 双层黄牌 的位置
        :param origin_image: 要识别的原始大图片
        :return: 车牌位置的 list[(x,y,w,h)]
        """
        list_position = []

        image_gray = cv2.cvtColor(origin_image, cv2.COLOR_BGR2GRAY)
        cropped_images = self._pr_object.detect_traditional(image_gray)
        for _, (x1, y1, x2, y2) in cropped_images:
            list_position.append((x1, y1, x2 - x1, y2 - y1))
        pass
        return list_position
