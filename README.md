# ai-blocks 

AI 积木

AI开源项目整合：车牌识别、车道线检测与分类。

awesome ai applications, lane line detection, license plate detection, etc.


## 展示视频

[![AI-BLOCKS](https://res.cloudinary.com/marcomontalbano/image/upload/v1602207766/video_to_markdown/images/youtube--SIKfIZABbfg-c05b58ac6eb4c4700831b2b3070cd403.jpg)](https://www.youtube.com/watch?v=SIKfIZABbfg "AI-BLOCKS")


## 代码引用和开源感谢

    https://github.com/szad670401/HyperLPR（车牌识别）
    https://github.com/SeokjuLee/VPGNet（车道线检测）
    https://github.com/akashgokul/294_FinalProj（车道线检测，vpgnet的pytorch实现）
    https://github.com/cardwing/Codes-for-Lane-Detection/tree/master/ERFNet-CULane-PyTorch（车道线检测）


## 运行环境

> 为兼容arm平台，默认为CPU运行

- 支持jetson nano的cpu/cuda，支持x86的cpu/cuda
- ubuntu 18.04
- python 3.6及以上
- cuda 10.2
- pip 20.1.1及以上


## 目录结构

```
.
├── config.py「tricks的参数」
├── lane_line「车道线识别 目录」
├── license_plate「车牌识别 目录」
│   ├── hyperlpr_v1_color_type「hyperlpr_v1的车牌类型功能」
│   ├── hyperlpr_v2「hyperlpr_v2的完整git clone」
│   ├── tricks.py「车牌识别小技巧」
│   ├── wrapper_hyperlpr_v1_color_type.py「对 hyperlpr_v1 车牌类型功能的封装」
│   └── wrapper_hyperlpr_v2.py「对 hyperlpr_v2 的封装」
├── socket_handle「socket服务端和客户端 目录」
├── test-server.py 「服务端启动程序」
├── test-client.py 「客户端启动程序，通过socket发送图片给服务端test-server.py，接收并显示结果」
├── push.sh 「git命令」
├── README.md「本文」
└── requirements.txt「pip freeze > requirements.txt」

```

## 配置pip虚拟环境

```
# 克隆程序代码
git clone https://github.com/dyh/ai-blocks.git 

# 进入程序目录
cd ai-blocks

# 安装python虚拟环境
sudo apt-get install python3-venv

# 创建虚拟环境目录
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 更新pip
python -m pip install --upgrade pip
    
# 通过pip安装软件包
pip install -r requirements.txt

```

## 运行准备与输出结果

1. 下载训练好的vpgnet模型文件
    
    vpg-1-4-6.pth [百度网盘 提取码: yd4c](https://pan.baidu.com/s/1Kjp2NeSv8jHBb5F66_n3lQ)

    形成 ./ai-blocks/lane_line/vpgnet/weights/vpg-1-4-6.pth 路径

2. 准备一些测试用的图片数据
    
    ```
    # 建立目录 ./pytest/images/
    # 拷贝图片文件到 ./pytest/images/ 目录
    # 形成 "./pytest/images/0001.png", "./pytest/images/0002.png", "./pytest/images/0003.png" 这样的路径
    ```   

3. 运行 test-server.py
    
    ```
    
    (venv) dyh@ubuntu:/mnt/work/workspace/ai-blocks$ python test-server.py
    listening 0.0.0.0:65432 ...
    accepted connection from ('192.168.31.21', 53352)
    listening 0.0.0.0:65432 ...
    
    received binary/image request from ('192.168.31.21', 53352) , length: 2349096
     # 1601989759.1194181, 车牌数量: 1, 车牌用时: 0:00:00.114332, 车道线用时: 0:00:00.556526, 单张图片总用时: 0:00:00.670894
    sending 2383498 buffer to ('192.168.31.21', 53352)
    
    received binary/image request from ('192.168.31.21', 53352) , length: 1976309
     # 1601989759.1194181, 车牌数量: 2, 车牌用时: 0:00:00.117357, 车道线用时: 0:00:00.588078, 单张图片总用时: 0:00:00.705472
    sending 2030339 buffer to ('192.168.31.21', 53352)
    
    received binary/image request from ('192.168.31.21', 53352) , length: 2108057
     # 1601989759.1194181, 车牌数量: 2, 车牌用时: 0:00:00.126276, 车道线用时: 0:00:00.638094, 单张图片总用时: 0:00:00.764404
    sending 2148503 buffer to ('192.168.31.21', 53352)
    
    received binary/image request from ('192.168.31.21', 53352) , length: 2373786
     # 1601989759.1194181, 车牌数量: 3, 车牌用时: 0:00:00.137280, 车道线用时: 0:00:00.551417, 单张图片总用时: 0:00:00.688731
    sending 2414243 buffer to ('192.168.31.21', 53352)
    
    received binary/image request from ('192.168.31.21', 53352) , length: 2233284
     # 1601989759.1194181, 车牌数量: 1, 车牌用时: 0:00:00.115119, 车道线用时: 0:00:00.595961, 单张图片总用时: 0:00:00.711116
    sending 2245467 buffer to ('192.168.31.21', 53352)
    
    received binary/image request from ('192.168.31.21', 53352) , length: 2425929
     # 1601989759.1194181, 车牌数量: 1, 车牌用时: 0:00:00.116927, 车道线用时: 0:00:00.539524, 单张图片总用时: 0:00:00.656487
    sending 2454052 buffer to ('192.168.31.21', 53352)
    
    ```


4. 运行 test-client.py
    
    ```
    
    (venv) dyh@ubuntu:/mnt/work/workspace/ai-blocks$ python test-client.py 
    socket client is starting...
    connecting 192.168.31.21:65432 ...
   
    sending 3026602 buffer to ('192.168.31.21', 65432)
    received text/json request from ('192.168.31.21', 65432) , length: 169
    {'result': "data: [('辽AB1U52', '蓝牌', 0.9245611599513462, 1194, 706, 93, 26), ('辽AM78A8', '蓝牌', 0.9468862499509539, 608, 640, 64, 26)], time: 0:00:00.780417"}
    received binary/image request from ('192.168.31.21', 65432) , length: 3027637

    sending 2494244 buffer to ('192.168.31.21', 65432)
    received text/json request from ('192.168.31.21', 65432) , length: 44
    {'result': 'data: [], time: 0:00:00.654163'}
    received binary/image request from ('192.168.31.21', 65432) , length: 2520666
    
    sending 2302256 buffer to ('192.168.31.21', 65432)
    received text/json request from ('192.168.31.21', 65432) , length: 106
    {'result': "data: [('辽AV17A8', '蓝牌', 0.942786693572998, 1064, 835, 175, 53)], time: 0:00:00.758924"}
    received binary/image request from ('192.168.31.21', 65432) , length: 2347663
    
    sending 2171010 buffer to ('192.168.31.21', 65432)
    received text/json request from ('192.168.31.21', 65432) , length: 106
    {'result': "data: [('辽AV17A8', '蓝牌', 0.968366699559348, 1216, 783, 130, 45)], time: 0:00:00.714810"}
    received binary/image request from ('192.168.31.21', 65432) , length: 2179818
    
    ```
