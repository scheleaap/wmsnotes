# -*- coding: utf-8 -*-

from collections import namedtuple

__all__ = [
    'NotebookNode',
]


class NodeCreated(object):
    def __init__(self, node):
        self.node = node  # type: NotebookNode

    def __repr__(self):
        return '{cls}[{node}]'.format(cls=self.__class__.__name__, **self.__dict__)


class NodePayloadChanged(object):
    def __init__(self, node_id: str, new_payload: str):
        self.node_id = node_id
        self.new_payload = new_payload

    def __repr__(self):
        return '{cls}[{node_id}, new payload length={len}]'.format(
            cls=self.__class__.__name__,
            len=len(self.new_payload),
            **self.__dict__)


class FolderPath(object):
    @staticmethod
    def from_string(string_path: str):
        if string_path is None:
            return FolderPath([])
        else:
            stripped_string_path = string_path.strip()
            if stripped_string_path == '':
                return FolderPath([])
            else:
                return FolderPath(stripped_string_path.split('/'))

    def __init__(self, elements):
        self.elements = elements

    def __eq__(self, other):
        return \
            isinstance(other, self.__class__) and \
            self.elements == other.elements

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{cls}[{path}]'.format(
            cls=self.__class__.__name__,
            path='/'.join(self.elements),
            **self.__dict__
        )


class NotebookNode(object):
    """A node in a notebook.

    @ivar node_id: The id of the node.
    @ivar title: The title of the node.
    @ivar folder_path: The path of the node's folder.
    """

    def __init__(
            self,
            node_id: str,
            title: str,
            folder_path: FolderPath,
    ):
        """Constructor.

        @param node_id: See the class documentation.
        @param title: See the class documentation.
        @param folder_path: See the class documentation.
        """
        self._title = title
        self._node_id = node_id
        self._folder_path = folder_path

    def create(self) -> NodeCreated:
        return NodeCreated(self)

    @property
    def node_id(self):
        return self._node_id

    @property
    def folder_path(self):
        return self._folder_path

    # @folder_path.setter
    # def folder_path(self, folder_path):
    #     self._folder_path = folder_path

    @property
    def title(self):
        return self._title

    # @title.setter
    # def title(self, title):
    #     self._title = title

    def set_payload(self, payload) -> NodePayloadChanged:
        return NodePayloadChanged(self.node_id, payload)

    def __repr__(self):
        return '{cls}[id={_node_id}, folder={_folder_path}, title={_title}]'.format(
            cls=self.__class__.__name__,
            **self.__dict__
        )
