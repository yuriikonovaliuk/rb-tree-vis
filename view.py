from math import sqrt
from sys import stderr

from model import RED, BLACK

from PySide import QtGui, QtCore
from PySide.QtCore import Qt


_CIRCLE_RADIUS = 12
_ROW_DISTANCE = 50

_LINE_Z_VALUE = 1
_CIRCLE_Z_VALUE = 2
_TEXT_Z_VALUE = 3

_PEN_WEIGHT = 2

class RBTreeView(object):

    _app = None
    _canvas = None
    _nodes = None
    _black_pen = None
    _red_pen = None


    class Node(object):

        _canvas = None
        _pen = None
        _default_pen = None
        _back_brush = None
        _fore_brush = None
        _model_node = None

        _old_slot = None
        _old_color = None
        _old_key = None

        _line = None
        _circle = None
        _text = None

        _to_delete = None

        def __init__(self, canvas, black_pen, red_pen, model_node):
            self._canvas = canvas
            self._pen = {RED: red_pen, BLACK: black_pen}
            self._default_pen = black_pen
            self._back_brush = QtGui.QBrush(Qt.white)
            self._fore_brush = QtGui.QBrush(Qt.black)
            self._model_node = model_node
            self._model_node.update_hooks({
                'before_slot_changed': self._before_slot_changed,
                'before_color_changed': self._before_color_changed,
                'before_key_changed': self._before_key_changed,
                'before_delete': self._before_delete,
            })
            self._line = QtGui.QGraphicsLineItem(parent=None, scene=self._canvas)
            self._circle = QtGui.QGraphicsEllipseItem(parent=None, scene=self._canvas)
            self._text = QtGui.QGraphicsTextItem(parent=None, scene=self._canvas)
            self.draw()
            self._to_delete = False

        ########################################################################
        # Representation related methods

        def draw(self):
            slot = self._model_node.get_slot()
            node_point = self._get_slot_coord(slot)
            parent_slot = self._get_parent_slot(slot)
            parent_point = self._get_slot_coord(parent_slot)
            # Draw line
            self._line.setLine(*(list(node_point) + list(parent_point)))
            self._line.setPen(self._pen[self._model_node.get_color()])
            self._line.setZValue(_LINE_Z_VALUE)
            # Draw circle
            self._circle.setRect(*self._get_circle_rect(*node_point))
            self._circle.setPen(self._default_pen)
            self._circle.setBrush(self._back_brush)
            self._circle.setZValue(_CIRCLE_Z_VALUE)
            # Draw text
            self._text.setPlainText(str(self._model_node.get_key()))
            self._text.setParentItem(self._circle)
            self._text.setZValue(_TEXT_Z_VALUE)
            self._adjust_font()
            self._text.setPos(*self._get_text_coord(*node_point))

        def delete(self):
            if self._to_delete:
                for item in (self._circle, self._line):
                    item.setParentItem(None)
                    item.hide()
                    self._canvas.removeItem(item)
                return self

        def start_move(self):
            if self._old_slot is not None:
                # Calculate slots and coords
                old_slot = self._old_slot
                new_slot = self._model_node.get_slot()
                old_parent_slot = self._get_parent_slot(old_slot)
                new_parent_slot = self._get_parent_slot(new_slot)
                self._old_node_coord = self._get_slot_coord(old_slot)
                self._new_node_coord = self._get_slot_coord(new_slot)
                self._old_parent_coord = self._get_slot_coord(old_parent_slot)
                self._new_parent_coord = self._get_slot_coord(new_parent_slot)
            if self._old_color is not None:
                self._old_color_map = self._pen[self._old_color].color().getRgbF()[:3]
                self._new_color_map = self._pen[self._model_node.get_color()].color().getRgbF()[:3]

        def step(self, ratio):
            if self._old_slot is not None:
                begin1, begin2 = self._old_node_coord, self._new_node_coord
                end1, end2 = self._old_parent_coord, self._new_parent_coord

                begin = tuple(map(lambda x, y: x + (y - x) * ratio, begin1, begin2))
                end = tuple(map(lambda x, y: x + (y - x) * ratio, end1, end2))

                self._circle.setRect(*self._get_circle_rect(*begin))
                self._line.setLine(*(list(begin) + list(end)))
                self._text.setPos(*self._get_text_coord(*begin))
            if self._old_color is not None:
                color = tuple(map(lambda x, y: x + (y - x) * ratio, self._old_color_map,
                                  self._new_color_map))
                qcolor = QtGui.QColor()
                qcolor.setRgbF(*color)
                self._line.setPen(QtGui.QPen(qcolor, _PEN_WEIGHT))

        def finish_move(self):
            self._old_slot = None
            if self._old_color is not None:
                self._old_color = None
                del self._old_color_map
                del self._new_color_map

        ########################################################################

        def get_key_update_action(self):
            if self._old_key is not None:
                return self._update_key

        def need_graphics_update(self):
            return (self._old_slot is not None) or (self._old_color is not None)

        ########################################################################
        # Hooks

        def _before_color_changed(self):
            self._old_color = self._model_node.get_color()

        def _before_key_changed(self):
            self._old_key = self._model_node.get_key()

        def _before_slot_changed(self):
            self._old_slot = self._model_node.get_slot()

        def _before_delete(self):
            self._to_delete = True

        ########################################################################

        def _get_parent_slot(self, slot):
            if slot is None or slot == (0, 0):
                return None
            return (slot[0] - 1, slot[1] >> 1)

        def _update_key(self):
            self._text.setPlainText(str(self._model_node.get_key()))
            self._adjust_font()
            self._old_key = None

        ########################################################################
        # Font manipulation methods

        def _adjust_font(self):
            font = self._text.font()
            while self._text_fits_circle(font):
                font = self._change_font_size(font, 1)
            while not self._text_fits_circle(font):
                font = self._change_font_size(font, -1)
            self._text.setFont(font)

        def _change_font_size(self, font, delta):
            size = font.pixelSize()
            pixel = True
            if size < 0:
                size = font.pointSize()
                pixel = False
            size += delta
            if pixel:
                font.setPixelSize(size)
            else:
                font.setPointSize(size)
            return font

        def _text_fits_circle(self, font):
            metrics = QtGui.QFontMetrics(font)
            diagonal = sqrt(metrics.height() ** 2 + metrics.width(self._text.toPlainText()) ** 2)
            return diagonal <= (_CIRCLE_RADIUS * 2)

        ########################################################################
        # Graphics calculation methods

        def _get_circle_rect(self, cx, cy):
            diameter = _CIRCLE_RADIUS << 1
            return cx - _CIRCLE_RADIUS, cy - _CIRCLE_RADIUS, diameter, diameter

        def _get_text_coord(self, cx, cy):
            metrics = QtGui.QFontMetrics(self._text.font())
            return (cx - metrics.width(self._text.toPlainText()) / 2 - _CIRCLE_RADIUS * 0.3,
                    cy - metrics.height() / 2 - _CIRCLE_RADIUS * 0.3)

        def _get_slot_coord(self, slot):
            if slot == None:
                return (self._get_slot_coord((0, 0))[0], 0.0)
            y = (slot[0] + 1.0) * _ROW_DISTANCE
            level_width = self._canvas.width() / 2.0
            x = level_width
            if slot[0]:
                side_markers = bin(slot[1])[2:]
                side_markers = '0' * (slot[0] - len(side_markers)) + side_markers
                for item in side_markers:
                    level_width /= 2.0
                    x += (-level_width, level_width)[int(item)]
            return (x, y)

    ############################################################################

    def __init__(self, app, gui):
        self._app = app
        self._gui = gui
        self._canvas = gui.get_canvas()
        self._canvas.setSceneRect(0, 0, self._canvas.width(), self._canvas.height())
        gui.canvasResized.connect(self._handle_resize)
        self._nodes = []
        self._black_pen = QtGui.QPen(Qt.black, _PEN_WEIGHT)
        self._red_pen = QtGui.QPen(Qt.red, _PEN_WEIGHT)

    def add_node(self, model_node):
        view_node = self.Node(self._canvas, self._black_pen,
                              self._red_pen, model_node)
        self._nodes.append(view_node)
        self._app.processEvents()
        QtCore.QThread.msleep(1000)

    def delete_node(self):
        for node in self._nodes:
            node = node.delete()
            if node:
                self._nodes.remove(node)
                QtCore.QThread.msleep(1000)

    def visualize_changes(self):
        text_changes = filter(lambda x: x is not None,
            map(lambda x: x.get_key_update_action(), self._nodes))
        if text_changes:
            for item in text_changes:
                item()
            self._canvas.update()
            self._app.processEvents()

        nodes_to_graphics_update = filter(lambda x: x.need_graphics_update(), self._nodes)
        if nodes_to_graphics_update:
            QtCore.QThread.msleep(1000)
            map(lambda x: x.start_move(), nodes_to_graphics_update)
            for i in xrange(51):
                map(lambda x: x.step(i / 50.0), nodes_to_graphics_update)
                QtCore.QThread.msleep(20)
                self._canvas.update()
                self._app.processEvents()
            map(lambda x: x.finish_move(), nodes_to_graphics_update)
            QtCore.QThread.msleep(50)
            self._app.processEvents()

    ############################################################################

    def _handle_resize(self, *args):
        self._canvas.setSceneRect(0, 0, self._gui.graph_view.width(),
                                  self._gui.graph_view.height())
        self._repaint_all()

    def _repaint_all(self):
        map(lambda x: x.draw(), self._nodes)

