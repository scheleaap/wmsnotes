# -*- coding: utf-8 -*-
import io

from notebook.aggregate import NotebookNode
from notebook.dao import NoteRepository
from notebook.storage import NotebookStorage


class StorageNoteRepository(NoteRepository):
    """TODO
    """

    def __init__(self, storage: NotebookStorage):
        self.storage = storage

    def add_or_update_node(self, node: NotebookNode):
        self.storage.set_node_payload(node.node_id, 'main', io.BytesIO(bytes(node.payload, encoding='utf-8')))

    def get_all_nodes(self):
        for node in self.storage.get_all_nodes():
            yield node

    def get_node(self, node_id) -> NotebookNode:
        node = self.storage.get_node(node_id)
        payload_file = self.storage.get_node_payload(node_id, 'main')
        try:
            # TODO
            node._payload = str(payload_file.read(), encoding='utf-8')
        finally:
            payload_file.close()
        return node

    def has_node(self, node_id) -> bool:
        return self.storage.has_node(node_id)
