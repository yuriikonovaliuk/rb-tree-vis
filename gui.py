from random import randint

from PySide import QtCore, QtGui


class MainWindow(QtGui.QDialog):

    _app = None

    _add_node_subscribers = None
    _delete_node_subscribers = None

    _add_node_event = QtCore.Signal(str, QtCore.QSemaphore)
    _delete_node_event = QtCore.Signal(str, QtCore.QSemaphore)

    _stop_mode_changed_event = QtCore.Signal(int)

    _continue_condition = None

    canvasResized = QtCore.Signal()

    def __init__(self, app, parent=None):
        super(MainWindow, self).__init__(parent)

        self._app = app

        self.add_label = QtGui.QLabel('Add node')
        self.add_edit = QtGui.QLineEdit()
        self.delete_label = QtGui.QLabel('Delete node')
        self.delete_edit = QtGui.QLineEdit()

        self.canvas = QtGui.QGraphicsScene()
        self.graph_view = QtGui.QGraphicsView(self.canvas)
        self.graph_view.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        ########################################################################

        main_layout = QtGui.QGridLayout()
        top_layout = QtGui.QHBoxLayout()
        top_layout.addWidget(self.add_label)
        top_layout.addWidget(self.add_edit)
        top_layout.addWidget(self.delete_label)
        top_layout.addWidget(self.delete_edit)

        main_layout.addLayout(top_layout, 0, 0)
        main_layout.addWidget(self.graph_view, 1, 0)
        self.setLayout(main_layout)

        ########################################################################

        self.add_edit.returnPressed.connect(self._add_return_pressed)
        self.delete_edit.returnPressed.connect(self._delete_return_pressed)

        ########################################################################

        self._add_node_subscribers = 0
        self._delete_node_subscribers = 0

        ########################################################################

        self._continue_condition = QtCore.QWaitCondition()
        self.canvas.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.GraphicsSceneMousePress:
            self._continue_condition.wakeAll()
            return True
        return False

    def get_canvas(self):
        return self.canvas

    def resizeEvent(self, event):
        self.canvasResized.emit()

    def subscribe_add_node_event(self, slot):
        self._add_node_event.connect(slot)
        self._add_node_subscribers += 1

    def subscribe_delete_node_event(self, slot):
        self._delete_node_event.connect(slot)
        self._delete_node_subscribers += 1

    def subscribe_stop_mode_changed_event(self, slot):
        self._stop_mode_changed_event.connect(slot)
        return self.stop_mode_group.checkedId()

    ############################################################################

    def _add_return_pressed(self):
        self._edit_action(self._add_node_event, self.sender().text(),
                          self._add_node_subscribers)

    def _delete_return_pressed(self):
        self._edit_action(self._delete_node_event, self.sender().text(),
                          self._delete_node_subscribers)

    def _clear_edit(self):
        self.add_edit.clear()
        self.delete_edit.clear()

    def _edit_action(self, signal, value, subsribers_amount):
        semaphore = QtCore.QSemaphore(subsribers_amount)
        self._set_edit_read_only(True)
        semaphore.acquire(subsribers_amount)
        signal.emit(value, semaphore)
        semaphore.acquire(subsribers_amount)
        self._clear_edit()
        self._set_edit_read_only(False)

    def _set_edit_read_only(self, read_only):
        self.add_edit.setReadOnly(read_only)
        self.delete_edit.setReadOnly(read_only)

    def _stop_mode_changed(self, button_id):
        self._stop_mode_changed_event.emit(button_id)

