# -*- coding: utf-8 -*-
from notebook.aggregate import NotebookNode
from notebook.dao import NoteRepository
from notebook.storage import NodeDoesNotExistError


class InMemoryNoteRepository(NoteRepository):
    """Stores notes in memory.
    """

    def __init__(self):
        self.notes = dict()

    def add_or_update_node(self, node: NotebookNode):
        self.notes[node.node_id] = node

    def get_all_nodes(self):
        for node in self.notes.values():
            yield node

    def get_node(self, node_id) -> NotebookNode:
        if not self.has_node(node_id):
            raise NodeDoesNotExistError
        return self.notes[node_id]

    def has_node(self, node_id) -> bool:
        return node_id in self.notes
