import os

import numpy as np
import torch
import torchvision
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim
import cv2
import torch.nn.functional as F

import config
from lane_line.erfnet import models
import lane_line.erfnet.utils.transforms as tf


class WrapperERFNet:
    def __init__(self):

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # self.device = torch.device('cpu')

        self.blank_image_erfnet = np.zeros((590, 1640, 3), dtype=np.uint8)

        num_class = 5
        ignore_label = 255

        self.model = models.ERFNet(num_class)
        input_mean = self.model.input_mean
        input_std = self.model.input_std
        policies = self.model.get_optim_policies()
        # self.model = torch.nn.DataParallel(self.model, device_ids=range(1)).cuda()
        # self.model = torch.load(self.model)
        # torch.load with map_location=torch.device('cpu')

        weight_file = './lane_line/erfnet/trained/ERFNet_trained.tar'

        if os.path.isfile(weight_file):
            # print(("=> loading checkpoint '{}'".format(args.resume)))
            # checkpoint =
            # start_epoch = checkpoint['epoch']
            # best_mIoU = checkpoint['best_mIoU']
            # torch.nn.Module.load_state_dict(self.model, checkpoint['state_dict'])
            # torch.nn.Module.load_state_dict(torch.load(weight_file, map_location=torch.device('cpu')))
            self.model.load_state_dict(torch.load(weight_file, map_location=self.device))

            # print(("=> loaded checkpoint '{}' (epoch {})".format(args.evaluate, checkpoint['epoch'])))

        cudnn.benchmark = True
        cudnn.fastest = True
        # define loss function (criterion) optimizer and evaluator
        weights = [1.0 for _ in range(5)]
        weights[0] = 0.4
        # class_weights = torch.FloatTensor(weights).cuda()
        # class_weights = torch.FloatTensor(weights).cpu()

        # criterion = torch.nn.NLLLoss(ignore_index=ignore_label, weight=class_weights).cuda()
        # criterion = torch.nn.NLLLoss(ignore_index=ignore_label, weight=class_weights).cpu()

        for group in policies:
            print(('group: {} has {} params, lr_mult: {}, decay_mult: {}'.format(group['name'], len(group['params']),
                                                                                 group['lr_mult'],
                                                                                 group['decay_mult'])))

        self.model.to(device=self.device)

        # switch to evaluate mode
        self.model.eval()

        self.label = cv2.imread('./lane_line/erfnet/label_image/04280.png', cv2.IMREAD_UNCHANGED)
        self.label = self.label[240:, :]
        self.label = self.label.squeeze()

        input_mean = [103.939, 116.779, 123.68]  # [0, 0, 0]
        input_std = [1, 1, 1]

        self.transform = torchvision.transforms.Compose([
            tf.GroupRandomScaleNew(size=(976, 208), interpolation=(cv2.INTER_LINEAR, cv2.INTER_NEAREST)),
            tf.GroupNormalize(mean=(input_mean, (0,)), std=(input_std, (1,))),
        ])

        pass

    def get_lane_line_from_image_1640x350(self, origin_image_976x208):

        if self.transform:
            origin_image_976x208, label = self.transform((origin_image_976x208, self.label))
            origin_image_976x208 = torch.from_numpy(origin_image_976x208).permute(2, 0, 1).contiguous().float()
            # origin_image_976x208 = torch.from_numpy(np.ascontiguousarray(torch.from_numpy(origin_image_976x208).permute(2, 0, 1)))

            # origin_image_976x208 = np.ascontiguousarray(torch.from_numpy(origin_image_976x208).permute(2, 0, 1))
            # origin_image_976x208 = torch.from_numpy(origin_image_976x208).permute(2, 0, 1)
            # np.ascontiguousarray(arr1)
            # .permute(2, 0, 1).contiguous()
            # .float()
            # .cpu().detach().numpy()
            pass

        # 升1
        new_image = torch.unsqueeze(origin_image_976x208, 0)

        # 这里得到的是tensor[3]
        input_var = torch.autograd.Variable(new_image, volatile=True)

        # 输出结果
        # compute output
        output, output_exist = self.model(input_var)

        # measure accuracy and record loss
        output = F.softmax(output, dim=1)

        output = (output >= config.tricks_erfnet_confidence_mask_pred).int()
        # pred = output.data.cpu().numpy()  # BxCxHxW
        pred = output.cpu().detach().numpy()  # BxCxHxW

        # 1,5,208,976
        return pred[0, 1:5, :, :]


# def img_add(img_bg, img_line):
#     img_line = cv2.resize(img_line, (1640, 350))
#     # I want to put logo on top-left corner, So I create a ROI
#     rows, cols, channels = img_line.shape
#     # rows, cols = img_line.shape
#     roi = img_bg[240:rows + 240, 0:cols]
#
#     dst = cv2.addWeighted(img_line, 1, roi, 1, 0)  # 图像融合
#     img_result = img_bg.copy()  # 对原图像进行拷贝
#     img_result[240:rows + 240, 0:cols] = dst  # 将融合后的区域放进原图
#
#     return img_result
