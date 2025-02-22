"""
Provides nodes for the Merkle-tree data structure.
"""

from abc import ABCMeta, abstractmethod
import json


L_BRACKET_SHORT = '└─'
L_BRACKET_LONG = '└──'
T_BRACKET = '├──'
VERTICAL_BAR = '│'


NODE_TEMPLATE = """
    memid   : {node}
    left    : {left}
    right   : {right}
    parent  : {parent}
    hash    : {checksum}
"""


class Node:
    """
    Merkle-tree generic node.

    :param value: the hash value to be stored by the node.
    :type value: bytes
    :param parent: [optional] parent node. Defaults to *None*.
    :type parent: Node
    :param left: [optional] parent node. Defaults to *None*.
    :type left: Node
    :param right: [optional] right child. Defaults to *None*.
    :type right: Node
    :returns: Node storing the digest of the concatenation of the provided
        nodes' digests.
    :rtype: Node
    """

    __slots__ = ('__value', '__parent', '__left', '__right')

    def __init__(self, value, parent=None, left=None, right=None):
        self.__value = value
        self.__parent = parent
        self.__left = left
        self.__right = right

        if left:
            left.__parent = self
        if right:
            right.__parent = self

    @property
    def value(self):
        """
        The digest currently stored by the node.

        :rtype: bytes
        """
        return self.__value

    @property
    def left(self):
        """
        The left child of the node.

        .. note:: Rerturns *None* if the node has no left child.

        :rtype: Node
        """
        return self.__left

    @property
    def right(self):
        """
        The right child of the node.

        .. note:: Rerturns *None* if the node has no right child.

        :rtype: Node
        """
        return self.__right

    @property
    def parent(self):
        """
        The parent of the node.

        .. note:: Rerturns *None* if the node has no parent.
        .. attention:: A prentless node is the root of the containing tree.

        :rtype: Node
        """
        return self.__parent

    def set_left(self, node):
        """
        Updates the left child of the present node.

        :param left: the new left child
        :type left: Node
        """
        self.__left = node

    def set_right(self, node):
        """
        Updates the right child of the present node.

        :param right: the new right child
        :type right: Node
        """
        self.__right = node

    def set_parent(self, node):
        """
        Updates the parent of the present node.

        :param parent: the new parent
        :type parent: Node
        """
        self.__parent = node

    def is_left_child(self):
        """
        Returns *True* if this is the left child of some other node within the
        containing tree.

        :rtype: bool
        """
        parent = self.__parent
        if not parent:
            return False

        return self == parent.left

    def is_right_child(self):
        """
        Returns *True* if this is the right child of some other node within the
        containing tree.

        :rtype: bool
        """
        parent = self.__parent
        if not parent:
            return False

        return self == parent.right

    def is_leaf(self):
        """
        Returns *True* if this is a leaf node in the containing tree.

        .. note:: This is equivalent to being an instance of the *Leaf* class.

        :rtype: bool
        """
        return isinstance(self, Leaf)

    def get_checksum(self, encoding):
        """
        Returns the hex string representing hash value stored by the node.

        :param encoding: encoding type of the containing tree.
        :type encoding: str

        :rtype: str
        """
        return self.value.decode(encoding)

    @classmethod
    def from_children(cls, left, right, engine):
        """
        Construction of node from a given pair of nodes.

        :param left: left child
        :type left: Node
        :param right: right child
        :type right: Node
        :param engine: hash-engine to be used for digest computation
        :type engine: HashEngine
        :returns: a node storing the digest of the concatenation of the
            provided nodes' digests.
        :rtype: Node

        .. note:: No parent is specified during construction. Relation must be
            set afterwards.
        """
        digest = engine.hash_pair(left.__value, right.__value)

        return cls(value=digest, left=left, right=right, parent=None)

    def ancestor(self, degree):
        """
        Detects and returns the node that is *degree* steps upwards within
        the containing tree.

        .. note:: Returns *None* if the requested degree exceeds possibilities.

        .. note:: Ancestor of degree 0 is the node itself, ancestor of degree
            1 is the node's parent, etc.

        :param degree: depth of ancenstry
        :type degree: int
        :returns: the ancestor corresdponding to the requested degree
        :rtype: Node
        """
        if degree == 0:
            return self

        if not self.__parent:
            return

        return self.__parent.ancestor(degree - 1)

    def recalculate_hash(self, engine):
        """
        Recalculates the node's value under account of the possibly new
        values of its children.

        :param engine: hash-engine to be used for digest computation
        :type engine: HashEngine
        """
        self.__value = engine.hash_pair(self.left.value, self.right.value)

    def __str__(self, encoding, level=0, indent=3, ignored=None):
        """
        Designed so that printing the node amounts to printing the subtree
        having that node as root (similar to what is printed at console when
        running the ``tree`` command of Unix based platforms).

        :param encoding: encoding type of the containing tree.
        :type encoding: str
        :param level: [optional] Defaults to 0. Must be left equal to the
            default value when called externally by the user. Increased by
            1 whenever the function is recursively called in order to keep
            track of depth while printing.
        :type level: int
        :param indent: [optional] Defaults to 3. The horizontal depth at which
            each level of the tree will be indented with respect to the
            previous one.
        :type indent: int
        :param ignored: [optional] Defaults to empty. Must be left equal to the
            *default* value when called externally by the user. Augmented
            appropriately whenever the function is recursively invoked in order
            to keep track of where vertical bars should be omitted.
        :type ignored: list
        :rtype: str

        .. note:: Left children appear above the right ones.
        """
        if level == 0:
            out = '\n'
            if not self.is_left_child() and not self.is_right_child():
                out += f' {L_BRACKET_SHORT}'
        else:
            out = (indent + 1) * ' '

        count = 1
        if ignored is None:
            ignored = []
        while count < level:
            out += f' {VERTICAL_BAR}' if count not in ignored else 2 * ' '
            out += indent * ' '
            count += 1

        if self.is_left_child():
            out += f' {T_BRACKET}'
        if self.is_right_child():
            out += f' {L_BRACKET_LONG}'
            ignored.append(level)

        checksum = self.get_checksum(encoding)
        out += f'{checksum}\n'

        if not self.is_leaf():
            args = (encoding, level + 1, indent, ignored)
            out += self.left.__str__(*args)
            out += self.right.__str__(*args)

        return out

    def serialize(self, encoding):
        """
        Returns a JSON dictionary with the node's characteristics as key-value pairs.

        :param encoding: encoding type of the containing tree.
        :type encoding: str
        :rtype: dict

        .. note:: The *parent* attribute is ommited from node serialization in
            order for circular reference error to be avoided.
        """
        out = {'hash': self.get_checksum(encoding)}

        if self.left:
            out.update({'left': self.left.serialize(encoding)})

        if self.right:
            out.update({'right': self.right.serialize(encoding)})

        return out

    def toJSONtext(self, encoding, indent=4):
        """
        Returns a JSON text with the node's characteristics as key-value pairs.

        :param encoding: encoding type of the containing tree.
        :type encoding: str
        :rtype: str

        .. note:: The *parent* attribute is ommited from node serialization in
            order for circular reference error to be avoided.
        """
        return json.dumps(self.serialize(encoding), sort_keys=True, indent=indent)


class Leaf(Node):
    """
    Merkle-tree leaf node.

    :param value: the digest to be stored by the leaf.
    :type value: bytes
    :param leaf: [optional] leaf leaf node. Defaults to *None*.
    :type leaf: Leaf
    :rtype: Leaf
    """

    __slots__ = ('__next',)

    def __init__(self, value, leaf=None):
        self.__next = leaf
        super().__init__(value)

    @property
    def next(self):
        return self.__next

    def set_next(self, leaf):
        self.__next = leaf

    @classmethod
    def from_data(cls, data, engine):
        """
        Creates a leaf storing the digest of the provided record under the
        provided hash engine.

        :param data: bytestring to encrypt
        :type data: bytes
        :param engine: hash-engine to be used for digest computation
        :type engine: HashEngine
        :returns: the created leaf
        :rtype: Leaf
        """
        return cls(engine.hash_data(data), leaf=None)

    @classmethod
    def from_file(cls, filepath, engine):
        """
        Creates a leaf storing the digest of the provided file's content under
        the provided hash function.

        :param filepath: Relative path of the file to encrypt with respect to
            the current working directory.
        :type filepath: str
        :param engine: hash-engine to be used for digest computation
        :type engine: HashEngine
        :returns: the created leaf
        :rtype: Leaf
        """
        return cls(engine.hash_file(filepath), leaf=None)
