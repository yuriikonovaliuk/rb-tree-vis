RED = True
BLACK = False


class RedBlackTree(object):

    _root = None

    class Node(object):
        _color = None
        _key = None
        _left = None
        _right = None

        def __init__(self, key):
            self._key = key
            self._color = RED

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self._key == other._key
            return self._key == other

        def __lt__(self, other):
            if isinstance(other, self.__class__):
                return self._key < other._key
            return self._key < other

        def __invert__(self):
            self._color = not self._color

        def get_color(self):
            return self._color

        def get_key(self):
            return self._key

    ############################################################################

    def delete(self, key):
        if self.search(key):
            if not(self._red(self._root._left) or self._red(self._root._right)):
                self._root._color = RED
            self._root = self._delete(self._root, key)
            if self._root:
                self._root._color = BLACK

    def insert(self, key):
        self._root = self._insert(self._root, key)
        self._root._color = BLACK

    def search(self, key):
        return bool(self._search(self._root, key))

    ############################################################################

    def _delete(self, node, key):
        go_right = None
        if node == key:
            if node._left is not None:
                go_right = False
                node = self._make_left_red(node)
            elif node._right is not None:
                go_right = True
                node = self._make_right_red(node)
            else:
                return None

            if node == key:
                if go_right:
                    min_node = self._get_min(node._right)
                    self._swap_nodes(node, min_node)
                else:
                    max_node = self._get_max(node._left)
                    self._swap_nodes(node, max_node)
            else:
                go_right = None

        if (go_right is not None and go_right) or (go_right is None and (node < key)):
            node = self._make_right_red(node)
            node._right = self._delete(node._right, key)
        else:
            node = self._make_left_red(node)
            node._left = self._delete(node._left, key)

        node = self._local_balance(node)
        return node

    def _insert(self, node, key):
        if node is None:
            return self.Node(key)

        if node == key:
            return node
        elif node < key:
            node._right = self._insert(node._right, key)
        else:
            node._left = self._insert(node._left, key)

        node = self._local_balance(node)

        return node

    def _search(self, node, key):
        if node is None:
            return False
        elif node == key:
            return node
        elif node < key:
            return self._search(node._right, key)
        else:
            return self._search(node._left, key)

    ############################################################################

    def _get_min(self, node):
        while node._left:
            node = node._left
        return node

    def _get_max(self, node):
        while node._right:
            node = node._right
        return node

    def _red(self, node):
        return node and node._color == RED

    ############################################################################

    def _flip_color(self, node):
        ~node
        ~node._left
        ~node._right

    def _local_balance(self, node):
        if self._red(node._right) and not self._red(node._left):
            node = self._rotate_left(node)
        if self._red(node._left) and self._red(node._left._left):
            node = self._rotate_right(node)
        if self._red(node._left) and self._red(node._right):
            self._flip_color(node)
        return node

    def _make_left_red(self, node):
        if self._red(node._left) or self._red(node._left._left):
            return node
        self._flip_color(node)
        if self._red(node._right._left):
            node._right = self._rotate_right(node._right)
            node = self._rotate_left(node)
            self._flip_color(node)
        return node

    def _make_right_red(self, node):
        if self._red(node._left) and not self._red(node._right._left):
            node = self._rotate_right(node)
        if self._red(node._right) or self._red(node._right._left):
            return node
        self._flip_color(node)
        if self._red(node._left._left):
            node = self._rotate_right(node)
            self._flip_color(node)
        return node

    def _rotate_left(self, node):
        right_left = node._right._left
        node._right._left = node
        node = node._right
        node._left._right = right_left
        node._color, node._left._color = node._left._color, node._color
        return node

    def _rotate_right(self, node):
        left_right = node._left._right
        node._left._right = node
        node = node._left
        node._right._left = left_right
        node._color, node._right._color = node._right._color, node._color
        return node

    def _swap_nodes(self, a, b):
        a._key, b._key = b._key, a._key

