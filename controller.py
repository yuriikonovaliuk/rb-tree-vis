from random import randint


class RBTreeController(object):

    _gui = None
    _model = None
    _view = None

    def __init__(self, gui, model, view):
        self._gui = gui
        self._model = model
        self._view = view

        self._model.update_hooks({
            'after_tree_update': self._after_tree_update,
            'after_create_node': self._after_create_node,
            'after_delete_node': self._after_delete_node,
        })

        self._gui.subscribe_add_node_event(self._add_node)
        self._gui.subscribe_delete_node_event(self._delete_node)

    ############################################################################

    def _add_node(self, value, semaphore):
        try:
            values = [int(value)]
        except ValueError:
            num, lower, upper = map(int, value.split(','))
            values = [randint(lower, upper) for i in xrange(num)]
        for index, item in enumerate(values):
            self._model.insert(item)
        semaphore.release()

    def _delete_node(self, value, semaphore):
        self._model.delete(int(value))
        semaphore.release()

    def _after_create_node(self, node):
        self._view.add_node(node)

    def _after_delete_node(self):
        self._view.delete_node()

    def _after_tree_update(self):
        self._view.visualize_changes()

