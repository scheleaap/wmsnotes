# -*- coding: utf-8 -*-
from notebook.aggregate import NotebookNode


class NoteRepository(object):
    """Classes implementing this interface can store notebooks.
    """

    def add_or_update_node(self, node):
        """TODO
        """
        raise NotImplementedError(self.has_node.__name__)

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

    def has_node(self, node_id) -> bool:
        """Returns whether a node exists within the notebook.

        @param node_id: The id of the node.
        @return Whether a node exists within the notebook.
        """
        raise NotImplementedError(self.has_node.__name__)
