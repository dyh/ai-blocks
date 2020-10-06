import cv2
# coding=utf-8
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPool2D
from keras.optimizers import SGD
from keras import backend as k1

import cv2
import numpy as np
from tensorflow.python import get_default_graph


class WrapperHyperLPRV1:

    def __init__(self):
        k1.image_data_format()

        self.plateType = ["蓝牌", "单层黄牌", "新能源车牌", "白色", "黑色-港澳"]
        self.model = self.__getmodel_tensorflow(5)
        self.model.load_weights("./license_plate/hyperlpr_v1_color_type/model/plate_type.h5")
        self.model._make_predict_function()
        self.graph = get_default_graph()
        pass

    def __getmodel_tensorflow(self, nb_classes):
        # nb_classes = len(charset)

        img_rows, img_cols = 9, 34
        # number of convolutional filters to use
        nb_filters = 32
        # size of pooling area for max pooling
        nb_pool = 2
        # convolution kernel size
        nb_conv = 3

        # x = np.load('x.npy')
        # y = np_utils.to_categorical(range(3062)*45*5*2, nb_classes)
        # weight = ((type_class - np.arange(type_class)) / type_class + 1) ** 3
        # weight = dict(zip(range(3063), weight / weight.mean()))  # 调整权重，高频字优先

        model = Sequential()
        model.add(Conv2D(16, (5, 5), input_shape=(img_rows, img_cols, 3)))
        model.add(Activation('relu'))
        model.add(MaxPool2D(pool_size=(nb_pool, nb_pool)))
        model.add(Flatten())
        model.add(Dense(64))
        model.add(Activation('relu'))
        model.add(Dropout(0.5))
        model.add(Dense(nb_classes))
        model.add(Activation('softmax'))
        model.compile(loss='categorical_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])
        return model

    def __simple_predict(self, image):
        image = cv2.resize(image, (34, 9))
        image = image.astype(np.float) / 255
        with self.graph.as_default():
            res = np.array(self.model.predict(np.array([image]))[0])
            return res.argmax()

    def get_plate_type_from_cropped_image(self, cropped_image):
        cropped_image = cv2.resize(cropped_image, (136, 90))
        plate_type = self.__simple_predict(cropped_image)
        return self.plateType[plate_type]
