import cv2

import config

_chinese_chars = {"京": 0, "沪": 1, "津": 2, "渝": 3, "冀": 4, "晋": 5, "蒙": 6, "辽": 7, "吉": 8, "黑": 9,
                  "苏": 10, "浙": 11, "皖": 12, "闽": 13, "赣": 14, "鲁": 15, "豫": 16, "鄂": 17, "湘": 18,
                  "粤": 19, "桂": 20, "琼": 21, "川": 22, "贵": 23, "云": 24, "藏": 25, "陕": 26, "甘": 27,
                  "青": 28, "宁": 29, "新": 30, "港": 65, "学": 66, "使": 68, "警": 69, "澳": 70, "挂": 71}


# _plate_type = ["蓝牌", "单层黄牌", "新能源车牌", "白色", "黑色-港澳", "双层黄牌"]

# 大图片 预处理 减小图片尺寸
def preprocess_reduce_image_size(origin_image, reserved_scale=config.tricks_prep_reduce_image_reserved):
    """
    大图片 预处理 减小图片尺寸
    :param reserved_scale: 宽度、高度 保留的比例
    :param origin_image: 原始图片
    :return: 新的图片对象
    """
    height, width, _ = origin_image.shape
    return cv2.resize(origin_image, (int(width * reserved_scale), int(height * reserved_scale)))


# 大图片 预处理 剪裁掉上方区域
def preprocess_clip_image_top(origin_image, clip_scale=config.tricks_prep_clip_image_top):
    """
    大图片 预处理 剪裁掉上方区域
    :param clip_scale: 高度剪裁掉的区域，比例
    :param origin_image: 原始图片
    :return: 新的图片对象
    """
    height, _, _ = origin_image.shape
    return origin_image[int(height * clip_scale):, :]


def plate_confidence_filter(plate_char_1, plate_confidence, confidence1=config.tricks_confidence_primary,
                            confidence2=config.tricks_confidence_secondary):
    # 如果是 重点省份，置信度可以稍微降低
    if plate_char_1 == config.tricks_selected_province_name:
        if plate_confidence >= confidence1:
            pass
        else:
            return False
    else:
        # 如果不是 重点省份，置信度需要提高
        if plate_confidence >= confidence2:
            pass
        else:
            return False
        pass
    return True


def sub_func_get_numbers_count(plate_text):
    """
    子函数-获得数字个数
    """
    ret = 0
    for i in plate_text:
        if i.isdigit():
            ret += 1
            pass
        pass
    return ret


# 车牌基础逻辑过滤
def plate_logical_filter(plate_type, plate_text):
    """
    车牌基础逻辑过滤：首字符判断，位数判断
    :param plate_text:
    :param plate_type: 车牌类型
    :return: 正确 0；首字符错误 -1;车牌位数错误 -2;未知的车牌类型错误 -3;数字位数少错误 -4
    """
    ret = 0

    plate_text_length = len(plate_text)

    # 首字符
    plate_text_first_char = plate_text[0]

    # 首字符判断
    # 第一个字符必须是中文，不是中文则过滤掉（军牌 除外）
    # 必须包含chars中的中文之一

    # 位数判断
    # 如果是 蓝牌 或 黄牌，则必须是7位数
    # _plate_type = ["蓝牌", "单层黄牌", "新能源车牌", "白色", "黑色-港澳", "双层黄牌"]

    # 蓝牌
    if plate_type == '蓝牌':
        if plate_text_length != 7:
            ret = -2
        else:
            if _chinese_chars.get(plate_text_first_char) is None:
                ret = -1
            elif sub_func_get_numbers_count(plate_text) < 3:
                # 数字位数少错误
                ret = -4
                pass
            pass
    elif plate_type == '单层黄牌':
        # 单层黄牌
        if plate_text_length != 7:
            ret = -2
        else:
            if _chinese_chars.get(plate_text_first_char) is None:
                ret = -1
            elif sub_func_get_numbers_count(plate_text) < 3:
                # 数字位数少错误
                ret = -4
            pass
    elif plate_type == '双层黄牌':
        # 双层黄牌
        if plate_text_length != 7:
            ret = -2
        else:
            if _chinese_chars.get(plate_text_first_char) is None:
                ret = -1
            elif sub_func_get_numbers_count(plate_text) < 3:
                # 数字位数少错误
                ret = -4
            pass
    elif plate_type == '新能源车牌':
        # 新能源车牌
        if plate_text_length != 8:
            ret = -2
        else:
            if _chinese_chars.get(plate_text_first_char) is None:
                ret = -1
            elif sub_func_get_numbers_count(plate_text) < 4:
                # 数字位数少错误
                ret = -4
            pass
        pass
    elif plate_type == '白色':
        # 白色，警牌 或 军牌，警牌 有 警字，军牌 无汉字
        if plate_text_length != 7:
            ret = -2
        pass
    elif plate_type == '黑色-港澳':
        # 黑色-港澳
        if plate_text_length != 7:
            ret = -2
        else:
            if _chinese_chars.get(plate_text_first_char) is None:
                ret = -1
            pass
        pass
    else:
        # hyperlpr_v2 空
        # 未知的车牌类型错误
        ret = -3
        pass

    return ret


# 车牌最小尺寸过滤器
def plate_min_size_filter(plate_width, plate_height):
    """
    车牌最小尺寸过滤器
    :param plate_width: 车牌宽度
    :param plate_height: 车牌高度
    :return: True/False
    """
    # 车牌高度
    if plate_height < config.tricks_plate_min_height or plate_width < config.tricks_plate_min_width:
        return False
    else:
        return True
    pass


# 筛选车牌的小技巧
def all_tricks_filter(plate_text, plate_type, plate_confidence, plate_width, plate_height,
                      confidence1=config.tricks_confidence_primary, confidence2=config.tricks_confidence_secondary):
    """
    筛选车牌的小技巧
    :param plate_text: 车牌号
    :param plate_type: 车牌类型
    :param plate_width: 车牌宽度
    :param plate_height: 车牌高度
    :param plate_confidence: 置信度
    :param confidence2: 重点省份置信度
    :param confidence1: 其他省份置信度
    :return: True/False
    """
    ret = False
    # 重点省份

    # 首字符
    plate_text_first_char = plate_text[0]

    # 车牌最小尺寸过滤器
    if plate_min_size_filter(plate_width, plate_height) is False:
        return ret

    # 置信度判断
    if plate_confidence_filter(plate_text_first_char, plate_confidence, confidence1, confidence2) is False:
        return ret

    # 车牌基础逻辑过滤：首字符判断，位数判断
    flag = plate_logical_filter(plate_type, plate_text)
    if flag == 0:
        pass
    elif flag == -1:
        print("首字符错误：" + plate_text + "|" + plate_type)
        return ret
    elif flag == -2:
        print("车牌位数错误：" + plate_text + "|" + plate_type)
        return ret
    elif flag == -3:
        print("未知车牌类型错误：" + plate_text + "|" + plate_type)
        return ret
    elif flag == -4:
        print("数字位数少错误：" + plate_text + "|" + plate_type)
        return ret

    # 如果通过上面所有考验，则返回True
    return True
