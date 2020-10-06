import datetime

import cv2
import numpy as np
import torch
import torch.nn as nn
from past.builtins import xrange
from torchvision import transforms

import config
from lane_line.vpgnet.vpgnet_torch import VPGNet


# 1	lane_solid_white
# 2	lane_broken_white
# 3	lane_double_white
# 4	lane_solid_yellow
# 5	lane_broken_yellow
# 6	lane_double_yellow


class WrapperVPGNet:

    def __init__(self):
        model_path = './lane_line/vpgnet/weights/vpg-1-4-6.pth'
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # self.device = torch.device('cpu')

        self.model = VPGNet()
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        # model = torch.load(model_path)
        if torch.cuda.device_count() > 1:
            self.model = nn.DataParallel(self.model)
        self.model.to(device=self.device)
        self.model.eval()

        self.optimizer = torch.optim.Adam(params=self.model.parameters(), lr=1e-4)
        self.tensor_transform = transforms.ToTensor()
        pass

    def get_lane_line_from_image_640x480(self, origin_image_640x480):
        # # --------------------------时间测试--------------------------
        # # 识别开始时间
        # start1 = datetime.datetime.now()
        # # --------------------------时间测试--------------------------
        # image_obj = cv2.resize(origin_image_640x480, (640, 480))
        # 颜色
        image_obj = origin_image_640x480[:, :, [2, 1, 0]]

        # tensor_transform = transforms.ToTensor()
        image_obj = self.tensor_transform(image_obj)

        image_obj = image_obj.view((1, 3, 480, 640))
        image_obj = image_obj.to(device=self.device)
        obj_mask_pred_160x120, _ = self.model(image_obj)

        # 车道线
        obj_mask_pred_160x120 = (obj_mask_pred_160x120 >= config.tricks_vpgnet_confidence_mask_pred).int()
        obj_mask_pred_160x120 = obj_mask_pred_160x120.cpu().detach().numpy()

        # # vp
        # vp_pred = (vp_pred > 0.9).float()
        # vp_pred = vp_pred.cpu().detach().numpy()
        # vp_sum = vp_pred[0, 0, :, :] + vp_pred[0, 1, :, :] + vp_pred[0, 2, :, :] + vp_pred[0, 3, :, :]
        # # --------------------------时间测试--------------------------
        # # 识别结束时间
        # if config.print_running_time:
        #     print('车道线用时: ' + str(datetime.datetime.now() - start1) + ', ', end='')
        # # --------------------------时间测试--------------------------
        # return obj_mask_pred[0, 0, :, :], obj_mask_pred[0, 1, :, :], obj_mask_pred[0, 2, :, :]
        return obj_mask_pred_160x120[0, :, :, :]

