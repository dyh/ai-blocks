# coding:utf-8
import inspect

# 输出运行耗时
print_running_time = True

# --------------------license plate tricks--------------------

# 重点省份
tricks_selected_province_name = '辽'

# 主要 省份 置信度
tricks_confidence_primary = 0.91

# 次要 省份 置信度
tricks_confidence_secondary = 0.94

# 有效的最小车牌宽度
tricks_plate_min_width = 0  # 88

# 有效的最小车牌宽度
tricks_plate_min_height = 15  # 32

# 大图片 预处理 减小图片尺寸 宽度、高度 保留的比例
tricks_prep_reduce_image_reserved = 0.8

# 大图片 预处理 剪裁掉上方区域 高度剪裁掉的区域，比例
tricks_prep_clip_image_top = 0.4

# --------------------VPGNET--------------------
# vpgnet 车道线置信度阈值
tricks_vpgnet_confidence_mask_pred = 0.9

# --------------------ERFNET--------------------
# 顶部 预处理 剪裁掉上方区域
tricks_erfnet_prep_clip_image_top = 0.4

# erfnet 车道线置信度阈值
tricks_erfnet_confidence_mask_pred = 0.6


# 生成参数字符串
def get_args_string():
    # str1 = '试验参数: '
    str_result = ''

    # --------------------tricks--------------------
    # 重点省份
    # tricks_selected_province_name = '辽'

    # 主要 省份 置信度
    str_result += get_var_name_and_value(tricks_confidence_primary) + ', '

    # 次要 省份 置信度
    str_result += get_var_name_and_value(tricks_confidence_secondary) + ', '

    # 有效的最小车牌宽度
    str_result += get_var_name_and_value(tricks_plate_min_width) + ', '

    # 有效的最小车牌宽度
    str_result += get_var_name_and_value(tricks_plate_min_height) + ', '

    # 大图片 预处理 减小图片尺寸 宽度、高度 保留的比例
    str_result += get_var_name_and_value(tricks_prep_reduce_image_reserved) + ', '

    # 大图片 预处理 剪裁掉上方区域 高度剪裁掉的区域，比例
    str_result += get_var_name_and_value(tricks_prep_clip_image_top) + ', '

    return str_result


# 子函数-生成参数字符串
def sub_func_retrieve_name_ex():
    stacks = inspect.stack()
    call_func = stacks[1].function
    code = stacks[2].code_context[0]
    start_index = code.index(call_func)
    start_index = code.index("(", start_index + len(call_func)) + 1
    end_index = code.index(")", start_index)
    str_var_name = code[start_index:end_index].strip()
    return str_var_name


def get_var_name_and_value(var_object):
    return "{} = {}".format(sub_func_retrieve_name_ex(), var_object)
