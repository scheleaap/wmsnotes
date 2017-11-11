# -*- coding: utf-8 -*-
import io

import cyrusbus.bus

from notebook.aggregate import NotebookNode
from notebook.dao import NoteRepository
from notebook.dao.delayed_persist import DelayedPersistNoteRepository
from .event import NODE_EVENTS_TOPIC, APPLICATION_TOPIC


class NoteOpened(object):
    def __init__(self, node: NotebookNode, payload: str):
        self.node = node
        self.payload = payload

    def __repr__(self):
        return '{cls}[{node}, payload length={len}]'.format(
            cls=self.__class__.__name__,
            len=len(self.payload) if self.payload is not None else '',
            **self.__dict__)


class Controller(object):
    def __init__(self, note_repository: DelayedPersistNoteRepository, bus: cyrusbus.bus.Bus):
        self.bus = bus
        self.note_repository = note_repository

    def load_notebook(self):
        for node in self.note_repository.get_all_nodes():  # type: NotebookNode
            self.bus.publish(NODE_EVENTS_TOPIC, node.create())

    def publish_node_event(self, event):
        if event is not None:
            self.bus.publish(NODE_EVENTS_TOPIC, event)

    def save(self):
        """Saves unsaved changes."""
        self.note_repository.persist()

    def set_open_node(self, node_id: str):
        """Sets the currently open node.

        @param node_id: The id of the node that should be open. May be None to indicate the currently open node should be closed.
        """
        if node_id is not None:
            node = self.note_repository.get_node(node_id)
            self.bus.publish(APPLICATION_TOPIC, NoteOpened(node, node.payload))
        else:
            # TODO: Replace with different event
            self.bus.publish(APPLICATION_TOPIC, NoteOpened(None, None))

    def update_node_payload(self, node_id: str, payload: str):
        """Updates the payload of a node.

        @param node_id: The id of the note to update.
        @param payload: The new payload.
        """
        node = self.note_repository.get_node(node_id)
        event = node.set_payload(payload)
        self.publish_node_event(event)

        # TODO: This should be done by another class reacting to the event
        if event is not None:
            self.note_repository.add_or_update_node(node)
