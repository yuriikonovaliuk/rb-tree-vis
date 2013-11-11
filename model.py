from sys import stderr

from rbtree import RedBlackTree, RED, BLACK


class RBTreeModel(RedBlackTree):

    _hooks = None
    _slot_stack = None


    class Node(RedBlackTree.Node):
        _slot = None
        _hooks = None

        def __init__(self, key):
            self._hooks = {}
            super(type(self), self).__init__(key)

        def __setattr__(self, key, value):
            if key == '_slot' and self._slot != value:
                self._hooks.get('before_slot_changed', lambda: False)()
            if key == '_color' and self._color != value:
                self._hooks.get('before_color_changed', lambda: False)()
            if key == '_key' and self._key != value:
                self._hooks.get('before_key_changed', lambda: False)()
            return super(type(self), self).__setattr__(key, value)

        def delete(self):
            self._hooks.get('before_delete', lambda: False)()

        def get_slot(self):
            return self._slot

        def set_slot(self, slot):
            self._slot = slot
            row, col = slot
            if self._left:
                self._left.set_slot((row + 1, col * 2))
            if self._right:
                self._right.set_slot((row + 1, col * 2 + 1))

        def update_hooks(self, hooks):
            self._hooks.update(hooks)

    ############################################################################

    def __init__(self):
        super(RBTreeModel, self).__init__()
        self._hooks = {}
        self._slot_stack = []

    def update_hooks(self, hooks):
        self._hooks.update(hooks)

    ############################################################################

    def delete(self, key):
        super(RBTreeModel, self).delete(key)
        if self._root:
            self._root.set_slot((0, 0))
        self._hooks.get('after_tree_update', lambda: False)()

    def insert(self, key):
        self._slot_stack = [(0, 0)]
        super(RBTreeModel, self).insert(key)
        self._hooks.get('after_tree_update', lambda: False)()
        self._slot_stack.pop()

    ############################################################################

    def _delete(self, node, key):
        new_node = super(RBTreeModel, self)._delete(node, key)
        if new_node is None:
            node.delete()
            self._hooks.get('after_delete_node', lambda: False)()
        return new_node

    def _insert(self, node, key):
        if node:
            row, col = self._slot_stack[-1]
            if node < key:
                self._slot_stack.append((row + 1, col * 2 + 1))
            else:
                self._slot_stack.append((row + 1, col * 2))
        new_node = super(RBTreeModel, self)._insert(node, key)
        if node:
            self._slot_stack.pop()
        else:
            new_node.set_slot(self._slot_stack[-1])
            self._hooks.get('after_create_node', lambda x: False)(new_node)
        return new_node

    ############################################################################

    def _flip_color(self, node):
        super(RBTreeModel, self)._flip_color(node)
        self._hooks.get('after_tree_update', lambda: False)()

    def _rotate_left(self, node):
        slot = node.get_slot()
        node = super(RBTreeModel, self)._rotate_left(node)
        node.set_slot(slot)
        self._hooks.get('after_tree_update', lambda: False)()
        return node

    def _rotate_right(self, node):
        slot = node.get_slot()
        node = super(RBTreeModel, self)._rotate_right(node)
        node.set_slot(slot)
        self._hooks.get('after_tree_update', lambda: False)()
        return node

    def _swap_nodes(self, a, b):
        super(RBTreeModel, self)._swap_nodes(a, b)
        self._hooks.get('after_tree_update', lambda: False)()

