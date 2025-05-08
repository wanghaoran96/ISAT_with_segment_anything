# encoding=utf-8
import cv2
import numpy as np
import os
import screeninfo

scale = 1.0


def draw_text_with_box(image_path, centers, start=0, show=True):
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print("Image not found")
        return

    # 获取字体和字体大小
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2

    for keypoint_count, pixel in enumerate(centers):
        keypoint_count = int(keypoint_count + start)
        # 计算矩形的左上角和右下角坐标
        x, y = pixel

        # draw text

        displayed_text = f"{keypoint_count}"
        text_length = len(displayed_text)
        # box大小
        box_width = 30 + 10 * (text_length - 1)
        box_height = 30

        top_left_y = y - box_width // 2
        top_left_x = x - box_height // 2
        bottom_right_y = y + box_width // 2
        bottom_right_x = x + box_height // 2

        # 创建一个纯白色的矩形
        cv2.rectangle(image, (top_left_y, top_left_x), (bottom_right_y, bottom_right_x), (255, 255, 255), -1)
        cv2.rectangle(image, (top_left_y, top_left_x), (bottom_right_y, bottom_right_x), (0, 0, 0), 2)

        # 在矩形中心绘制文本，自定义想要绘制的图像，圆圈或者方框
        # cv2.putText(img, text, (y - text_size[0] // 2, x + text_size[1] // 2), font, font_scale, (0, 0, 255), thickness)
        cv2.putText(image, str(keypoint_count), (y - 7 * (text_length), x + 7), font, font_scale, (0, 0, 255),
                    thickness)

    if show:
        # 创建窗口
        cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
        # 获取屏幕分辨率
        monitor = screeninfo.get_monitors()[0]
        screen_width = monitor.width
        screen_height = monitor.height

        # 计算窗口大小，确保不超过屏幕尺寸
        window_width = int(min(image.shape[1], screen_width) * scale)
        window_height = int(min(image.shape[0], screen_height) * scale)
        # 设置窗口大小
        cv2.resizeWindow('Image', window_width, window_height)
        # 显示图片
        cv2.imshow('Image', image)
        # 等待直到用户按下任意键
        cv2.waitKey(0)
        # 关闭所有OpenCV窗口
        cv2.destroyAllWindows()
    return image


def manual_point_drawing(img):
    image = cv2.imread(img)
    # 手动打标签
    if image is None:
        print("Error: Image not found.")
        exit()

    radius = 10  # 光圈的半径
    coordinates = []

    # 鼠标回调函数
    def click_event(event, x, y, flags, param):
        # 获取图像的副本，以便在副本上绘制
        image_copy = image.copy()

        if event == cv2.EVENT_LBUTTONDOWN:
            # 在点击的位置绘制一个红色的光圈
            cv2.circle(image_copy, (x, y), radius, (0, 0, 255), -1)
            cv2.imshow('Image', image_copy)
            print(f'坐标  -  W: {x}, H: {y}')
            coordinates.append((y, x))

    # 创建窗口，窗口名称可以改为文件名，不容易混淆
    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    # 获取屏幕分辨率
    monitor = screeninfo.get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height
    # scale = 1.0 # 0.75,1.75,1.0
    # 计算窗口大小，确保不超过屏幕尺寸
    window_width = int(min(image.shape[1], screen_width) * scale)
    window_height = int(min(image.shape[0], screen_height) * scale)
    # 设置窗口大小
    cv2.resizeWindow('Image', window_width, window_height)

    # 显示图片
    cv2.imshow('Image', image)
    # 设置鼠标回调函数
    cv2.setMouseCallback('Image', click_event)
    # 等待直到用户按下任意键
    cv2.waitKey(0)
    # 关闭所有OpenCV窗口
    cv2.destroyAllWindows()

    return coordinates


if __name__ == '__main__':
    base_path = r"...\origin"
    # base_path = ""
    out_path = r"...\target"
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    images = os.listdir(base_path)
    images.sort()

    flag = 1
    for idx in range(0, len(images)):
        if not flag:
            print(f"下一次打标索引为：{idx - 1}")
            break

        image = images[idx]
        print("*" * 100)
        print("当前顺序：", idx + 1, "/", len(images))
        print("当前文件名称：", image)
        image_path = os.path.join(base_path, image)

        # image_ndarray = None
        while True:
            # 1、手动打坐标
            coordinates = manual_point_drawing(image_path)  # (H,W) 注意的是xy的顺序，这里是yx，
            # coordinates.append((125, 764))
            # print("坐标", coordinates)  # [(1025, 284), (443, 777), (191, 194), (872, 780)]

            # 2、绘制box和text
            image_ndarray = draw_text_with_box(image_path, coordinates, 0)

            human_instruction = "XX"
            while human_instruction != "0" and human_instruction != "1" and human_instruction != "9":
                human_instruction = input("\n请给出评判意见:(0是保存,1是否,9是结束当前评判)")

            if human_instruction == "0":
                for coord in coordinates:  # 这里可以一个点存一张图片，也可以所以点位存一张图片
                    coordinates_str = '_'.join(map(str, coord))
                    # 2、绘制box和text
                    image_ndarray = draw_text_with_box(
                        image_path,
                        [coord],
                        0,
                        False
                    )
                    image_nname = os.path.basename(image_path).replace(".png", "") + f"_coord_{coordinates_str}.jpg"
                    # image_nname = os.path.join(out_path, image_nname)
                    cv2.imwrite(os.path.join(out_path, image_nname), image_ndarray)
                print("保存完成！")
                break
            elif human_instruction == "1":
                continue
            elif human_instruction == "9":
                flag = 0
                break
