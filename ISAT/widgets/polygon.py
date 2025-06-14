# -*- coding: utf-8 -*-
# @Author  : LG

from PyQt5 import QtCore, QtWidgets, QtGui
from ISAT.annotation import Object
import typing
from ISAT.configs import STATUSMode, CLICKMode, DRAWMode, CONTOURMode


class PromptPoint(QtWidgets.QGraphicsPathItem):
    def __init__(self, pos, type=0):
        super(PromptPoint, self).__init__()
        self.color = QtGui.QColor('#0000FF') if type == 0 else QtGui.QColor('#00FF00')
        self.color.setAlpha(255)
        self.painterpath = QtGui.QPainterPath()
        self.painterpath.addEllipse(
            QtCore.QRectF(-1, -1, 2, 2))
        self.setPath(self.painterpath)
        self.setBrush(self.color)
        self.setPen(QtGui.QPen(self.color, 3))
        self.setZValue(1e5)

        self.setPos(pos)


class Vertex(QtWidgets.QGraphicsPathItem):
    def __init__(self, polygon, color, nohover_size=2):
        super(Vertex, self).__init__()
        self.polygon = polygon
        self.color = color
        self.color.setAlpha(255)
        self.nohover_size = nohover_size
        self.hover_size = self.nohover_size + 2
        self.line_width = 0

        self.nohover = QtGui.QPainterPath()
        self.nohover.addEllipse(
            QtCore.QRectF(-self.nohover_size // 2, -self.nohover_size // 2, self.nohover_size, self.nohover_size))
        self.hover = QtGui.QPainterPath()
        self.hover.addRect(
            QtCore.QRectF(-self.nohover_size // 2, -self.nohover_size // 2, self.nohover_size, self.nohover_size))

        self.setPath(self.nohover)
        self.setBrush(self.color)
        self.setPen(QtGui.QPen(self.color, self.line_width))
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(1e5)

    def setColor(self, color):
        self.color = QtGui.QColor(color)
        self.color.setAlpha(255)
        self.setPen(QtGui.QPen(self.color, self.line_width))
        self.setBrush(self.color)

    def itemChange(self, change: 'QtWidgets.QGraphicsItem.GraphicsItemChange', value: typing.Any):
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.scene().mainwindow.actionDelete.setEnabled(self.isSelected())
            if self.isSelected():
                selected_color = QtGui.QColor('#00A0FF')
                self.setBrush(selected_color)
            else:
                self.setBrush(self.color)

        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.isEnabled():
            # 限制顶点移动到图外
            if value.x() < 0:
                value.setX(0)
            if value.x() > self.scene().width() - 1:
                value.setX(self.scene().width() - 1)
            if value.y() < 0:
                value.setY(0)
            if value.y() > self.scene().height() - 1:
                value.setY(self.scene().height() - 1)
            index = self.polygon.vertexs.index(self)
            self.polygon.movePoint(index, value)

        return super(Vertex, self).itemChange(change, value)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent'):
        self.scene().hovered_vertex = self
        if self.scene().mode == STATUSMode.CREATE:  # CREATE
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        else:  # EDIT, VIEW
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
            if not self.isSelected():
                self.setBrush(QtGui.QColor(255, 255, 255, 255))
            self.setPath(self.hover)
        super(Vertex, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        self.scene().hovered_vertex = None
        if not self.isSelected():
            self.setBrush(self.color)
        self.setPath(self.nohover)
        super(Vertex, self).hoverLeaveEvent(event)


class Polygon(QtWidgets.QGraphicsPolygonItem):
    def __init__(self):
        super(Polygon, self).__init__(parent=None)
        self.line_width = 1
        self.hover_alpha = 150
        self.nohover_alpha = 80
        self.points = []
        self.vertexs = []
        self.category = ''
        self.action = ''
        self.group = 0
        self.iscrowd = 0
        self.note = ''
        self.center = []

        self.rxmin, self.rxmax, self.rymin, self.rymax = 0, 0, 0, 0  # 用于绘画完成后，记录多边形的各边界，此处与points对应
        self.color = QtGui.QColor('#ff0000')
        self.is_drawing = True

        self.setPen(QtGui.QPen(self.color, self.line_width))
        self.setBrush(QtGui.QBrush(self.color, QtCore.Qt.BrushStyle.FDiagPattern))

        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setZValue(1e5)

    def addPoint(self, point):
        self.points.append(point)
        vertex = Vertex(self, self.color, self.scene().mainwindow.cfg['software']['vertex_size'] * 2)
        # 添加路径点
        self.scene().addItem(vertex)
        self.vertexs.append(vertex)
        vertex.setPos(point)

    def movePoint(self, index, point):
        if not 0 <= index < len(self.points):
            return
        self.points[index] = self.mapFromScene(point)

        self.redraw()
        if self.scene().mainwindow.load_finished and not self.is_drawing:
            self.scene().mainwindow.set_saved_state(False)

    def removePoint(self, index):
        if not self.points:
            return
        self.points.pop(index)
        vertex = self.vertexs.pop(index)
        self.scene().removeItem(vertex)
        del vertex
        self.redraw()

    def delete(self):
        self.points.clear()
        while self.vertexs:
            vertex = self.vertexs.pop()
            self.scene().removeItem(vertex)
            del vertex

    def moveVertex(self, index, point):
        if not 0 <= index < len(self.vertexs):
            return
        vertex = self.vertexs[index]
        vertex.setEnabled(False)
        vertex.setPos(point)
        vertex.setEnabled(True)

    def itemChange(self, change: 'QGraphicsItem.GraphicsItemChange', value: typing.Any):
        if (change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged
                and not self.is_drawing
                and self.scene().mode != STATUSMode.CREATE):  # 选中改变
            if self.isSelected():
                color = QtGui.QColor('#00A0FF')
                color.setAlpha(self.hover_alpha)
                self.setBrush(color)
                self.scene().selected_polygons_list.append(self)
            else:
                self.color.setAlpha(self.nohover_alpha)
                self.setBrush(self.color)
                if self in self.scene().selected_polygons_list:
                    self.scene().selected_polygons_list.remove(self)
            self.scene().mainwindow.annos_dock_widget.set_selected(self)  # 更新label面板

        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:  # ItemPositionHasChanged
            bias = value
            l, t, b, r = self.boundingRect().left(), self.boundingRect().top(), self.boundingRect().bottom(), self.boundingRect().right()
            if l + bias.x() < 0: bias.setX(-l)
            if r + bias.x() > self.scene().width(): bias.setX(self.scene().width() - r)
            if t + bias.y() < 0: bias.setY(-t)
            if b + bias.y() > self.scene().height(): bias.setY(self.scene().height() - b)

            for index, point in enumerate(self.points):
                self.moveVertex(index, point + bias)

            if self.scene().mainwindow.load_finished and not self.is_drawing:
                self.scene().mainwindow.set_saved_state(False)

        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            value = 0 if self.is_drawing else value
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged and self.isSelected():
            self.setSelected(not self.is_drawing)
        return super(Polygon, self).itemChange(change, value)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent'):
        if not self.is_drawing and not self.isSelected():
            self.color.setAlpha(self.hover_alpha)
            self.setBrush(self.color)
        super(Polygon, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        if not self.is_drawing and not self.isSelected():
            self.color.setAlpha(self.nohover_alpha)
            self.setBrush(self.color)
        super(Polygon, self).hoverEnterEvent(event)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent'):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.scene().mainwindow.category_edit_widget.polygon = self
            self.scene().mainwindow.category_edit_widget.load_cfg()
            self.scene().mainwindow.category_edit_widget.show()

    def redraw(self):
        if len(self.points) < 1:
            return
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        self.rxmin, self.rymin, self.rxmax, self.rymax = min(xs), min(ys), max(xs), max(ys)
        self.setPolygon(QtGui.QPolygonF(self.points))

    def change_color(self, color):
        self.color = color
        if not self.scene().mainwindow.cfg['software']['show_edge']:
            color.setAlpha(0)
        self.setPen(QtGui.QPen(color, self.line_width))
        self.color.setAlpha(self.nohover_alpha)
        self.setBrush(self.color)
        for vertex in self.vertexs:
            vertex_color = self.color
            vertex_color.setAlpha(255)
            vertex.setPen(QtGui.QPen(vertex_color, self.line_width))
            vertex.setBrush(vertex_color)

    def set_drawed(self, category, group, iscrowd, note, color: QtGui.QColor, layer=None, center=[], action=None):
        self.is_drawing = False
        self.category = category
        self.action = action
        if isinstance(group, str):
            group = 0 if group == '' else int(group)
        self.group = group
        self.iscrowd = iscrowd
        self.note = note
        self.center = center

        self.color = color
        if not self.scene().mainwindow.cfg['software']['show_edge']:
            color.setAlpha(0)
        self.setPen(QtGui.QPen(color, self.line_width))
        self.color.setAlpha(self.nohover_alpha)
        self.setBrush(self.color)
        if layer is not None:
            self.setZValue(layer)
            for vertex in self.vertexs:
                vertex.setZValue(layer)
        for vertex in self.vertexs:
            vertex.setColor(color)

    def set_drawed_action(self, action, group, iscrowd, note, color: QtGui.QColor, layer=None, center=[]):
        self.is_drawing = False
        self.action = action
        if isinstance(group, str):
            group = 0 if group == '' else int(group)
        self.group = group
        self.iscrowd = iscrowd
        self.note = note
        self.center = center

        self.color = color
        if not self.scene().mainwindow.cfg['software']['show_edge']:
            color.setAlpha(0)
        self.setPen(QtGui.QPen(color, self.line_width))
        self.color.setAlpha(self.nohover_alpha)
        self.setBrush(self.color)
        if layer is not None:
            self.setZValue(layer)
            for vertex in self.vertexs:
                vertex.setZValue(layer)
        for vertex in self.vertexs:
            vertex.setColor(color)

    def calculate_area(self):
        area = 0
        num_points = len(self.points)
        for i in range(num_points):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % num_points]
            d = p1.x() * p2.y() - p2.x() * p1.y()
            area += d
        return abs(area) / 2

    def load_object(self, object):
        segmentation = object.segmentation
        for x, y in segmentation:
            point = QtCore.QPointF(x, y)
            self.addPoint(point)
        color = self.scene().mainwindow.category_color_dict.get(object.category, '#000000')
        self.set_drawed(object.category, object.group, object.iscrowd, object.note, QtGui.QColor(color),
                        object.layer)  # ...

    def to_object(self):
        if self.is_drawing:
            return None
        segmentation = []
        for point in self.points:
            point = point + self.pos()
            segmentation.append((round(point.x(), 2), round(point.y(), 2)))
        xmin = self.boundingRect().x() + self.pos().x()
        ymin = self.boundingRect().y() + self.pos().y()
        xmax = xmin + self.boundingRect().width()
        ymax = ymin + self.boundingRect().height()

        object = Object(self.category, group=self.group, segmentation=segmentation,
                        area=self.calculate_area(), layer=self.zValue(), bbox=(xmin, ymin, xmax, ymax),
                        iscrowd=self.iscrowd, note=self.note, center=self.center,action=self.action)
        return object


class LineVertex(QtWidgets.QGraphicsPathItem):
    def __init__(self, polygon, color, nohover_size=2):
        super(LineVertex, self).__init__()
        self.polygon = polygon
        self.color = color
        self.color.setAlpha(255)
        self.nohover_size = nohover_size
        self.hover_size = self.nohover_size + 2
        self.line_width = 0

        self.nohover = QtGui.QPainterPath()
        self.nohover.addEllipse(
            QtCore.QRectF(-self.nohover_size // 2, -self.nohover_size // 2, self.nohover_size, self.nohover_size))
        self.hover = QtGui.QPainterPath()
        self.hover.addRect(
            QtCore.QRectF(-self.nohover_size // 2, -self.nohover_size // 2, self.nohover_size, self.nohover_size))

        self.setPath(self.nohover)
        self.setBrush(self.color)
        self.setPen(QtGui.QPen(self.color, self.line_width))
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(1e5)

    def itemChange(self, change: 'QtWidgets.QGraphicsItem.GraphicsItemChange', value: typing.Any):
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.scene().mainwindow.actionDelete.setEnabled(self.isSelected())
            if self.isSelected():
                selected_color = QtGui.QColor('#00A0FF')
                self.setBrush(selected_color)
            else:
                self.setBrush(self.color)

        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.isEnabled():
            # 限制顶点移动到图外
            if value.x() < 0:
                value.setX(0)
            if value.x() > self.scene().width() - 1:
                value.setX(self.scene().width() - 1)
            if value.y() < 0:
                value.setY(0)
            if value.y() > self.scene().height() - 1:
                value.setY(self.scene().height() - 1)
            index = self.polygon.vertexs.index(self)
            self.polygon.movePoint(index, value)

        return super(LineVertex, self).itemChange(change, value)


class Line(QtWidgets.QGraphicsPathItem):
    def __init__(self):
        super().__init__(parent=None)
        self.line_width = 1
        # self.hover_alpha = 150
        # self.nohover_alpha = 80
        self.points = []
        self.vertexs = []
        self.color = QtGui.QColor('#ff0000')

    def addPoint(self, point):
        self.points.append(point)
        vertex = LineVertex(self, self.color, self.scene().mainwindow.cfg['software']['vertex_size'] * 2)
        # 添加路径点
        self.scene().addItem(vertex)
        self.vertexs.append(vertex)
        vertex.setPos(point)

    def movePoint(self, index, point):
        if not 0 <= index < len(self.points):
            return
        self.points[index] = self.mapFromScene(point)
        self.redraw()

    def removePoint(self, index):
        if not self.points:
            return
        self.points.pop(index)
        vertex = self.vertexs.pop(index)
        self.scene().removeItem(vertex)
        del vertex
        self.redraw()

    def delete(self):
        self.points.clear()
        while self.vertexs:
            vertex = self.vertexs.pop()
            self.scene().removeItem(vertex)
            del vertex

    def redraw(self):
        if len(self.points) < 1:
            return
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        self.rxmin, self.rymin, self.rxmax, self.rymax = min(xs), min(ys), max(xs), max(ys)

        line_path = QtGui.QPainterPath()
        if self.points:
            line_path.moveTo(self.points[0])
            for point in self.points[1:]:
                line_path.lineTo(point)

        self.setPath(line_path)


class RectVertex(QtWidgets.QGraphicsPathItem):
    def __init__(self, rect, color, nohover_size=2):
        super(RectVertex, self).__init__()
        self.rect = rect
        self.color = color
        self.color.setAlpha(255)
        self.nohover_size = nohover_size
        self.hover_size = self.nohover_size + 2
        self.line_width = 0

        self.nohover = QtGui.QPainterPath()
        self.nohover.addEllipse(
            QtCore.QRectF(-self.nohover_size // 2, -self.nohover_size // 2, self.nohover_size, self.nohover_size))
        self.hover = QtGui.QPainterPath()
        self.hover.addRect(
            QtCore.QRectF(-self.nohover_size // 2, -self.nohover_size // 2, self.nohover_size, self.nohover_size))

        self.setPath(self.nohover)
        self.setBrush(self.color)
        self.setPen(QtGui.QPen(self.color, self.line_width))
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(1e5)

    def itemChange(self, change: 'QtWidgets.QGraphicsItem.GraphicsItemChange', value: typing.Any):
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.scene().mainwindow.actionDelete.setEnabled(self.isSelected())
            if self.isSelected():
                selected_color = QtGui.QColor('#00A0FF')
                self.setBrush(selected_color)
            else:
                self.setBrush(self.color)

        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.isEnabled():
            # 限制顶点移动到图外
            if value.x() < 0:
                value.setX(0)
            if value.x() > self.scene().width() - 1:
                value.setX(self.scene().width() - 1)
            if value.y() < 0:
                value.setY(0)
            if value.y() > self.scene().height() - 1:
                value.setY(self.scene().height() - 1)
            index = self.rect.vertexs.index(self)
            self.rect.movePoint(index, value)

        return super(RectVertex, self).itemChange(change, value)


class Rect(QtWidgets.QGraphicsRectItem):
    def __init__(self):
        super().__init__(parent=None)
        self.line_width = 1
        self.points = []
        self.vertexs = []
        self.color = QtGui.QColor('#ff0000')

    def addPoint(self, point):
        self.points.append(point)
        vertex = RectVertex(self, self.color, self.scene().mainwindow.cfg['software']['vertex_size'] * 2)
        # 添加路径点
        self.scene().addItem(vertex)
        self.vertexs.append(vertex)
        vertex.setPos(point)

    def movePoint(self, index, point):
        if not 0 <= index < len(self.points):
            return
        self.points[index] = self.mapFromScene(point)
        self.redraw()

    def removePoint(self, index):
        if not self.points:
            return
        self.points.pop(index)
        vertex = self.vertexs.pop(index)
        self.scene().removeItem(vertex)
        del vertex
        self.redraw()

    def delete(self):
        self.points.clear()
        while self.vertexs:
            vertex = self.vertexs.pop()
            self.scene().removeItem(vertex)
            del vertex

    def redraw(self):
        if len(self.points) < 2:
            return

        self.setRect(QtCore.QRectF(self.points[0], self.points[-1]))
