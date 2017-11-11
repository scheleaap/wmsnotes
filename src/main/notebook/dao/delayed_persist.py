# -*- coding: utf-8 -*-
from notebook.aggregate import NotebookNode
from notebook.dao import NoteRepository
from notebook.storage import NodeDoesNotExistError


class DelayedPersistNoteRepository(NoteRepository):
    """TODO
    """

    def __init__(self, repository1: NoteRepository, repository2: NoteRepository):
        self.repository1 = repository1
        self.repository2 = repository2
        self.node_ids_added_or_updated = set()
        self.node_ids_deleted = set()

    def add_or_update_node(self, node: NotebookNode):
        self.repository1.add_or_update_node(node)
        self.node_ids_added_or_updated.add(node.node_id)

    def get_all_nodes(self):
        nodes1_ids = set()
        for node in self.repository1.get_all_nodes():
            nodes1_ids.add(node.node_id)
            yield node
        for node in self.repository2.get_all_nodes():
            if node.node_id not in nodes1_ids:
                yield node

    def get_node(self, node_id) -> NotebookNode:
        if self.repository1.has_node(node_id):
            return self.repository1.get_node(node_id)
        else:
            return self.repository2.get_node(node_id)

    def has_node(self, node_id) -> bool:
        return self.repository1.has_node(node_id) or \
               self.repository2.has_node(node_id)

    def persist(self):
        for node in self.repository1.get_all_nodes():
            self.repository2.add_or_update_node(node)
