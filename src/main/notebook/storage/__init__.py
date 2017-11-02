# -*- coding: utf-8 -*-
from notebook.aggregate import NotebookNode

__all__ = [
    'NotebookStorage',
    'NodeDoesNotExistError',
]


class NotebookStorage:
    """Classes implementing this interface can store notebooks.
    """

    def get_all_nodes(self):
        """Loads the metadata of all nodes in the notebook.

        @return: An iterable returning NotebookNode objects.
        @raise IOError: If one or nodes cannot be read.
        @raise ParseError: If the file has an invalid syntax.
        """
        raise NotImplementedError(self.get_all_nodes.__name__)

    def get_node(self, node_id) -> NotebookNode:
        """Loads the metadata of a node in the notebook.

        @param node_id: The id of the node to be read.
        @return: A NotebookNode.
        @raise NodeDoesNotExistError: If a node with the id does not exist.
        @raise IOError: If the node cannot be read.
        @raise ParseError: If the file has an invalid syntax.
        """
        raise NotImplementedError(self.get_node.__name__)

    def get_node_payload(self, node_id, payload_name):
        """Loads a payload of a node in the notebook.

        @param node_id: The id of the node.
        @param payload_name: The name of the payload.
        @return: A file-like object with the payload data.
        @raise NodeDoesNotExistError: If a node with the id does not exist.
        @raise PayloadDoesNotExistError: If a payload with the name does not exist.
        @raise IOError: If the payload cannot be read.
        """
        raise NotImplementedError(self.get_node_payload.__name__)

    def has_node(self, node_id):
        """Returns whether a node exists within the notebook.

        @param node_id: The id of the node.
        @return Whether a node exists within the notebook.
        """
        raise NotImplementedError(self.has_node.__name__)

    def set_node_payload(self, node_id, payload_name, payload_file):
        """Sets a payload for a node.

        @param node_id: The id of the node.
        @param payload_name: The name of the new payload. Must be unique for the node.
        @param payload_file: A file-like object with the payload data.
        @raise NodeDoesNotExistError: If a node with the id does not exist.
        """
        raise NotImplementedError(self.set_node_payload.__name__)


class NodeDoesNotExistError(Exception):
    pass


class ParseError(Exception):
    pass


class PayloadDoesNotExistError(Exception):
    pass
