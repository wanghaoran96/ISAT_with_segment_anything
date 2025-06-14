# -*- coding: utf-8 -*-
# @Author  : LG

from PyQt5 import QtWidgets, QtGui, QtCore
from ISAT.widgets.polygon import Polygon, Vertex, PromptPoint, Line, Rect
from ISAT.configs import STATUSMode, CLICKMode, DRAWMode, CONTOURMode
import numpy as np
import cv2
import time  # 拖动鼠标描点
import shapely


class AnnotationScene(QtWidgets.QGraphicsScene):
    def __init__(self, mainwindow):
        super(AnnotationScene, self).__init__()
        self.mainwindow = mainwindow
        self.image_item: QtWidgets.QGraphicsPixmapItem = None
        self.mask_item: QtWidgets.QGraphicsPixmapItem = None
        self.image_data = None
        self.current_graph: Polygon = None
        self.current_sam_rect: Rect = None
        self.current_line: Line = None
        self.mode = STATUSMode.VIEW
        self.click = CLICKMode.POSITIVE
        self.draw_mode = DRAWMode.SEGMENTANYTHING  # 默认使用segment anything进行快速标注
        self.contour_mode = CONTOURMode.SAVE_EXTERNAL  # 默认SAM只保留外轮廓
        self.click_points = []  # SAM point prompt
        self.click_points_mode = []  # SAM point prompt
        self.prompt_points = []
        self.masks: np.ndarray = None
        self.mask_alpha = 0.5
        self.top_layer = 1

        self.guide_line_x: QtWidgets.QGraphicsLineItem = None
        self.guide_line_y: QtWidgets.QGraphicsLineItem = None

        # 拖动鼠标描点
        self.last_draw_time = time.time()
        self.draw_interval = 0.15
        self.pressd = False

        #
        self.selected_polygons_list = list()

        self.repaint_start_vertex = None
        self.repaint_end_vertex = None
        self.hovered_vertex: Vertex = None

    def load_image(self, image_path: str):
        self.clear()
        if self.mainwindow.use_segment_anything:
            self.mainwindow.segany.reset_image()

        # image_data = cv2.imread(image_path)
        image_data = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        self.image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)

        self.image_item = QtWidgets.QGraphicsPixmapItem()
        self.image_item.setZValue(0)
        self.addItem(self.image_item)
        self.mask_item = QtWidgets.QGraphicsPixmapItem()
        self.mask_item.setZValue(1)
        self.addItem(self.mask_item)

        self.image_item.setPixmap(QtGui.QPixmap(image_path))
        self.setSceneRect(self.image_item.boundingRect())
        self.change_mode_to_view()

    def unload_image(self):
        self.clear()
        self.setSceneRect(QtCore.QRectF())
        self.mainwindow.polygons.clear()
        self.image_item = None
        self.mask_item = None
        self.current_graph = None

    def change_mode_to_create(self):
        if self.image_item is None:
            return
        self.mode = STATUSMode.CREATE
        if self.image_item is not None:
            self.image_item.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.mainwindow.actionPrev_image.setEnabled(False)
        self.mainwindow.actionNext_image.setEnabled(False)

        self.mainwindow.actionSegment_anything_point2.setEnabled(False)
        self.mainwindow.actionSegment_anything_point.setEnabled(False)
        self.mainwindow.actionSegment_anything_box.setEnabled(False)
        self.mainwindow.actionPolygon.setEnabled(False)
        self.mainwindow.actionBackspace.setEnabled(True)
        self.mainwindow.actionFinish.setEnabled(True)
        self.mainwindow.actionCancel.setEnabled(True)

        self.mainwindow.actionTo_top.setEnabled(False)
        self.mainwindow.actionTo_bottom.setEnabled(False)
        self.mainwindow.actionEdit.setEnabled(False)
        self.mainwindow.actionCopy.setEnabled(False)
        self.mainwindow.actionUnion.setEnabled(False)
        self.mainwindow.actionSubtract.setEnabled(False)
        self.mainwindow.actionIntersect.setEnabled(False)
        self.mainwindow.actionExclude.setEnabled(False)
        self.mainwindow.actionDelete.setEnabled(False)
        self.mainwindow.actionSave.setEnabled(False)
        self.mainwindow.actionVisible.setEnabled(True)

        self.mainwindow.annos_dock_widget.setEnabled(False)
        self.mainwindow.actionRepaint.setEnabled(False)

        self.mainwindow.modeState.setText('C')
        self.mainwindow.modeState.setStatusTip(QtCore.QCoreApplication.translate('MainWindow', 'Create mode.'))
        self.mainwindow.modeState.setStyleSheet("""
            background-color: #6CAB74;
            border-radius : 5px; 
            color: white;
        """)

    def change_mode_to_create_manual_keypoint(self):
        if self.image_item is None:
            return
        self.mode = STATUSMode.KEYPOINT
        if self.image_item is not None:
            self.image_item.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.mainwindow.actionPrev_image.setEnabled(False)
        self.mainwindow.actionNext_image.setEnabled(False)

        self.mainwindow.actionSegment_anything_point2.setEnabled(False)
        self.mainwindow.actionSegment_anything_point.setEnabled(False)
        self.mainwindow.actionSegment_anything_box.setEnabled(False)
        self.mainwindow.actionPolygon.setEnabled(False)
        self.mainwindow.actionBackspace.setEnabled(True)
        self.mainwindow.actionFinish.setEnabled(True)
        self.mainwindow.actionCancel.setEnabled(True)

        self.mainwindow.actionTo_top.setEnabled(False)
        self.mainwindow.actionTo_bottom.setEnabled(False)
        self.mainwindow.actionEdit.setEnabled(False)
        self.mainwindow.actionCopy.setEnabled(False)
        self.mainwindow.actionUnion.setEnabled(False)
        self.mainwindow.actionSubtract.setEnabled(False)
        self.mainwindow.actionIntersect.setEnabled(False)
        self.mainwindow.actionExclude.setEnabled(False)
        self.mainwindow.actionDelete.setEnabled(False)
        self.mainwindow.actionSave.setEnabled(False)
        self.mainwindow.actionVisible.setEnabled(True)

        self.mainwindow.annos_dock_widget.setEnabled(False)
        self.mainwindow.actionRepaint.setEnabled(False)

        self.mainwindow.modeState.setText('C')
        self.mainwindow.modeState.setStatusTip(QtCore.QCoreApplication.translate('MainWindow', 'Create mode.'))
        self.mainwindow.modeState.setStyleSheet("""
            background-color: #6CAB74;
            border-radius : 5px; 
            color: white;
        """)

    def change_mode_to_view(self):
        self.mode = STATUSMode.VIEW
        if self.image_item is not None:
            self.image_item.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

        self.mainwindow.actionPrev_image.setEnabled(True)
        self.mainwindow.actionNext_image.setEnabled(True)
        self.mainwindow.SeganyEnabled()
        self.mainwindow.actionPolygon.setEnabled(self.mainwindow.can_be_annotated)
        self.mainwindow.actionBackspace.setEnabled(False)
        self.mainwindow.actionFinish.setEnabled(False)
        self.mainwindow.actionCancel.setEnabled(True)

        self.mainwindow.actionTo_top.setEnabled(False)
        self.mainwindow.actionTo_bottom.setEnabled(False)
        self.mainwindow.actionEdit.setEnabled(False)
        self.mainwindow.actionCopy.setEnabled(False)
        self.mainwindow.actionUnion.setEnabled(False)
        self.mainwindow.actionSubtract.setEnabled(False)
        self.mainwindow.actionIntersect.setEnabled(False)
        self.mainwindow.actionExclude.setEnabled(False)
        self.mainwindow.actionDelete.setEnabled(False)
        self.mainwindow.actionSave.setEnabled(self.mainwindow.can_be_annotated)
        self.mainwindow.actionVisible.setEnabled(True)
        self.mainwindow.actionRepaint.setEnabled(True)

        self.mainwindow.annos_dock_widget.setEnabled(True)

        self.mainwindow.modeState.setText('V')
        self.mainwindow.modeState.setStatusTip(QtCore.QCoreApplication.translate('MainWindow', 'View mode.'))
        self.mainwindow.modeState.setStyleSheet("""
            background-color: #70AEFF;
            border-radius : 5px; 
            color: white;
        """)

    def change_mode_to_edit(self):
        self.mode = STATUSMode.EDIT
        if self.image_item is not None:
            self.image_item.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))

        self.mainwindow.actionPrev_image.setEnabled(False)
        self.mainwindow.actionNext_image.setEnabled(False)

        self.mainwindow.actionSegment_anything_point2.setEnabled(False)  # TODO
        self.mainwindow.actionSegment_anything_point.setEnabled(False)
        self.mainwindow.actionSegment_anything_box.setEnabled(False)
        self.mainwindow.actionPolygon.setEnabled(False)
        self.mainwindow.actionBackspace.setEnabled(False)
        self.mainwindow.actionFinish.setEnabled(False)
        self.mainwindow.actionCancel.setEnabled(True)

        self.mainwindow.actionTo_top.setEnabled(True)
        self.mainwindow.actionTo_bottom.setEnabled(True)
        self.mainwindow.actionEdit.setEnabled(True)
        self.mainwindow.actionCopy.setEnabled(True)
        self.mainwindow.actionUnion.setEnabled(True)
        self.mainwindow.actionSubtract.setEnabled(True)
        self.mainwindow.actionIntersect.setEnabled(True)
        self.mainwindow.actionExclude.setEnabled(True)
        self.mainwindow.actionDelete.setEnabled(True)
        self.mainwindow.actionSave.setEnabled(True)
        self.mainwindow.actionVisible.setEnabled(True)
        self.mainwindow.actionRepaint.setEnabled(False)

        self.mainwindow.modeState.setText('E')
        self.mainwindow.modeState.setStatusTip(QtCore.QCoreApplication.translate('MainWindow', 'Edit mode.'))
        self.mainwindow.modeState.setStyleSheet("""
            background-color: #51C0CF;
            border-radius : 5px; 
            color: white;
        """)

    def change_mode_to_repaint(self):
        self.mode = STATUSMode.REPAINT
        self.repaint_start_vertex = None
        self.repaint_end_vertex = None

        self.current_line = Line()  # 重绘部分，由起始点开始的线段显示
        self.addItem(self.current_line)

        if self.image_item is not None:
            self.image_item.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))

        self.mainwindow.actionPrev_image.setEnabled(False)
        self.mainwindow.actionNext_image.setEnabled(False)

        self.mainwindow.actionSegment_anything_point2.setEnabled(False)  # todo
        self.mainwindow.actionSegment_anything_point.setEnabled(False)
        self.mainwindow.actionSegment_anything_box.setEnabled(False)
        self.mainwindow.actionPolygon.setEnabled(False)
        self.mainwindow.actionBackspace.setEnabled(True)
        self.mainwindow.actionFinish.setEnabled(False)
        self.mainwindow.actionCancel.setEnabled(True)

        self.mainwindow.actionTo_top.setEnabled(False)
        self.mainwindow.actionTo_bottom.setEnabled(False)
        self.mainwindow.actionEdit.setEnabled(False)
        self.mainwindow.actionCopy.setEnabled(False)
        self.mainwindow.actionUnion.setEnabled(False)
        self.mainwindow.actionSubtract.setEnabled(False)
        self.mainwindow.actionIntersect.setEnabled(False)
        self.mainwindow.actionExclude.setEnabled(False)
        self.mainwindow.actionDelete.setEnabled(False)
        self.mainwindow.actionSave.setEnabled(True)
        self.mainwindow.actionVisible.setEnabled(False)

        self.mainwindow.modeState.setText('R')
        self.mainwindow.modeState.setStatusTip(QtCore.QCoreApplication.translate('MainWindow', 'Repaint mode.'))
        self.mainwindow.modeState.setStyleSheet("""
            background-color: #CF84CF;
            border-radius : 5px; 
            color: white;
        """)

    def change_click_to_positive(self):
        self.click = CLICKMode.POSITIVE

    def change_click_to_negative(self):
        self.click = CLICKMode.NEGATIVE

    def change_contour_mode_to_save_all(self):
        self.contour_mode = CONTOURMode.SAVE_ALL

    def change_contour_mode_to_save_max_only(self):
        self.contour_mode = CONTOURMode.SAVE_MAX_ONLY

    def change_contour_mode_to_save_external(self):
        self.contour_mode = CONTOURMode.SAVE_EXTERNAL

    def start_segment_anything(self):
        self.draw_mode = DRAWMode.SEGMENTANYTHING
        self.start_draw()

    def start_manual_keypoint(self):  # 自定义keypoint的人工标注
        self.draw_mode = DRAWMode.MANUALKEYPOINT
        # self.start_draw()
        # 只有view模式时，才能切换create模式
        if self.mode != STATUSMode.VIEW:
            return
        # 否则，切换到绘图模式
        self.change_mode_to_create_manual_keypoint()  # 切换为keypoint
        if self.mainwindow.cfg['software']['create_mode_invisible_polygon']:
            self.mainwindow.set_labels_visible(False)

        # 绘图模式
        if self.mode == STATUSMode.KEYPOINT:
            self.current_graph = Polygon()
            self.addItem(self.current_graph)

    def start_segment_anything_box(self):
        self.draw_mode = DRAWMode.SEGMENTANYTHING_BOX
        self.start_draw()

    def start_draw_polygon(self):
        self.draw_mode = DRAWMode.POLYGON
        self.start_draw()

    def start_draw(self):
        # 只有view模式时，才能切换create模式
        if self.mode != STATUSMode.VIEW:
            return
        # 否则，切换到绘图模式
        self.change_mode_to_create()
        if self.mainwindow.cfg['software']['create_mode_invisible_polygon']:
            self.mainwindow.set_labels_visible(False)

        # 绘图模式
        if self.mode == STATUSMode.CREATE:
            self.current_graph = Polygon()
            self.addItem(self.current_graph)

    def finish_draw(self):

        if self.current_graph is None:
            return

        category = self.mainwindow.current_category
        action = self.mainwindow.current_action
        group = self.mainwindow.current_group
        is_crowd = False
        note = ''

        if self.draw_mode == DRAWMode.SEGMENTANYTHING or self.draw_mode == DRAWMode.SEGMENTANYTHING_BOX or self.draw_mode == DRAWMode.MANUALKEYPOINT:
            # mask to polygon
            # --------------
            if self.masks is not None:
                masks = self.masks
                masks = masks.astype('uint8') * 255
                h, w = masks.shape[-2:]
                masks = masks.reshape(h, w)  # TODO 这里保存为objects是单个保存的，改为多个mask循环保存

                if self.draw_mode == DRAWMode.MANUALKEYPOINT:  # TODO 当为点标注时，应该是保存所有的边界
                    # TODO 当为点标注时，应该是保存所有的边界
                    contours, hierarchy = cv2.findContours(masks, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
                elif self.contour_mode == CONTOURMode.SAVE_ALL:
                    # 当保留所有轮廓时，检测所有轮廓，并建立二层等级关系
                    contours, hierarchy = cv2.findContours(masks, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
                else:
                    # 当只保留外轮廓或单个mask时，只检测外轮廓
                    contours, hierarchy = cv2.findContours(masks, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

                if self.contour_mode == CONTOURMode.SAVE_MAX_ONLY:
                    largest_contour = max(contours, key=cv2.contourArea)  # 只保留面积最大的轮廓
                    contours = [largest_contour]

                for index, contour in enumerate(contours):
                    # polydp
                    if self.mainwindow.cfg['software']['use_polydp']:
                        epsilon_factor = 0.001
                        epsilon = epsilon_factor * cv2.arcLength(contour, True)
                        contour = cv2.approxPolyDP(contour, epsilon, True)

                    if self.current_graph is None:
                        self.current_graph = Polygon()
                        self.addItem(self.current_graph)

                    if len(contour) < 3:
                        continue
                    for point in contour:
                        x, y = point[0]
                        x = max(0.1, x)
                        y = max(0.1, y)
                        self.current_graph.addPoint(QtCore.QPointF(x, y))
                    center = [int(sum(point[0][0] for point in contour) / len(contour)),
                              int(sum(point[0][1] for point in contour) / len(contour))]
                    if self.contour_mode == CONTOURMode.SAVE_ALL and hierarchy[0][index][3] != -1:
                        # 保存所有轮廓，且当前轮廓为子轮廓，则自轮廓类别设置为背景
                        category = '__background__'
                        action = '__background__'
                        group = 0
                    else:
                        category = self.mainwindow.current_category
                        action = self.mainwindow.current_action
                        group = self.mainwindow.current_group

                    self.current_graph.set_drawed(category,
                                                  group,
                                                  is_crowd,
                                                  note,
                                                  QtGui.QColor(self.mainwindow.category_color_dict[category]),
                                                  self.top_layer,
                                                  center=center, action=action)

                    # 添加新polygon
                    self.mainwindow.polygons.append(self.current_graph)
                    self.mainwindow.annos_dock_widget.listwidget_add_polygon(self.current_graph)
                    # 设置为最高图层
                    self.current_graph.setZValue(len(self.mainwindow.polygons))
                    for vertex in self.current_graph.vertexs:
                        vertex.setZValue(len(self.mainwindow.polygons))
                    self.current_graph = None
                # self.current_graph = None
                if self.mainwindow.group_select_mode == 'auto':
                    self.mainwindow.current_group += 1
                    self.mainwindow.categories_dock_widget.lineEdit_currentGroup.setText(
                        str(self.mainwindow.current_group))
                self.masks = None
        elif self.draw_mode == DRAWMode.POLYGON:
            if len(self.current_graph.points) < 1:
                return

            # 移除鼠标移动点
            self.current_graph.removePoint(len(self.current_graph.points) - 1)

            # 单点，删除
            if len(self.current_graph.points) < 2:
                self.current_graph.delete()
                self.removeItem(self.current_graph)

                self.change_mode_to_view()
                if self.mainwindow.cfg['software']['create_mode_invisible_polygon']:
                    self.mainwindow.set_labels_visible(True)

                return

            # 两点，默认矩形
            if len(self.current_graph.points) == 2:
                first_point = self.current_graph.points[0]
                last_point = self.current_graph.points[-1]
                self.current_graph.removePoint(len(self.current_graph.points) - 1)
                self.current_graph.addPoint(QtCore.QPointF(first_point.x(), last_point.y()))
                self.current_graph.addPoint(last_point)
                self.current_graph.addPoint(QtCore.QPointF(last_point.x(), first_point.y()))

            # 设置polygon 属性
            self.current_graph.set_drawed(category,
                                          group,
                                          is_crowd,
                                          note,
                                          QtGui.QColor(self.mainwindow.category_color_dict[category]),
                                          self.top_layer)
            if self.mainwindow.group_select_mode == 'auto':
                self.mainwindow.current_group += 1
                self.mainwindow.categories_dock_widget.lineEdit_currentGroup.setText(str(self.mainwindow.current_group))
            # 添加新polygon
            self.mainwindow.polygons.append(self.current_graph)
            self.mainwindow.annos_dock_widget.listwidget_add_polygon(self.current_graph)
            # 设置为最高图层
            self.current_graph.setZValue(len(self.mainwindow.polygons))
            for vertex in self.current_graph.vertexs:
                vertex.setZValue(len(self.mainwindow.polygons))
        # 选择类别
        # self.mainwindow.category_choice_widget.load_cfg()
        # self.mainwindow.category_choice_widget.show()

        self.current_graph = None

        if self.current_sam_rect is not None:
            self.current_sam_rect.delete()
            self.removeItem(self.current_sam_rect)
            self.current_sam_rect = None

        self.change_mode_to_view()
        if self.mainwindow.cfg['software']['create_mode_invisible_polygon']:
            self.mainwindow.set_labels_visible(True)

        # mask清空
        self.click_points.clear()
        self.click_points_mode.clear()
        for prompt_point in self.prompt_points:
            try:
                self.removeItem(prompt_point)
            finally:
                del prompt_point
        self.prompt_points.clear()
        self.update_mask()

    def cancel_draw(self):
        if self.mode == STATUSMode.CREATE:
            if self.current_graph is not None:
                self.current_graph.delete()  # 清除所有路径
                self.removeItem(self.current_graph)
                self.current_graph = None
        if self.mode == STATUSMode.REPAINT:
            if self.current_line is not None:
                self.current_line.delete()
                self.removeItem(self.current_line)
                self.current_line = None
        if self.mode == STATUSMode.EDIT:
            for item in self.selectedItems():
                item.setSelected(False)

        if self.current_sam_rect is not None:
            self.current_sam_rect.delete()
            self.removeItem(self.current_sam_rect)
            self.current_sam_rect = None

        self.change_mode_to_view()
        if self.mainwindow.cfg['software']['create_mode_invisible_polygon']:
            self.mainwindow.set_labels_visible(True)

        self.click_points.clear()
        self.click_points_mode.clear()
        for prompt_point in self.prompt_points:
            try:
                self.removeItem(prompt_point)
            finally:
                del prompt_point
        self.prompt_points.clear()

        self.update_mask()
        self.update_mask_manual_key_point()

    def delete_selected_graph(self):
        deleted_layer = None
        for item in self.selectedItems():
            if isinstance(item, Polygon) and (item in self.mainwindow.polygons):
                if item in self.selected_polygons_list:
                    self.selected_polygons_list.remove(item)
                self.mainwindow.polygons.remove(item)
                self.mainwindow.annos_dock_widget.listwidget_remove_polygon(item)
                item.delete()
                self.removeItem(item)
                deleted_layer = item.zValue()
                del item
            elif isinstance(item, Vertex):
                polygon = item.polygon
                if polygon.vertexs:
                    index = polygon.vertexs.index(item)
                    item.polygon.removePoint(index)
                else:
                    self.removeItem(item)
                    del item
                # 如果剩余顶点少于三个，删除多边形
                if len(polygon.vertexs) < 3:
                    if polygon in self.mainwindow.polygons:
                        self.mainwindow.polygons.remove(polygon)
                        self.mainwindow.annos_dock_widget.listwidget_remove_polygon(polygon)
                        polygon.delete()
                    if polygon in self.items():
                        self.removeItem(polygon)
                    deleted_layer = polygon.zValue()
                    del polygon

        if deleted_layer is not None:
            for p in self.mainwindow.polygons:
                if p.zValue() > deleted_layer:
                    p.setZValue(p.zValue() - 1)

    def edit_polygon(self):
        selectd_items = self.selectedItems()
        selectd_items = [item for item in selectd_items if isinstance(item, Polygon)]
        if len(selectd_items) < 1:
            return
        item = selectd_items[0]
        if not item:
            return
        self.mainwindow.category_edit_widget.polygon = item
        self.mainwindow.category_edit_widget.load_cfg()
        self.mainwindow.category_edit_widget.show()

    def move_polygon_to_top(self):
        selectd_items = self.selectedItems()
        selectd_items = [item for item in selectd_items if isinstance(item, Polygon)]
        if len(selectd_items) < 1:
            return
        current_polygon = selectd_items[0]
        max_layer = len(self.mainwindow.polygons)

        current_layer = current_polygon.zValue()
        for p in self.mainwindow.polygons:
            if p.zValue() > current_layer:
                p.setZValue(p.zValue() - 1)

        current_polygon.setZValue(max_layer)
        for vertex in current_polygon.vertexs:
            vertex.setZValue(max_layer)
        self.mainwindow.set_saved_state(False)

    def move_polygon_to_bottom(self):
        selectd_items = self.selectedItems()
        selectd_items = [item for item in selectd_items if isinstance(item, Polygon)]

        if len(selectd_items) < 1:
            return
        current_polygon = selectd_items[0]

        if current_polygon is not None:
            current_layer = current_polygon.zValue()

            for p in self.mainwindow.polygons:
                if p.zValue() < current_layer:
                    p.setZValue(p.zValue() + 1)

            current_polygon.setZValue(1)
            for vertex in current_polygon.vertexs:
                vertex.setZValue(1)
        self.mainwindow.set_saved_state(False)

    def copy_item(self):
        for item in self.selectedItems():
            if isinstance(item, Polygon):
                index = self.mainwindow.polygons.index(item)
                if self.current_graph is None:
                    self.current_graph = Polygon()
                    self.addItem(self.current_graph)

                for point in item.vertexs:
                    x, y = point.x(), point.y()
                    self.current_graph.addPoint(QtCore.QPointF(x, y))

                self.current_graph.set_drawed(item.category, item.group, item.iscrowd, item.note, item.color,
                                              item.zValue())
                self.mainwindow.polygons.insert(index, self.current_graph)
                self.mainwindow.annos_dock_widget.listwidget_add_polygon(self.current_graph)
                item.setSelected(False)
                self.current_graph.setSelected(True)
                self.current_graph = None
            elif isinstance(item, Vertex):
                polygon = item.polygon
                index = polygon.vertexs.index(item)
                point = QtCore.QPointF(item.x(), item.y())

                polygon.points.insert(index, point)
                vertex = Vertex(self, polygon.color, self.mainwindow.cfg['software']['vertex_size'] * 2)
                self.addItem(vertex)
                polygon.vertexs.insert(index, vertex)
                vertex.setPos(point)

    # 感谢[XieDeWu](https://github.com/XieDeWu)提的有关交、并、差、异或的[建议](https://github.com/yatengLG/ISAT_with_segment_anything/issues/167)。
    def polygons_union(self):
        if len(self.selected_polygons_list) == 2:
            index = self.mainwindow.polygons.index(self.selected_polygons_list[0])

            category = self.selected_polygons_list[0].category
            group = self.selected_polygons_list[0].group
            iscrowd = self.selected_polygons_list[0].iscrowd
            note = self.selected_polygons_list[0].note
            layer = self.selected_polygons_list[0].zValue()
            color = self.selected_polygons_list[0].color

            try:
                polygon1_shapely = shapely.Polygon(
                    [(point.x(), point.y()) for point in self.selected_polygons_list[0].vertexs])
                polygon2_shapely = shapely.Polygon(
                    [(point.x(), point.y()) for point in self.selected_polygons_list[1].vertexs])
                return_shapely = polygon1_shapely.union(polygon2_shapely)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.mainwindow, 'Warning', 'Polygon warning: {}'.format(e))
                return

            if isinstance(return_shapely, shapely.Polygon):

                # 创建新多边形
                if self.current_graph is None:
                    self.current_graph = Polygon()
                    self.addItem(self.current_graph)

                for point in return_shapely.exterior.coords:
                    x, y = point[0], point[1]
                    self.current_graph.addPoint(QtCore.QPointF(x, y))

                self.current_graph.set_drawed(category, group, iscrowd, note, color, layer)
                self.mainwindow.polygons.insert(index, self.current_graph)
                self.current_graph = None

                # 删除旧的多边形
                for polygon_item in self.selected_polygons_list:
                    self.mainwindow.polygons.remove(polygon_item)
                    polygon_item.delete()
                    self.removeItem(polygon_item)
                    del polygon_item
                self.selected_polygons_list.clear()

                self.mainwindow.annos_dock_widget.update_listwidget()

    def polygons_difference(self):
        if len(self.selected_polygons_list) == 2:
            index = self.mainwindow.polygons.index(self.selected_polygons_list[0])

            category = self.selected_polygons_list[0].category
            group = self.selected_polygons_list[0].group
            iscrowd = self.selected_polygons_list[0].iscrowd
            note = self.selected_polygons_list[0].note
            layer = self.selected_polygons_list[0].zValue()
            color = self.selected_polygons_list[0].color
            try:
                polygon1_shapely = shapely.Polygon(
                    [(point.x(), point.y()) for point in self.selected_polygons_list[0].vertexs])
                polygon2_shapely = shapely.Polygon(
                    [(point.x(), point.y()) for point in self.selected_polygons_list[1].vertexs])
                return_shapely = polygon1_shapely.difference(polygon2_shapely)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.mainwindow, 'Warning', 'Polygon warning: {}'.format(e))
                return

            if isinstance(return_shapely, shapely.Polygon):
                if self.current_graph is None:
                    self.current_graph = Polygon()
                    self.addItem(self.current_graph)

                for point in return_shapely.exterior.coords:
                    x, y = point[0], point[1]
                    self.current_graph.addPoint(QtCore.QPointF(x, y))

                self.current_graph.set_drawed(category, group, iscrowd, note, color, layer)
                self.mainwindow.polygons.insert(index, self.current_graph)
                self.current_graph = None

            elif isinstance(return_shapely, shapely.MultiPolygon):
                for return_shapely_polygon in return_shapely.geoms:
                    if self.current_graph is None:
                        self.current_graph = Polygon()
                        self.addItem(self.current_graph)

                    for point in return_shapely_polygon.exterior.coords:
                        x, y = point[0], point[1]
                        self.current_graph.addPoint(QtCore.QPointF(x, y))

                    self.current_graph.set_drawed(category, group, iscrowd, note, color, layer)
                    self.mainwindow.polygons.insert(index, self.current_graph)
                    self.current_graph = None

            # 删除旧的多边形
            for polygon_item in self.selected_polygons_list:
                self.mainwindow.polygons.remove(polygon_item)
                polygon_item.delete()
                self.removeItem(polygon_item)
                del polygon_item
            self.selected_polygons_list.clear()

            self.mainwindow.annos_dock_widget.update_listwidget()

    def polygons_intersection(self):
        if len(self.selected_polygons_list) == 2:
            index = self.mainwindow.polygons.index(self.selected_polygons_list[0])

            category = self.selected_polygons_list[0].category
            group = self.selected_polygons_list[0].group
            iscrowd = self.selected_polygons_list[0].iscrowd
            note = self.selected_polygons_list[0].note
            layer = self.selected_polygons_list[0].zValue()
            color = self.selected_polygons_list[0].color
            try:
                polygon1_shapely = shapely.Polygon(
                    [(point.x(), point.y()) for point in self.selected_polygons_list[0].vertexs])
                polygon2_shapely = shapely.Polygon(
                    [(point.x(), point.y()) for point in self.selected_polygons_list[1].vertexs])
                return_shapely = polygon1_shapely.intersection(polygon2_shapely)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.mainwindow, 'Warning', 'Polygon warning: {}'.format(e))
                return

            if isinstance(return_shapely, shapely.Polygon):
                if self.current_graph is None:
                    self.current_graph = Polygon()
                    self.addItem(self.current_graph)

                for point in return_shapely.exterior.coords:
                    x, y = point[0], point[1]
                    self.current_graph.addPoint(QtCore.QPointF(x, y))

                self.current_graph.set_drawed(category, group, iscrowd, note, color, layer)
                self.mainwindow.polygons.insert(index, self.current_graph)
                self.current_graph = None

            elif isinstance(return_shapely, shapely.MultiPolygon):
                for return_shapely_polygon in return_shapely.geoms:
                    if self.current_graph is None:
                        self.current_graph = Polygon()
                        self.addItem(self.current_graph)

                    for point in return_shapely_polygon.exterior.coords:
                        x, y = point[0], point[1]
                        self.current_graph.addPoint(QtCore.QPointF(x, y))

                    self.current_graph.set_drawed(category, group, iscrowd, note, color, layer)
                    self.mainwindow.polygons.insert(index, self.current_graph)
                    self.current_graph = None

            # 删除旧的多边形
            for polygon_item in self.selected_polygons_list:
                self.mainwindow.polygons.remove(polygon_item)
                polygon_item.delete()
                self.removeItem(polygon_item)
                del polygon_item
            self.selected_polygons_list.clear()

            self.mainwindow.annos_dock_widget.update_listwidget()

    def polygons_symmetric_difference(self):
        if len(self.selected_polygons_list) == 2:
            index = self.mainwindow.polygons.index(self.selected_polygons_list[0])

            category = self.selected_polygons_list[0].category
            group = self.selected_polygons_list[0].group
            iscrowd = self.selected_polygons_list[0].iscrowd
            note = self.selected_polygons_list[0].note
            layer = self.selected_polygons_list[0].zValue()
            color = self.selected_polygons_list[0].color
            try:
                polygon1_shapely = shapely.Polygon(
                    [(point.x(), point.y()) for point in self.selected_polygons_list[0].vertexs])
                polygon2_shapely = shapely.Polygon(
                    [(point.x(), point.y()) for point in self.selected_polygons_list[1].vertexs])
                return_shapely = polygon1_shapely.symmetric_difference(polygon2_shapely)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.mainwindow, 'Warning', 'Polygon warning: {}'.format(e))
                return

            if isinstance(return_shapely, shapely.Polygon):
                if self.current_graph is None:
                    self.current_graph = Polygon()
                    self.addItem(self.current_graph)

                for point in return_shapely.exterior.coords:
                    x, y = point[0], point[1]
                    self.current_graph.addPoint(QtCore.QPointF(x, y))

                self.current_graph.set_drawed(category, group, iscrowd, note, color, layer)
                self.mainwindow.polygons.insert(index, self.current_graph)
                self.current_graph = None

            elif isinstance(return_shapely, shapely.MultiPolygon):
                for return_shapely_polygon in return_shapely.geoms:
                    if self.current_graph is None:
                        self.current_graph = Polygon()
                        self.addItem(self.current_graph)

                    for point in return_shapely_polygon.exterior.coords:
                        x, y = point[0], point[1]
                        self.current_graph.addPoint(QtCore.QPointF(x, y))

                    self.current_graph.set_drawed(category, group, iscrowd, note, color, layer)
                    self.mainwindow.polygons.insert(index, self.current_graph)
                    self.current_graph = None

            # 删除旧的多边形
            for polygon_item in self.selected_polygons_list:
                self.mainwindow.polygons.remove(polygon_item)
                polygon_item.delete()
                self.removeItem(polygon_item)
                del polygon_item
            self.selected_polygons_list.clear()

            self.mainwindow.annos_dock_widget.update_listwidget()

    def mousePressEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        sceneX, sceneY = event.scenePos().x(), event.scenePos().y()
        sceneX = 0 if sceneX < 0 else sceneX
        sceneX = self.width() - 1 if sceneX > self.width() - 1 else sceneX
        sceneY = 0 if sceneY < 0 else sceneY
        sceneY = self.height() - 1 if sceneY > self.height() - 1 else sceneY

        if self.mode == STATUSMode.KEYPOINT:  # mkp
            # 拖动鼠标描点
            self.last_draw_time = time.time()
            self.pressd = True

            if event.button() == QtCore.Qt.MouseButton.LeftButton:  # 鼠标左键事件
                if self.draw_mode == DRAWMode.MANUALKEYPOINT:
                    self.click_points.append([sceneX, sceneY])  # 添加鼠标点位
                    self.click_points_mode.append(1)
                    prompt_point = PromptPoint(QtCore.QPointF(sceneX, sceneY), 1)
                    prompt_point.setVisible(self.mainwindow.cfg['software']['show_prompt'])
                    self.prompt_points.append(prompt_point)
                    self.addItem(prompt_point)
            if self.draw_mode == DRAWMode.MANUALKEYPOINT:
                self.update_mask_manual_key_point()

        if self.mode == STATUSMode.CREATE:
            # 拖动鼠标描点
            self.last_draw_time = time.time()
            self.pressd = True

            if event.button() == QtCore.Qt.MouseButton.LeftButton:  # 鼠标左键事件
                if self.draw_mode == DRAWMode.SEGMENTANYTHING:
                    self.click_points.append([sceneX, sceneY])  # 添加鼠标点位
                    self.click_points_mode.append(1)
                    prompt_point = PromptPoint(QtCore.QPointF(sceneX, sceneY), 1)
                    prompt_point.setVisible(self.mainwindow.cfg['software']['show_prompt'])
                    self.prompt_points.append(prompt_point)
                    self.addItem(prompt_point)

                elif self.draw_mode == DRAWMode.SEGMENTANYTHING_BOX:  # sam 矩形框提示
                    if self.current_sam_rect is None:
                        self.current_sam_rect = Rect()
                        self.current_sam_rect.setZValue(2)
                        self.addItem(self.current_sam_rect)
                        self.current_sam_rect.addPoint(QtCore.QPointF(sceneX, sceneY))
                        self.current_sam_rect.addPoint(QtCore.QPointF(sceneX, sceneY))

                elif self.draw_mode == DRAWMode.POLYGON:
                    # 移除随鼠标移动的点
                    self.current_graph.removePoint(len(self.current_graph.points) - 1)
                    # 添加当前点
                    self.current_graph.addPoint(QtCore.QPointF(sceneX, sceneY))
                    # 添加随鼠标移动的点
                    self.current_graph.addPoint(QtCore.QPointF(sceneX, sceneY))
                else:
                    raise ValueError('The draw mode named {} not supported.')
            if event.button() == QtCore.Qt.MouseButton.RightButton:
                if self.draw_mode == DRAWMode.SEGMENTANYTHING:
                    self.click_points.append([sceneX, sceneY])
                    self.click_points_mode.append(0)
                    prompt_point = PromptPoint(QtCore.QPointF(sceneX, sceneY), 0)
                    prompt_point.setVisible(self.mainwindow.cfg['software']['show_prompt'])
                    self.prompt_points.append(prompt_point)
                    self.addItem(prompt_point)

                elif self.draw_mode == DRAWMode.POLYGON:
                    pass
                elif self.draw_mode == DRAWMode.SEGMENTANYTHING_BOX:
                    try:
                        self.finish_draw()
                    except:
                        pass
                else:
                    raise ValueError('The draw mode named {} not supported.')
            if self.draw_mode == DRAWMode.SEGMENTANYTHING:
                self.update_mask()

        if self.mode == STATUSMode.REPAINT:
            # 拖动鼠标描点
            self.last_draw_time = time.time()
            self.pressd = True

            if self.repaint_start_vertex is None:
                # 开始repaint
                if self.hovered_vertex is not None:
                    self.repaint_start_vertex = self.hovered_vertex
                    self.current_line.addPoint(self.repaint_start_vertex.pos())  # 添加当前点
                    self.current_line.addPoint(self.repaint_start_vertex.pos())  # 添加随鼠标移动的点
            else:
                # 结束repaint
                if self.hovered_vertex is not None and self.hovered_vertex.polygon == self.repaint_start_vertex.polygon:
                    self.repaint_end_vertex = self.hovered_vertex

                    # 移除随鼠标移动的点
                    self.current_line.removePoint(len(self.current_line.points) - 1)
                    # 添加结束点
                    self.current_line.addPoint(self.repaint_end_vertex.pos())

                    repaint_polygon = self.repaint_start_vertex.polygon
                    repaint_start_index = repaint_polygon.vertexs.index(self.repaint_start_vertex)
                    repaint_end_index = repaint_polygon.vertexs.index(self.repaint_end_vertex)
                    replace_points = [QtCore.QPointF(vertex.pos()) for vertex in self.current_line.vertexs]

                    if repaint_start_index > repaint_end_index:
                        record = repaint_start_index
                        repaint_start_index = repaint_end_index
                        repaint_end_index = record
                        replace_points = replace_points[::-1]

                    # 这里永远替换数量最少的顶点
                    distance = abs(repaint_end_index - repaint_start_index)
                    if len(repaint_polygon.vertexs) - distance < distance:
                        # 替换两端的点
                        points = ([vertex.pos() for vertex in
                                   repaint_polygon.vertexs[repaint_start_index + 1: repaint_end_index]]
                                  + replace_points[::-1])
                    else:
                        # 替换中间的点
                        points = ([vertex.pos() for vertex in repaint_polygon.vertexs[:repaint_start_index]] +
                                  replace_points +
                                  [vertex.pos() for vertex in repaint_polygon.vertexs[repaint_end_index + 1:]])
                    repaint_polygon.delete()
                    for point in points:
                        repaint_polygon.addPoint(point)
                    repaint_polygon.redraw()

                    self.current_line.delete()  # 清除所有路径
                    self.removeItem(self.current_line)

                    self.repaint_start_vertex = None
                    self.repaint_end_vertex = None
                    self.change_mode_to_view()
                else:
                    # 移除随鼠标移动的点
                    self.current_line.removePoint(len(self.current_line.points) - 1)
                    # 添加当前点
                    self.current_line.addPoint(QtCore.QPointF(sceneX, sceneY))
                    # 添加随鼠标移动的点
                    self.current_line.addPoint(QtCore.QPointF(sceneX, sceneY))

        super(AnnotationScene, self).mousePressEvent(event)

    # 拖动鼠标描点
    def mouseReleaseEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        self.pressd = False
        super(AnnotationScene, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        # 辅助线
        if self.guide_line_x is not None and self.guide_line_y is not None:
            if self.guide_line_x in self.items():
                self.removeItem(self.guide_line_x)

            if self.guide_line_y in self.items():
                self.removeItem(self.guide_line_y)

            self.guide_line_x = None
            self.guide_line_y = None

        pos = event.scenePos()
        if pos.x() < 0: pos.setX(0)
        if pos.x() > self.width() - 1: pos.setX(self.width() - 1)
        if pos.y() < 0: pos.setY(0)
        if pos.y() > self.height() - 1: pos.setY(self.height() - 1)
        # 限制在图片范围内

        if self.mode == STATUSMode.CREATE:
            if self.draw_mode == DRAWMode.POLYGON:
                # 随鼠标位置实时更新多边形
                self.current_graph.movePoint(len(self.current_graph.points) - 1, pos)
            if self.draw_mode == DRAWMode.SEGMENTANYTHING_BOX:
                if self.current_sam_rect is not None:
                    self.current_sam_rect.movePoint(len(self.current_sam_rect.points) - 1, pos)
                    self.update_mask()

        if self.mode == STATUSMode.KEYPOINT:
            if self.draw_mode == DRAWMode.POLYGON:
                # 随鼠标位置实时更新多边形
                self.current_graph.movePoint(len(self.current_graph.points) - 1, pos)
            if self.draw_mode == DRAWMode.MANUALKEYPOINT:
                pass  # TODO 改为多点后不需要每次都更新，只有在点击时更新
                # if len(self.click_points)>0:
                #     self.update_mask_manual_key_point()

        if self.mode == STATUSMode.REPAINT:
            self.current_line.movePoint(len(self.current_line.points) - 1, pos)

        # 辅助线
        if self.guide_line_x is None and self.width() > 0 and self.height() > 0:
            self.guide_line_x = QtWidgets.QGraphicsLineItem(QtCore.QLineF(pos.x(), 0, pos.x(), self.height()))
            self.guide_line_x.setZValue(1)
            self.addItem(self.guide_line_x)
        if self.guide_line_y is None and self.width() > 0 and self.height() > 0:
            self.guide_line_y = QtWidgets.QGraphicsLineItem(QtCore.QLineF(0, pos.y(), self.width(), pos.y()))
            self.guide_line_y.setZValue(1)
            self.addItem(self.guide_line_y)

        # 状态栏,显示当前坐标
        if self.image_data is not None:
            x, y = round(pos.x()), round(pos.y())
            self.mainwindow.labelCoord.setText('xy: ({:>4d},{:>4d})'.format(x, y))

            data = self.image_data[y][x]
            if self.image_data.ndim == 2:
                self.mainwindow.labelData.setText('pix: [{:^3d}]'.format(data))
            elif self.image_data.ndim == 3:
                if len(data) == 3:
                    self.mainwindow.labelData.setText('rgb: [{:>3d},{:>3d},{:>3d}]'.format(data[0], data[1], data[2]))
                else:
                    self.mainwindow.labelData.setText('pix: [{}]'.format(data))

        # 拖动鼠标描点
        if self.pressd:  # 拖动鼠标
            current_time = time.time()
            if self.last_draw_time is not None and current_time - self.last_draw_time < self.draw_interval:
                return  # 时间小于给定值不画点
            self.last_draw_time = current_time
            sceneX, sceneY = event.scenePos().x(), event.scenePos().y()
            sceneX = 0 if sceneX < 0 else sceneX
            sceneX = self.width() - 1 if sceneX > self.width() - 1 else sceneX
            sceneY = 0 if sceneY < 0 else sceneY
            sceneY = self.height() - 1 if sceneY > self.height() - 1 else sceneY

            if self.current_graph is not None:
                if self.draw_mode == DRAWMode.POLYGON:
                    # 移除随鼠标移动的点
                    self.current_graph.removePoint(len(self.current_graph.points) - 1)
                    # 添加当前点
                    self.current_graph.addPoint(QtCore.QPointF(sceneX, sceneY))
                    # 添加随鼠标移动的点
                    self.current_graph.addPoint(QtCore.QPointF(sceneX, sceneY))

            if self.mode == STATUSMode.REPAINT and self.current_line is not None:
                # 移除随鼠标移动的点
                self.current_line.removePoint(len(self.current_line.points) - 1)
                # 添加当前点
                self.current_line.addPoint(QtCore.QPointF(sceneX, sceneY))
                # 添加随鼠标移动的点
                self.current_line.addPoint(QtCore.QPointF(sceneX, sceneY))

        super(AnnotationScene, self).mouseMoveEvent(event)

    def update_mask(self):
        if not self.mainwindow.use_segment_anything:
            return
        if self.image_data is None:
            return
        if not (self.image_data.ndim == 3 and self.image_data.shape[-1] == 3):
            return

        if len(self.click_points) > 0 and len(self.click_points_mode) > 0:
            masks = self.mainwindow.segany.predict_with_point_prompt(self.click_points,
                                                                     self.click_points_mode)  # (1,480,640)
            self.masks = masks
            color = np.array([0, 0, 255])  # 蓝色
            h, w = masks.shape[-2:]
            mask_image = masks.reshape(h, w, 1) * color.reshape(1, 1, -1)
            mask_image = mask_image.astype("uint8")
            mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2RGB)
            mask_image = cv2.addWeighted(self.image_data, self.mask_alpha, mask_image, 1, 0)
        elif self.current_sam_rect is not None:
            point1 = self.current_sam_rect.points[0]
            point2 = self.current_sam_rect.points[1]
            box = np.array([min(point1.x(), point2.x()),
                            min(point1.y(), point2.y()),
                            max(point1.x(), point2.x()),
                            max(point1.y(), point2.y()),
                            ])
            masks = self.mainwindow.segany.predict_with_box_prompt(box)

            self.masks = masks
            color = np.array([0, 0, 255])
            h, w = masks.shape[-2:]
            mask_image = masks.reshape(h, w, 1) * color.reshape(1, 1, -1)
            mask_image = mask_image.astype("uint8")
            mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2RGB)
            # 这里通过调整原始图像的权重self.mask_alpha，来调整mask的明显程度。
            mask_image = cv2.addWeighted(self.image_data, self.mask_alpha, mask_image, 1, 0)
        else:
            mask_image = np.zeros(self.image_data.shape, dtype=np.uint8)
            mask_image = cv2.addWeighted(self.image_data, 1, mask_image, 0, 0)
        mask_image = QtGui.QImage(mask_image[:], mask_image.shape[1], mask_image.shape[0], mask_image.shape[1] * 3,
                                  QtGui.QImage.Format_RGB888)  # 将一个OpenCV图像（通常是一个NumPy数组）转换为Qt的QImage，然后再转换为QPixmap。这个过程通常用于在基于Qt的应用程序中显示OpenCV处理过的图像
        mask_pixmap = QtGui.QPixmap(mask_image)
        if self.mask_item is not None:
            self.mask_item.setPixmap(mask_pixmap)

    def create_circular_mask(self, centers, image_shape=(480, 640), radius=10):
        """
        创建一个以centers坐标为圆心、radius为半径的圆形掩膜。

        参数:
        - centers: 圆心坐标 [(x1, y1), (x2, y2), ...] 的列表。
        - image_shape: 目标掩膜的大小，默认是(480, 640)。
        - radius: 圆形区域的半径，默认是10。

        返回:
        - 形状为 (1, 480, 640) 的布尔类型 ndarray，圆形区域内为 True，其余部分为 False。
        """
        mask = np.zeros(image_shape, dtype=np.uint8)
        for center in centers:
            center = (int(center[0]), int(center[1]))
            cv2.circle(mask, center, radius, color=1, thickness=-1)
        bool_mask = mask.astype(bool)
        return bool_mask[np.newaxis, :, :]

    def update_mask_manual_key_point(self):
        if not self.mainwindow.use_manual_keypoint:
            return
        if self.image_data is None:
            return
        if not (self.image_data.ndim == 3 and self.image_data.shape[-1] == 3):
            return

        if len(self.click_points) > 0 and len(self.click_points_mode) > 0:
            masks = self.create_circular_mask(self.click_points, self.image_data.shape[:2])
            # self.click_points = []  # TODO 这里为什么直接清空，正常的seg是什么时候清空的？1、finish_draw（对应对号图标键？） 2、cancel_draw 两个函数
            # self.click_points_mode = []  # TODO 点标注模式下需要连续多点标注，查看在两个函数使用得时候，应该不清空
            self.masks = masks  # TODO 一个mask多个点位
            # color = np.array([255, 0, 0])  # 红色
            color = np.array([255, 0, 255])  # 红色
            h, w = masks.shape[-2:]
            mask_image = masks.reshape(h, w, 1) * color.reshape(1, 1, -1)
            mask_image = mask_image.astype("uint8")
            mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2RGB)
            mask_image = cv2.addWeighted(self.image_data, self.mask_alpha, mask_image, 1, 0)
        else:
            mask_image = np.zeros(self.image_data.shape, dtype=np.uint8)
            mask_image = cv2.addWeighted(self.image_data, 1, mask_image, 0, 0)

        mask_image = QtGui.QImage(mask_image[:], mask_image.shape[1], mask_image.shape[0], mask_image.shape[1] * 3,
                                  QtGui.QImage.Format_RGB888)
        mask_pixmap = QtGui.QPixmap(mask_image)
        if self.mask_item is not None:
            self.mask_item.setPixmap(mask_pixmap)

    def backspace(self):
        if self.mode == STATUSMode.CREATE:
            # 返回上一步操作
            if self.draw_mode == DRAWMode.SEGMENTANYTHING:
                if len(self.click_points) > 0:
                    self.click_points.pop()
                if len(self.click_points_mode) > 0:
                    self.click_points_mode.pop()
                if len(self.prompt_points) > 0:
                    prompt_point = self.prompt_points.pop()
                    self.removeItem(prompt_point)
                    del prompt_point
                self.update_mask()
            elif self.draw_mode == DRAWMode.POLYGON:
                if len(self.current_graph.points) < 2:
                    return
                # 移除随鼠标移动的点
                self.current_graph.removePoint(len(self.current_graph.points) - 2)

        if self.mode == STATUSMode.REPAINT:
            if len(self.current_line.points) < 2:
                return
            self.current_line.removePoint(len(self.current_line.points) - 2)


class AnnotationView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(AnnotationView, self).__init__(parent)
        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.factor = 1.2

        # 影响了窗口截图功能，暂时注释掉
        # self.setViewport(QtWidgets.QOpenGLWidget())
        # self.setRenderHint(QtGui.QPainter.Antialiasing, False)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        angel = event.angleDelta()
        angelX, angelY = angel.x(), angel.y()
        point = event.pos()  # 当前鼠标位置
        if angelY > 0:
            self.zoom(self.factor, point)
        else:
            self.zoom(1 / self.factor, point)

    def zoom_in(self):
        self.zoom(self.factor)

    def zoom_out(self):
        self.zoom(1 / self.factor)

    def zoomfit(self):
        self.fitInView(0, 0, self.scene().width(), self.scene().height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def zoom(self, factor, point=None):
        mouse_old = self.mapToScene(point) if point is not None else None
        # 缩放比例

        pix_widget = self.transform().scale(factor, factor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if pix_widget > 30 and factor > 1: return
        if pix_widget < 0.01 and factor < 1: return

        self.scale(factor, factor)
        if point is not None:
            mouse_now = self.mapToScene(point)
            center_now = self.mapToScene(self.viewport().width() // 2, self.viewport().height() // 2)
            center_new = mouse_old - mouse_now + center_now
            self.centerOn(center_new)
