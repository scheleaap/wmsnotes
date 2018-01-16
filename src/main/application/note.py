# -*- coding: utf-8 -*-
import io
import logging
from collections import namedtuple

import cyrusbus.bus

from notebook.aggregate import NotebookNode
from notebook.dao import NoteRepository
from notebook.dao.delayed_persist import DelayedPersistNoteRepository
from .event import APPLICATION_TOPIC

OpenNoteCommand = namedtuple('OpenNoteCommand', ['note_id'])
UpdateNodePayloadCommand = namedtuple('UpdateNodePayloadCommand', ['note_id', 'payload'])


class NoteOpened(object):
    def __init__(self, node: NotebookNode, payload: str):
        self.node = node
        self.payload = payload

    def __repr__(self):
        return '{cls}[{node}, payload length={len}]'.format(
            cls=self.__class__.__name__,
            len=len(self.payload) if self.payload is not None else '',
            **self.__dict__)


class NoteService(object):
    def __init__(self, note_repository: DelayedPersistNoteRepository, bus: cyrusbus.bus.Bus):
        self.log = logging.getLogger('{m}.{c}'.format(m=self.__class__.__module__, c=self.__class__.__name__))
        self.bus = bus
        self.note_repository = note_repository

        self.bus.subscribe(APPLICATION_TOPIC, self.on_event)

    def load_notebook(self):
        for node in self.note_repository.get_all_nodes():  # type: NotebookNode
            self.bus.publish(APPLICATION_TOPIC, node.create())

    def on_event(self, bus, event):
        self.log.debug(u'Event received: {event}'.format(event=event))

        if isinstance(event, OpenNoteCommand):  # type: OpenNoteCommand
            self.set_open_node(event.note_id)
        elif isinstance(event, UpdateNodePayloadCommand): # type: UpdateNodePayloadCommand
            self.update_node_payload(event.note_id, event.payload)
        else:
            self.log.debug(u'Unhandled event: {event}'.format(event=event))

    def _publish_node_event(self, event):
        if event is not None:
            self.bus.publish(APPLICATION_TOPIC, event)

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
        self._publish_node_event(event)

        # TODO: This should be done by another class reacting to the event
        if event is not None:
            self.note_repository.add_or_update_node(node)
