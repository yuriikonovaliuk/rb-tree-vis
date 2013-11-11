import sys

from PySide.QtGui import QApplication

from gui import MainWindow
from model import RBTreeModel
from view import RBTreeView
from controller import RBTreeController


if __name__ == '__main__':
    app = QApplication(sys.argv)

    form = MainWindow(app)
    model = RBTreeModel()
    view = RBTreeView(app, form)
    controller = RBTreeController(form, model, view)

    form.showMaximized()
    app.exec_()

