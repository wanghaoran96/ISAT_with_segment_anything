# -*- coding: utf-8 -*-
# @Author  : LG

import os
from PIL import Image, ImageDraw
import numpy as np
from json import load, dump
from typing import List, Union


class Object:
    def __init__(self, category: str, group: int, segmentation, area, layer, bbox, iscrowd=0, note='', center=None,
                 action=None):
        if center is None:
            center = []
        self.action = action if action is not None else "unknow"  # TODO 右侧新添列表，提供场景选择
        self.category = category
        self.group = group
        self.segmentation = segmentation
        self.area = area
        self.layer = layer
        self.bbox = bbox
        self.iscrowd = iscrowd
        self.note = note
        self.center = center


class Annotation:
    def __init__(self, image_path, label_path):
        img_folder, img_name = os.path.split(image_path)
        self.description = 'ISAT'
        self.img_folder = img_folder
        self.img_name = img_name
        self.label_path = label_path
        self.note = ''

        image = np.array(Image.open(image_path))
        if image.ndim == 3:
            self.height, self.width, self.depth = image.shape
        elif image.ndim == 2:
            self.height, self.width = image.shape
            self.depth = 0
        else:
            self.height, self.width, self.depth = image.shape[:, :3]
            print('Warning: Except image has 2 or 3 ndim, but get {}.'.format(image.ndim))
        del image

        self.objects: List[Object, ...] = []

    def load_annotation(self):
        if os.path.exists(self.label_path):
            with open(self.label_path, 'r', encoding="utf-8") as f:
                dataset = load(f)
                info = dataset.get('info', {})
                description = info.get('description', '')
                if description == 'ISAT':
                    # ISAT格式json
                    objects = dataset.get('objects', [])
                    self.img_name = info.get('name', '')
                    width = info.get('width', None)
                    if width is not None:
                        self.width = width
                    height = info.get('height', None)
                    if height is not None:
                        self.height = height
                    depth = info.get('depth', None)
                    if depth is not None:
                        self.depth = depth
                    self.note = info.get('note', '')
                    for obj in objects:
                        category = obj.get('category', 'unknow')
                        action = obj.get('action', 'unknow')
                        group = obj.get('group', 0)
                        if group is None: group = 0
                        segmentation = obj.get('segmentation', [])
                        iscrowd = obj.get('iscrowd', 0)
                        note = obj.get('note', '')
                        area = obj.get('area', 0)
                        layer = obj.get('layer', 2)
                        bbox = obj.get('bbox', [])
                        center = obj.get('center', [])
                        obj = Object(category, group, segmentation, area, layer, bbox, iscrowd, note, center, action)
                        self.objects.append(obj)
                else:
                    # 不再支持直接打开labelme标注文件（在菜单栏-tool-convert中提供了isat<->labelme相互转换工具）
                    print('Warning: The file {} is not a ISAT json.'.format(self.label_path))
        return self

    def save_annotation(self):
        dataset = {}
        dataset['info'] = {}
        dataset['info']['description'] = self.description
        dataset['info']['folder'] = self.img_folder
        dataset['info']['name'] = self.img_name
        dataset['info']['width'] = self.width
        dataset['info']['height'] = self.height
        dataset['info']['depth'] = self.depth
        dataset['info']['note'] = self.note
        dataset['objects'] = []
        for obj in self.objects:
            object = {}
            object['category'] = obj.category
            object['action'] = obj.action
            object['group'] = obj.group
            object['segmentation'] = obj.segmentation
            object['area'] = obj.area
            object['layer'] = obj.layer
            object['bbox'] = obj.bbox
            object['iscrowd'] = obj.iscrowd
            object['note'] = obj.note
            object["center"] = obj.center
            # TODO 20250317根据box和segment创建一个mask,mask太大，不易存储，放在后处理，实际使用位置
            # # 创建一个空白的二值掩码
            # mask = Image.new('L', (dataset['info']['width'], dataset['info']['height']), 0)
            # draw = ImageDraw.Draw(mask)
            # # 绘制多边形
            # draw.polygon(object['segmentation'], outline=1, fill=1)
            # object['mask'] = [list((int(v) for v in mk)) for mk in np.array(mask)]

            dataset['objects'].append(object)

        # 后处理，计算center
        for obj in dataset["objects"]:
            points = obj["segmentation"]
            center = [int(sum(point[0] for point in points) / len(points)),
                      int(sum(point[1] for point in points) / len(points))]
            obj["center"] = center
        with open(self.label_path, 'w', encoding="utf-8") as f:
            dump(dataset, f, indent=4, ensure_ascii=False)
            print("now is using annotation.py")
        return True
