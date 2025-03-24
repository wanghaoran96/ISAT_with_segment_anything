# encoding=utf-8

import cv2
import numpy as np
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt


# 根据segment创建mask
def create_mask(image_size, points):
    # 创建一个空白的二值掩码
    mask = Image.new('L', image_size, 0)
    draw = ImageDraw.Draw(mask)
    # 绘制多边形
    draw.polygon(points, outline=1, fill=1)

    return np.array(mask)


# 根据圆心创建mask
def create_circular_mask(center, image_shape=(480, 640), radius=10):
    """
    创建一个以center坐标为圆心、radius为半径的圆形掩膜。

    参数:
    - center: 圆心坐标 (x, y) 的元组。
    - image_shape: 目标掩膜的大小，默认是(480, 640)。
    - radius: 圆形区域的半径，默认是10。

    返回:
    - 形状为 (1, 480, 640) 的布尔类型 ndarray，圆形区域内为 True，其余部分为 False。
    """
    mask = np.zeros(image_shape, dtype=np.uint8)
    cv2.circle(mask, center, radius, color=1, thickness=-1)
    bool_mask = mask.astype(bool)
    return bool_mask[np.newaxis, :, :]


# 计算质心，针对圆形mask使用
def calculate_center(points):
    center = [int(sum(point[0] for point in points) / len(points)),
              int(sum(point[1] for point in points) / len(points))]
    return center


def display_mask(mask):
    """
    显示掩膜图像。

    参数:
    - mask: 要显示的掩膜，形状应为 (1, H, W) 的布尔类型 ndarray。
    """
    # 移除第一个维度并转换为整数类型以便于显示
    mask_to_display = mask.squeeze().astype(np.uint8) * 255

    plt.figure(figsize=(10, 7))
    plt.imshow(mask_to_display, cmap='gray')
    plt.title('Mask Display')
    plt.axis('off')  # 不显示坐标轴
    plt.show()


if __name__ == '__main__':
    # 示例用法
    image_size = (400, 500)  # 图像尺寸
    points = [
        [
            173,
            226
        ],
        [
            169,
            227
        ],
        [
            166,
            228
        ],
        [
            164,
            229
        ],
        [
            159,
            232
        ],
        [
            156,
            234
        ],
        [
            152,
            238
        ],
        [
            149,
            244
        ],
        [
            148,
            247
        ],
        [
            148,
            255
        ],
        [
            153,
            268
        ],
        [
            153,
            272
        ],
        [
            155,
            276
        ],
        [
            155,
            281
        ],
        [
            158,
            289
        ],
        [
            158,
            299
        ],
        [
            159,
            302
        ],
        [
            160,
            304
        ],
        [
            161,
            306
        ],
        [
            163,
            309
        ],
        [
            165,
            311
        ],
        [
            169,
            313
        ],
        [
            173,
            317
        ],
        [
            176,
            318
        ],
        [
            182,
            319
        ],
        [
            192,
            319
        ],
        [
            197,
            318
        ],
        [
            200,
            317
        ],
        [
            203,
            316
        ],
        [
            210,
            312
        ],
        [
            217,
            305
        ],
        [
            220,
            301
        ],
        [
            221,
            297
        ],
        [
            221,
            288
        ],
        [
            220,
            279
        ],
        [
            219,
            274
        ],
        [
            216,
            266
        ],
        [
            211,
            257
        ],
        [
            207,
            252
        ],
        [
            206,
            250
        ],
        [
            206,
            248
        ],
        [
            205,
            246
        ],
        [
            199,
            235
        ],
        [
            195,
            231
        ],
        [
            192,
            229
        ],
        [
            190,
            228
        ],
        [
            188,
            227
        ],
        [
            184,
            226
        ]
    ]  # 分割坐标点
    points = [(float(x[0]), float(x[1])) for x in points]
    mask = create_mask(image_size, points)

    ################################################
    # 示例使用
    center_coord = (320, 240)  # 假设中心点坐标为(320, 240)
    mask = create_circular_mask(center_coord)
    # 检查生成的mask尺寸是否正确
    print("Mask shape:", mask.shape)
    # 展示掩膜
    display_mask(mask)
    ###############################################
    points = [
        [
            173,
            226
        ],
        [
            169,
            227
        ],
        [
            166,
            228
        ],
        [
            164,
            229
        ],
        [
            159,
            232
        ],
        [
            156,
            234
        ],
        [
            152,
            238
        ],
        [
            149,
            244
        ],
        [
            148,
            247
        ],
        [
            148,
            255
        ],
        [
            153,
            268
        ],
        [
            153,
            272
        ],
        [
            155,
            276
        ],
        [
            155,
            281
        ],
        [
            158,
            289
        ],
        [
            158,
            299
        ],
        [
            159,
            302
        ],
        [
            160,
            304
        ],
        [
            161,
            306
        ],
        [
            163,
            309
        ],
        [
            165,
            311
        ],
        [
            169,
            313
        ],
        [
            173,
            317
        ],
        [
            176,
            318
        ],
        [
            182,
            319
        ],
        [
            192,
            319
        ],
        [
            197,
            318
        ],
        [
            200,
            317
        ],
        [
            203,
            316
        ],
        [
            210,
            312
        ],
        [
            217,
            305
        ],
        [
            220,
            301
        ],
        [
            221,
            297
        ],
        [
            221,
            288
        ],
        [
            220,
            279
        ],
        [
            219,
            274
        ],
        [
            216,
            266
        ],
        [
            211,
            257
        ],
        [
            207,
            252
        ],
        [
            206,
            250
        ],
        [
            206,
            248
        ],
        [
            205,
            246
        ],
        [
            199,
            235
        ],
        [
            195,
            231
        ],
        [
            192,
            229
        ],
        [
            190,
            228
        ],
        [
            188,
            227
        ],
        [
            184,
            226
        ]
    ]
    center = calculate_center(points)
    print(center)
