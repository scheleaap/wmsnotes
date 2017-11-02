# -*- coding: utf-8 -*-
import io

import cyrusbus.bus

from notebook.aggregate import NotebookNode
from notebook.storage import NotebookStorage
from .event import NODE_EVENTS_TOPIC, APPLICATION_TOPIC


class OpenNodeChanged(object):
    def __init__(self, node: NotebookNode, payload: str):
        self.node = node
        self.payload = payload

    def __repr__(self):
        return '{cls}[{node}, payload length={len}]'.format(
            cls=self.__class__.__name__,
            len=len(self.payload) if self.payload is not None else '',
            **self.__dict__)


class Controller(object):
    def __init__(self, notebook_storage: NotebookStorage, bus: cyrusbus.bus.Bus):
        self.bus = bus
        self.notebook_storage = notebook_storage

    def load_notebook(self):
        for node in self.notebook_storage.get_all_nodes():  # type: NotebookNode
            self.bus.publish(NODE_EVENTS_TOPIC, node.create())

    def publish_node_event(self, event):
        if event is not None:
            self.bus.publish(NODE_EVENTS_TOPIC, event)

    def set_open_node(self, node_id: str):
        """Sets the currently open node.

        @param node_id: The id of the node that should be open. May be None to indicate the currently open node should be closed.
        """
        if node_id is not None:
            node = self.notebook_storage.get_node(node_id)
            payload_file = self.notebook_storage.get_node_payload(node_id, 'main')
            try:
                payload = str(payload_file.read(), encoding='utf-8')
            finally:
                payload_file.close()
            self.bus.publish(APPLICATION_TOPIC, OpenNodeChanged(node, payload))
        else:
            self.bus.publish(APPLICATION_TOPIC, OpenNodeChanged(None, None))

    def update_node_payload(self, node_id: str, payload: str):
        """Updates the payload of a node.

        @param node_id: The id of the note to update.
        @param payload: The new payload.
        """
        node = self.notebook_storage.get_node(node_id)
        event = node.set_payload(payload)
        self.publish_node_event(event)

        # TODO: This should be done by another class reacting to the event
        if event is not None:
            self.notebook_storage.set_node_payload(node_id, 'main', io.BytesIO(bytes(payload, encoding='utf-8')))
